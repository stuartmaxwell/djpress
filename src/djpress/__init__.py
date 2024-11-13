"""djpress module."""

from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Alias tomli as tomllib for compatibility with Python versions < 3.11


def load_version() -> str:
    """Load the version from pyproject.toml."""
    # Define the path to pyproject.toml
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    # Read the version from pyproject.toml
    with pyproject_path.open("rb") as f:
        pyproject_data = tomllib.load(f)
        return pyproject_data["project"]["version"]


__version__ = load_version()
