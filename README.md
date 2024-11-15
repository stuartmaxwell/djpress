# DJ Press

A blog application for Django sites, inspired by classic WordPress.

> Warning - very alpha.

## Versioning

This package uses semantic versioning, but until we reach version 1.x.x, the following rules will apply:

- MAJOR version will remain on 0 until the base functionality is complete.
- MINOR version indicates that an incompatible or breaking change has been introduced.
- PATCH version indicates a bug fix or a backward compatible change.

If you choose to use this package prior to version 1.x being release, please pin your requirements to a specific minor version, e.g. `djpress~=0.11.0`

## Installation

- Install `djpress` by adding it to your requirements file, e.g. `djpress~=0.11.0` (see versioning note, above).
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
    "BLOG_TITLE": "My Awesome Blog",
    "POST_PREFIX": "{{ year }}/{{ month }}",
}
```

There are lots more settings available. Please checks the docs or look at the source code:
[src/djpress/app_settings.py](https://github.com/stuartmaxwell/djpress/blob/main/src/djpress/app_settings.py)

## Documentation

Documentation is a work-in-progress but is available on GitHub Pages: <https://stuartmaxwell.github.io/djpress>

## Badges

[![codecov](https://codecov.io/github/stuartmaxwell/djpress/graph/badge.svg?token=IOS7BCD54B)](https://codecov.io/github/stuartmaxwell/djpress)
