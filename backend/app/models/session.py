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


@dataclass(slots=True)
class Session:
    id: str
    prompts: list[SessionPrompt]
    started_at: datetime
    submitted_at: datetime | None = None
    answers: list[SessionAnswer] = field(default_factory=list)
