from __future__ import annotations

import argparse
from collections import deque
import time

import cv2
import numpy as np
import torch

from .camera import open_camera
from .config import DEFAULT_WEIGHTS_PATH
from .features import HAND_BONES, build_hand_sample
from .hand_detection import HandDetector
from .model import load_model_bundle, predict_top_k, standardize_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live ASL alphabet recognition.")
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS_PATH, help="Model checkpoint path.")
    parser.add_argument(
        "--camera",
        type=int,
        default=-1,
        help="Webcam index. Use -1 to auto-try several camera indices.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.55,
        help="Minimum smoothed confidence to display a letter.",
    )
    parser.add_argument(
        "--min-frame-confidence",
        type=float,
        default=0.35,
        help="Ignore very weak single-frame predictions below this confidence.",
    )
    parser.add_argument(
        "--smoothing-window",
        type=int,
        default=7,
        help="How many frames to use for prediction smoothing.",
    )
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror the webcam view.")
    return parser.parse_args()


def smooth_prediction(history: deque[tuple[str, float]]) -> tuple[str, float]:
    if not history:
        return "No hand", 0.0

    scores: dict[str, float] = {}
    total = 0.0
    for label, confidence in history:
        if label == "?":
            continue
        scores[label] = scores.get(label, 0.0) + confidence
        total += confidence

    if not scores or total <= 0.0:
        return "Unsure", 0.0

    best_label, best_score = max(scores.items(), key=lambda item: item[1])
    return best_label, best_score / total


def draw_prediction(
    frame: np.ndarray,
    bbox: tuple[int, int, int, int] | None,
    label: str,
    confidence: float,
) -> None:
    frame_height, frame_width = frame.shape[:2]
    text = f"{label} {confidence:.2f}" if label not in {"No hand", "Unsure"} else label

    if bbox:
        x1, y1, x2, y2 = bbox
        color = (33, 204, 116) if label not in {"Unsure", "No hand"} else (0, 165, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

        label_y1 = max(0, y1 - 42)
        cv2.rectangle(frame, (x1, label_y1), (x2, y1), color, -1)
        cv2.putText(
            frame,
            text,
            (x1 + 10, max(24, y1 - 14)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return

    cv2.putText(
        frame,
        text,
        (24, frame_height - 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.rectangle(frame, (12, frame_height - 58), (260, frame_height - 10), (0, 0, 0), 2)


def draw_hand_landmarks(frame: np.ndarray, landmarks: np.ndarray) -> None:
    frame_height, frame_width = frame.shape[:2]
    points = [
        (int(point[0] * frame_width), int(point[1] * frame_height))
        for point in landmarks
    ]

    for start, end in HAND_BONES:
        cv2.line(frame, points[start], points[end], (93, 173, 226), 2, cv2.LINE_AA)

    for point in points:
        cv2.circle(frame, point, 4, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, point, 2, (33, 204, 116), -1, cv2.LINE_AA)


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    bundle = load_model_bundle(args.weights, device=device)

    cap, active_camera_index = open_camera(args.camera)
    print(f"Using camera index {active_camera_index}")

    history: deque[tuple[str, float]] = deque(maxlen=args.smoothing_window)

    with HandDetector(
        running_mode="video",
        num_hands=1,
        min_hand_detection_confidence=0.65,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.6,
    ) as detector:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            if not args.no_mirror:
                frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            timestamp_ms = int(time.monotonic() * 1000)
            detections = detector.detect_video_frame(rgb_frame, timestamp_ms)

            displayed_label = "No hand"
            displayed_confidence = 0.0
            raw_label = "No hand"
            raw_confidence = 0.0
            bbox = None

            if detections:
                detection = detections[0]
                sample = build_hand_sample(detection.landmarks, detection.handedness, frame.shape)
                features = standardize_features(
                    sample.features, bundle.feature_mean, bundle.feature_std
                )
                prediction = predict_top_k(bundle, features, device=device, k=3)
                raw_label = prediction.top_label
                raw_confidence = prediction.top_confidence

                if raw_confidence >= args.min_frame_confidence:
                    history.append((raw_label, raw_confidence))
                else:
                    history.append(("?", raw_confidence))

                displayed_label, displayed_confidence = smooth_prediction(history)
                if displayed_confidence < args.confidence_threshold:
                    displayed_label = "Unsure"

                bbox = sample.bbox
                draw_hand_landmarks(frame, detection.landmarks)
            else:
                history.clear()

            draw_prediction(frame, bbox, displayed_label, displayed_confidence)
            cv2.putText(
                frame,
                f"Top-1 raw: {raw_label} {raw_confidence:.2f}",
                (24, 34),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("ASL Alphabet Recognizer", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
