from fastapi import APIRouter, HTTPException

from app.schemas.session import (
    SessionStartRequest,
    SessionStartResponse,
    SessionSubmitRequest,
    SessionSummaryResponse,
)
from app.services.session_service import session_service

router = APIRouter(tags=["practice"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sessions/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest) -> SessionStartResponse:
    return session_service.create_session(payload)


@router.post("/sessions/{session_id}/submit", response_model=SessionSummaryResponse)
def submit_session(
    session_id: str,
    payload: SessionSubmitRequest,
) -> SessionSummaryResponse:
    try:
        return session_service.submit_answers(session_id=session_id, answers=payload.answers)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/sessions/{session_id}", response_model=SessionStartResponse)
def get_session(session_id: str) -> SessionStartResponse:
    try:
        session = session_service.get_session(session_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return SessionStartResponse(
        session_id=session.id,
        started_at=session.started_at,
        prompts=[{"id": prompt.id, "target": prompt.target} for prompt in session.prompts],
    )
