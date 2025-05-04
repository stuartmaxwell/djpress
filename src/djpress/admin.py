"""djpress admin configuration."""

from typing import Any

from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html

# Register the models here.
from djpress.models import Category, Media, PluginStorage, Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin configuration."""

    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "slug"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration."""

    list_display = ["title", "slug"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Post admin configuration."""

    list_display = ["post_type", "published_status", "title", "parent", "formatted_date", "author"]
    list_display_links = ["title", "formatted_date"]
    ordering = ["post_type", "-published_at"]
    list_filter = ["post_type", "published_at", "author"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "content", "slug"]
    readonly_fields = ["updated_at"]
    fieldsets = [
        (
            None,
            {
                "fields": ("title", "slug"),
            },
        ),
        (
            "Content",
            {
                "fields": ("content", "author"),
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "post_type",
                    "published_at",
                    "updated_at",
                ),
            },
        ),
        (
            "Post Settings",
            {
                "fields": ("categories", "tags"),
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
        """Format the published_at date and show future posts distinctly."""
        if obj.published_at > timezone.now():
            return format_html(
                '<span style="color: #666;">{} (Scheduled)</span>',
                obj.published_at.strftime("%Y-%m-%d %H:%M"),
            )
        return obj.published_at.strftime("%Y-%m-%d %H:%M")

    formatted_date.short_description = "Date"

    def get_form(self, request: HttpRequest, obj: Any | None = None, **kwargs: dict[str, Any]) -> forms.ModelForm:  # noqa: ANN401
        """Set the initial value for the author field to the current user."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["author"].initial = request.user
        return form

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        """Limit the queryset based on user role.

        - Superusers and Editors can see all posts.
        - Contributors and Authors can only see their own posts.

        Args:
            request: The request object.

        Returns:
            A queryset of posts.
        """
        qs = super().get_queryset(request)

        # Superusers can see all posts
        if request.user.is_superuser:
            return qs

        # Editors can see all posts
        if request.user.groups.filter(name="editor").exists():
            return qs

        # Authors and Contributors see only their own posts
        return qs.filter(author=request.user)

    def has_change_permission(self, request: HttpRequest, obj: Post = None) -> bool:
        """Limit the change permission based on user role.

        Args:
            request: The request object.
            obj: The post object.

        Returns:
            A boolean indicating if the user has change permission.
        """
        # First check if they have basic change permission
        if not super().has_change_permission(request, obj):
            return False

        # Superusers can change any post
        if request.user.is_superuser:
            return True

        # If no specific object, they have general change permission
        if obj is None:
            return True

        # Editors can change any post
        if request.user.groups.filter(name="editor").exists():
            return True

        # Others can only change their own posts
        return obj.author == request.user

    def get_readonly_fields(self, request: HttpRequest, _: Post = None) -> tuple[str, ...]:
        """Limit the readonly fields based on user role.

        Args:
            request: The request object.
            _: The post object.

        Returns:
            A tuple of readonly fields.
        """
        # Superusers can edit all fields
        if request.user.is_superuser:
            return self.readonly_fields

        # Restrict status field if user can't publish
        if not request.user.has_perm("djpress.can_publish_post"):
            return (*self.readonly_fields, "status")

        return self.readonly_fields


@admin.register(PluginStorage)
class PluginStorageAdmin(admin.ModelAdmin):
    """PluginStorage admin configuration."""

    list_display = ["plugin_name", "plugin_data"]
    list_display_links = ["plugin_name"]
    ordering = ["plugin_name"]
    search_fields = ["plugin_name"]
    list_filter = ["plugin_name"]


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Media admin configuration."""

    list_display = ["title", "media_type", "filename", "uploaded_by", "uploaded_at"]
    list_filter = ["media_type", "uploaded_at", "uploaded_by"]
    search_fields = ["title", "description", "alt_text", "file"]
    readonly_fields = ["uploaded_at", "updated_at", "filesize", "preview", "markdown_text"]
    fieldsets = [
        (
            None,
            {
                "fields": ("title", "file", "media_type", "uploaded_by"),
            },
        ),
        (
            "Details",
            {
                "fields": ("alt_text", "description"),
            },
        ),
        (
            "File Information",
            {
                "fields": ("uploaded_at", "updated_at", "filesize", "preview", "markdown_text"),
            },
        ),
    ]

    def get_form(self, request: HttpRequest, obj: Any | None = None, **kwargs: dict[str, Any]) -> forms.ModelForm:  # noqa: ANN401
        """Set the initial value for the uploaded_by field to the current user."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["uploaded_by"].initial = request.user
        return form

    def preview(self, obj: Media) -> str:
        """Display a preview of the file if it's an image."""
        if obj.media_type == "image":
            return format_html('<img src="{}" style="max-height: 200px; max-width: 300px;">', obj.file.url)
        return "-"

    preview.short_description = "Preview"

    def markdown_text(self, obj: Media) -> str:
        """Get the URL for the file in markdown format."""
        return obj.markdown_url

    markdown_text.short_description = "Markdown URL"
