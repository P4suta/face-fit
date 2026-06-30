"""Tests for the core pipeline helpers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from face_fit import core
from face_fit.presets import ID_PHOTO


def _write_image(path: Path, size=(480, 640)) -> None:
    Image.new("RGB", size, (255, 255, 255)).save(path)


def test_build_spec_default_and_overrides():
    assert core.build_spec("id-photo") is ID_PHOTO
    spec = core.build_spec("id-photo", face_ratio=0.8, width=600)
    assert spec.face_ratio == 0.8
    assert spec.out_w == 600
    assert spec.out_h == ID_PHOTO.out_h  # untouched


def test_default_output():
    assert core.default_output(Path("a/b/photo.png")).name == "photo_fitted.jpg"


def test_fit_file_writes_and_reports(monkeypatch, tmp_path, synthetic_rgb, fake_geometry):
    monkeypatch.setattr(core, "detect_face", lambda rgb: fake_geometry)
    monkeypatch.setattr(core, "load_rgb", lambda p: synthetic_rgb)
    src = tmp_path / "in.jpg"
    _write_image(src)
    out = tmp_path / "sub" / "out.jpg"  # nested dir is created
    report = core.fit_file(src, out, ID_PHOTO, debug=True)

    assert out.exists()
    assert report.debug_path is not None and report.debug_path.exists()
    assert (report.width, report.height) == (480, 640)
    assert report.face_ratio_ok is True
    assert "face_ratio" in report.to_dict()


def test_iter_image_files_dir_glob_dedup(tmp_path):
    (tmp_path / "a.jpg").write_bytes(b"x")
    (tmp_path / "b.png").write_bytes(b"x")
    (tmp_path / "c.txt").write_bytes(b"x")  # ignored ext
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "d.jpeg").write_bytes(b"x")

    # directory expansion
    in_dir = core.iter_image_files([str(tmp_path)])
    names = {p.name for p in in_dir}
    assert names == {"a.jpg", "b.png"}  # non-recursive, ext-filtered

    # glob + explicit file, de-duplicated
    mixed = core.iter_image_files([str(tmp_path / "*.jpg"), str(tmp_path / "a.jpg")])
    assert [p.name for p in mixed] == ["a.jpg"]


def test_open_file_uses_startfile_on_windows(monkeypatch, tmp_path):
    called = {}
    monkeypatch.setattr(core.os, "startfile", lambda t: called.setdefault("t", t), raising=False)
    p = tmp_path / "x.jpg"
    p.write_bytes(b"x")
    core.open_file(p)
    assert called["t"] == str(p)
