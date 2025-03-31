# Installation

> Note: If you choose to use this package prior to version 1.x being release, please pin your requirements to a specific minor version, e.g. `djpress~=0.11.0`

- Install `djpress` by adding it to your requirements file, e.g. `djpress~=0.15.0` (see versioning note, above).
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

If you want your site to be in a subdirectory, e.g. `https://example.com/blog/`, use something like the following:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("blog/", include("djpress.urls")),
    # ...
]
```

- Run migrations: `python3 manage.py migrate`

> Note that DJ Press relies on the Django Admin for content management, so ensure that you have a user with at least `staff` status to manage content.

- Access your site's admin panel to manage content, e.g. `https://example.com/admin/djpress/`
