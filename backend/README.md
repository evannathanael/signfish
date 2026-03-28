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
