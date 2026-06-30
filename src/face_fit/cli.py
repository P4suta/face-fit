"""Command-line interface (Typer + Rich).

Commands:
    face-fit fit INPUT [OUTPUT]      fit a single photo
    face-fit batch INPUTS... -o DIR  fit many photos
    face-fit presets                 list composition presets

Examples:
    face-fit fit photo.jpg
    face-fit fit photo.jpg id.jpg --debug --open
    face-fit batch "*.jpg" -o out/
"""

from __future__ import annotations

import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table

from . import __version__
from .core import (
    FitReport,
    build_spec,
    default_output,
    fit_file,
    iter_image_files,
    open_file,
)
from .landmarks import FaceDetector
from .presets import PRESETS

app = typer.Typer(
    name="face-fit",
    help="Auto-fit a photo into an ID-photo composition (face 70-80%, centered, level).",
    no_args_is_help=True,
    add_completion=True,
    rich_markup_mode="rich",
)
console = Console()
err_console = Console(stderr=True)

# Reusable option type aliases (shared by fit and batch).
PresetOpt = Annotated[str, typer.Option("--preset", help="composition preset")]
WidthOpt = Annotated[int | None, typer.Option("--width", help="output width in px")]
HeightOpt = Annotated[int | None, typer.Option("--height", help="output height in px")]
FaceRatioOpt = Annotated[
    float | None, typer.Option("--face-ratio", help="fraction of height the face occupies")
]
TopMarginOpt = Annotated[
    float | None, typer.Option("--top-margin", help="headroom fraction above the crown")
]
QualityOpt = Annotated[int, typer.Option("--quality", help="JPEG quality 1-100")]
RenderScaleOpt = Annotated[
    int, typer.Option("--render-scale", help="internal supersampling factor")
]
DebugOpt = Annotated[bool, typer.Option("--debug", help="also write a *_debug.png with guides")]
JsonOpt = Annotated[bool, typer.Option("--json", help="print machine-readable JSON")]
QuietOpt = Annotated[bool, typer.Option("--quiet", "-q", help="suppress decorative output")]


def _fail(msg: str, code: int, hint: str | None = None) -> None:
    err_console.print(f"[bold red]error:[/] {msg}")
    if hint:
        err_console.print(f"[dim]hint: {hint}[/]")
    raise typer.Exit(code)


def _badge(ok: bool) -> str:
    return "[bold green]PASS[/]" if ok else "[bold red]FAIL[/]"


def _report_table(report: FitReport) -> Panel:
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="dim", justify="right")
    grid.add_column()
    grid.add_row("output", str(report.output))
    grid.add_row("size", f"{report.width}x{report.height}")
    grid.add_row(
        "face ratio",
        f"{report.face_ratio * 100:.1f}%  {_badge(report.face_ratio_ok)}  [dim](target 70-80%)[/]",
    )
    grid.add_row("eye line", f"{report.eye_line * 100:.1f}% from top")
    grid.add_row("roll fix", f"{report.roll_deg:+.2f} deg")
    grid.add_row("crown", report.crown_source)
    grid.add_row("scale", f"x{report.scale:.3f}")
    if report.debug_path:
        grid.add_row("debug", str(report.debug_path))
    ok = report.face_ratio_ok
    return Panel(
        grid,
        title="[green]done[/]" if ok else "[yellow]done (out of range)[/]",
        border_style="green" if ok else "yellow",
        expand=False,
    )


def _emit_fit(report: FitReport, *, json_out: bool, quiet: bool) -> None:
    if json_out:
        print(json.dumps(report.to_dict()))
    elif not quiet:
        console.print(_report_table(report))


def _watch(in_path: Path, run, *, json_out: bool, quiet: bool) -> None:  # pragma: no cover - loop
    if not (json_out or quiet):
        console.print(f"[dim]watching {in_path.name} for changes (Ctrl+C to stop)…[/]")
    last = in_path.stat().st_mtime
    try:
        while True:
            time.sleep(0.5)
            if not in_path.exists():
                continue
            mtime = in_path.stat().st_mtime
            if mtime != last:
                last = mtime
                try:
                    _emit_fit(run(), json_out=json_out, quiet=quiet)
                except RuntimeError as exc:
                    err_console.print(f"[bold red]error:[/] {exc}")
    except KeyboardInterrupt:
        if not (json_out or quiet):
            console.print("[dim]stopped.[/]")


@app.command()
def fit(
    input: Annotated[Path, typer.Argument(help="input image path")],
    output: Annotated[
        Path | None, typer.Argument(help="output JPEG (default: <stem>_fitted.jpg)")
    ] = None,
    preset: PresetOpt = "id-photo",
    width: WidthOpt = None,
    height: HeightOpt = None,
    face_ratio: FaceRatioOpt = None,
    top_margin: TopMarginOpt = None,
    quality: QualityOpt = 95,
    render_scale: RenderScaleOpt = 2,
    debug: DebugOpt = False,
    open_result: Annotated[
        bool, typer.Option("--open", help="open the result in the default viewer")
    ] = False,
    watch: Annotated[bool, typer.Option("--watch", help="re-run when the input changes")] = False,
    json_out: JsonOpt = False,
    quiet: QuietOpt = False,
) -> None:
    """Fit a single photo into the ID-photo composition."""
    if not input.exists():
        _fail(f"input does not exist: {input}", 2)
    out = output or default_output(input)
    if out.resolve() == input.resolve():
        _fail("output is the same path as input (overwrite guard)", 2)

    spec = build_spec(
        preset, width=width, height=height, face_ratio=face_ratio, top_margin=top_margin
    )

    def run() -> FitReport:
        return fit_file(input, out, spec, render_scale=render_scale, quality=quality, debug=debug)

    try:
        if quiet or json_out:
            report = run()
        else:
            with console.status(f"[bold]Detecting face[/] in {input.name}…", spinner="dots"):
                report = run()
    except RuntimeError as exc:
        _fail(str(exc), 1, hint="use a clear, front-facing photo with a plain background")

    _emit_fit(report, json_out=json_out, quiet=quiet)
    if open_result:
        open_file(out)
    if watch:
        _watch(input, run, json_out=json_out, quiet=quiet)


def _plan_batch(
    files: list[Path], output_dir: Path, *, force: bool
) -> tuple[list[tuple[Path, Path]], list[Path]]:
    """Split inputs into (to-process, skipped-because-output-exists)."""
    tasks: list[tuple[Path, Path]] = []
    skipped: list[Path] = []
    for f in files:
        out = output_dir / f"{f.stem}.jpg"
        if out.exists() and not force:
            skipped.append(f)
        else:
            tasks.append((f, out))
    return tasks, skipped


def _run_batch(
    tasks: list[tuple[Path, Path]],
    spec,
    *,
    render_scale: int,
    quality: int,
    debug: bool,
    jobs: int,
    show_progress: bool,
) -> tuple[list[FitReport], list[tuple[Path, str]]]:
    """Process tasks across a thread pool (one reusable detector per worker)."""
    workers = jobs if jobs > 0 else min(4, os.cpu_count() or 1)
    tls = threading.local()
    detectors: list[FaceDetector] = []
    lock = threading.Lock()
    reports: list[FitReport] = []
    failures: list[tuple[Path, str]] = []

    def work(task: tuple[Path, Path]) -> FitReport:
        detector = getattr(tls, "detector", None)
        if detector is None:
            detector = FaceDetector()
            with lock:
                detectors.append(detector)
            tls.detector = detector
        f, out = task
        return fit_file(
            f, out, spec, render_scale=render_scale, quality=quality, debug=debug, detector=detector
        )

    def run_pool(on_done) -> None:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futures = {pool.submit(work, t): t for t in tasks}
            for fut in futures:
                src = futures[fut][0]
                try:
                    reports.append(fut.result())
                except (RuntimeError, OSError) as exc:
                    failures.append((src, str(exc)))
                on_done()

    try:
        if not show_progress:
            run_pool(lambda: None)
        else:
            with Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task_id = progress.add_task("fitting", total=len(tasks))
                run_pool(lambda: progress.advance(task_id))
    finally:
        for det in detectors:
            det.close()
    return reports, failures


@app.command()
def batch(
    inputs: Annotated[list[str], typer.Argument(help="images, directories or glob patterns")],
    output_dir: Annotated[Path, typer.Option("-o", "--output-dir", help="destination directory")],
    preset: PresetOpt = "id-photo",
    width: WidthOpt = None,
    height: HeightOpt = None,
    face_ratio: FaceRatioOpt = None,
    top_margin: TopMarginOpt = None,
    quality: QualityOpt = 95,
    render_scale: RenderScaleOpt = 2,
    debug: DebugOpt = False,
    jobs: Annotated[int, typer.Option("-j", "--jobs", help="parallel workers (0 = auto)")] = 0,
    force: Annotated[bool, typer.Option("--force", help="overwrite existing outputs")] = False,
    json_out: JsonOpt = False,
    quiet: QuietOpt = False,
) -> None:
    """Fit many photos at once (folders, globs), in parallel."""
    files = iter_image_files(inputs)
    if not files:
        _fail("no input images found", 2)

    spec = build_spec(
        preset, width=width, height=height, face_ratio=face_ratio, top_margin=top_margin
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    tasks, skipped = _plan_batch(files, output_dir, force=force)

    reports, failures = _run_batch(
        tasks,
        spec,
        render_scale=render_scale,
        quality=quality,
        debug=debug,
        jobs=jobs,
        show_progress=not (quiet or json_out),
    )

    if json_out:
        print(
            json.dumps(
                {
                    "processed": [r.to_dict() for r in reports],
                    "skipped": [str(p) for p in skipped],
                    "failed": [{"input": str(p), "error": e} for p, e in failures],
                }
            )
        )
    elif not quiet:
        _emit_batch_summary(reports, skipped, failures, output_dir)

    if failures:
        raise typer.Exit(1)


def _emit_batch_summary(
    reports: list[FitReport],
    skipped: list[Path],
    failures: list[tuple[Path, str]],
    output_dir: Path,
) -> None:
    out_of_range = [r for r in reports if not r.face_ratio_ok]
    table = Table.grid(padding=(0, 2))
    table.add_column(style="dim", justify="right")
    table.add_column()
    table.add_row("output dir", str(output_dir))
    table.add_row("fitted", f"[green]{len(reports)}[/]")
    table.add_row("skipped (exists)", f"[yellow]{len(skipped)}[/]" if skipped else "0")
    table.add_row("failed", f"[red]{len(failures)}[/]" if failures else "0")
    if out_of_range:
        table.add_row("out of 70-80%", f"[yellow]{len(out_of_range)}[/]")
    console.print(Panel(table, title="batch summary", expand=False))
    for src, err in failures:
        err_console.print(f"[red]failed:[/] {src} - {err}")


@app.command()
def presets() -> None:
    """List the available composition presets."""
    table = Table(title="presets")
    table.add_column("name", style="bold")
    table.add_column("size")
    table.add_column("face ratio")
    table.add_column("top margin")
    table.add_column("background")
    for name, spec in PRESETS.items():
        table.add_row(
            name,
            f"{spec.out_w}x{spec.out_h}",
            f"{spec.face_ratio:.2f}",
            f"{spec.top_margin:.2f}",
            str(spec.bg),
        )
    console.print(table)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"face-fit {__version__}")
        raise typer.Exit(0)


@app.callback()
def _main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="show the version and exit",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """face-fit command-line interface."""


if __name__ == "__main__":  # pragma: no cover
    app()
