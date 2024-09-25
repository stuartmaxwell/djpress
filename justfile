# Set the default recipe to list all available commands
default:
    @just --list

# Set the Python version
python_version := "3.12"

# Set the uv run command
uv := "uv run --python 3.12 --extra test"

#Set the uv command to run a tool
uv-tool := "uv tool run"

# Run the Django development server
run:
    @just sync
    {{uv}} example/manage.py runserver

# Make migrations
makemigrations:
    {{uv}} example/manage.py makemigrations

# Apply migrations
migrate:
    {{uv}} example/manage.py migrate

# Create a superuser
createsuperuser:
    {{uv}} example/manage.py createsuperuser

# Collect static files
collectstatic:
    {{uv}} example/manage.py collectstatic

# Run Django shell
shell:
    {{uv}} example/manage.py shell

# Check for any problems in your project
check:
    {{uv}} example/manage.py check

# Run pytest
test:
    {{uv}} pytest

# Run Ruff linking
lint:
    {{uv-tool}} ruff check

# Run Ruff formatting
format:
    {{uv-tool}} ruff format

# Run nox
nox:
    {{uv-tool}} nox --session test

# Run coverage
cov:
    {{uv}} coverage run -m pytest
    {{uv}} coverage report -m

# Run coverage
cov-html:
    {{uv}} coverage run -m pytest
    {{uv}} coverage html

# Sync the package
sync:
    uv sync --python {{python_version}} --all-extras

# Lock the package version
lock:
    uv lock

# Build the package
build:
    uv build

# Publish the package - this requires a $HOME/.pypirc file with your credentials
publish:
      rm -rf ./dist/*
      uv build
      {{uv-tool}} twine check dist/*
      {{uv-tool}} twine upload dist/*

# Upgrade pre-commit hooks
pc-up:
    {{uv-tool}} pre-commit autoupdate

# Run pre-commit hooks
pc-run:
    {{uv-tool}} pre-commit run --all-files
