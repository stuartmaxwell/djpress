"""djpress admin configuration."""

from typing import ClassVar

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

# Register the models here.
from djpress.models import Category, PluginStorage, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""

    list_display: ClassVar["str"] = ["title", "slug"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin configuration."""

    list_display: ClassVar[list[str]] = ["post_type", "published_status", "title", "parent", "formatted_date", "author"]
    list_display_links: ClassVar[list[str]] = ["title"]
    ordering: ClassVar[list[str]] = ["post_type", "-date"]  # Displays pages first, then sorted by date.
    list_filter: ClassVar[list[str]] = ["post_type", "date", "author"]
    prepopulated_fields: ClassVar[dict[str, str]] = {"slug": ("title",)}
    search_fields: ClassVar[list[str]] = ["title", "content", "slug"]
    readonly_fields: ClassVar[list[str]] = ["modified_date"]
    fieldsets: ClassVar = [
        (
            None,
            {
                "fields": ("title", "slug", "author"),
            },
        ),
        (
            "Content",
            {
                "fields": ("content",),
                "classes": ("wide",),
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "post_type",
                    "date",
                    "modified_date",
                ),
            },
        ),
        (
            "Post Settings",
            {
                "fields": ("categories",),
                "description": "These settings only apply to posts",
            },
        ),
        (
            "Page Settings",
            {
                "fields": ("parent", "menu_order"),
                "description": "These settings only apply to pages",
            },
        ),
    ]

    @admin.display(
        boolean=True,
        description="Published",
    )
    def published_status(self, obj: Post) -> bool:
        """Display published status using Django's built-in boolean icon."""
        return obj.is_published

    def formatted_date(self, obj: Post) -> str:
        """Format the date and show future posts distinctly."""
        if obj.date > timezone.now():
            return format_html(
                '<span style="color: #666;">{} (Scheduled)</span>',
                obj.date.strftime("%Y-%m-%d %H:%M"),
            )
        return obj.date.strftime("%Y-%m-%d %H:%M")

    formatted_date.short_description = "Date"


@admin.register(PluginStorage)
class PluginStorageAdmin(admin.ModelAdmin):
    """PluginStorage admin configuration."""

    list_display: ClassVar["str"] = ["plugin_name", "plugin_data"]
    list_display_links: ClassVar["str"] = ["plugin_name"]
    ordering: ClassVar["str"] = ["plugin_name"]
    search_fields: ClassVar["str"] = ["plugin_name"]
    list_filter: ClassVar["str"] = ["plugin_name"]
