# SignFish

SignFish is an ASL-powered typing and practice app with a web frontend, a FastAPI backend, and an ML workspace for dataset preparation, training, and evaluation.

## Repo Layout

- `frontend/`: website UI
- `backend/`: FastAPI inference service
- `ml/`: ASL training code, data workflow, and trained artifacts

## Current ASL Integration

- The ASL landmark classifier now lives in `ml/src/asl_recognizer/`.
- The current trained model artifact is stored in `ml/models/`.
- A local launcher script is available at `run_asl.sh` for smoke training, webcam inference, and the OpenCV viewer UI.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install kagglehub scikit-learn tqdm
```

Run the local ASL viewer:

```bash
ASL_CAMERA_INDEX=1 ./run_asl.sh smoke ui-only
```

Train with combined datasets:

```bash
ASL_DATASET_PATH=/path/to/ASL-Alphabet-Dataset/Data/train \
ASL_EXTRA_DATASET_PATHS="/path/to/mendeley-48dg9vhmyk" \
ASL_FULL_KAGGLE_HANDLE=grassknoted/asl-alphabet \
./run_asl.sh full train-only
```
