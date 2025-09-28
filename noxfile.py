"""Nox file."""

import nox

# The dictionary of supported Django and Python versions.
SUPPORTED_VERSIONS = {
    "4.2": ["3.10", "3.11", "3.12"],
    "5.0": ["3.10", "3.11", "3.12"],
    "5.1": ["3.10", "3.11", "3.12", "3.13"],
    "5.2": ["3.10", "3.11", "3.12", "3.13", "3.14"],
}

# The list of all supported Python versions across all Django versions.
# This list is used by the @nox.session decorator to create virtual environments.
python_versions = sorted({py_ver for python_list in SUPPORTED_VERSIONS.values() for py_ver in python_list})


@nox.session(venv_backend="uv", python=python_versions)
@nox.parametrize("django_ver", sorted(SUPPORTED_VERSIONS.keys()))
def test(session: nox.Session, django_ver: str) -> None:
    """Run the test suite for supported Python/Django combinations."""
    # Check if the current Python version is supported for the given Django version.
    # If not, skip the session.
    if session.python not in SUPPORTED_VERSIONS[django_ver]:
        session.skip(
            f"Python {session.python} is not a supported version for Django {django_ver}",
        )

    # Install dependencies from your project and pyproject.toml.
    session.install("-e", ".", "--extra", "test", "-r", "pyproject.toml")

    # Install the correct Django version for the current session.
    session.install(f"django~={django_ver}.0")

    # Run your tests using pytest.
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
