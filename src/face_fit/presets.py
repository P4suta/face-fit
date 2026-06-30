"""Output composition presets.

The numbers follow the photo requirements:
- Image size 640 (H) x 480 (W), 4:3.
- Face (crown-to-chin) covers about 70-80% of the image height.
- White background.

`face_ratio` defaults to 0.75, the middle of the 0.70-0.80 range.
`top_margin` matches the headroom ratio in the requirement diagram (~9%).
`eye_line` is a reference value for validation/debug (vertical placement is
driven by `top_margin`).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Spec:
    """Output composition specification.

    Attributes:
        out_w: Output width in pixels.
        out_h: Output height in pixels.
        face_ratio: Fraction of the height the face (crown-to-chin) should occupy.
        top_margin: Fraction of headroom above the crown. Drives vertical placement.
        eye_line: Reference vertical position of the eyes (fraction from top). For validation.
        bg: Background color (RGB) used to fill any margins.
    """

    out_w: int = 480
    out_h: int = 640
    face_ratio: float = 0.75
    top_margin: float = 0.09
    eye_line: float = 0.45
    bg: tuple[int, int, int] = (255, 255, 255)


#: Default preset compliant with the LINE Yahoo ID-photo requirements.
ID_PHOTO = Spec()

PRESETS: dict[str, Spec] = {
    "id-photo": ID_PHOTO,
}


def get_preset(name: str) -> Spec:
    """Return a preset by name. Raises ``KeyError`` for an unknown name."""
    try:
        return PRESETS[name]
    except KeyError as exc:  # pragma: no cover - handled by the CLI
        raise KeyError(f"unknown preset: {name!r} (available: {sorted(PRESETS)})") from exc
