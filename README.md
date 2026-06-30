# face-fit

[![CI](https://github.com/P4suta/face-fit/actions/workflows/ci.yml/badge.svg)](https://github.com/P4suta/face-fit/actions/workflows/ci.yml)
[![Docs](https://github.com/P4suta/face-fit/actions/workflows/docs.yml/badge.svg)](https://p4suta.github.io/face-fit/)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/P4suta/face-fit/badge)](https://scorecard.dev/viewer/?uri=github.com/P4suta/face-fit)
[![Python](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue)](https://github.com/P4suta/face-fit)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with ty](https://img.shields.io/badge/types-ty-261230)](https://github.com/astral-sh/ty)

Auto-fit any photo into an **ID-photo composition** (face 70-80% of the height,
centered, level, white background) from the command line.

**Project page:** [p4suta.github.io/face-fit](https://p4suta.github.io/face-fit/)

Ships a default preset compliant with the LINE Yahoo ID-photo requirements
(640 x 480 px, face 70-80% of the height, white background). It performs
**geometric edits only** (roll correction, scaling, cropping, white-margin fill)
and does **no retouching** of skin or color, because the requirements forbid
"images edited so the person is hard to recognize".

## How it works

1. **MediaPipe FaceLandmarker** (478 landmarks) locates the eyes, chin, face
   width, center and roll angle.
2. The **crown** (top of the head), which is not a landmark, is recovered by
   segmenting the subject from the white background (luminance threshold).
3. A **similarity transform** (rotation + uniform scale + translation) maps the
   face to the target composition; Pillow renders it, fills white, and downscales.

See the [documentation](https://p4suta.github.io/face-fit/) for details.

## Setup

[uv](https://docs.astral.sh/uv/) is used. Supported Python: **3.10 to latest (3.14)**.

```sh
uv sync
```

> The default dev interpreter is pinned to 3.13 via `.python-version`; uv fetches it.
> On first run the MediaPipe model (`face_landmarker.task`, ~3.7 MB) is downloaded
> to `~/.cache/face-fit/` (override with `FACE_FIT_CACHE`).

## Usage

```sh
# Fit one photo (output defaults to <stem>_fitted.jpg)
uv run face-fit fit photo.jpg

# Explicit output, guides preview, and auto-open the result
uv run face-fit fit photo.jpg id.jpg --debug --open

# Re-run automatically whenever the source file changes (hot reload)
uv run face-fit fit photo.jpg --watch

# Fit a whole folder / glob in parallel
uv run face-fit batch "shots/*.jpg" -o out/

# List presets, print the version
uv run face-fit presets
uv run face-fit --version
```

Each command shows a Rich summary with a **PASS/FAIL** badge for the 70-80%
face-ratio requirement. Add `--json` for machine-readable output (pipe-friendly,
no color) and `--quiet` to suppress decorative output.

### Main options (`fit` / `batch`)

| Option | Default | Description |
|---|---|---|
| `--preset` | `id-photo` | composition preset |
| `--width` / `--height` | 480 / 640 | output size (px) |
| `--face-ratio` | 0.75 | fraction of height the face occupies |
| `--top-margin` | 0.09 | headroom fraction above the crown |
| `--quality` | 95 | JPEG quality |
| `--render-scale` | 2 | internal supersampling factor |
| `--debug` | off | also write a `*_debug.png` with guides |
| `--open` | off | open the result in the default viewer (`fit`) |
| `--watch` | off | re-run when the input changes (`fit`) |
| `-j, --jobs` | auto | parallel workers (`batch`) |
| `--force` | off | overwrite existing outputs (`batch`) |

The output is never written to the input path (overwrite guard).

### Shell completion

```sh
uv run face-fit --install-completion   # bash / zsh / fish / PowerShell
```

## Development

Tooling is pinned in `mise.toml` and driven through a `justfile`.

```sh
mise install      # provision uv / just / lefthook / typos / committed / taplo
just setup        # uv sync --all-groups + install git hooks (lefthook)

just lint         # ruff + typos + yamllint + actionlint + taplo
just type         # ty
just test         # unit tests + coverage
just test-all     # tests on every supported Python (3.10–3.14)
just docs         # serve the docs locally
just ci           # full local gate (mirrors CI)
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
(enforced locally by `committed` and on PRs by the title check); releases are cut
by [release-please](https://github.com/googleapis/release-please). See
[CONTRIBUTING.md](CONTRIBUTING.md) and the
[Architecture Decision Records](docs/ADR_INDEX.md).

## Notes

- Shooting issues such as glasses-lens glare or hair covering the eyes cannot be
  fixed by geometric processing.
- A higher-resolution portrait makes the best input (the tool zooms in, then
  downscales to the target size).

## License

[Apache-2.0](LICENSE) © 2026 face-fit contributors
