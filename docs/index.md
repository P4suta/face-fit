# face-fit

Auto-fit any photo into an **ID-photo composition** (face 70-80% of the height,
centered, level, white background) from the command line.

It ships a default preset compliant with the LINE Yahoo ID-photo requirements
(640 x 480 px, face 70-80% of the height, white background). It performs
**geometric edits only** (roll correction, scaling, cropping, white-margin fill)
and does **no retouching** of skin or color, because the requirements forbid
"images edited so the person is hard to recognize".

## Highlights

- **MediaPipe FaceLandmarker** (478 landmarks) for precise eyes / chin / face
  width / roll angle.
- The **crown** (not a landmark) is recovered via white-background segmentation.
- A similarity transform (rotation + uniform scale + translation) fits the
  composition exactly.
- High-quality output via supersampled downscaling.
- `--debug` writes a preview with composition guides.

## Quick start

```sh
uv sync
uv run face-fit "input.jpg" -o "output.jpg"
```

See [Usage](usage.md) and [How it works](how-it-works.md) for details.
