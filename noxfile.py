"""Nox file."""

import nox


@nox.session(venv_backend="uv", python=["3.10", "3.11", "3.12", "3.13"])
@nox.parametrize("django_ver", ["~=4.2.0", "~=5.0.0", "~=5.1.0", ">=5.2b1,<5.3"])
def test(session: nox.Session, django_ver: str) -> None:
    """Run the test suite."""
    session.install("-e", ".", "--extra", "test", "-r", "pyproject.toml")
    session.install(f"django{django_ver}")
    session.run("pytest")
