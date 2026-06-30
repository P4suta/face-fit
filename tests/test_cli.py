"""Tests for the Typer CLI (face detection is mocked at the detector seam)."""

from __future__ import annotations

import json

import pytest
from PIL import Image
from typer.testing import CliRunner

from face_fit import cli
from face_fit.cli import app
from face_fit.landmarks import FaceDetector

runner = CliRunner()


@pytest.fixture(autouse=True)
def _mock_detector(monkeypatch, fake_landmarks):
    # Make every detector return our fake landmarks instead of running MediaPipe.
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: fake_landmarks)


def _img(path, size=(480, 640)):
    Image.new("RGB", size, (255, 255, 255)).save(path)


def test_fit_success_auto_output(tmp_path):
    src = tmp_path / "photo.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src)])
    assert result.exit_code == 0
    assert (tmp_path / "photo_fitted.jpg").exists()


def test_fit_explicit_output_and_debug(tmp_path):
    src = tmp_path / "p.jpg"
    _img(src)
    out = tmp_path / "out.jpg"
    result = runner.invoke(app, ["fit", str(src), str(out), "--debug"])
    assert result.exit_code == 0
    assert out.exists()
    assert (tmp_path / "out_debug.png").exists()


def test_fit_json_output(tmp_path):
    src = tmp_path / "p.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["size"] == [480, 640]
    assert payload["face_ratio_ok"] is True


def test_fit_open_calls_opener(tmp_path, monkeypatch):
    opened = {}
    monkeypatch.setattr(cli, "open_file", lambda p: opened.setdefault("p", p))
    src = tmp_path / "p.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src), "--open"])
    assert result.exit_code == 0
    assert "p" in opened


def test_fit_missing_input(tmp_path):
    result = runner.invoke(app, ["fit", str(tmp_path / "nope.jpg")])
    assert result.exit_code == 2


def test_fit_output_equals_input(tmp_path):
    src = tmp_path / "same.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src), str(src)])
    assert result.exit_code == 2


def test_fit_no_face(tmp_path, monkeypatch):
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: None)
    src = tmp_path / "p.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src)])
    assert result.exit_code == 1


def test_fit_out_of_range_face_ratio(tmp_path):
    src = tmp_path / "p.jpg"
    _img(src)
    result = runner.invoke(app, ["fit", str(src), "--face-ratio", "0.50"])
    assert result.exit_code == 0  # still succeeds, just flagged


def test_presets_command():
    result = runner.invoke(app, ["presets"])
    assert result.exit_code == 0
    assert "id-photo" in result.stdout


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "face-fit" in result.stdout
