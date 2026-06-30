"""Tests for the presets module."""

from __future__ import annotations

import dataclasses

import pytest

from face_fit.presets import ID_PHOTO, PRESETS, Spec, get_preset


def test_id_photo_defaults():
    assert ID_PHOTO.out_w == 480
    assert ID_PHOTO.out_h == 640
    assert 0.70 <= ID_PHOTO.face_ratio <= 0.80
    assert ID_PHOTO.bg == (255, 255, 255)


def test_get_preset_known():
    assert get_preset("id-photo") is ID_PHOTO
    assert "id-photo" in PRESETS


def test_get_preset_unknown_raises():
    with pytest.raises(KeyError):
        get_preset("does-not-exist")


def test_spec_is_frozen():
    spec = Spec()
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.out_w = 100  # ty: ignore[invalid-assignment]
