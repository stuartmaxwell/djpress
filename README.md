# DJ Press

A blog application for Django sites, inspired by classic WordPress, [available on PyPI](https://pypi.org/project/djpress/).

> Warning - very alpha.

## Goals

Why build another blog engine? These are my goals...

- Simple to get started with sensible defaults: install plugin, configure `urls.py`, and migrate.
- Follows Django patterns: configuration in `settings.py`, content management in the Django admin.
- Configurable to suit a wide variety of use-cases: lots of configuration available, but not required.
- Customisable with themes: themes can be written using only template tags, no knowledge of models required.
- Customisable with plugins: simple plugins are easy to write, but complex plugins are possible.
- Powerful but lightweight: provide core functionality, allow plugins to fill gaps and enhance.

## Versioning

This package uses semantic versioning, but until we reach version 1.x.x, the following rules will apply:

- MAJOR version will remain on 0 until the base functionality is complete.
- MINOR version indicates that an incompatible or breaking change has been introduced.
- PATCH version indicates a bug fix or a backward compatible change.

If you choose to use this package prior to version 1.x being release, please pin your requirements to a specific minor version, e.g. `djpress~=0.16.0`

## Installation

- Install `djpress` by adding it to your requirements file, e.g. `djpress~=0.16.0` (see versioning note, above).
- Add it to your `INSTALLED_APPS` in Django:

```python
INSTALLED_APPS = [
    # ...
    "djpress.apps.DjpressConfig",
    # ...
]
```

- Add the URLs to your project's main `urls.py` file.

The following will set DJ Press to be available at the root of your site, e.g. `https://example.com/`

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("", include("djpress.urls")),
    # ...
]
```

If you want your blog to be in a subdirectory, use something like the following:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("blog/", include("djpress.urls")),
    # ...
]
```

- Run migrations: `python3 manage.py migrate`

> Note that this relies on the Django Admin for content management, so ensure that you have a user with at least `staff` status to manage content.

## Configuration

In your settings.py file, create a `DJPRESS_SETTINGS` dictionary. Here are some common settings:

```python
# DJPress settings
DJPRESS_SETTINGS = {
    "SITE_TITLE": "My Awesome Blog",
    "POST_PREFIX": "{{ year }}/{{ month }}",  # blog post URLs are prefixed with "year/month": /2024/10/blog-post-slug/
}
```

There are lots more settings available. Please check [the docs](https://stuartmaxwell.github.io/djpress) or look at the source code:
[src/djpress/app_settings.py](https://github.com/stuartmaxwell/djpress/blob/main/src/djpress/app_settings.py)

## Documentation

Documentation is a work-in-progress, but is available on GitHub Pages: <https://stuartmaxwell.github.io/djpress>

## Badges

[![codecov](https://codecov.io/github/stuartmaxwell/djpress/graph/badge.svg?token=IOS7BCD54B)](https://codecov.io/github/stuartmaxwell/djpress)
