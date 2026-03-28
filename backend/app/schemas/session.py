from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SessionStartRequest(BaseModel):
    prompt_count: int = Field(default=15, ge=1, le=200)


class PromptOut(BaseModel):
    id: int
    target: str


class SessionStartResponse(BaseModel):
    session_id: str
    started_at: datetime
    prompts: list[PromptOut]


class AnswerIn(BaseModel):
    prompt_id: int = Field(ge=0)
    input_char: str = Field(min_length=1, max_length=1)
    response_time_ms: int = Field(ge=0)

    @field_validator("input_char")
    @classmethod
    def normalize_character(cls, value: str) -> str:
        return value.upper()


class SessionSubmitRequest(BaseModel):
    answers: list[AnswerIn] = Field(min_length=1)


class SessionSummaryResponse(BaseModel):
    session_id: str
    total_prompts: int
    answered_prompts: int
    correct: int
    accuracy: float
    chars_per_minute: float
