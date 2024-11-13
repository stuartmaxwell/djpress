"""Configuration file for the Sphinx documentation builder."""

from pathlib import Path

import tomllib

# Define the path to pyproject.toml
pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

# Read the version from pyproject.toml
with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)
    djpress_version = pyproject_data["project"]["version"]

# General information about the project.
project = "DJ Press"
copyright = "2024, Stuart Maxwell"  # noqa: A001
author = "Stuart Maxwell"
release = djpress_version

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
]
myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

language = "en"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "nord"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {}
html_title = project
html_static_path = []
