"""nox sessions (uv backend).

Examples:
    uvx nox            # default sessions (tests on all Pythons + lint + type)
    uvx nox -s tests   # unit tests on every supported Python
    uvx nox -s lint type docs
"""

from __future__ import annotations

import nox

nox.options.default_venv_backend = "uv"
nox.options.sessions = ["tests", "lint", "type"]

PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


@nox.session(python=PYTHONS)
def tests(session: nox.Session) -> None:
    """Run unit tests with coverage on every supported Python."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", *session.posargs)


@nox.session(python="3.13")
def lint(session: nox.Session) -> None:
    """Lint and format-check with ruff."""
    session.install("ruff")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(python="3.13")
def type(session: nox.Session) -> None:
    """Type-check with ty."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "dev",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ty", "check")


@nox.session(python="3.13")
def docs(session: nox.Session) -> None:
    """Build the docs in strict mode with mkdocs."""
    session.run_install(
        "uv",
        "sync",
        "--group",
        "docs",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("mkdocs", "build", "--strict")
