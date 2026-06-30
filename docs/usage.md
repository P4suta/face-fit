# Usage

## Install

[uv](https://docs.astral.sh/uv/) is used.

```sh
git clone https://github.com/P4suta/face-fit.git
cd face-fit
uv sync
```

On first run the MediaPipe model (`face_landmarker.task`, ~3.7 MB) is downloaded
to `~/.cache/face-fit/` (override with the `FACE_FIT_CACHE` environment variable).

## Commands

face-fit has three commands: `fit`, `batch` and `presets`.

### `fit` — one photo

```sh
# Output defaults to <stem>_fitted.jpg next to the input
uv run face-fit fit photo.jpg

# Explicit output, guides preview, and auto-open
uv run face-fit fit photo.jpg id.jpg --debug --open

# Hot reload: re-run whenever the source changes
uv run face-fit fit photo.jpg --watch
```

The result is shown as a Rich panel with a **PASS/FAIL** badge for the 70-80%
face-ratio requirement.

### `batch` — many photos

```sh
# Folders, globs and explicit files are all accepted
uv run face-fit batch shots/ "extra/*.jpg" -o out/ --jobs 4
```

Detection is parallelized (one reusable detector per worker). Existing outputs
are skipped unless `--force` is given. A summary table reports fitted / skipped /
failed counts.

### `presets` — list presets

```sh
uv run face-fit presets
```

## Common options

| Option | Default | Description |
|---|---|---|
| `--preset` | `id-photo` | composition preset |
| `--width` / `--height` | 480 / 640 | output size (px) |
| `--face-ratio` | 0.75 | fraction of height the face (crown-to-chin) occupies |
| `--top-margin` | 0.09 | headroom fraction above the crown |
| `--quality` | 95 | JPEG quality (1-100) |
| `--render-scale` | 2 | internal supersampling factor |
| `--debug` | off | also write a `*_debug.png` with guides |
| `--json` | off | machine-readable output (no color) |
| `--quiet` | off | suppress decorative output |

## Scripting

`--json` prints a machine-readable summary, ideal for pipelines:

```sh
uv run face-fit fit photo.jpg --json | jq .face_ratio_ok
```

## Shell completion

```sh
uv run face-fit --install-completion   # bash / zsh / fish / PowerShell
uv run face-fit --show-completion      # print the script instead of installing
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | no face detected (`fit`) / at least one failure (`batch`) |
| 2 | input error (file missing, output equals input, no inputs found) |

## Notes

- Shooting issues such as glasses-lens glare or hair covering the eyes cannot be
  fixed by geometric processing.
- When multiple faces are present, the largest face is used.
