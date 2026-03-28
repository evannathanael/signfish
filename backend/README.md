# SignFish Backend

FastAPI backend for SignFish frontend integration.

## Run
```bash
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
