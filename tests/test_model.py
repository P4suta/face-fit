"""Tests for the model module (network is mocked)."""

from __future__ import annotations

from pathlib import Path

from face_fit import model


def test_cache_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("FACE_FIT_CACHE", str(tmp_path))
    assert model._cache_dir() == tmp_path


def test_cache_dir_default(monkeypatch):
    monkeypatch.delenv("FACE_FIT_CACHE", raising=False)
    assert model._cache_dir() == Path.home() / ".cache" / "face-fit"


class _FakeResp:
    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self) -> bytes:
        return self._data


def test_ensure_model_downloads_then_caches(monkeypatch, tmp_path):
    monkeypatch.setenv("FACE_FIT_CACHE", str(tmp_path))
    calls = {"n": 0}

    def fake_urlopen(url):
        calls["n"] += 1
        return _FakeResp(b"MODEL-BYTES")

    monkeypatch.setattr(model.urllib.request, "urlopen", fake_urlopen)

    path = model.ensure_model()
    assert path.exists()
    assert path.read_bytes() == b"MODEL-BYTES"
    assert calls["n"] == 1

    # Second call uses the cache and does not download.
    def boom(url):
        raise AssertionError("should not download again")

    monkeypatch.setattr(model.urllib.request, "urlopen", boom)
    path2 = model.ensure_model()
    assert path2 == path
