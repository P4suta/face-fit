"""Face landmark detection + crown estimation via white-background segmentation.

MediaPipe FaceLandmarker (Tasks API, 478 landmarks) provides the eyes, chin,
face width and center. The crown (top of the head), which is not a landmark, is
recovered by extracting the subject silhouette from the white background.
Image I/O uses PIL (Unicode-path safe); array work uses numpy/OpenCV.

Use :class:`FaceDetector` to load the model once and process many images (e.g.
in batch mode); :func:`detect_face` is a convenience wrapper over a shared
default detector.
"""

from __future__ import annotations

import functools
import io
from dataclasses import dataclass
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from PIL import Image, ImageOps

from .model import ensure_model

Point = tuple[float, float]

# MediaPipe FaceMesh landmark indices.
_R_IRIS = 468  # iris center on the image's right (subject's left eye)
_L_IRIS = 473  # iris center on the image's left (subject's right eye)
_CHIN = 152
_RIGHT_CHEEK = 234
_LEFT_CHEEK = 454
# Fallback eye corners for models without iris landmarks.
_R_EYE_CORNERS = (33, 133)
_L_EYE_CORNERS = (362, 263)

# Luminance threshold below which a pixel is treated as subject (not background).
_BG_LUMA_THRESHOLD = 235


@dataclass(frozen=True)
class FaceGeometry:
    """Detected face geometry (all values in source px)."""

    crown: Point
    chin: Point
    eye_left: Point  # image-left (smaller x)
    eye_right: Point
    face_width: float
    crown_from_segmentation: bool


def load_rgb(path: str | Path) -> np.ndarray:
    """Load an image as a uint8 RGB array (applies EXIF orientation; Unicode-safe)."""
    data = Path(path).read_bytes()
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("RGB")
    return np.ascontiguousarray(np.asarray(img, dtype=np.uint8))


def _landmark_xy(landmarks, idx: int, w: int, h: int) -> Point:
    lm = landmarks[idx]
    return (lm.x * w, lm.y * h)


def _eye_centers(lms, w: int, h: int) -> tuple[Point, Point]:
    """Return the image-left and image-right eye centers (iris first, else corner average)."""
    if len(lms) > _L_IRIS:
        right_img = _landmark_xy(lms, _R_IRIS, w, h)  # smaller-x side
        left_img = _landmark_xy(lms, _L_IRIS, w, h)
    else:  # pragma: no cover - not reached with the 478-point model

        def avg(idxs):
            xs = [lms[i].x * w for i in idxs]
            ys = [lms[i].y * h for i in idxs]
            return (sum(xs) / len(xs), sum(ys) / len(ys))

        right_img = avg(_R_EYE_CORNERS)
        left_img = avg(_L_EYE_CORNERS)
    # Put the image-left (smaller x) point into eye_left.
    if right_img[0] <= left_img[0]:
        return right_img, left_img
    return left_img, right_img


def _detect_crown(
    rgb: np.ndarray, center_x: float, face_width: float, eye_y: float, chin_y: float
) -> tuple[Point, bool]:
    """Estimate the crown from the white background.

    Scan a vertical band (about as wide as the face) around the face center from
    the top; the crown is the first row where enough non-background pixels line
    up. On failure, fall back to an estimate extrapolated from the eye-chin gap.
    """
    w = rgb.shape[1]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    non_bg = gray < _BG_LUMA_THRESHOLD

    # Denoise (remove small specks).
    kernel = np.ones((3, 3), np.uint8)
    non_bg = cv2.morphologyEx(non_bg.astype(np.uint8), cv2.MORPH_OPEN, kernel) > 0

    half = max(4.0, face_width * 0.45)
    x0 = max(0, int(center_x - half))
    x1 = min(w, int(center_x + half))
    band = non_bg[:, x0:x1]
    band_w = max(1, x1 - x0)
    need = max(3, int(band_w * 0.10))

    counts = band.sum(axis=1)
    # Only scan above the chin (avoid false hits on neck/shoulders).
    upper_limit = int(min(eye_y, chin_y))
    crown_y = None
    for y in range(0, max(1, upper_limit)):
        if counts[y] >= need:
            crown_y = y
            break

    if crown_y is not None and crown_y < eye_y:
        return (center_x, float(crown_y)), True

    # Fallback: crown ~= eye_y - (chin_y - eye_y) * 1.1
    fallback_y = eye_y - (chin_y - eye_y) * 1.1
    return (center_x, float(max(0.0, fallback_y))), False


def _geometry_from_landmarks(rgb: np.ndarray, lms) -> FaceGeometry:
    """Assemble :class:`FaceGeometry` from a landmark list (no MediaPipe runtime)."""
    h, w = rgb.shape[:2]
    eye_left, eye_right = _eye_centers(lms, w, h)
    chin = _landmark_xy(lms, _CHIN, w, h)
    right_cheek = _landmark_xy(lms, _RIGHT_CHEEK, w, h)
    left_cheek = _landmark_xy(lms, _LEFT_CHEEK, w, h)
    face_width = abs(left_cheek[0] - right_cheek[0])

    eye_mid_x = (eye_left[0] + eye_right[0]) / 2.0
    eye_mid_y = (eye_left[1] + eye_right[1]) / 2.0
    crown, from_seg = _detect_crown(rgb, eye_mid_x, face_width, eye_mid_y, chin[1])

    return FaceGeometry(
        crown=crown,
        chin=chin,
        eye_left=eye_left,
        eye_right=eye_right,
        face_width=face_width,
        crown_from_segmentation=from_seg,
    )


class FaceDetector:
    """Reusable face detector that loads the MediaPipe model once.

    Create one instance and call :meth:`detect` for many images (the heavy model
    load happens only once). Usable as a context manager.
    """

    def __init__(self) -> None:
        """Create a detector; the model loads lazily on first use."""
        self._landmarker = None

    def _landmarker_obj(self):  # pragma: no cover - mediapipe runtime
        if self._landmarker is None:
            base = mp_python.BaseOptions(model_asset_path=str(ensure_model()))
            options = mp_vision.FaceLandmarkerOptions(base_options=base, num_faces=5)
            self._landmarker = mp_vision.FaceLandmarker.create_from_options(options)
        return self._landmarker

    def _run(self, rgb: np.ndarray):  # pragma: no cover - mediapipe runtime (integration-tested)
        """Return the largest face's landmark list, or ``None`` if no face is found."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._landmarker_obj().detect(mp_image)
        if not result.face_landmarks:
            return None
        return max(result.face_landmarks, key=lambda lms: abs(lms[_L_IRIS].x - lms[_R_IRIS].x))

    def detect(self, rgb: np.ndarray) -> FaceGeometry:
        """Extract face geometry from an RGB array. Raises ``RuntimeError`` if no face."""
        lms = self._run(rgb)
        if lms is None:
            raise RuntimeError("no face detected")
        return _geometry_from_landmarks(rgb, lms)

    def close(self) -> None:
        """Release the underlying MediaPipe landmarker."""
        if self._landmarker is not None:  # pragma: no cover - mediapipe runtime
            self._landmarker.close()
            self._landmarker = None

    def __enter__(self) -> FaceDetector:
        """Enter the context, returning this detector."""
        return self

    def __exit__(self, *exc) -> None:
        """Exit the context, releasing the landmarker."""
        self.close()


@functools.cache
def _shared_detector() -> FaceDetector:
    return FaceDetector()


def detect_face(rgb: np.ndarray) -> FaceGeometry:
    """Detect face geometry using a shared default :class:`FaceDetector`."""
    return _shared_detector().detect(rgb)
