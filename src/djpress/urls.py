"""djpress URLs file."""

from django.urls import path, register_converter

from djpress.url_converters import SlugPathConverter
from djpress.views import entry, index, plugin_action

register_converter(SlugPathConverter, "djpress_path")


app_name = "djpress"

urlpatterns = [
    path("<djpress_path:path>", entry, name="entry"),
    path("", index, name="index"),
    path("admin/plugin-action/<str:plugin_name>/<int:post_id>/", plugin_action, name="plugin_action"),
]
