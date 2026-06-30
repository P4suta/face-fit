"""Shared high-level pipeline used by the CLI commands.

Wraps the load -> detect -> fit -> save flow and small helpers (output naming,
input expansion, opening files) so that the ``fit`` and ``batch`` commands stay
thin. Reuses :mod:`face_fit.landmarks`, :mod:`face_fit.compose`,
:mod:`face_fit.render` and :mod:`face_fit.presets`.
"""

from __future__ import annotations

import dataclasses
import glob
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .landmarks import FaceDetector, detect_face, load_rgb
from .presets import Spec, get_preset
from .render import draw_debug, fit_to_image, save_jpeg, save_png

#: Required face-ratio range from the ID-photo requirements.
FACE_RATIO_MIN = 0.70
FACE_RATIO_MAX = 0.80

#: Image extensions recognized when expanding directories/globs.
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class FitReport:
    """Outcome of fitting one image."""

    input: Path
    output: Path
    width: int
    height: int
    face_ratio: float
    face_ratio_ok: bool
    eye_line: float
    roll_deg: float
    crown_source: str
    scale: float
    debug_path: Path | None

    def to_dict(self) -> dict:
        """Return a JSON-serializable summary."""
        return {
            "input": str(self.input),
            "output": str(self.output),
            "size": [self.width, self.height],
            "face_ratio": round(self.face_ratio, 4),
            "face_ratio_ok": self.face_ratio_ok,
            "eye_line": round(self.eye_line, 4),
            "roll_deg": round(self.roll_deg, 3),
            "crown_source": self.crown_source,
            "scale": round(self.scale, 4),
            "debug_path": str(self.debug_path) if self.debug_path else None,
        }


def build_spec(
    preset: str,
    *,
    width: int | None = None,
    height: int | None = None,
    face_ratio: float | None = None,
    top_margin: float | None = None,
) -> Spec:
    """Resolve a preset and apply optional overrides."""
    spec = get_preset(preset)
    overrides: dict[str, object] = {}
    if width:
        overrides["out_w"] = width
    if height:
        overrides["out_h"] = height
    if face_ratio is not None:
        overrides["face_ratio"] = face_ratio
    if top_margin is not None:
        overrides["top_margin"] = top_margin
    return dataclasses.replace(spec, **overrides) if overrides else spec


def default_output(in_path: Path) -> Path:
    """Derive a default output path next to the input (``<stem>_fitted.jpg``)."""
    return in_path.with_name(in_path.stem + "_fitted.jpg")


def fit_file(
    in_path: Path,
    out_path: Path,
    spec: Spec,
    *,
    render_scale: int = 2,
    quality: int = 95,
    debug: bool = False,
    detector: FaceDetector | None = None,
) -> FitReport:
    """Run the full pipeline on one file and write the JPEG output.

    Args:
        in_path: Source image path.
        out_path: Destination JPEG path.
        spec: Target composition.
        render_scale: Internal supersampling factor.
        quality: JPEG quality.
        debug: Also write a ``*_debug.png`` with composition guides.
        detector: Reusable detector (recommended for batch); falls back to the
            shared default detector when ``None``.

    Returns:
        A :class:`FitReport`.
    """
    rgb = load_rgb(in_path)
    geom = detector.detect(rgb) if detector is not None else detect_face(rgb)
    out_img, fit = fit_to_image(rgb, geom, spec, render_scale=render_scale)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    save_jpeg(out_img, out_path, quality=quality)

    debug_path: Path | None = None
    if debug:
        debug_img = draw_debug(out_img, spec, fit)
        debug_path = out_path.with_name(out_path.stem + "_debug.png")
        save_png(debug_img, debug_path)

    face_pct = fit.chin_line_actual - spec.top_margin
    return FitReport(
        input=in_path,
        output=out_path,
        width=spec.out_w,
        height=spec.out_h,
        face_ratio=face_pct,
        face_ratio_ok=FACE_RATIO_MIN <= face_pct <= FACE_RATIO_MAX,
        eye_line=fit.eye_line_actual,
        roll_deg=fit.roll_deg,
        crown_source="segmentation" if geom.crown_from_segmentation else "extrapolated",
        scale=fit.scale,
        debug_path=debug_path,
    )


def iter_image_files(inputs: list[str]) -> list[Path]:
    """Expand a list of files, directories and glob patterns into image paths.

    Directories are scanned non-recursively. Results are de-duplicated and sorted.
    """
    found: list[Path] = []
    seen: set[Path] = set()

    def add(p: Path) -> None:
        rp = p.resolve()
        if rp not in seen and p.suffix.lower() in IMAGE_EXTS:
            seen.add(rp)
            found.append(p)

    for item in inputs:
        path = Path(item)
        if path.is_dir():
            for child in sorted(path.iterdir()):
                if child.is_file():
                    add(child)
        elif any(ch in item for ch in "*?[") and not path.exists():
            for match in sorted(glob.glob(item)):  # noqa: PTH207 (glob patterns)
                mp = Path(match)
                if mp.is_file():
                    add(mp)
        elif path.is_file():
            add(path)
    return found


def open_file(path: Path) -> None:
    """Open a file with the OS default application (Windows/macOS/Linux)."""
    target = str(path)
    startfile = getattr(os, "startfile", None)
    if startfile is not None:  # Windows
        startfile(target)
        return
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.run([opener, target], check=False)  # noqa: S603
