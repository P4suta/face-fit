# 0001. Record architecture decisions

- Status: accepted
- Date: 2026-06-30
- Deciders: P4suta
- Tags: infra

## Context

face-fit makes a handful of non-obvious choices (geometry-only editing, the
crown-estimation trick, the detect-once architecture). Without a record, the
*why* is lost and future contributors re-litigate settled questions.

## Decision

Use [MADR 4.0](https://adr.github.io/madr/) Architecture Decision Records under
`docs/adr/`. Each decision is one immutable file; a superseding decision links
back rather than editing the original. `docs/ADR_INDEX.md` lists them.

## Consequences

- The rationale behind a choice lives next to the code and ships in the docs site.
- A small authoring cost per decision; only architecturally significant choices
  warrant an ADR, not every change.

## Alternatives considered

- **No ADRs.** Cheapest, but the reasoning evaporates and reviews repeat.
- **A single DECISIONS.md.** Simpler, but it grows unstructured and invites
  editing past decisions in place (losing history).

## References

- <https://adr.github.io/madr/>
