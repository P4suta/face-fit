"""Tests for the MediaPipe-independent parts of landmarks."""

from __future__ import annotations

import numpy as np
from PIL import Image

import face_fit.landmarks as lm
from face_fit.landmarks import FaceDetector, detect_face, load_rgb


def test_load_rgb_roundtrip(tmp_path):
    p = tmp_path / "img.png"
    Image.new("RGB", (12, 8), (10, 20, 30)).save(p)
    arr = load_rgb(p)
    assert arr.shape == (8, 12, 3)
    assert arr.dtype == np.uint8
    assert tuple(arr[0, 0]) == (10, 20, 30)


def test_eye_centers_orders_left_right(fake_landmarks):
    left, right = lm._eye_centers(fake_landmarks, w=480, h=640)
    assert left[0] < right[0]
    assert left[0] == 0.40 * 480
    assert right[0] == 0.60 * 480


def test_detect_crown_from_segmentation(synthetic_rgb):
    crown, from_seg = lm._detect_crown(
        synthetic_rgb, center_x=240.0, face_width=144.0, eye_y=256.0, chin_y=480.0
    )
    assert from_seg is True
    assert abs(crown[1] - 40.0) <= 5.0
    assert crown[0] == 240.0


def test_detect_crown_fallback_on_white():
    white = np.full((640, 480, 3), 255, dtype=np.uint8)
    crown, from_seg = lm._detect_crown(
        white, center_x=240.0, face_width=144.0, eye_y=256.0, chin_y=480.0
    )
    assert from_seg is False
    expected = max(0.0, 256.0 - (480.0 - 256.0) * 1.1)
    assert abs(crown[1] - expected) < 1e-6
    assert crown[0] == 240.0


def test_geometry_from_landmarks(synthetic_rgb, fake_landmarks):
    geom = lm._geometry_from_landmarks(synthetic_rgb, fake_landmarks)
    assert geom.chin[1] == 0.75 * 640
    assert geom.eye_left[0] < geom.eye_right[0]
    assert geom.face_width > 0


def test_face_detector_detect(monkeypatch, synthetic_rgb, fake_landmarks):
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: fake_landmarks)
    geom = FaceDetector().detect(synthetic_rgb)
    assert geom.crown[1] < geom.chin[1]


def test_detect_face_uses_shared_detector(monkeypatch, synthetic_rgb, fake_landmarks):
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: fake_landmarks)
    geom = detect_face(synthetic_rgb)
    assert geom.eye_left[0] < geom.eye_right[0]


def test_detect_no_face_raises(monkeypatch, synthetic_rgb):
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: None)
    try:
        FaceDetector().detect(synthetic_rgb)
    except RuntimeError as exc:
        assert "no face" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("RuntimeError should be raised")
