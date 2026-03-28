from __future__ import annotations

import argparse
from pathlib import Path
import time

import cv2

from .camera import open_camera
from .config import DEFAULT_DATASET_DIR, DYNAMIC_ASL_LABELS, STATIC_ASL_LABELS
from .features import build_hand_sample
from .hand_detection import HandDetector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture ASL training images from a webcam.")
    parser.add_argument("--label", required=True, help="Target ASL letter label.")
    parser.add_argument("--output", default=DEFAULT_DATASET_DIR, help="Dataset root directory.")
    parser.add_argument("--samples", type=int, default=250, help="Number of images to capture.")
    parser.add_argument(
        "--camera",
        type=int,
        default=-1,
        help="Webcam index. Use -1 to auto-try several camera indices.",
    )
    parser.add_argument(
        "--cooldown-ms",
        type=int,
        default=200,
        help="Minimum delay between captures while holding the key.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    label = args.label.strip().upper()

    if label in DYNAMIC_ASL_LABELS:
        raise ValueError(
            f"{label} is motion-based in ASL. This single-frame collector is intended for the static letters only."
        )
    if label not in STATIC_ASL_LABELS:
        raise ValueError(f"Unsupported label: {label}. Supported labels: {' '.join(STATIC_ASL_LABELS)}")

    output_dir = Path(args.output) / label
    output_dir.mkdir(parents=True, exist_ok=True)

    cap, active_camera_index = open_camera(args.camera)
    print(f"Using camera index {active_camera_index}")

    saved = len(list(output_dir.glob("*.jpg")))
    last_capture_time = 0.0

    with HandDetector(
        running_mode="video",
        num_hands=1,
        min_hand_detection_confidence=0.65,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.6,
    ) as detector:
        while saved < args.samples:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            detections = detector.detect_video_frame(rgb_frame, int(time.monotonic() * 1000))
            sample = None
            if detections:
                detection = detections[0]
                sample = build_hand_sample(detection.landmarks, detection.handedness, frame.shape)

            if sample is not None:
                x1, y1, x2, y2 = sample.bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (33, 204, 116), 3)
                cv2.putText(
                    frame,
                    f"{label} {saved}/{args.samples}",
                    (x1 + 10, max(24, y1 - 14)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.putText(
                frame,
                "Press C to capture, Q to quit",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Capture ASL Dataset", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                break

            if key == ord("c") and sample is not None:
                now = time.time()
                if (now - last_capture_time) * 1000 < args.cooldown_ms:
                    continue

                x1, y1, x2, y2 = sample.bbox
                crop = frame[y1:y2, x1:x2]
                image_path = output_dir / f"{label}_{saved:04d}.jpg"
                if crop.size > 0 and cv2.imwrite(str(image_path), crop):
                    saved += 1
                    last_capture_time = now

    cap.release()
    cv2.destroyAllWindows()
    print(f"Saved {saved} images for label {label} in {output_dir}")


if __name__ == "__main__":
    main()
