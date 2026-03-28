from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SessionPrompt:
    id: int
    target: str


@dataclass
class SessionAnswer:
    prompt_id: int
    input_char: str
    response_time_ms: int
    is_correct: bool


@dataclass
class Session:
    id: str
    prompts: list[SessionPrompt]
    started_at: datetime
    submitted_at: Optional[datetime] = None
    current_index: int = 0
    correct_count: int = 0
    total_response_time_ms: int = 0
    answers: list[SessionAnswer] = field(default_factory=list)
