# Sitemap

DJ Press provides sitemap support for your site's content through Django's built-in sitemap framework. This allows search engines to more intelligently crawl your site by providing information about:

- Blog posts
- Static pages
- Category archives
- Date-based archives

## Setup

> Note: please refer to the current, official Django documentation for up-to-date instructions on how to configure sitemaps:
> <https://docs.djangoproject.com/en/stable/ref/contrib/sitemaps/>.
> The following information should be seen as a guide only and may need modifying for your specific requirements.

1. First, ensure Django's sitemap framework is installed. Add `django.contrib.sitemaps` to your `INSTALLED_APPS`:

    ```python
    INSTALLED_APPS = [
        ...
        'django.contrib.sitemaps',
        ...
    ]
    ```

2. Import the DJ Press sitemap classes in your project's `urls.py`:

    ```python
    from django.contrib.sitemaps.views import sitemap
    from djpress.sitemaps import (
        CategorySitemap,
        DateBasedSitemap,
        PageSitemap,
        PostSitemap,
    )

    # Define your sitemaps dictionary
    sitemaps = {
        'posts': PostSitemap,
        'pages': PageSitemap,
        'categories': CategorySitemap,
        'archives': DateBasedSitemap,
    }

    # Add the sitemap URL patterns
    urlpatterns = [
        ...
        path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
        ...
    ]
    ```

That's it! Your site will now have a sitemap at `/sitemap.xml` that includes all your site's content.

## What's Included

The sitemap will include URLs for:

- **Posts**: All published blog posts
- **Pages**: All published static pages
- **Categories**: All categories that contain published posts
- **Archives**: Date-based archives (year, month, day) that contain posts

Each URL in the sitemap includes:

- The location (URL) of the content
- Last modified date
- Change frequency
- Protocol (https by default)

## Customisation

### Disabling Sections

You can choose which sections to include in your sitemap by only adding the desired classes to your sitemaps dictionary. For example, to only include posts and pages:

```python
sitemaps = {
    'posts': PostSitemap,
    'pages': PageSitemap,
}
```

### Date-based Archives

The date-based archives sitemap respects your DJ Press archive settings. If you have disabled archives in your DJ Press settings (`ARCHIVE_ENABLED = False`), the archive URLs will not be included in the sitemap.

### Protocol

By default, all URLs in the sitemap use the HTTPS protocol. To change this, subclass any of the sitemap classes:

```python
from djpress.sitemaps import PostSitemap

class CustomPostSitemap(PostSitemap):
    protocol = 'http'

sitemaps = {
    'posts': CustomPostSitemap,
    ...
}
```

### Change Frequencies

The default change frequencies are:

- Posts: monthly
- Pages: monthly
- Categories: daily
- Archives: daily

To customise these, subclass the relevant sitemap class:

```python
from djpress.sitemaps import PostSitemap

class CustomPostSitemap(PostSitemap):
    changefreq = 'weekly'

sitemaps = {
    'posts': CustomPostSitemap,
    ...
}
```

## Performance

The sitemap classes are designed to work efficiently with Django's ORM and respect DJ Press's caching settings. However, for sites with many posts, you may want to consider implementing caching for the sitemap views.

Caching can be complex to implement depending on your site's set up, but as an example, to cache the sitemap, use Django's cache framework:

```python
from django.views.decorators.cache import cache_page

urlpatterns = [
    ...
    path('sitemap.xml', cache_page(86400)(sitemap),  # Cache for 24 hours
         {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
    ...
]
```

## Generating the Sitemap

Once configured, your sitemap will be available at `/sitemap.xml`. You can verify it's working by visiting this URL in your browser or using a tool like curl:

```bash
curl http://your-site.com/sitemap.xml
```

The sitemap follows the [sitemaps.org protocol](https://www.sitemaps.org/protocol.html) and can be submitted to search engines through their respective webmaster tools.
