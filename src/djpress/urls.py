"""djpress URLs file."""

from django.urls import path, register_converter

from djpress.url_converters import SlugPathConverter
from djpress.views import entry, index, post_admin_button_action

register_converter(SlugPathConverter, "djpress_path")


app_name = "djpress"

urlpatterns = [
    path(
        "post-admin-button-action/<str:plugin_name>/<int:post_id>/",
        post_admin_button_action,
        name="post_admin_button_action",
    ),
    path("<djpress_path:path>", entry, name="entry"),
    path("", index, name="index"),
]
