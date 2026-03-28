from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import urllib.request

from .runtime import configure_runtime_dirs

configure_runtime_dirs()

import mediapipe as mp
import numpy as np

HAND_LANDMARKER_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
DEFAULT_HAND_LANDMARKER_PATH = ".runtime/models/hand_landmarker.task"


@dataclass
class DetectedHand:
    landmarks: np.ndarray
    handedness: str


def ensure_hand_landmarker_model(model_path: str | Path = DEFAULT_HAND_LANDMARKER_PATH) -> str:
    output_path = Path(model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.exists():
        urllib.request.urlretrieve(HAND_LANDMARKER_MODEL_URL, output_path)
    return str(output_path)


class HandDetector:
    def __init__(
        self,
        running_mode: str,
        model_path: str | Path = DEFAULT_HAND_LANDMARKER_PATH,
        num_hands: int = 1,
        min_hand_detection_confidence: float = 0.55,
        min_hand_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        model_asset_path = ensure_hand_landmarker_model(model_path)
        vision = mp.tasks.vision
        base_options = mp.tasks.BaseOptions(model_asset_path=model_asset_path)

        mode_map = {
            "image": vision.RunningMode.IMAGE,
            "video": vision.RunningMode.VIDEO,
        }
        if running_mode not in mode_map:
            raise ValueError(f"Unsupported running mode: {running_mode}")

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=mode_map[running_mode],
            num_hands=num_hands,
            min_hand_detection_confidence=min_hand_detection_confidence,
            min_hand_presence_confidence=min_hand_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        self.running_mode = running_mode

    def __enter__(self) -> "HandDetector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        self.landmarker.close()

    @staticmethod
    def _to_mp_image(rgb_image: np.ndarray):
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    @staticmethod
    def _convert_result(result) -> list[DetectedHand]:
        detections: list[DetectedHand] = []
        for index, hand_landmarks in enumerate(result.hand_landmarks):
            handedness = "Right"
            if index < len(result.handedness) and result.handedness[index]:
                handedness = result.handedness[index][0].category_name

            detections.append(
                DetectedHand(
                    landmarks=np.asarray(
                        [(point.x, point.y, point.z) for point in hand_landmarks],
                        dtype=np.float32,
                    ),
                    handedness=handedness,
                )
            )
        return detections

    def detect_image(self, rgb_image: np.ndarray) -> list[DetectedHand]:
        result = self.landmarker.detect(self._to_mp_image(rgb_image))
        return self._convert_result(result)

    def detect_video_frame(self, rgb_image: np.ndarray, timestamp_ms: int) -> list[DetectedHand]:
        result = self.landmarker.detect_for_video(self._to_mp_image(rgb_image), timestamp_ms)
        return self._convert_result(result)
