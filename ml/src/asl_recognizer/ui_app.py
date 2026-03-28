from __future__ import annotations

import argparse
from collections import deque
import time

import cv2
import numpy as np
import torch

from .camera import open_camera
from .config import DEFAULT_WEIGHTS_PATH
from .features import build_hand_sample
from .hand_detection import HandDetector
from .live_inference import draw_hand_landmarks, smooth_prediction
from .model import load_model_bundle, predict_top_k, standardize_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the ASL live viewer UI.")
    parser.add_argument("--weights", default=DEFAULT_WEIGHTS_PATH, help="Model checkpoint path.")
    parser.add_argument(
        "--camera",
        type=int,
        default=-1,
        help="Webcam index. Use -1 to auto-try several camera indices.",
    )
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror the webcam view.")
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
    return parser.parse_args()


def draw_ui_panel(
    frame: np.ndarray,
    label: str,
    confidence: float,
    raw_label: str,
    raw_confidence: float,
    top_predictions: list[tuple[str, float]],
    camera_index: int,
    status: str,
) -> np.ndarray:
    frame_height, frame_width = frame.shape[:2]
    panel_width = 300
    canvas = np.zeros((frame_height, frame_width + panel_width, 3), dtype=np.uint8)
    canvas[:, :frame_width] = frame
    canvas[:, frame_width:] = (15, 23, 42)

    x0 = frame_width + 20
    y = 40

    def put(line: str, color: tuple[int, int, int], scale: float = 0.7, thickness: int = 2) -> None:
        nonlocal y
        cv2.putText(
            canvas,
            line,
            (x0, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        y += int(34 * scale / 0.7)

    put("ASL Live Viewer", (255, 255, 255), scale=0.9, thickness=2)
    y += 12
    put(f"Camera: {camera_index}", (191, 219, 254))
    put(f"Status: {status}", (147, 197, 253))
    y += 10
    put(f"Letter: {label}", (255, 255, 255), scale=0.85, thickness=2)
    put(f"Smoothed confidence: {confidence:.2f}", (134, 239, 172))
    put(f"Top-1 raw: {raw_label} {raw_confidence:.2f}", (250, 204, 21))
    y += 18
    put("Top Predictions", (255, 255, 255), scale=0.8, thickness=2)

    for index, (pred_label, pred_conf) in enumerate(top_predictions[:3], start=1):
        put(f"{index}. {pred_label}  {pred_conf:.2f}", (226, 232, 240), scale=0.72, thickness=1)

    y += 18
    put("Controls", (255, 255, 255), scale=0.8, thickness=2)
    put("Q or Esc to quit", (203, 213, 225), scale=0.7, thickness=1)
    put("Hold the sign steady", (203, 213, 225), scale=0.7, thickness=1)

    return canvas


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
            detections = detector.detect_video_frame(rgb_frame, int(time.monotonic() * 1000))

            displayed_label = "No hand"
            displayed_confidence = 0.0
            raw_label = "No hand"
            raw_confidence = 0.0
            bbox = None
            top_predictions: list[tuple[str, float]] = []
            status = "Waiting for hand"

            if detections:
                detection = detections[0]
                sample = build_hand_sample(detection.landmarks, detection.handedness, frame.shape)
                features = standardize_features(
                    sample.features, bundle.feature_mean, bundle.feature_std
                )
                prediction = predict_top_k(bundle, features, device=device, k=3)
                top_predictions = prediction.top_k
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
                status = "Tracking hand"
                draw_hand_landmarks(frame, detection.landmarks)

                if bbox:
                    x1, y1, x2, y2 = bbox
                    color = (33, 204, 116) if displayed_label != "Unsure" else (0, 165, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            else:
                history.clear()

            composed = draw_ui_panel(
                frame,
                displayed_label,
                displayed_confidence,
                raw_label,
                raw_confidence,
                top_predictions,
                active_camera_index,
                status,
            )
            cv2.imshow("ASL Live Viewer", composed)

            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
