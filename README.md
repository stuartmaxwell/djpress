# DJ Press

A blog application for Django sites, inspired by classic WordPress.

> Warning - very alpha.

## Versioning

This package uses semantic versioning, but until we reach version 1.x.x, the following rules will apply:

- MAJOR version will remain on 0 until the base functionality is complete.
- MINOR version indicates that an incompatible or breaking change has been introduced.
- PATCH version indicates a bug fix or a backward compatible change.

If you choose to use this package prior to version 1.x being release, please pin your requirements to a specific minor version, e.g. `djpress==0.3.*`

## Installation

- Install `djpress` by adding it to your requirements file, e.g. `djpress==0.3.*` (see versioning note, above).
- Add it to your `INSTALLED_APPS` in Django:

```python
INSTALLED_APPS = [
    # ...
    "djpress.apps.DjpressConfig",
    # ...
]
```

- Add the URLs to your project's main `urls.py` file.

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("", include("djpress.urls")),
    # ...
]
```

- Run migrations: `python3 manage.py migrate`

> Note that this relies on the Django Admin for content management, so ensure that you have a user with at least `staff` status to manage content.
