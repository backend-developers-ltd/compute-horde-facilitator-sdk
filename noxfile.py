import os

import nox

os.environ["PDM_IGNORE_SAVED_PYTHON"] = "1"

CI = os.environ.get("CI") is not None
PYTHON_VERSIONS = ["3.11"]

nox.options.default_venv_backend = "venv"
nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = not CI
nox.options.tags = ["check"]


def install(session: nox.Session, *args, no_default=False):
    other_args = []
    for group in args:
        other_args.extend(["--group", group])
    if no_default:
        other_args.append("--no-default")
    session.run("pdm", "install", "--check", *other_args, external=True)


@nox.session(name="lint-fix", tags=["fix"], python=PYTHON_VERSIONS)
def lint_fix(session: nox.Session):
    """Lint the code and apply fixes in-place whenever possible."""
    install(session, "format", no_default=True)
    session.run("ruff", "check", "--fix", ".")


@nox.session(name="format", tags=["fix"], python=PYTHON_VERSIONS)
def format_(session: nox.Session):
    """Lint the code and apply fixes in-place whenever possible."""
    install(session, "format", no_default=True)
    session.run("ruff", "format", ".")


@nox.session(tags=["check"], python=PYTHON_VERSIONS)
def lint(session: nox.Session):
    """Run linters in readonly mode."""
    install(session, "format", no_default=True)
    session.run("ruff", "check", "--diff", ".")


@nox.session(tags=["check"], python=PYTHON_VERSIONS)
def codespell(session: nox.Session):
    install(session, "codespell", no_default=True)
    session.run("codespell", ".")


@nox.session(name="format-check", tags=["check"], python=PYTHON_VERSIONS)
def format_check(session: nox.Session):
    """Run linters in readonly mode."""
    install(session, "format", no_default=True)
    session.run("ruff", "format", "--diff", ".")


@nox.session(tags=["test"], python=PYTHON_VERSIONS)
def test(session):
    install(session, "test")
    session.run(
        "pytest",
        "-W",
        "ignore::DeprecationWarning",
        "-s",
        "-x",
        "-vv",
        # '-n', 'auto',
        "tests",
        *session.posargs,
    )
