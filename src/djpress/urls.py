"""djpress URLs file."""

from django.urls import path, register_converter

from djpress.url_converters import SlugPathConverter
from djpress.views import entry, index

register_converter(SlugPathConverter, "djpress_path")


app_name = "djpress"

urlpatterns = [
    path("<djpress_path:path>", entry, name="entry"),
    path("", index, name="index"),
]
