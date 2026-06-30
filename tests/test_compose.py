"""Unit tests for compose.compute_fit (no images, no MediaPipe)."""

from __future__ import annotations

import math

import pytest

from face_fit.compose import _affine, compute_fit
from face_fit.presets import Spec


def _upright_points():
    # Synthetic upright face: crown (100,20), chin (100,220), eyes at y=80.
    return {
        "crown": (100.0, 20.0),
        "chin": (100.0, 220.0),
        "eye_left": (80.0, 80.0),
        "eye_right": (120.0, 80.0),
    }


def test_scale_and_placement_upright():
    spec = Spec()  # 480x640, face_ratio .75, top_margin .09
    fit = compute_fit(spec=spec, **_upright_points())

    # face_height = 200 -> scale = .75*640/200 = 2.4
    assert fit.scale == pytest.approx(2.4, rel=1e-6)
    assert fit.roll_deg == pytest.approx(0.0, abs=1e-9)

    # Crown at top_margin*h; eye midpoint at center x.
    crown_out = fit.info_points["crown"]
    assert crown_out[1] == pytest.approx(0.09 * 640, abs=1e-6)
    eye_out = fit.info_points["eye_mid"]
    assert eye_out[0] == pytest.approx(480 / 2, abs=1e-6)

    # Face ratio = chin_line - top_margin ~= face_ratio.
    assert (fit.chin_line_actual - spec.top_margin) == pytest.approx(0.75, abs=1e-6)


def test_face_ratio_override():
    spec = Spec(face_ratio=0.80)
    fit = compute_fit(spec=spec, **_upright_points())
    assert (fit.chin_line_actual - spec.top_margin) == pytest.approx(0.80, abs=1e-6)


def test_roll_correction_levels_eyes():
    # Eyes tilted 15 degrees. After correction the eyes should be level.
    angle = math.radians(15)
    cx, cy, half = 100.0, 80.0, 20.0
    eye_left = (cx - half * math.cos(angle), cy - half * math.sin(angle))
    eye_right = (cx + half * math.cos(angle), cy + half * math.sin(angle))
    spec = Spec()
    fit = compute_fit(
        crown=(100.0, 20.0), chin=(100.0, 220.0), eye_left=eye_left, eye_right=eye_right, spec=spec
    )

    assert fit.roll_deg == pytest.approx(15.0, abs=1e-6)
    el = fit.info_points["eye_left"]
    er = fit.info_points["eye_right"]
    assert el[1] == pytest.approx(er[1], abs=1e-6)  # eyes level


def test_inverse_coeffs_roundtrip():
    # forward and inverse_coeffs are consistent (output->source->output is identity).
    spec = Spec()
    fit = compute_fit(spec=spec, **_upright_points())
    a, b, c, d, e, f = fit.inverse_coeffs
    out_pt = (123.0, 456.0)
    src_pt = (a * out_pt[0] + b * out_pt[1] + c, d * out_pt[0] + e * out_pt[1] + f)
    back = _affine(fit.forward, src_pt)
    assert back[0] == pytest.approx(out_pt[0], abs=1e-6)
    assert back[1] == pytest.approx(out_pt[1], abs=1e-6)


def test_degenerate_face_height_raises():
    with pytest.raises(ValueError):
        compute_fit(
            crown=(100.0, 220.0),  # crown below chin
            chin=(100.0, 20.0),
            eye_left=(80.0, 80.0),
            eye_right=(120.0, 80.0),
            spec=Spec(),
        )
