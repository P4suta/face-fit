# 0002. Geometric edits only — no retouching

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: architecture

## Context

The motivating requirement (a corporate ID / employee-directory photo) explicitly
rejects "images edited so the person is hard to recognize" and AI-altered photos,
while *also* asking the applicant to "adjust the size yourself". So resizing and
recomposition are expected, but beautification is forbidden.

## Decision

face-fit performs **only geometry**: rotation (roll correction), uniform scaling,
cropping, and white-background fill. No skin smoothing, color grading, relighting,
or generative edits. The output is the same pixels, repositioned.

## Consequences

- Output stays compliant and "still the same person"; safe for ID use.
- Predictable, explainable transforms; the composition math is a pure function.
- Lens glare, hair over the eyes, etc. are out of scope — they need a reshoot,
  not software.

## Alternatives considered

- **Add optional enhancement (auto-levels, skin retouch).** Rejected: it would
  put the tool's main use case (ID photos) on the wrong side of the requirements,
  and "optional" features get used by default.

## References

- `README.md`, `docs/how-it-works.md`
