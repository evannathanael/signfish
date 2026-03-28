# SignFish Backend

FastAPI backend for SignFish frontend integration.

## Run
```bash
# Backend

FastAPI service for SignFish inference and application APIs.

## Current state

- `app/main.py` boots the API
- `app/models/loader.py` loads the trained ASL model from `ml/models/`
- `app/services/inference.py` contains the ASL runtime inference pipeline
- `app/routes/predict.py` is the first prediction route stub
# Signfish Backend

Minimal FastAPI backend scaffold for ASL fingerspelling practice.

## Run locally

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --reload
```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Letter inference contract
- Frontend sends `POST /api/infer` with:
  - `frame` (base64 webcam frame)
  - `question` (prompt shown to player)
- Backend extracts expected letter from `question` and compares it with model output letter.
- Response includes:
  - `predicted_letter`
  - `expected_letter`
  - `match`
  - `confidence`

## Optional model integration
Set these env vars to connect the real model service:

```bash
TINYFISH_MODEL_URL=http://localhost:9000/infer
TINYFISH_MODEL_TIMEOUT=5
MODEL_FALLBACK_LETTER=A
```
uvicorn app.main:app --reload
```

## Practice flow

1. Frontend calls `POST /api/v1/sessions/start`.
2. API returns `active_prompts` with **10 letters visible by default**.
3. Frontend calls `POST /api/v1/sessions/{session_id}/answer` per keypress.
4. If the answer is correct, backend advances to the next letter and returns a shifted `active_prompts` window immediately.

## Initial endpoints

- `GET /` - root status message
- `GET /api/v1/health` - health check
- `POST /api/v1/sessions/start` - create randomized fingerspelling prompts and get current state
- `GET /api/v1/sessions/{session_id}` - fetch current state for a session
- `POST /api/v1/sessions/{session_id}/answer` - submit one answer and receive updated 10-letter window
