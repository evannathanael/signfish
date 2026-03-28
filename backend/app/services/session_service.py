from datetime import datetime, timezone
from random import choices
from string import ascii_uppercase
from uuid import uuid4

from app.models.session import Session, SessionAnswer, SessionPrompt
from app.schemas.session import (
    SessionAnswerRequest,
    SessionAnswerResponse,
    SessionStartRequest,
    SessionStateResponse,
)
from app.utils.metrics import calculate_accuracy, calculate_chars_per_minute


class SessionService:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._visible_prompt_count_by_session: dict[str, int] = {}

    def create_session(self, payload: SessionStartRequest) -> SessionStateResponse:
        session_id = str(uuid4())
        prompts = [
            SessionPrompt(id=index, target=char)
            for index, char in enumerate(choices(ascii_uppercase, k=payload.prompt_count))
        ]

        session = Session(id=session_id, prompts=prompts, started_at=datetime.now(timezone.utc))
        self._sessions[session_id] = session
        self._visible_prompt_count_by_session[session_id] = payload.visible_prompt_count
        return self._build_state(session)

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session {session_id} was not found")
        return session

    def get_state(self, session_id: str) -> SessionStateResponse:
        return self._build_state(self.get_session(session_id))

    def submit_answer(
        self,
        session_id: str,
        payload: SessionAnswerRequest,
    ) -> SessionAnswerResponse:
        session = self.get_session(session_id)

        if self._is_completed(session):
            state = self._build_state(session)
            return SessionAnswerResponse(
                correct=False,
                expected_char="",
                received_char=payload.input_char,
                state=state,
            )

        current_prompt = session.prompts[session.current_index]
        is_correct = payload.input_char == current_prompt.target

        session.total_response_time_ms += payload.response_time_ms
        session.answers.append(
            SessionAnswer(
                prompt_id=current_prompt.id,
                input_char=payload.input_char,
                response_time_ms=payload.response_time_ms,
                is_correct=is_correct,
            )
        )

        if is_correct:
            session.correct_count += 1
            session.current_index += 1
            if self._is_completed(session):
                session.submitted_at = datetime.now(timezone.utc)

        return SessionAnswerResponse(
            correct=is_correct,
            expected_char=current_prompt.target,
            received_char=payload.input_char,
            state=self._build_state(session),
        )

    def _build_state(self, session: Session) -> SessionStateResponse:
        attempted = len(session.answers)
        accuracy = calculate_accuracy(correct=session.correct_count, total=attempted)
        chars_per_minute = calculate_chars_per_minute(
            total_chars=session.correct_count,
            total_time_ms=session.total_response_time_ms,
        )
        visible_prompt_count = self._visible_prompt_count_by_session[session.id]

        return SessionStateResponse(
            session_id=session.id,
            started_at=session.started_at,
            total_prompts=len(session.prompts),
            current_index=session.current_index,
            remaining_prompts=max(0, len(session.prompts) - session.current_index),
            visible_prompt_count=visible_prompt_count,
            active_prompts=self._active_prompts(session=session, visible_prompt_count=visible_prompt_count),
            correct=session.correct_count,
            attempted=attempted,
            accuracy=accuracy,
            chars_per_minute=chars_per_minute,
            completed=self._is_completed(session),
        )

    def _active_prompts(self, session: Session, visible_prompt_count: int) -> list[dict[str, object]]:
        start = session.current_index
        end = start + visible_prompt_count
        return [
            {"id": prompt.id, "target": prompt.target}
            for prompt in session.prompts[start:end]
        ]

    @staticmethod
    def _is_completed(session: Session) -> bool:
        return session.current_index >= len(session.prompts)


session_service = SessionService()
