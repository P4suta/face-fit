# Architecture Decision Records

This directory holds [MADR 4.0](https://adr.github.io/madr/)
Architecture Decision Records. Each file documents one decision; once accepted an
ADR is never edited — it is *superseded* by a later ADR that links back.

| ADR                                                            | Title                                            | Status   |
| -------------------------------------------------------------- | ------------------------------------------------ | -------- |
| [0001](./adr/0001-record-architecture-decisions.md)            | Record architecture decisions                    | accepted |
| [0002](./adr/0002-geometric-edits-only.md)                     | Geometric edits only — no retouching             | accepted |
| [0003](./adr/0003-mediapipe-landmarker-and-crown-segmentation.md) | MediaPipe FaceLandmarker + crown segmentation | accepted |
| [0004](./adr/0004-detect-once-architecture.md)                 | Detect-once architecture (reusable FaceDetector) | accepted |
| [0005](./adr/0005-typer-rich-cli.md)                           | Typer + Rich CLI                                 | accepted |
| [0006](./adr/0006-support-python-3.10-to-latest.md)            | Support Python 3.10 through the latest release   | accepted |

## Authoring a new ADR

1. Copy `adr/0000-template.md` to `adr/NNNN-short-slug.md` with the next
   sequential number.
2. Fill in the sections; keep paragraphs short and action-oriented.
3. Add a row to the table above.
4. Open a PR. ADRs are normally accepted on merge; controversial ones are landed
   as `proposed` and flipped to `accepted` once the discussion concludes.
