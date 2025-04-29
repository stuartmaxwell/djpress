"""URL configuration for config project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from djpress.sitemaps import (
    CategorySitemap,
    DateBasedSitemap,
    PageSitemap,
    PostSitemap,
)

# Define your sitemaps dictionary
sitemaps = {
    "posts": PostSitemap,
    "pages": PageSitemap,
    "categories": CategorySitemap,
    "archives": DateBasedSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("", include("djpress.urls")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
