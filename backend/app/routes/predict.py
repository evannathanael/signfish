from __future__ import annotations

from fastapi import APIRouter

from ..models.loader import load_asl_bundle
from ..schemas.predict import PredictResponse

router = APIRouter()
_bundle = load_asl_bundle()


@router.get("/predict/example", response_model=PredictResponse)
def predict_example() -> PredictResponse:
    labels = _bundle.labels[:3]
    top_k = [(label, 0.0) for label in labels]
    return PredictResponse(top_label=labels[0], top_confidence=0.0, top_k=top_k)
