"""Nox file."""

import nox


@nox.session(venv_backend="uv", python=["3.10", "3.11", "3.12", "3.13"])
@nox.parametrize("django_ver", ["~=4.2.0", "~=5.0.0", "~=5.1.0", "~=5.2.0"])
def test(session: nox.Session, django_ver: str) -> None:
    """Run the test suite."""
    session.install("-e", ".", "--extra", "test", "-r", "pyproject.toml")
    session.install(f"django{django_ver}")
    session.run("pytest")


TIME_ZONES = [
    "US/Samoa",
    "America/Adak",
    "Pacific/Marquesas",
    "America/Anchorage",
    "America/Ensenada",
    "America/Boise",
    "America/Bahia_Banderas",
    "America/Atikokan",
    "America/Anguilla",
    "America/St_Johns",
    "America/Araguaina",
    "America/Godthab",
    "Atlantic/Azores",
    "Africa/Abidjan",
    "Africa/Algiers",
    "Africa/Blantyre",
    "Africa/Addis_Ababa",
    "Asia/Tehran",
    "Asia/Baku",
    "Asia/Kabul",
    "Antarctica/Mawson",
    "Asia/Calcutta",
    "Asia/Kathmandu",
    "Asia/Bishkek",
    "Asia/Rangoon",
    "Antarctica/Davis",
    "Antarctica/Casey",
    "Australia/Eucla",
    "Asia/Chita",
    "Australia/Adelaide",
    "Antarctica/DumontDUrville",
    "Australia/LHI",
    "Asia/Magadan",
    "Antarctica/McMurdo",
    "NZ-CHAT",
    "Etc/GMT-13",
    "Etc/GMT-14",
]


@nox.session(venv_backend="uv", python=["3.13"])
@nox.parametrize("time_zone", TIME_ZONES)
def test_timezones(session: nox.Session, time_zone: str) -> None:
    """Run the test suite."""
    session.install("-e", ".", "--extra", "test", "-r", "pyproject.toml")
    session.run("pytest", env={"TEST_TIME_ZONE": time_zone})
