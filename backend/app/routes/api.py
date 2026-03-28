from fastapi import APIRouter, HTTPException

from app.schemas.session import (
    SessionAnswerRequest,
    SessionAnswerResponse,
    SessionStartRequest,
    SessionStateResponse,
)
from app.services.session_service import session_service

router = APIRouter(tags=["practice"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sessions/start", response_model=SessionStateResponse)
def start_session(payload: SessionStartRequest) -> SessionStateResponse:
    return session_service.create_session(payload)


@router.post("/sessions/{session_id}/answer", response_model=SessionAnswerResponse)
def answer_prompt(session_id: str, payload: SessionAnswerRequest) -> SessionAnswerResponse:
    try:
        return session_service.submit_answer(session_id=session_id, payload=payload)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/sessions/{session_id}", response_model=SessionStateResponse)
def get_session(session_id: str) -> SessionStateResponse:
    try:
        return session_service.get_state(session_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
