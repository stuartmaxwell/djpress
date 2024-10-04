"""djpress URLs file."""

from django.conf import settings
from django.urls import path, register_converter
from django.urls.converters import get_converters

from djpress.url_converters import SlugPathConverter
from djpress.views import entry, index

if "djpress_path" not in get_converters():
    register_converter(SlugPathConverter, "djpress_path")

app_name = "djpress"

urlpatterns = []

if settings.APPEND_SLASH:
    urlpatterns.append(path("<djpress_path:path>/", entry, name="entry"))
else:
    urlpatterns.append(path("<djpress_path:path>", entry, name="entry"))

urlpatterns.append(path("", index, name="index"))
