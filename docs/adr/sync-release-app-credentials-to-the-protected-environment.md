---
date: 2026-11-09
status: proposed
---

# Sync release App credentials to the protected environment

## Context

The release App requires stored credentials.
Doppler's [identity limit](https://docs.doppler.com/docs/platform-limits) constrains fleet growth.
The release-please environment admits main and prevents administrator bypass.

## Decision

Use [native GitHub synchronization](https://docs.doppler.com/docs/github-actions) from a purpose-specific config into the existing environment.
Pass named secrets only to repository-scoped App token actions with explicit permissions.
Keep release approval and GitHub Pages authentication unchanged.
Run read-only credential verification only on explicit dispatch from main.

## Alternatives

Doppler OIDC avoids GitHub copies and retains workflow and event claims, but consumes identity capacity.
A service token adds another stored credential.

## Consequences

GitHub stores credential copies.
Protected main and environment policies replace Doppler claims.
The shared App key retains authority across its installations.
Reconsider when the App supports workload identity.

## Confirmation

Verify synchronization and read-only App authentication from reviewed main before identity retirement.
Pause release proposals and documentation publication during merge, then restore their previous states.
Migration creates no release, tag, or package publication.
