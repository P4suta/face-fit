# 0004. Detect-once architecture (reusable FaceDetector)

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: architecture

## Context

Detection (model load + inference) is the only expensive step; composition and
rendering take milliseconds. Two needs exposed this: parameter tweaking
(re-render the same photo many times) and batch (many photos). Loading the model
per image wastes seconds each time.

## Decision

Wrap detection in a reusable **`FaceDetector`** that loads the MediaPipe model
once and serves many `detect(rgb)` calls. `detect_face()` is a thin wrapper over a
shared cached detector; batch creates one detector per worker thread (native
inference releases the GIL, so threads parallelize). The composition math
(`compose.compute_fit`) is a dependency-free pure function, re-runnable per tweak.

## Consequences

- Batch and re-render are fast; the heavy cost is paid once.
- Clear seam for testing: the detector is mocked in unit tests, so the suite needs
  neither MediaPipe nor real images and stays fast.
- A small amount of lifecycle care (closing detectors) to keep native threads tidy.

## Alternatives considered

- **Stateless `detect_face` per call.** Simpler, but reloads the model every time —
  unacceptable for batch and interactive use.
- **Process pool for batch.** MediaPipe + Windows spawn semantics make this fragile;
  a thread pool with per-thread detectors is simpler and effective.

## References

- `src/face_fit/landmarks.py`, `src/face_fit/core.py`
