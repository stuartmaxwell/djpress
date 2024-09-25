"""Nox file."""

import nox


@nox.session(venv_backend="uv", python=["3.10", "3.11", "3.12"])
@nox.parametrize("django_ver", ["~=4.2.0", "~=5.0.0", "~=5.1.0"])
def test(session: nox.Session, django_ver: str) -> None:
    """Run the test suite."""
    session.install(".", "--all-extras", "-r", "pyproject.toml")
    session.install(f"django{django_ver}")
    session.run("pytest")
