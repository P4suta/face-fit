# 0003. MediaPipe FaceLandmarker + white-background crown segmentation

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: architecture

## Context

ID-photo composition needs the crown-to-chin span, the eye line (for roll), and a
horizontal center. Face detectors give the face box and some landmarks, but the
**crown** (top of the hair) is not a facial landmark — yet it defines the headroom
and the face-height ratio the requirement specifies.

## Decision

Detect with **MediaPipe FaceLandmarker** (478 landmarks) for eyes/chin/face
width/roll. Recover the crown separately by **segmenting the subject from the
white background** with a luminance threshold and scanning a vertical band around
the face center for the first subject row. Fall back to extrapolation from the
eye-chin gap when segmentation is inconclusive.

## Consequences

- Accurate, requirement-aligned composition on the expected white-background input.
- A dependency on a near-white, uniform background for best crown accuracy; the
  fallback keeps it working otherwise.
- One extra, cheap CV step (OpenCV threshold + morphology) per image.

## Alternatives considered

- **Face-box only.** Rejected: the box top sits at the forehead/hairline, not the
  crown, so headroom and face ratio would be wrong.
- **A hair/person segmentation model.** Heavier and overkill given the controlled
  white background makes a threshold sufficient.

## References

- `src/face_fit/landmarks.py`, `docs/how-it-works.md`
