# 0006. Support Python 3.10 through the latest release

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: infra

## Context

The riskiest dependency for Python-version support is MediaPipe (a binding-heavy
package). It would be easy to cap `requires-python` conservatively, but that locks
out users on the newest interpreters for no real reason.

## Decision

Set `requires-python = ">=3.10"` with **no upper bound**, and test the matrix
3.10–3.14 in CI. This is safe because MediaPipe 0.10.x ships a version-agnostic
`mediapipe-<ver>-py3-none-<platform>.whl` (one wheel installs on every Python 3),
and numpy / opencv-python / pillow all publish 3.13/3.14 wheels (numpy via cp314,
opencv via abi3). uv resolves a per-interpreter-appropriate numpy.

## Consequences

- Works on the newest interpreters out of the box; verified on 3.14.
- The real ceiling is whatever MediaPipe's `py3-none` wheel supports, not an
  arbitrary pin; revisit only if a future MediaPipe drops that wheel form.

## Alternatives considered

- **Cap at `<3.13`.** Conservative but needless — it was the original guess and
  empirically wrong; the stack runs on 3.14.

## References

- `pyproject.toml`, `.github/workflows/ci.yml`, `noxfile.py`
