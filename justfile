# Set the default recipe to list all available commands
@default:
    @just --list

# Run a command in the PDM-managed environment
pdm-run := "pdm run"

# Sphinx settings
SPHINXOPTS    := ""
SPHINXBUILD   := "sphinx-build"
SPHINXPROJ    := "djpress"
SOURCEDIR     := "docs"
BUILDDIR      := "docs/_build"

# Run the Django development server
@run:
    @just sync
    {{pdm-run}} example/manage.py runserver

# Make migrations
@makemigrations:
    {{pdm-run}} example/manage.py makemigrations

# Apply migrations
@migrate:
    {{pdm-run}} example/manage.py migrate

# Create a superuser
@createsuperuser:
    {{pdm-run}} example/manage.py createsuperuser

# Collect static files
@collectstatic:
    {{pdm-run}} example/manage.py collectstatic

# Run Django shell
@shell:
    {{pdm-run}} example/manage.py shell

# Check for any problems in your project
@check:
    {{pdm-run}} example/manage.py check

# Generic manage command
@manage *ARGS:
    {{pdm-run}} example/manage.py {{ ARGS }}

# Run pytest
@test *ARGS:
    {{pdm-run}} pytest {{ ARGS }}

@test-tz tz:
    TEST_TIME_ZONE={{tz}} {{pdm-run}} pytest

# Run Ruff linting
@lint:
    {{pdm-run}} ruff check .

# Run Ruff formatting
@format:
    {{pdm-run}} ruff format .

# Run nox
@nox:
    {{pdm-run}} nox --session test

# Run nox timezone test
@nox-tz:
    {{pdm-run}} nox --session test_timezones

# Run coverage
@cov:
    {{pdm-run}} pytest --cov

# Run coverage
@cov-html:
    {{pdm-run}} pytest --cov --cov-report=html --cov-context=test
    echo Coverage report: file://`pwd`/htmlcov/index.html

# Sync the package
@sync:
    pdm sync -G :all

# Sync the package
@sync-up:
    pdm update -G :all

# Lock the package version
@lock:
    pdm lock

# Build the package
@build:
    pdm build

# Upgrade pre-commit hooks
@pc-up:
    {{pdm-run}} pre-commit autoupdate

# Run pre-commit hooks
@pc-run:
    {{pdm-run}} pre-commit run --all-files

# Use Sphinx to build and view the documentation
@docs:
    {{pdm-run}} sphinx-autobuild -b html "{{SOURCEDIR}}" "{{BUILDDIR}}" {{SPHINXOPTS}}

# Use BumpVer to increase the patch version number. Use just bump -d to view a dry-run.
@bump *ARGS:
    {{pdm-run}} bumpver update --patch {{ ARGS }}
    pdm lock

# Use Bumpver to create a minor beta version. Use just bump-minor-beta -d to view a dry-run.
@bump-beta *ARGS:
    {{pdm-run}} bumpver update --patch --tag beta {{ ARGS }}
    pdm lock

# Use BumpVer to increase the minor version number. Use just bump-minor -d to view a dry-run.
@bump-minor *ARGS:
    {{pdm-run}} bumpver update --minor {{ ARGS }}
    pdm lock

# Use Bumpver to create a minor beta version. Use just bump-minor-beta -d to view a dry-run.
@bump-minor-beta *ARGS:
    {{pdm-run}} bumpver update --minor --tag beta {{ ARGS }}
    pdm lock

# Use Bumpver to create a minor beta version increment. Use just bump-minor-beta-inc -d to view a dry-run.
@bump-minor-beta-inc *ARGS:
    {{pdm-run}} bumpver update --tag-num {{ ARGS }}
    pdm lock



# Create a new GitHub release - this requires Python 3.11 or newer, and the GitHub CLI must be installed and configured
version := `python -c "from tomllib import load; print(load(open('pyproject.toml', 'rb'))['project']['version'])"`

[confirm("Are you sure you want to create a new release?\nThis will create a new GitHub release and will build and deploy a new version to PyPi.\nYou should have already updated the version number using one of the bump recipes.\nTo check the version number, run just version.\n\nCreate release?")]
@release:
    echo "Creating a new release for v{{version}}"
    git pull
    gh release create "v{{version}}" --generate-notes

@version:
    echo {{version}}
