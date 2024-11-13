"""djpress module."""

from pathlib import Path

import tomllib

# Define the path to pyproject.toml
pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

# Read the version from pyproject.toml
with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)
    __version__ = pyproject_data["project"]["version"]
