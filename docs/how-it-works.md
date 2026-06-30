# How it works

face-fit builds the ID-photo composition with **geometric edits only**, in three
stages.

## 1. Detection (`landmarks.py`)

[MediaPipe FaceLandmarker](https://ai.google.dev/edge/mediapipe) (478 landmarks)
provides:

- the two eye centers (iris landmarks 468 / 473) -> **eye line** and **roll angle**
- the chin tip (landmark 152)
- the left/right cheek extremes (234 / 454) -> **face width**

## 2. Crown recovery (white-background segmentation)

Landmarks do not include the crown (top of the head). Because ID photos have a
uniform white background, the subject silhouette is extracted with a **luminance
threshold**, and a vertical band around the face center is scanned from the top;
the first row where subject pixels line up is the crown. On failure it
extrapolates from the eye-chin gap.

## 3. Composition (`compose.py` -> `render.py`)

From the crown, chin and eyes, a **similarity transform** (rotation + uniform
scale + translation) is solved analytically so that:

- the line between the eyes is level (roll correction)
- crown-to-chin height equals `out_h * face_ratio`
- the crown sits at `top_margin`, and the eye midpoint is horizontally centered

Pillow applies the transform and fills margins with white. For quality it renders
at `render_scale` times the size and downscales with LANCZOS.

```text
input ──[FaceLandmarker]──▶ eyes / chin / face width
      └─[white-bg segmentation]─▶ crown
                          │
                          ▼
                similarity transform (compose)
                          │
                          ▼
         affine apply → white fill → downscale (render)
                          │
                          ▼
                   480x640 JPEG
```

The composition math (`compose.compute_fit`) is a pure function that never
touches the image and is covered by unit tests. See the
[API reference](reference.md).
