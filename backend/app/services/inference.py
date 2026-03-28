from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Optional

import cv2
import numpy as np

from ml.src.asl_recognizer.features import build_hand_sample
from ml.src.asl_recognizer.hand_detection import HandDetector
from ml.src.asl_recognizer.model import ModelBundle, predict_top_k, standardize_features


@dataclass
class InferenceOutput:
    top_label: str
    top_confidence: float
    top_k: list[tuple[str, float]]


class ASLInferenceService:
    def __init__(self, bundle: ModelBundle) -> None:
        self.bundle = bundle
        self.detector = HandDetector(
            running_mode="video",
            num_hands=1,
            min_hand_detection_confidence=0.65,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.6,
        )

    def predict_bgr_frame(self, frame: np.ndarray) -> Optional[InferenceOutput]:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = self.detector.detect_video_frame(rgb_frame, int(time.monotonic() * 1000))
        if not detections:
            return None

        detection = detections[0]
        sample = build_hand_sample(detection.landmarks, detection.handedness, frame.shape)
        features = standardize_features(
            sample.features, self.bundle.feature_mean, self.bundle.feature_std
        )
        prediction = predict_top_k(self.bundle, features, k=3)
        return InferenceOutput(
            top_label=prediction.top_label,
            top_confidence=prediction.top_confidence,
            top_k=prediction.top_k,
        )
