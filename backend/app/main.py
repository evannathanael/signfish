from __future__ import annotations

import base64
import binascii
import os
from datetime import datetime, timezone
from typing import Any, Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class InferRequest(BaseModel):
    frame: str = Field(..., description="Base64-encoded image from webcam")
    question: str = Field(..., description="Prompt shown to the user")


class InferResponse(BaseModel):
    predicted_letter: str
    expected_letter: str
    match: bool
    confidence: float


class ScoreInput(BaseModel):
    username: str = "anonymous"
    wpm: int
    accuracy: int
    consistency: int
    date: Optional[str] = None


class SettingsInput(BaseModel):
    difficulty: str


app = FastAPI(title="SignFish API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


leaderboard_rows: list[dict[str, Any]] = []
settings_state: dict[str, str] = {"difficulty": "normal"}


def normalize_letter(value: str) -> str:
    for char in value.upper():
        if "A" <= char <= "Z":
            return char
    return ""


def extract_expected_letter(question: str) -> str:
    expected = normalize_letter(question)
    if not expected:
        raise HTTPException(status_code=400, detail="Question must contain a valid letter")
    return expected


def normalize_frame(frame: str) -> str:
    image_payload = frame.strip()
    if image_payload.startswith("data:"):
        _, _, image_payload = image_payload.partition(",")

    try:
        base64.b64decode(image_payload, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="Frame must be valid base64 image data") from exc

    return image_payload


def infer_model_letter(frame: str, question: str) -> tuple[str, float]:
    endpoint = os.getenv("TINYFISH_MODEL_URL")
    timeout_seconds = float(os.getenv("TINYFISH_MODEL_TIMEOUT", "5"))
    fallback_letter = normalize_letter(os.getenv("MODEL_FALLBACK_LETTER", "A")) or "A"

    if endpoint:
        try:
            response = requests.post(
                endpoint,
                json={"frame": frame, "question": question},
                timeout=timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException:
            # If remote model is unavailable, gracefully degrade to fallback output
            # so frontend rounds continue instead of failing each capture.
            return fallback_letter, 0.0

        raw_prediction = (
            payload.get("predicted_letter")
            or payload.get("letter")
            or payload.get("prediction")
            or payload.get("pred")
            or ""
        )
        predicted_letter = normalize_letter(str(raw_prediction))
        if not predicted_letter:
            return fallback_letter, 0.0

        confidence = float(payload.get("confidence", 1.0))
        return predicted_letter, confidence

    # Local fallback keeps integration testable when model endpoint is offline.
    return fallback_letter, 0.5


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/infer", response_model=InferResponse)
def infer_sign(payload: InferRequest) -> InferResponse:
    expected_letter = extract_expected_letter(payload.question)
    normalized_frame = normalize_frame(payload.frame)
    predicted_letter, confidence = infer_model_letter(normalized_frame, payload.question)

    return InferResponse(
        predicted_letter=predicted_letter,
        expected_letter=expected_letter,
        match=predicted_letter == expected_letter,
        confidence=confidence,
    )


@app.get("/leaderboard")
def get_leaderboard() -> dict[str, list[dict[str, Any]]]:
    return {"rows": leaderboard_rows}


@app.post("/leaderboard")
def post_leaderboard(payload: ScoreInput) -> dict[str, Any]:
    row = {
        "username": payload.username,
        "wpm": payload.wpm,
        "accuracy": payload.accuracy,
        "consistency": payload.consistency,
        "date": payload.date or datetime.now(timezone.utc).isoformat(),
    }
    leaderboard_rows.append(row)
    leaderboard_rows.sort(key=lambda item: item["wpm"], reverse=True)
    del leaderboard_rows[100:]
    return {"ok": True, "row": row}


@app.get("/settings")
def get_settings() -> dict[str, str]:
    return settings_state


@app.put("/settings")
def put_settings(payload: SettingsInput) -> dict[str, str]:
    settings_state["difficulty"] = payload.difficulty
    return settings_state
