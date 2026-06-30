"""Composition math (pure functions).

Given the face reference points (crown, chin, both eyes) and a target
composition :class:`~face_fit.presets.Spec`, compute a similarity transform
(roll correction + uniform scale + translation).

Coordinates are image pixels (x right, y down). The only dependency is numpy and
nothing touches the image itself, which keeps this easy to unit-test.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .presets import Spec

Point = tuple[float, float]

#: Minimum valid face height (px) to avoid division by ~zero.
_MIN_FACE_HEIGHT = 1e-6


@dataclass(frozen=True)
class Fit:
    """Result of the similarity-transform computation.

    Attributes:
        forward: 2x3 affine matrix mapping source -> output.
        inverse_coeffs: Coefficients for PIL ``Image.transform(AFFINE)``
            (output -> source) as ``(a, b, c, d, e, f)``.
        scale: Applied uniform scale.
        roll_deg: Corrected roll angle, in degrees.
        eye_line_actual: Eye line in the output, as a fraction of the height.
        chin_line_actual: Chin line in the output, as a fraction of the height.
        info_points: Reference points mapped to output coordinates, for debugging.
    """

    forward: np.ndarray
    inverse_coeffs: tuple[float, float, float, float, float, float]
    scale: float
    roll_deg: float
    eye_line_actual: float
    chin_line_actual: float
    info_points: dict[str, Point]


def _affine(matrix2x3: np.ndarray, p: Point) -> Point:
    x, y = p
    vec = np.array([x, y, 1.0])
    out = matrix2x3 @ vec
    return float(out[0]), float(out[1])


def compute_fit(
    *,
    crown: Point,
    chin: Point,
    eye_left: Point,
    eye_right: Point,
    spec: Spec,
) -> Fit:
    """Compute the similarity transform from reference points and a spec.

    Args:
        crown: Top of the head (source px).
        chin: Chin tip (source px).
        eye_left: Center of the left-in-image eye (smaller x).
        eye_right: Center of the right-in-image eye.
        spec: Target composition.

    Returns:
        A :class:`Fit`.

    Constraints:
        - Level the line between the eyes (roll correction).
        - Scale so crown-to-chin equals ``spec.face_ratio * out_h``.
        - Place the crown at ``y = top_margin * out_h`` (vertical).
        - Place the eye midpoint at ``x = out_w / 2`` (horizontal).
    """
    # Normalize so the smaller-x point is "left" (robust to swapped arguments).
    if eye_left[0] > eye_right[0]:
        eye_left, eye_right = eye_right, eye_left

    p_left = np.array(eye_left, dtype=float)
    p_right = np.array(eye_right, dtype=float)
    eye_mid = (p_left + p_right) / 2.0

    # Roll angle theta: tilt of the eye line. Rotate by phi = -theta to level it.
    theta = math.atan2(p_right[1] - p_left[1], p_right[0] - p_left[0])
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Components of rotation R(phi = -theta).
    r00, r01 = cos_t, sin_t
    r10, r11 = -sin_t, cos_t

    # Measure face height along the corrected "down" axis (removes the roll effect).
    down = np.array([-sin_t, cos_t])  # output-down direction in source coords
    crown_v = np.array(crown, dtype=float)
    chin_v = np.array(chin, dtype=float)
    face_height = float((chin_v - crown_v) @ down)
    if face_height <= _MIN_FACE_HEIGHT:
        raise ValueError(
            f"non-positive face height (crown below chin?): face_height={face_height:.3f}"
        )

    scale = spec.face_ratio * spec.out_h / face_height

    # Translation: horizontal = eye midpoint to center, vertical = crown to top_margin.
    tx = spec.out_w / 2.0 - scale * (r00 * eye_mid[0] + r01 * eye_mid[1])
    ty = spec.top_margin * spec.out_h - scale * (r10 * crown_v[0] + r11 * crown_v[1])

    forward = np.array(
        [
            [scale * r00, scale * r01, tx],
            [scale * r10, scale * r11, ty],
        ],
        dtype=float,
    )

    # Invert to output -> source (for PIL).
    m3 = np.vstack([forward, [0.0, 0.0, 1.0]])
    inv = np.linalg.inv(m3)
    inverse_coeffs = (
        float(inv[0, 0]),
        float(inv[0, 1]),
        float(inv[0, 2]),
        float(inv[1, 0]),
        float(inv[1, 1]),
        float(inv[1, 2]),
    )

    out_crown = _affine(forward, crown)
    out_chin = _affine(forward, chin)
    out_eye = _affine(forward, tuple(eye_mid))
    out_eye_l = _affine(forward, tuple(p_left))
    out_eye_r = _affine(forward, tuple(p_right))

    return Fit(
        forward=forward,
        inverse_coeffs=inverse_coeffs,
        scale=scale,
        roll_deg=math.degrees(theta),
        eye_line_actual=out_eye[1] / spec.out_h,
        chin_line_actual=out_chin[1] / spec.out_h,
        info_points={
            "crown": out_crown,
            "chin": out_chin,
            "eye_mid": out_eye,
            "eye_left": out_eye_l,
            "eye_right": out_eye_r,
        },
    )
