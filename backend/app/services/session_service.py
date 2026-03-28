from datetime import datetime, timezone
from random import choices
from string import ascii_uppercase
from uuid import uuid4

from app.models.session import Session, SessionAnswer, SessionPrompt
from app.schemas.session import (
    AnswerIn,
    SessionStartRequest,
    SessionStartResponse,
    SessionSummaryResponse,
)
from app.utils.metrics import calculate_accuracy, calculate_chars_per_minute


class SessionService:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(self, payload: SessionStartRequest) -> SessionStartResponse:
        session_id = str(uuid4())
        prompts = [
            SessionPrompt(id=index, target=char)
            for index, char in enumerate(choices(ascii_uppercase, k=payload.prompt_count))
        ]
        session = Session(id=session_id, prompts=prompts, started_at=datetime.now(timezone.utc))
        self._sessions[session_id] = session
        return SessionStartResponse(
            session_id=session.id,
            started_at=session.started_at,
            prompts=[{"id": prompt.id, "target": prompt.target} for prompt in prompts],
        )

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session {session_id} was not found")
        return session

    def submit_answers(
        self,
        session_id: str,
        answers: list[AnswerIn],
    ) -> SessionSummaryResponse:
        session = self.get_session(session_id)
        answer_models = [
            SessionAnswer(
                prompt_id=answer.prompt_id,
                input_char=answer.input_char,
                response_time_ms=answer.response_time_ms,
            )
            for answer in answers
        ]
        session.answers = answer_models
        session.submitted_at = datetime.now(timezone.utc)

        prompt_by_id = {prompt.id: prompt for prompt in session.prompts}
        correct = 0
        total_time_ms = 0

        for answer in answer_models:
            prompt = prompt_by_id.get(answer.prompt_id)
            if prompt and prompt.target == answer.input_char:
                correct += 1
            total_time_ms += answer.response_time_ms

        answered = len(answer_models)
        accuracy = calculate_accuracy(correct=correct, total=answered)
        cpm = calculate_chars_per_minute(total_chars=answered, total_time_ms=total_time_ms)

        return SessionSummaryResponse(
            session_id=session.id,
            total_prompts=len(session.prompts),
            answered_prompts=answered,
            correct=correct,
            accuracy=accuracy,
            chars_per_minute=cpm,
        )


session_service = SessionService()
