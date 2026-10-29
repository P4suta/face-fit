# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/).

## [0.1.1](https://github.com/P4suta/face-fit/compare/v0.1.0...v0.1.1) (2026-10-29)


### Bug Fixes

* unblock dependency updates and simplify project maintenance ([#36](https://github.com/P4suta/face-fit/issues/36)) ([b830938](https://github.com/P4suta/face-fit/commit/b830938b1fb20b3f0742f5822f86f0cbe6e721d3))

## [Unreleased]

### Added

- `batch` command: fit folders / globs / multiple files in parallel, with a Rich
  progress bar, a summary table, skip-existing and `--force`.
- Reusable `FaceDetector` (loads the model once) and a shared `core` pipeline.
- `presets` command listing presets as a table.
- `fit` niceties: optional `OUTPUT` argument with auto-naming (`<stem>_fitted.jpg`),
  `--open` to open the result, `--watch` for hot reload on file change.
- `--json` machine-readable output and `--quiet`, plus a `--version` flag.
- Shell completion via Typer (`--install-completion` / `--show-completion`).

### Changed

- Require Python 3.11 or newer and Pillow 13.0.0 or newer for the supported dependency fixes.
- CLI rewritten with **Typer + Rich**. Single-image use is now `face-fit fit INPUT` (was `face-fit INPUT -o OUTPUT`).
  Rich output shows a PASS/FAIL face-ratio badge.
- Relicensed from MIT to **Apache-2.0**.
- Adopted house tooling: mise + lefthook + typos + committed (Conventional Commits)
  + justfile, with release-please, CodeQL, OpenSSF Scorecard and OSV-Scanner CI and MADR architecture decision records.

## [0.1.0] - 2026-06-30

### Added

- `face-fit` CLI that auto-fits a photo into an ID-photo composition (face
  70-80%, centered, level, white background).
- Eye line / chin / face width / roll detection via MediaPipe FaceLandmarker
  (478 landmarks).
- Crown recovery via white-background segmentation.
- Composition via a similarity transform (rotation + uniform scale + translation).
- `id-photo` preset (480x640, face ratio 0.75, top margin 0.09).
- `--debug` output with composition guides.
- Unit tests for the pure composition math.

[Unreleased]: https://github.com/P4suta/face-fit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/P4suta/face-fit/releases/tag/v0.1.0
