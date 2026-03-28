from __future__ import annotations

from dataclasses import dataclass

from .runtime import configure_runtime_dirs

configure_runtime_dirs()

import mediapipe as mp
import numpy as np


@dataclass
class DetectedHand:
    landmarks: np.ndarray
    handedness: str


class HandDetector:
    def __init__(
        self,
        running_mode: str,
        model_path: str | None = None,
        num_hands: int = 1,
        min_hand_detection_confidence: float = 0.55,
        min_hand_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        if running_mode not in {"image", "video"}:
            raise ValueError(f"Unsupported running mode: {running_mode}")

        self.running_mode = running_mode
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=running_mode == "image",
            max_num_hands=num_hands,
            min_detection_confidence=min_hand_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def __enter__(self) -> "HandDetector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self._hands.close()

    @staticmethod
    def _convert_result(result) -> list[DetectedHand]:
        if not result.multi_hand_landmarks:
            return []

        detections: list[DetectedHand] = []
        handedness_list = result.multi_handedness or []

        for index, hand_landmarks in enumerate(result.multi_hand_landmarks):
            handedness = "Right"
            if index < len(handedness_list) and handedness_list[index].classification:
                handedness = handedness_list[index].classification[0].label

            detections.append(
                DetectedHand(
                    landmarks=np.asarray(
                        [(point.x, point.y, point.z) for point in hand_landmarks.landmark],
                        dtype=np.float32,
                    ),
                    handedness=handedness,
                )
            )

        return detections

    def detect_image(self, rgb_image: np.ndarray) -> list[DetectedHand]:
        result = self._hands.process(rgb_image)
        return self._convert_result(result)

    def detect_video_frame(self, rgb_image: np.ndarray, timestamp_ms: int) -> list[DetectedHand]:
        del timestamp_ms
        result = self._hands.process(rgb_image)
        return self._convert_result(result)
