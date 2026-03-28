from __future__ import annotations

from pydantic import BaseModel


class PredictResponse(BaseModel):
    top_label: str
    top_confidence: float
    top_k: list[tuple[str, float]]
