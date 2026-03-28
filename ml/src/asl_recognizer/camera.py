from __future__ import annotations

import cv2


def open_camera(camera_index: int) -> tuple[cv2.VideoCapture, int]:
    candidate_indices = [camera_index] if camera_index >= 0 else [0, 1, 2, 3]
    if camera_index >= 0:
        for fallback in [0, 1, 2, 3]:
            if fallback not in candidate_indices:
                candidate_indices.append(fallback)

    for index in candidate_indices:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            return cap, index
        cap.release()

    raise RuntimeError(
        "Could not open any camera. On macOS, make sure camera access is allowed for your terminal app "
        "in System Settings > Privacy & Security > Camera. You can also retry with "
        "`--camera 1` or another index."
    )
