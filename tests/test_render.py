"""Tests for the render module (synthetic data)."""

from __future__ import annotations

from PIL import Image

from face_fit.presets import ID_PHOTO
from face_fit.render import draw_debug, fit_to_image, save_jpeg, save_png


def test_fit_to_image_size_and_type(synthetic_rgb, fake_geometry):
    out, fit = fit_to_image(synthetic_rgb, fake_geometry, ID_PHOTO, render_scale=1)
    assert out.size == (ID_PHOTO.out_w, ID_PHOTO.out_h)
    assert out.mode == "RGB"
    assert fit.scale > 0
    # By construction, face ratio == face_ratio.
    assert abs((fit.chin_line_actual - ID_PHOTO.top_margin) - ID_PHOTO.face_ratio) < 1e-6


def test_fit_to_image_supersample(synthetic_rgb, fake_geometry):
    out, _ = fit_to_image(synthetic_rgb, fake_geometry, ID_PHOTO, render_scale=2)
    assert out.size == (ID_PHOTO.out_w, ID_PHOTO.out_h)


def test_draw_debug_size(synthetic_rgb, fake_geometry):
    out, fit = fit_to_image(synthetic_rgb, fake_geometry, ID_PHOTO, render_scale=1)
    dbg = draw_debug(out, ID_PHOTO, fit)
    assert dbg.size == out.size
    assert dbg.mode == "RGB"


def test_save_jpeg(tmp_path, synthetic_rgb, fake_geometry):
    out, _ = fit_to_image(synthetic_rgb, fake_geometry, ID_PHOTO, render_scale=1)
    p = tmp_path / "o.jpg"
    save_jpeg(out, p)
    assert p.exists()
    assert Image.open(p).size == (ID_PHOTO.out_w, ID_PHOTO.out_h)


def test_save_png(tmp_path, synthetic_rgb, fake_geometry):
    out, _ = fit_to_image(synthetic_rgb, fake_geometry, ID_PHOTO, render_scale=1)
    p = tmp_path / "o.png"
    save_png(out, p)
    assert p.exists()
    assert Image.open(p).format == "PNG"
