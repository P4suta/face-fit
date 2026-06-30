# face-fit task runner. Run `just` to list recipes.
# Tooling is pinned in mise.toml; run `just setup` once after cloning.

# List recipes.
default:
    @just --list

# One-time dev setup: sync deps and install git hooks.
setup:
    uv sync --all-groups
    lefthook install

# Auto-format Python and TOML.
fmt:
    uv run ruff format .
    taplo fmt

# Lint everything (no mutation).
lint:
    uv run ruff check .
    typos
    uv run yamllint .
    actionlint
    taplo fmt --check

# Type-check with ty.
type:
    uv run ty check

# Unit tests + coverage (gate lives in pyproject.toml).
test:
    uv run pytest

# Integration tests (need real images + the MediaPipe model download).
test-integration:
    uv run pytest -m integration

# Run the unit tests on every supported Python (3.10–3.14).
test-all:
    uv run nox -s tests

# Serve the docs locally with live reload.
docs:
    uv run --group docs mkdocs serve

# Build the docs in strict mode.
docs-build:
    uv run --group docs mkdocs build --strict

# Full local gate — mirrors CI.
ci: lint type test docs-build

# Verify the pinned toolchain is present.
doctor:
    mise --version
    uv --version
    just --version
    lefthook --version
    typos --version
    committed --version
    taplo --version
    actionlint --version
