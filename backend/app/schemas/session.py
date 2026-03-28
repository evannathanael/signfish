from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SessionStartRequest(BaseModel):
    prompt_count: int = Field(default=50, ge=10, le=500)
    visible_prompt_count: int = Field(default=10, ge=1, le=50)


class PromptOut(BaseModel):
    id: int
    target: str


class SessionStateResponse(BaseModel):
    session_id: str
    started_at: datetime
    total_prompts: int
    current_index: int
    remaining_prompts: int
    visible_prompt_count: int
    active_prompts: list[PromptOut]
    correct: int
    attempted: int
    accuracy: float
    chars_per_minute: float
    completed: bool


class SessionAnswerRequest(BaseModel):
    input_char: str = Field(min_length=1, max_length=1)
    response_time_ms: int = Field(ge=0)

    @field_validator("input_char")
    @classmethod
    def normalize_character(cls, value: str) -> str:
        return value.upper()


class SessionAnswerResponse(BaseModel):
    correct: bool
    expected_char: str
    received_char: str
    state: SessionStateResponse
