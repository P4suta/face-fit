# 0005. Typer + Rich CLI

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: architecture

## Context

The first cut was a single `argparse` command. The goal shifted to a CLI as
comfortable as modern web tooling: subcommands, color, a PASS/FAIL composition
badge, batch with progress, shell completion, and machine-readable output.

## Decision

Use **Typer** (subcommands, type-based parsing, shell completion) with **Rich**
(panels, tables, progress) for the CLI. A shared `core` pipeline
(`build_spec`/`fit_file`/`iter_image_files`) backs the `fit`, `batch` and
`presets` commands so presentation stays separate from logic.

## Consequences

- A polished terminal UX; `--json`/`--quiet` keep it scriptable (Rich auto-disables
  color when piped).
- Two runtime dependencies (typer, rich), both pure-Python and widely supported.
- Single-image use is now `face-fit fit INPUT` (a breaking change from the
  `argparse` form) — acceptable pre-1.0.

## Alternatives considered

- **Stay on argparse.** No new deps, but reimplementing completion, color, tables
  and subcommand ergonomics by hand is busywork.
- **Click directly.** Typer *is* Click with type-driven ergonomics and completion;
  no reason to drop down a level.

## References

- `src/face_fit/cli.py`, `src/face_fit/core.py`
