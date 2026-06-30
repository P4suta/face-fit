"""Shared fixtures (synthetic data, no MediaPipe)."""

from __future__ import annotations

import types

import numpy as np
import pytest

from face_fit.landmarks import FaceGeometry


@pytest.fixture
def synthetic_rgb() -> np.ndarray:
    """White 480x640 RGB with a dark 'head' block near the top center."""
    h, w = 640, 480
    img = np.full((h, w, 3), 255, dtype=np.uint8)
    # Head: rows 40-400, cols 160-320 are dark.
    img[40:400, 160:320] = 50
    return img


@pytest.fixture
def fake_geometry() -> FaceGeometry:
    """Plausible face geometry matching the synthetic image."""
    return FaceGeometry(
        crown=(240.0, 40.0),
        chin=(240.0, 480.0),
        eye_left=(192.0, 256.0),
        eye_right=(288.0, 256.0),
        face_width=144.0,
        crown_from_segmentation=True,
    )


@pytest.fixture
def fake_landmarks() -> list:
    """478 dummy landmarks; only the needed indices carry meaningful values."""
    pts = [types.SimpleNamespace(x=0.5, y=0.5, z=0.0) for _ in range(478)]
    pts[468] = types.SimpleNamespace(x=0.40, y=0.40, z=0.0)  # image-left iris
    pts[473] = types.SimpleNamespace(x=0.60, y=0.40, z=0.0)  # image-right iris
    pts[152] = types.SimpleNamespace(x=0.50, y=0.75, z=0.0)  # chin
    pts[234] = types.SimpleNamespace(x=0.35, y=0.50, z=0.0)  # right cheek
    pts[454] = types.SimpleNamespace(x=0.65, y=0.50, z=0.0)  # left cheek
    return pts
