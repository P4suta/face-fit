# Contributing

Thanks for your interest in face-fit. Bug reports, feature ideas and pull
requests are welcome.

## Development setup

Tooling is pinned in [`mise.toml`](https://github.com/P4suta/face-fit/blob/main/mise.toml)
and driven through a [`justfile`](https://github.com/P4suta/face-fit/blob/main/justfile).
[uv](https://docs.astral.sh/uv/) manages the Python deps.

```sh
git clone https://github.com/P4suta/face-fit.git
cd face-fit
mise install      # provision uv / just / lefthook / typos / committed / taplo / actionlint
just setup        # uv sync --all-groups + lefthook install (git hooks)
```

> The Python interpreter is chosen by uv from `.python-version` (3.13); the
> supported range is 3.10 to latest (3.14).

## Everyday commands

| Task | Command |
|---|---|
| Lint | `just lint` |
| Format | `just fmt` |
| Type check | `just type` |
| Tests (unit) | `just test` |
| Tests (integration) | `just test-integration` |
| Test all Pythons | `just test-all` |
| Serve docs | `just docs` |
| Full local gate | `just ci` |

Integration tests need real images (`FACE_FIT_SAMPLES`, or samples next to the
repo) and a MediaPipe model download; they are skipped when images are absent.

## Commits and pull requests

- **Conventional Commits.** Commit messages follow
  [Conventional Commits](https://www.conventionalcommits.org/) — enforced locally
  by the `committed` hook (commit-msg) and on PRs by the title check. Allowed
  types: `feat`, `fix`, `perf`, `docs`, `refactor`, `test`, `chore`, `ci`,
  `build`, `deps`, `style`, `revert`. Use lowercase subjects (`feat: add ...`).
- The git hooks (lefthook) run typos / ruff / taplo on commit and ty / pytest on
  push. Do not bypass with `--no-verify`.
- `just ci` must pass and coverage must not drop.

## Releases

Releases are automated by
[release-please](https://github.com/googleapis/release-please): merged
Conventional Commits keep a Release PR open that bumps the version and updates
`CHANGELOG.md`. Cutting a release is deliberate — a maintainer adds the
**`release: approved`** label (the CI `release-gate` job blocks the merge until
then), and merging the Release PR tags `vX.Y.Z`.

## Architecture decisions

Significant choices are recorded as
[ADRs](https://github.com/P4suta/face-fit/blob/main/docs/ADR_INDEX.md) (MADR
format). Add one when a change is architecturally significant.

## Design principles

- Perform **geometric edits only**; no skin or color retouching (the ID-photo
  requirements forbid edits that obscure identity — see
  [ADR-0002](https://github.com/P4suta/face-fit/blob/main/docs/adr/0002-geometric-edits-only.md)).
- Keep the composition math (`compose.py`) a dependency-free **pure function**.

## License

By contributing, you agree that your contributions are licensed under the
[Apache-2.0 License](https://github.com/P4suta/face-fit/blob/main/LICENSE)
(inbound = outbound).
