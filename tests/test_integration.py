"""Integration tests using real images (need MediaPipe + model download + images).

Marked ``@pytest.mark.integration``; excluded by default. Run with
``uv run pytest -m integration``. Samples come from the ``FACE_FIT_SAMPLES``
environment variable (os.pathsep-separated) or a default next to the repo;
missing files are skipped.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from face_fit.landmarks import detect_face, load_rgb
from face_fit.presets import ID_PHOTO
from face_fit.render import fit_to_image

pytestmark = pytest.mark.integration


def _samples() -> list[Path]:
    env = os.environ.get("FACE_FIT_SAMPLES")
    if env:
        return [Path(p) for p in env.split(os.pathsep) if p]
    # Default looks for generic sample names next to the repo; set FACE_FIT_SAMPLES
    # to point at your own photos. No personal filenames are committed.
    nearby = Path(__file__).resolve().parents[2]
    return [nearby / "profile_pic.jpg", nearby / "sample.jpg"]


@pytest.mark.parametrize("sample", _samples(), ids=lambda p: p.name)
def test_output_face_ratio_within_requirement(sample: Path):
    if not sample.exists():
        pytest.skip(f"sample image not found: {sample}")

    rgb = load_rgb(sample)
    geom = detect_face(rgb)
    out_img, fit = fit_to_image(rgb, geom, ID_PHOTO)

    assert out_img.size == (ID_PHOTO.out_w, ID_PHOTO.out_h)
    face_pct = fit.chin_line_actual - ID_PHOTO.top_margin
    assert 0.70 <= face_pct <= 0.80, f"face ratio {face_pct:.3f} out of range"
    assert abs(fit.roll_deg) < 20.0
