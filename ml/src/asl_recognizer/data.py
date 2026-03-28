from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import cv2
import numpy as np
from tqdm import tqdm

from .config import STATIC_ASL_LABELS
from .features import (
    augment_normalized_landmarks,
    build_feature_vector,
    make_feature_vector,
)
from .hand_detection import HandDetector

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass
class DatasetSummary:
    features: np.ndarray
    labels: np.ndarray
    class_names: list[str]
    skipped_files: list[str]
    samples_per_class: dict[str, int]
    dataset_root: str
    source_counts: dict[str, int]

IGNORED_LABEL_NAMES = {
    "DELETE",
    "DEL",
    "SPACE",
    "NOTHING",
    "BLANK",
    "BACKGROUND",
}


def image_files_for_directory(label_dir: Path) -> list[Path]:
    return sorted(
        path for path in label_dir.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS and path.is_file()
    )


def normalize_label_name(value: str) -> str | None:
    cleaned = "".join(character for character in value.upper() if character.isalnum())
    if not cleaned or cleaned in IGNORED_LABEL_NAMES:
        return None
    if len(cleaned) == 1 and cleaned in STATIC_ASL_LABELS:
        return cleaned
    return None


def coerce_dataset_dirs(dataset_dirs: str | Path | Sequence[str | Path]) -> list[Path]:
    if isinstance(dataset_dirs, (str, Path)):
        values: Iterable[str | Path] = [dataset_dirs]
    else:
        values = dataset_dirs
    return [Path(value).expanduser() for value in values]


def find_label_directories(dataset_dir: Path, labels: Sequence[str]) -> dict[str, list[Path]]:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_dir}")

    label_set = set(labels)
    directories_by_label: dict[str, list[Path]] = {label: [] for label in labels}
    candidate_dirs = [dataset_dir] + [path for path in dataset_dir.rglob("*") if path.is_dir()]

    for candidate in candidate_dirs:
        label = normalize_label_name(candidate.name)
        if label not in label_set:
            continue
        if image_files_for_directory(candidate):
            directories_by_label[label].append(candidate)

    directories_by_label = {
        label: sorted({directory.resolve() for directory in directories}, key=str)
        for label, directories in directories_by_label.items()
        if directories
    }

    if not directories_by_label:
        raise ValueError(
            f"No ASL letter folders with images were found under {dataset_dir}. "
            "Expected folders named like A, B, C, and so on."
        )

    return directories_by_label


def build_dataset(
    dataset_dir: str | Path | Sequence[str | Path],
    labels: Sequence[str] = STATIC_ASL_LABELS,
    augmentations_per_image: int = 4,
    max_samples_per_class: int = 0,
    seed: int = 7,
) -> DatasetSummary:
    dataset_roots = coerce_dataset_dirs(dataset_dir)
    if not dataset_roots:
        raise ValueError("At least one dataset directory is required.")

    rng = np.random.default_rng(seed)
    feature_rows: list[np.ndarray] = []
    label_rows: list[int] = []
    skipped_files: list[str] = []
    class_names: list[str] = []
    samples_per_class: dict[str, int] = {}
    source_counts: dict[str, int] = {}

    directories_by_label: dict[str, list[Path]] = {label: [] for label in labels}
    for dataset_root in dataset_roots:
        found_directories = find_label_directories(dataset_root, labels=labels)
        for label, directories in found_directories.items():
            directories_by_label[label].extend(directories)

    directories_by_label = {
        label: directories
        for label, directories in directories_by_label.items()
        if directories
    }
    if not directories_by_label:
        raise ValueError("No valid ASL alphabet image folders were found in the provided datasets.")

    with HandDetector(
        running_mode="image",
        num_hands=1,
        min_hand_detection_confidence=0.55,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as detector:
        for label in labels:
            if label not in directories_by_label:
                continue
            label_feature_rows: list[np.ndarray] = []
            remaining_original_images = max_samples_per_class if max_samples_per_class > 0 else None
            label_directories = directories_by_label[label]
            for label_dir in label_directories:
                files = image_files_for_directory(label_dir)
                if remaining_original_images is not None:
                    files = files[:remaining_original_images]
                for image_path in tqdm(files, desc=f"Loading {label}", leave=False):
                    image = cv2.imread(str(image_path))
                    if image is None:
                        skipped_files.append(str(image_path))
                        continue

                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    detections = detector.detect_image(rgb_image)
                    if not detections:
                        skipped_files.append(str(image_path))
                        continue

                    detection = detections[0]
                    handedness = detection.handedness
                    landmarks = detection.landmarks
                    base_features, normalized_landmarks = make_feature_vector(
                        landmarks, handedness=handedness
                    )

                    label_feature_rows.append(base_features)
                    source_key = str(label_dir.parent)
                    source_counts[source_key] = source_counts.get(source_key, 0) + 1

                    for _ in range(augmentations_per_image):
                        augmented = augment_normalized_landmarks(normalized_landmarks, rng=rng)
                        label_feature_rows.append(build_feature_vector(augmented))

                    if remaining_original_images is not None:
                        remaining_original_images -= 1
                        if remaining_original_images <= 0:
                            break
                if remaining_original_images is not None and remaining_original_images <= 0:
                    break

            if not label_feature_rows:
                continue

            class_index = len(class_names)
            class_names.append(label)
            samples_per_class[label] = len(label_feature_rows)
            feature_rows.extend(label_feature_rows)
            label_rows.extend([class_index] * len(label_feature_rows))

    if not feature_rows:
        raise ValueError(
            "No training samples were extracted. Check that the dataset images contain a clearly visible hand."
        )

    return DatasetSummary(
        features=np.asarray(feature_rows, dtype=np.float32),
        labels=np.asarray(label_rows, dtype=np.int64),
        class_names=class_names,
        skipped_files=skipped_files,
        samples_per_class=samples_per_class,
        dataset_root=";".join(str(path) for path in dataset_roots),
        source_counts=source_counts,
    )
