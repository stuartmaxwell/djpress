# Set the default recipe to list all available commands
default:
    @just --list

# Set the Python version
python_version := "3.12"

# Run the Django development server
run:
    @just sync
    uv run --python {{python_version}} example/manage.py runserver

# Make migrations
makemigrations:
    uv run --python {{python_version}} example/manage.py makemigrations

# Apply migrations
migrate:
    uv run --python {{python_version}} example/manage.py migrate

# Create a superuser
createsuperuser:
    uv run --python {{python_version}} example/manage.py createsuperuser

# Collect static files
collectstatic:
    uv run --python {{python_version}} example/manage.py collectstatic

# Run Django shell
shell:
    uv run --python {{python_version}} example/manage.py shell

# Check for any problems in your project
check:
    uv run --python {{python_version}} example/manage.py check

# Run pytest
test:
    uv run --python {{python_version}} pytest

# Run tox
tox:
    uv run --python {{python_version}} tox

# Run coverage
coverage:
    uv run --python {{python_version}} coverage run -m pytest
    uv run --python {{python_version}} coverage report --show-missing

# Sync the package
sync:
    uv sync --python {{python_version}} --all-extras

# Build the package
build:
    uv build

# Publish the package - this requires a $HOME/.pypirc file with your credentials
publish:
      rm -rf ./dist/*
      uv build
      uv tool run twine check dist/*
      uv tool run twine upload dist/*

# Upgrade pre-commit hooks
pc-upgrade:
    uv tool run pre-commit autoupdate

# Run pre-commit hooks
pc-run:
    uv tool run pre-commit run --all-files
