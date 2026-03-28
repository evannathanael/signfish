from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class SessionPrompt:
    id: int
    target: str


@dataclass(slots=True)
class SessionAnswer:
    prompt_id: int
    input_char: str
    response_time_ms: int
    is_correct: bool


@dataclass(slots=True)
class Session:
    id: str
    prompts: list[SessionPrompt]
    started_at: datetime
    submitted_at: datetime | None = None
    current_index: int = 0
    correct_count: int = 0
    total_response_time_ms: int = 0
    answers: list[SessionAnswer] = field(default_factory=list)
