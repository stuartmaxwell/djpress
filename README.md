# DJ Press

A blog application for Django sites, inspired by classic WordPress.

> Warning - very alpha.

## Instructions

- Install `djpress` by adding it to your requirements file.
- Add it to your `INSTALLED_APPS` in Django:

```python
INSTALLED_APPS = [
    ...
    "djpress.apps.DjpressConfig",
    ...
]
```

- Add the URLs to your project's main `urls.py` file.

```python
urlpatterns = [
    ...
    path("", include("djpress.urls")),
    ...
]
```

- Run migrations: `python3 manage.py migrate`
