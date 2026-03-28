from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from ml.src.asl_recognizer.model import ModelBundle, load_model_bundle


def load_asl_bundle(weights_path: Optional[Union[str, Path]] = None) -> ModelBundle:
    default_path = Path(__file__).resolve().parents[3] / "ml" / "models" / "asl_landmark_model.pt"
    return load_model_bundle(weights_path or default_path)
