---
date: 2026-10-22
---

# Require supported Pillow on Python 3.11

## Status

Accepted.
Supersedes the Python floor in [ADR 0006](0006-support-python-3.10-to-latest.md).
Its open upper Python bound still applies.

## Context

The Python 3.10 lock branch selects Pillow 12.3.0 and fails the dependency scan.
[Pillow 13](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html) contains security fixes and requires Python 3.11.
Retaining Python 3.10 prevents that branch from receiving those fixes.

## Decision

Require Python 3.11 or newer and Pillow 13.0.0 or newer in package metadata.
Use the same Python floor in Ruff, Nox, and the CI matrix.
Keep the frozen lockfile and dependency scan as gates for every supported interpreter.
Preserve the original ADR file and record its changed compatibility contract here.

## Consequences

Python 3.10 users must upgrade their interpreter before installing this version.
Supported interpreters share a dependency floor that includes the Pillow fixes.
Future dependencies can raise that floor only with an explicit compatibility decision and matching checks.

## Alternatives

Keeping Python 3.10 retains the flagged dependency branch.
Suppressing its advisories hides the unresolved dependency risk.
Maintaining a private Pillow backport would add an unsupported image-decoder maintenance obligation.
