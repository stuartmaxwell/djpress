"""Nox file."""

import nox

# The dictionary of supported Django and Python versions.
SUPPORTED_VERSIONS = {
    "5.2": ["3.10", "3.11", "3.12", "3.13", "3.14"],
    "6.0": ["3.12", "3.13", "3.14"],
    "6.1": ["3.12", "3.13", "3.14"],
}

# The list of all supported Python versions across all Django versions.
# This list is used by the @nox.session decorator to create virtual environments.
python_versions = sorted({py_ver for python_list in SUPPORTED_VERSIONS.values() for py_ver in python_list})

TEST_DEPENDENCIES = (
    "django-debug-toolbar~=7.1",
    "pytest~=9.1",
    "pytest-cov~=7.1",
    "pytest-django~=4.14",
    "rich~=15.0",
)


def install_test_dependencies(session: nox.Session) -> None:
    """Install DJ Press, its example plugin, and the test dependencies."""
    session.install("-e", ".", "-e", "./djpress-example-plugin", *TEST_DEPENDENCIES)


@nox.session(python=python_versions)
@nox.parametrize("django_ver", sorted(SUPPORTED_VERSIONS.keys()))
def test(session: nox.Session, django_ver: str) -> None:
    """Run the test suite for supported Python/Django combinations."""
    # Check if the current Python version is supported for the given Django version.
    # If not, skip the session.
    if session.python not in SUPPORTED_VERSIONS[django_ver]:
        session.skip(
            f"Python {session.python} is not a supported version for Django {django_ver}",
        )

    install_test_dependencies(session)

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
    "Pacific/Auckland",
    "NZ-CHAT",
    "Etc/GMT-13",
    "Etc/GMT-14",
]


@nox.session(python=["3.14"])
@nox.parametrize("time_zone", TIME_ZONES)
def test_timezones(session: nox.Session, time_zone: str) -> None:
    """Run the test suite."""
    install_test_dependencies(session)
    session.run("pytest", env={"TEST_TIME_ZONE": time_zone})
