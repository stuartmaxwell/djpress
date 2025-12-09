# Installation

This guide will walk you through installing DJ Press in your Django project.

## Requirements

DJ Press will always be compatible with any supported version of Django and Python. Right now this is:

- Django 4.2 or newer
- Python 3.10 and above

## Quick Start

> **Important:** DJ Press is pre-1.0 software. Until version 1.x is released, please pin your requirements to a
> specific minor version to avoid breaking changes, e.g. `djpress~=0.22.0`

1. Install the package:

```bash
# Using pip
pip install "djpress~=0.22.0"

# Using poetry
poetry add "djpress~=0.22.0"

# using uv
uv add "djpress~=0.22.0"
```

1. Add DJ Press to your `INSTALLED_APPS` in Django settings:

```python
INSTALLED_APPS = [
    # Django's built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # If you're using sitemaps (recommended)
    "django.contrib.sitemaps",

    # DJ Press
    "djpress.apps.DjpressConfig",
]
```

1. Add the URLs to your project's main `urls.py` file:

```python
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    # Other URL patterns

    # For blog at site root (https://example.com/)
    path("", include("djpress.urls")),

    # OR for blog in subdirectory (https://example.com/blog/)
    # path("blog/", include("djpress.urls")),
]
```

1. Run migrations:

```bash
python manage.py migrate
```

1. Create a superuser if you don't already have one:

```bash
python manage.py createsuperuser
```

1. Start the development server and access the admin:

```bash
python manage.py runserver
```

Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in to start creating content.

## Next Steps

1. Configure your blog settings by adding a `DJPRESS_SETTINGS` dictionary to your `settings.py`. See the
   [Configuration](configuration.md) documentation for available options.

2. Consider adding sitemap support to improve SEO. See the [Sitemap](sitemap.md) documentation for instructions.

3. Choose or create a theme for your blog. See the [Themes](themes.md) documentation.

## Group Permissions

DJ Press relies on the Django Admin for content management. Users need proper permissions to manage content:

- All users need **staff status** to access the admin interface
- Use the built-in Django groups and permissions system to control what users can do
- See the [Groups and Permissions](groups.md) documentation for details on DJ Press's predefined roles

## Troubleshooting

### Common Issues

#### Posts Not Appearing on the Frontend

1. Check that posts are marked as "Published" in the admin (not "Draft")
2. Verify the published date is not in the future
3. Check that the URL patterns aren't conflicting (see [URL Structure](url_structure.md))
4. Clear browser cache or use private browsing

#### Static Files Not Loading

1. Ensure `django.contrib.staticfiles` is in your `INSTALLED_APPS`
2. Run `python manage.py collectstatic`
3. Check that your web server is configured to serve static files

#### Template Errors

1. Make sure you've loaded the required template tags with `{% load djpress_tags %}`
2. Verify the template tag names and parameters match the documentation
3. Check that the selected theme exists and is properly installed

### Debug Mode

When troubleshooting, you can enable Django's debug mode to see detailed error information:

```python
# settings.py
DEBUG = True  # Only in development!
```

### Support

If you encounter issues not covered here, check:

1. The [GitHub Issues](https://github.com/stuartmaxwell/djpress/issues) for similar problems
2. Open a new issue with detailed information about your problem

## Upgrading

When upgrading DJ Press, always:

1. Review the release notes for breaking changes
2. Back up your database
3. Run migrations after upgrading: `python manage.py migrate`

*Remember:* there will be breaking changes with minor updates, until we reach version 1.x.
