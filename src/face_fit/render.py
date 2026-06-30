"""Apply the similarity transform, fill the white background, downscale, and save (Pillow)."""

from __future__ import annotations

import dataclasses
import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .compose import Fit, compute_fit
from .landmarks import FaceGeometry
from .presets import Spec


def fit_to_image(
    rgb: np.ndarray, geom: FaceGeometry, spec: Spec, render_scale: int = 2
) -> tuple[Image.Image, Fit]:
    """Produce the output image from the geometry and spec.

    The affine transform is applied onto a ``render_scale``-times larger canvas
    at full resolution, then downscaled with LANCZOS to reduce aliasing. Margins
    and missing areas are filled with the background color. No retouching
    (color/skin) is performed.

    Returns:
        ``(output image, Fit at the final size)``.
    """
    big = dataclasses.replace(
        spec, out_w=spec.out_w * render_scale, out_h=spec.out_h * render_scale
    )
    fit_big = compute_fit(
        crown=geom.crown,
        chin=geom.chin,
        eye_left=geom.eye_left,
        eye_right=geom.eye_right,
        spec=big,
    )

    src = Image.fromarray(rgb)
    big_img = src.transform(
        (big.out_w, big.out_h),
        Image.Transform.AFFINE,
        fit_big.inverse_coeffs,
        resample=Image.Resampling.BICUBIC,
        fillcolor=spec.bg,
    )
    out = big_img.resize((spec.out_w, spec.out_h), Image.Resampling.LANCZOS)

    fit_final = compute_fit(
        crown=geom.crown,
        chin=geom.chin,
        eye_left=geom.eye_left,
        eye_right=geom.eye_right,
        spec=spec,
    )
    return out, fit_final


def draw_debug(out_img: Image.Image, spec: Spec, fit: Fit) -> Image.Image:
    """Return a debug image with composition guides (crown/chin/center/eye lines) and points."""
    img = out_img.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = spec.out_w, spec.out_h

    crown_y = spec.top_margin * h
    chin_y = (spec.top_margin + spec.face_ratio) * h
    draw.line([(0, crown_y), (w, crown_y)], fill=(0, 170, 255), width=1)
    draw.line([(0, chin_y), (w, chin_y)], fill=(0, 170, 255), width=1)
    draw.line([(w / 2, 0), (w / 2, h)], fill=(0, 255, 0), width=1)
    eye_y = fit.eye_line_actual * h
    draw.line([(0, eye_y), (w, eye_y)], fill=(255, 120, 0), width=1)

    for name, (px, py) in fit.info_points.items():
        r = 3
        color = (255, 0, 0) if name in ("crown", "chin") else (255, 0, 255)
        draw.ellipse([px - r, py - r, px + r, py + r], outline=color, width=2)
    return img


def save_jpeg(img: Image.Image, path: str | Path, quality: int = 95) -> None:
    """Save as JPEG (Unicode-safe; chroma subsampling disabled for quality)."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality, subsampling=0)
    Path(path).write_bytes(buf.getvalue())


def save_png(img: Image.Image, path: str | Path) -> None:
    """Save as PNG (for debug images; Unicode-safe)."""
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    Path(path).write_bytes(buf.getvalue())
