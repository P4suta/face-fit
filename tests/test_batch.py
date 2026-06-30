"""Tests for the batch command."""

from __future__ import annotations

import json

import pytest
from PIL import Image
from typer.testing import CliRunner

from face_fit.cli import app
from face_fit.landmarks import FaceDetector

runner = CliRunner()


@pytest.fixture(autouse=True)
def _mock_detector(monkeypatch, fake_landmarks):
    monkeypatch.setattr(FaceDetector, "_run", lambda self, rgb: fake_landmarks)


def _make_images(d, names):
    for n in names:
        Image.new("RGB", (480, 640), (255, 255, 255)).save(d / n)


def test_batch_processes_directory(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _make_images(src, ["a.jpg", "b.png"])
    out = tmp_path / "out"
    result = runner.invoke(app, ["batch", str(src), "-o", str(out), "--jobs", "2"])
    assert result.exit_code == 0
    assert (out / "a.jpg").exists()
    assert (out / "b.jpg").exists()


def test_batch_skips_existing_then_force(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _make_images(src, ["a.jpg"])
    out = tmp_path / "out"
    runner.invoke(app, ["batch", str(src), "-o", str(out)])
    # second run: existing output is skipped
    r2 = runner.invoke(app, ["batch", str(src), "-o", str(out), "--json"])
    payload = json.loads(r2.stdout.strip().splitlines()[-1])
    assert len(payload["skipped"]) == 1
    assert len(payload["processed"]) == 0
    # with --force it is reprocessed
    r3 = runner.invoke(app, ["batch", str(src), "-o", str(out), "--force", "--json"])
    payload3 = json.loads(r3.stdout.strip().splitlines()[-1])
    assert len(payload3["processed"]) == 1


def test_batch_no_inputs(tmp_path):
    out = tmp_path / "out"
    result = runner.invoke(app, ["batch", str(tmp_path / "empty"), "-o", str(out)])
    assert result.exit_code == 2


def test_batch_glob(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _make_images(src, ["a.jpg", "b.jpg"])
    out = tmp_path / "out"
    result = runner.invoke(app, ["batch", str(src / "*.jpg"), "-o", str(out)])
    assert result.exit_code == 0
    assert len(list(out.glob("*.jpg"))) == 2
