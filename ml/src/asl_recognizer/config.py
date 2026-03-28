from pathlib import Path

STATIC_ASL_LABELS = list("ABCDEFGHIKLMNOPQRSTUVWXY")
DYNAMIC_ASL_LABELS = ["J", "Z"]

HAND_LANDMARK_COUNT = 21

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_ROOT = PROJECT_ROOT / "ml"
DEFAULT_DATASET_DIR = str(ML_ROOT / "data" / "raw" / "asl_alphabet")
DEFAULT_WEIGHTS_PATH = str(ML_ROOT / "models" / "asl_landmark_model.pt")
