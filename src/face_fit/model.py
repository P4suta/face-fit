"""Fetch and cache the MediaPipe FaceLandmarker model (.task)."""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
_MODEL_NAME = "face_landmarker.task"


def _cache_dir() -> Path:
    base = os.environ.get("FACE_FIT_CACHE")
    if base:
        return Path(base)
    return Path.home() / ".cache" / "face-fit"


def ensure_model() -> Path:
    """Return the model path, downloading and caching it if missing."""
    cache = _cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / _MODEL_NAME
    if path.exists() and path.stat().st_size > 0:
        return path

    tmp = path.with_suffix(".task.part")
    with urllib.request.urlopen(_MODEL_URL) as resp:  # noqa: S310 (trusted Google CDN)
        data = resp.read()
    tmp.write_bytes(data)
    tmp.replace(path)
    return path
