# SignFish

SignFish is an American Sign Language (ASL) practice platform that combines:

- a **Next.js frontend** for user interaction and practice flows,
- a **FastAPI backend** for prediction/inference APIs, and
- an **ML workspace** for dataset prep, model training, and live inference tools.

This README is intended for the **main branch** and gives a clean setup path for local development.

## Repository Structure

- `frontend/` — Next.js application (pages, components, hooks, services)
- `backend/` — FastAPI service (routes, schemas, services, model/session loaders)
- `ml/` — ASL recognizer code, scripts, model artifacts, and ML docs
- `docs/` — additional project documentation
- `run_asl.sh` — convenience script for local ML workflows

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+
- Webcam (for live ASL capture/inference)

## Quick Start (Local)

### 1) Clone and enter the repo

```bash
git clone <your-repo-url>
cd signfish
```

### 2) Backend setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Start backend:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000` by default.

### 4) Optional ML extras

Install additional ML utilities when working in `ml/`:

```bash
pip install kagglehub scikit-learn tqdm
```

## ASL Workflow Helpers

The repository includes a helper script for smoke checks, training, and UI inference:

```bash
./run_asl.sh smoke ui-only
```

Example training with multiple datasets:

```bash
ASL_DATASET_PATH=/path/to/ASL-Alphabet-Dataset/Data/train \
ASL_EXTRA_DATASET_PATHS="/path/to/mendeley-48dg9vhmyk" \
ASL_FULL_KAGGLE_HANDLE=grassknoted/asl-alphabet \
./run_asl.sh full train-only
```

## Where to Read More

- Frontend details: `frontend/README.md`
- Backend details: `backend/README.md`
- ML details: `ml/README.md`
- ML models and metrics: `ml/models/README.md`, `ml/models/*.json`

## Contributing

1. Create a feature branch from `main`.
2. Make focused changes with clear commit messages.
3. Run relevant local checks.
4. Open a pull request with a concise summary and test evidence.

## License

Add your project license information here (for example: MIT, Apache-2.0, or proprietary internal use).
