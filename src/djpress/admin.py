"""djpress admin configuration."""

from typing import ClassVar

from django.contrib import admin

# Register the models here.
from djpress.models import Category, PluginStorage, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""

    list_display: ClassVar["str"] = ["title", "slug"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin configuration."""

    list_display: ClassVar["str"] = ["post_type", "title", "slug", "date", "author"]
    list_display_links: ClassVar["str"] = ["title", "slug"]
    ordering: ClassVar["str"] = ["post_type", "-date"]  # Displays pages first, then sorted by date.
    list_filter: ClassVar["str"] = ["post_type", "date", "author"]


@admin.register(PluginStorage)
class PluginStorageAdmin(admin.ModelAdmin):
    """PluginStorage admin configuration."""

    list_display: ClassVar["str"] = ["plugin_name", "plugin_data"]
    list_display_links: ClassVar["str"] = ["plugin_name"]
    ordering: ClassVar["str"] = ["plugin_name"]
    search_fields: ClassVar["str"] = ["plugin_name"]
    list_filter: ClassVar["str"] = ["plugin_name"]
