from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import math
from typing import Optional

import numpy as np

HAND_BONES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
]

ANGLE_JOINTS = [
    (0, 1, 2),
    (1, 2, 3),
    (2, 3, 4),
    (0, 5, 6),
    (5, 6, 7),
    (6, 7, 8),
    (0, 9, 10),
    (9, 10, 11),
    (10, 11, 12),
    (0, 13, 14),
    (13, 14, 15),
    (14, 15, 16),
    (0, 17, 18),
    (17, 18, 19),
    (18, 19, 20),
]

TIP_IDS = [4, 8, 12, 16, 20]
MCP_IDS = [1, 5, 9, 13, 17]
PALM_IDS = [0, 1, 5, 9, 13, 17]


@dataclass
class HandSample:
    features: np.ndarray
    landmarks: np.ndarray
    normalized_landmarks: np.ndarray
    bbox: tuple[int, int, int, int]
    handedness: str


def mediapipe_landmarks_to_array(hand_landmarks) -> np.ndarray:
    return np.asarray(
        [(landmark.x, landmark.y, landmark.z) for landmark in hand_landmarks.landmark],
        dtype=np.float32,
    )


def build_hand_sample(
    landmarks: np.ndarray, handedness: str, frame_shape: tuple[int, int, int]
) -> HandSample:
    features, normalized_landmarks = make_feature_vector(landmarks, handedness=handedness)
    bbox = landmarks_to_bbox(landmarks, frame_shape)
    return HandSample(
        features=features,
        landmarks=landmarks,
        normalized_landmarks=normalized_landmarks,
        bbox=bbox,
        handedness=handedness,
    )


def resolve_handedness(results, index: int) -> str:
    if not getattr(results, "multi_handedness", None):
        return "Right"
    try:
        classification = results.multi_handedness[index].classification[0]
        return classification.label
    except (IndexError, AttributeError):
        return "Right"


def rotate_xy(points: np.ndarray, radians: float) -> np.ndarray:
    rotation = np.asarray(
        [
            [math.cos(radians), -math.sin(radians)],
            [math.sin(radians), math.cos(radians)],
        ],
        dtype=np.float32,
    )
    rotated = points.copy()
    rotated[:, :2] = points[:, :2] @ rotation.T
    return rotated


def normalize_landmarks(landmarks: np.ndarray, handedness: str = "Right") -> np.ndarray:
    centered = landmarks - landmarks[0]
    scale = float(np.max(np.linalg.norm(centered[:, :2], axis=1)))
    if scale < 1e-6:
        scale = 1.0
    centered /= scale

    anchor = centered[9, :2]
    angle = math.atan2(float(anchor[1]), float(anchor[0]))
    rotated = rotate_xy(centered, (math.pi / 2.0) - angle)

    if handedness.lower().startswith("left"):
        rotated[:, 0] *= -1.0

    return rotated.astype(np.float32)


def joint_angle(points: np.ndarray, a: int, b: int, c: int) -> float:
    v1 = points[a] - points[b]
    v2 = points[c] - points[b]
    denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-6
    cosine = float(np.clip(np.dot(v1, v2) / denom, -1.0, 1.0))
    return math.acos(cosine) / math.pi


def build_feature_vector(normalized_landmarks: np.ndarray) -> np.ndarray:
    bone_vectors = []
    for start, end in HAND_BONES:
        vector = normalized_landmarks[end] - normalized_landmarks[start]
        bone_vectors.append(vector / (np.linalg.norm(vector) + 1e-6))

    angles = [joint_angle(normalized_landmarks, a, b, c) for a, b, c in ANGLE_JOINTS]

    palm_center = normalized_landmarks[PALM_IDS].mean(axis=0)
    tip_to_palm = [
        np.linalg.norm(normalized_landmarks[index] - palm_center) for index in TIP_IDS
    ]
    tip_to_tip = [
        np.linalg.norm(normalized_landmarks[a] - normalized_landmarks[b])
        for a, b in combinations(TIP_IDS, 2)
    ]
    mcp_to_wrist = [np.linalg.norm(normalized_landmarks[index]) for index in MCP_IDS]

    spread_x = float(np.max(normalized_landmarks[:, 0]) - np.min(normalized_landmarks[:, 0]))
    spread_y = float(np.max(normalized_landmarks[:, 1]) - np.min(normalized_landmarks[:, 1]))
    depth_range = float(np.max(normalized_landmarks[:, 2]) - np.min(normalized_landmarks[:, 2]))

    return np.concatenate(
        [
            normalized_landmarks.reshape(-1),
            np.asarray(bone_vectors, dtype=np.float32).reshape(-1),
            np.asarray(angles, dtype=np.float32),
            np.asarray(tip_to_palm, dtype=np.float32),
            np.asarray(tip_to_tip, dtype=np.float32),
            np.asarray(mcp_to_wrist, dtype=np.float32),
            np.asarray([spread_x, spread_y, depth_range], dtype=np.float32),
        ]
    ).astype(np.float32)


def make_feature_vector(landmarks: np.ndarray, handedness: str = "Right") -> tuple[np.ndarray, np.ndarray]:
    normalized = normalize_landmarks(landmarks, handedness=handedness)
    features = build_feature_vector(normalized)
    return features, normalized


def augment_normalized_landmarks(
    normalized_landmarks: np.ndarray,
    rng: np.random.Generator,
    rotation_degrees: float = 15.0,
    scale_jitter: float = 0.08,
    noise_std: float = 0.012,
    depth_noise_std: float = 0.01,
) -> np.ndarray:
    augmented = normalized_landmarks.copy()

    rotation = math.radians(float(rng.uniform(-rotation_degrees, rotation_degrees)))
    augmented = rotate_xy(augmented, rotation)

    scale = float(rng.uniform(1.0 - scale_jitter, 1.0 + scale_jitter))
    augmented[:, :2] *= scale

    augmented[:, :2] += rng.normal(0.0, noise_std, size=(augmented.shape[0], 2)).astype(
        np.float32
    )
    augmented[:, 2] += rng.normal(0.0, depth_noise_std, size=augmented.shape[0]).astype(
        np.float32
    )

    return augmented.astype(np.float32)


def landmarks_to_bbox(
    landmarks: np.ndarray, frame_shape: tuple[int, int, int], padding: float = 0.20
) -> tuple[int, int, int, int]:
    frame_height, frame_width = frame_shape[:2]
    x_coords = landmarks[:, 0] * frame_width
    y_coords = landmarks[:, 1] * frame_height

    min_x, max_x = float(np.min(x_coords)), float(np.max(x_coords))
    min_y, max_y = float(np.min(y_coords)), float(np.max(y_coords))

    pad_x = max((max_x - min_x) * padding, 24.0)
    pad_y = max((max_y - min_y) * padding, 24.0)

    x1 = max(0, int(min_x - pad_x))
    y1 = max(0, int(min_y - pad_y))
    x2 = min(frame_width - 1, int(max_x + pad_x))
    y2 = min(frame_height - 1, int(max_y + pad_y))

    return x1, y1, x2, y2


def extract_hand_sample_from_results(
    results, index: int, frame_shape: tuple[int, int, int]
) -> Optional[HandSample]:
    if not getattr(results, "multi_hand_landmarks", None):
        return None
    if index >= len(results.multi_hand_landmarks):
        return None

    landmarks = mediapipe_landmarks_to_array(results.multi_hand_landmarks[index])
    handedness = resolve_handedness(results, index)
    features, normalized_landmarks = make_feature_vector(landmarks, handedness=handedness)
    bbox = landmarks_to_bbox(landmarks, frame_shape)

    return HandSample(
        features=features,
        landmarks=landmarks,
        normalized_landmarks=normalized_landmarks,
        bbox=bbox,
        handedness=handedness,
    )
