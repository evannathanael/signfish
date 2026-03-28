from __future__ import annotations

from pathlib import Path

from ml.src.asl_recognizer.model import ModelBundle, load_model_bundle


def load_asl_bundle(weights_path: str | Path | None = None) -> ModelBundle:
    default_path = Path(__file__).resolve().parents[3] / "ml" / "models" / "asl_landmark_model.pt"
    return load_model_bundle(weights_path or default_path)
