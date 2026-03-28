from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn


class ASLClassifier(nn.Module):
    def __init__(
        self,
        input_dim: int,
        num_classes: int,
        hidden_sizes: tuple[int, ...] = (256, 128),
        dropout: float = 0.35,
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        previous_dim = input_dim
        for hidden_dim in hidden_sizes:
            layers.extend(
                [
                    nn.Linear(previous_dim, hidden_dim),
                    nn.BatchNorm1d(hidden_dim),
                    nn.GELU(),
                    nn.Dropout(dropout),
                ]
            )
            previous_dim = hidden_dim

        layers.append(nn.Linear(previous_dim, num_classes))
        self.network = nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


@dataclass
class ModelBundle:
    model: ASLClassifier
    labels: list[str]
    feature_mean: np.ndarray
    feature_std: np.ndarray
    metadata: dict[str, Any]


@dataclass
class PredictionResult:
    top_label: str
    top_confidence: float
    top_index: int
    top_k: list[tuple[str, float]]


def standardize_features(
    features: np.ndarray, feature_mean: np.ndarray, feature_std: np.ndarray
) -> np.ndarray:
    return (features - feature_mean) / (feature_std + 1e-6)


def predict_top_k(
    bundle: ModelBundle,
    standardized_features: np.ndarray,
    device: str | torch.device = "cpu",
    k: int = 3,
) -> PredictionResult:
    feature_tensor = torch.tensor(
        standardized_features, dtype=torch.float32, device=device
    ).unsqueeze(0)

    with torch.no_grad():
        logits = bundle.model(feature_tensor)
        probabilities = torch.softmax(logits, dim=1)[0].cpu().numpy()

    sorted_indices = np.argsort(probabilities)[::-1]
    top_index = int(sorted_indices[0])
    top_k = [
        (bundle.labels[int(index)], float(probabilities[int(index)]))
        for index in sorted_indices[:k]
    ]

    return PredictionResult(
        top_label=bundle.labels[top_index],
        top_confidence=float(probabilities[top_index]),
        top_index=top_index,
        top_k=top_k,
    )


def save_model_bundle(
    output_path: str | Path,
    model: ASLClassifier,
    labels: list[str],
    feature_mean: np.ndarray,
    feature_std: np.ndarray,
    hidden_sizes: tuple[int, ...],
    dropout: float,
    metadata: dict[str, Any] | None = None,
) -> None:
    checkpoint = {
        "state_dict": model.state_dict(),
        "labels": labels,
        "feature_mean": feature_mean.astype(np.float32),
        "feature_std": feature_std.astype(np.float32),
        "hidden_sizes": tuple(hidden_sizes),
        "dropout": float(dropout),
        "input_dim": int(feature_mean.shape[0]),
        "metadata": metadata or {},
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, output_path)


def load_model_bundle(
    weights_path: str | Path, device: str | torch.device = "cpu"
) -> ModelBundle:
    checkpoint = torch.load(weights_path, map_location=device, weights_only=False)
    model = ASLClassifier(
        input_dim=int(checkpoint["input_dim"]),
        num_classes=len(checkpoint["labels"]),
        hidden_sizes=tuple(checkpoint["hidden_sizes"]),
        dropout=float(checkpoint["dropout"]),
    )
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()

    return ModelBundle(
        model=model,
        labels=list(checkpoint["labels"]),
        feature_mean=np.asarray(checkpoint["feature_mean"], dtype=np.float32),
        feature_std=np.asarray(checkpoint["feature_std"], dtype=np.float32),
        metadata=dict(checkpoint.get("metadata", {})),
    )
