from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
import random

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .config import DEFAULT_DATASET_DIR, DEFAULT_WEIGHTS_PATH
from .data import build_dataset
from .model import ASLClassifier, save_model_bundle, standardize_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train an ASL alphabet recognizer.")
    parser.add_argument(
        "--dataset",
        action="append",
        default=[],
        help="Dataset root directory. Repeat this flag to combine multiple extracted datasets.",
    )
    parser.add_argument(
        "--kaggle-handle",
        action="append",
        default=[],
        help="Optional Kaggle dataset handle. Repeat this flag to combine multiple Kaggle datasets.",
    )
    parser.add_argument("--output", default=DEFAULT_WEIGHTS_PATH, help="Output model path.")
    parser.add_argument("--epochs", type=int, default=80, help="Training epochs.")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size.")
    parser.add_argument("--learning-rate", type=float, default=1e-3, help="Learning rate.")
    parser.add_argument("--weight-decay", type=float, default=1e-4, help="AdamW weight decay.")
    parser.add_argument("--dropout", type=float, default=0.35, help="Dropout rate.")
    parser.add_argument(
        "--hidden-sizes",
        default="256,128",
        help="Comma-separated hidden layer sizes, for example 256,128.",
    )
    parser.add_argument(
        "--val-split", type=float, default=0.15, help="Validation split fraction."
    )
    parser.add_argument(
        "--augmentations-per-image",
        type=int,
        default=4,
        help="How many synthetic feature-space augmentations to add per image.",
    )
    parser.add_argument(
        "--max-samples-per-class",
        type=int,
        default=0,
        help="Optional cap on how many original images to load per class for faster smoke tests.",
    )
    parser.add_argument("--patience", type=int, default=12, help="Early stopping patience.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def parse_hidden_sizes(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def resolve_dataset_argument(args: argparse.Namespace) -> str:
    dataset_inputs = list(args.dataset) if args.dataset else [DEFAULT_DATASET_DIR]
    if not args.kaggle_handle:
        return dataset_inputs[0] if len(dataset_inputs) == 1 else dataset_inputs

    try:
        import kagglehub
        from kagglehub.exceptions import DataCorruptionError
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "kagglehub is not installed. Run `pip install kagglehub` or `pip install -r requirements.txt`."
        ) from exc

    downloaded_paths: list[str] = []
    for handle in args.kaggle_handle:
        try:
            downloaded_path = kagglehub.dataset_download(handle)
        except DataCorruptionError:
            print(f"Kaggle download checksum failed for {handle}. Retrying with a forced re-download...")
            try:
                downloaded_path = kagglehub.dataset_download(handle, force_download=True)
            except DataCorruptionError as exc:
                raise RuntimeError(
                    f"Kaggle dataset download failed checksum verification twice for {handle}. "
                    "This usually means the cached archive is corrupted or the download was interrupted. "
                    "Retry later, or download/extract the dataset manually and pass it with "
                    "`--dataset /path/to/extracted/dataset`."
                ) from exc

        print(f"Downloaded Kaggle dataset to: {downloaded_path}")
        downloaded_paths.append(downloaded_path)

    combined_inputs = dataset_inputs + downloaded_paths
    return combined_inputs[0] if len(combined_inputs) == 1 else combined_inputs


def evaluate_model(
    model: ASLClassifier,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, np.ndarray, np.ndarray]:
    model.eval()
    total_loss = 0.0
    all_predictions = []
    all_targets = []

    with torch.no_grad():
        for batch_features, batch_labels in loader:
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)

            logits = model(batch_features)
            loss = criterion(logits, batch_labels)
            total_loss += loss.item() * batch_features.size(0)

            predictions = torch.argmax(logits, dim=1)
            all_predictions.append(predictions.cpu().numpy())
            all_targets.append(batch_labels.cpu().numpy())

    predictions = np.concatenate(all_predictions)
    targets = np.concatenate(all_targets)
    average_loss = total_loss / len(loader.dataset)
    return average_loss, predictions, targets


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    hidden_sizes = parse_hidden_sizes(args.hidden_sizes)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset_arg = resolve_dataset_argument(args)

    dataset = build_dataset(
        dataset_arg,
        augmentations_per_image=args.augmentations_per_image,
        max_samples_per_class=args.max_samples_per_class,
        seed=args.seed,
    )

    class_counts = np.bincount(dataset.labels, minlength=len(dataset.class_names))
    test_size = max(1, math.ceil(len(dataset.labels) * args.val_split))
    train_size = len(dataset.labels) - test_size
    can_stratify = (
        len(dataset.class_names) > 1
        and int(np.min(class_counts)) >= 2
        and test_size >= len(dataset.class_names)
        and train_size >= len(dataset.class_names)
    )

    if can_stratify:
        x_train, x_val, y_train, y_val = train_test_split(
            dataset.features,
            dataset.labels,
            test_size=args.val_split,
            random_state=args.seed,
            stratify=dataset.labels,
        )
    else:
        print(
            "Dataset is too small or imbalanced for a stratified validation split. "
            "Using the full dataset for both training and validation in this smoke run."
        )
        x_train = dataset.features
        x_val = dataset.features
        y_train = dataset.labels
        y_val = dataset.labels

    feature_mean = x_train.mean(axis=0)
    feature_std = x_train.std(axis=0)

    x_train = standardize_features(x_train, feature_mean, feature_std)
    x_val = standardize_features(x_val, feature_mean, feature_std)

    train_tensor = TensorDataset(
        torch.tensor(x_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    val_tensor = TensorDataset(
        torch.tensor(x_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.long),
    )

    train_loader = DataLoader(train_tensor, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_tensor, batch_size=args.batch_size, shuffle=False)

    class_counts = np.bincount(y_train, minlength=len(dataset.class_names))
    class_weights = class_counts.sum() / np.maximum(class_counts, 1)
    class_weights = class_weights / class_weights.mean()

    model = ASLClassifier(
        input_dim=x_train.shape[1],
        num_classes=len(dataset.class_names),
        hidden_sizes=hidden_sizes,
        dropout=args.dropout,
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=torch.tensor(class_weights, dtype=torch.float32, device=device)
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )

    best_state = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")
    best_epoch = 0
    patience_left = args.patience

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss = 0.0

        for batch_features, batch_labels in train_loader:
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)

            optimizer.zero_grad(set_to_none=True)
            logits = model(batch_features)
            loss = criterion(logits, batch_labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * batch_features.size(0)

        train_loss = running_loss / len(train_loader.dataset)
        val_loss, val_predictions, val_targets = evaluate_model(
            model, val_loader, criterion, device
        )
        val_accuracy = accuracy_score(val_targets, val_predictions)

        print(
            f"Epoch {epoch:03d} | train_loss={train_loss:.4f} | "
            f"val_loss={val_loss:.4f} | val_acc={val_accuracy:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())
            best_epoch = epoch
            patience_left = args.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                print(f"Early stopping at epoch {epoch}.")
                break

    model.load_state_dict(best_state)
    final_val_loss, val_predictions, val_targets = evaluate_model(model, val_loader, criterion, device)
    val_accuracy = accuracy_score(val_targets, val_predictions)
    val_f1 = f1_score(val_targets, val_predictions, average="macro")

    metrics = {
        "best_epoch": best_epoch,
        "dataset_root": dataset.dataset_root,
        "validation_loss": float(final_val_loss),
        "validation_accuracy": float(val_accuracy),
        "validation_macro_f1": float(val_f1),
        "class_names": dataset.class_names,
        "samples_per_class": dataset.samples_per_class,
        "source_counts": dataset.source_counts,
        "skipped_files_count": len(dataset.skipped_files),
        "classification_report": classification_report(
            val_targets,
            val_predictions,
            labels=list(range(len(dataset.class_names))),
            target_names=dataset.class_names,
            output_dict=True,
            zero_division=0,
        ),
    }

    save_model_bundle(
        output_path=args.output,
        model=model,
        labels=dataset.class_names,
        feature_mean=feature_mean,
        feature_std=feature_std,
        hidden_sizes=hidden_sizes,
        dropout=args.dropout,
        metadata=metrics,
    )

    metrics_path = Path(args.output).with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2))

    print(f"Saved model to {args.output}")
    print(f"Saved metrics to {metrics_path}")
    print(f"Validation accuracy: {val_accuracy:.4f}")
    print(f"Validation macro F1: {val_f1:.4f}")


if __name__ == "__main__":
    main()
