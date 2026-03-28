# Signfish Backend

Minimal FastAPI backend scaffold for ASL fingerspelling practice.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Initial endpoints

- `GET /` - root status message
- `GET /api/v1/health` - health check
- `POST /api/v1/sessions/start` - create randomized fingerspelling prompts
- `GET /api/v1/sessions/{session_id}` - fetch a session
- `POST /api/v1/sessions/{session_id}/submit` - submit answers and receive summary metrics
