# Backend

FastAPI service for SignFish inference and application APIs.

## Current state

- `app/main.py` boots the API
- `app/models/loader.py` loads the trained ASL model from `ml/models/`
- `app/services/inference.py` contains the ASL runtime inference pipeline
- `app/routes/predict.py` is the first prediction route stub

## Run locally

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```
