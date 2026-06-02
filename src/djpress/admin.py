"""djpress admin configuration."""

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.html import format_html

# Register the models here.
from djpress.models import Category, Media, PluginStorage, Post, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin configuration.

    Note that we do not need to configure the has_delete_permission nor has_change_permission methods since we are not
    doing any specific checks on whether the user can edit or delete their own objects. Same with the get_queryset
    method - all users can see all objects.
    """

    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "slug"]


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
                "fields": ("title", "file", "media_type"),
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
                "fields": ("uploaded_by", "uploaded_at", "updated_at", "filesize", "preview", "markdown_text"),
            },
        ),
    ]

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

    def get_form(self, request, obj=None, change=False, **kwargs):  # noqa: ANN001, ANN003, ANN201, FBT002
        """Set the initial value for the uploaded_by field to the current user.

        This is over-riding a Django method and should not have type hints.
        """
        form = super().get_form(request, obj, change, **kwargs)
        base_fields = getattr(form, "base_fields", None)

        if base_fields and "uploaded_by" in base_fields:  # pragma: no cover
            base_fields["uploaded_by"].initial = request.user

        return form

    def save_model(self, request: HttpRequest, obj: Media, form, change: bool) -> None:  # noqa: ANN001, FBT001
        """Override the save_model method to set the uploaded_by field correctly.

        This is because contributors have this field set to read-only and are unable to set it correctly.
        """
        if not change and not obj.uploaded_by:
            obj.uploaded_by = request.user

        super().save_model(request, obj, form, change)  # pragma: no cover

    def get_readonly_fields(self, request: HttpRequest, _: Media | None = None):  # noqa: ANN201
        """Limit the readonly fields based on user role.

        Args:
            request: The request object.
            _: The Media object.

        Returns:
            A tuple of readonly fields.
        """
        # Superusers can edit all fields except the `readonly_fields` above
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return self.readonly_fields

        # Create a new list of readonly fields and add the uploaded_by field
        return [*self.readonly_fields, "uploaded_by"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Media]:
        """Limit the queryset based on user role.

        - Superusers and Editors can see all media.
        - Contributors and Authors can only see their own media.

        Args:
            request: The request object.

        Returns:
            A queryset of media.
        """
        qs = super().get_queryset(request)

        # Superusers, Admins, Editors can see all media
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return qs

        # Authors and Contributors see only their own media
        return qs.filter(uploaded_by=request.user)

    def has_change_permission(self, request: HttpRequest, obj: Media | None = None) -> bool:
        """Limit the change permission based on user role.

        Database-level `change` permissions are assigned in `permissions.py`.
        Superusers, Admins, Editors, can change any media.
        Contributors cannot change any media.
        Authors can change their own media

        Args:
            request: The request object.
            obj: The post object.

        Returns:
            A boolean indicating if the user has change permission.
        """
        # First check if they have basic change permission (this catches contributors too)
        if not super().has_change_permission(request, obj):
            return False

        # Superusers, Admins, Editors, can change any media
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return True

        # If no specific object, remove the change permission
        if obj is None:
            return False

        # Others (i.e. authors) can only change their own media
        return obj.uploaded_by == request.user

    def has_delete_permission(self, request: HttpRequest, obj: Media | None = None) -> bool:
        """Limit the delete permission based on user role.

        Database-level `delete` permissions are assigned in `permissions.py`.
        Superusers, Admins, Editors, can delete any media.
        No other groups can delete media.

        Args:
            request: The request object.
            obj: The media object.

        Returns:
            A boolean indicating if the user has delete permission.
        """
        # First check if they have basic delete permission
        return super().has_delete_permission(request, obj)


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
        """Format the published_at date and show future posts distinctly.

        Make sure the display date is in the local timezone.
        """
        display_date_format = "%Y-%m-%d %H:%M"
        display_date = timezone.localtime(obj.published_at).strftime(display_date_format)

        if obj.published_at > timezone.now():
            return format_html(
                '<span style="color: #666;">{} (Scheduled)</span>',
                display_date,
            )
        return display_date

    formatted_date.short_description = "Date"

    def get_form(self, request, obj=None, change=False, **kwargs):  # noqa: ANN001, ANN003, ANN201, FBT002
        """Set the initial value for the author field to the current user.

        This is over-riding a Django method and should not have type hints.
        """
        form = super().get_form(request, obj, change, **kwargs)
        base_fields = getattr(form, "base_fields", None)

        if base_fields and "author" in base_fields:  # pragma: no cover
            base_fields["author"].initial = request.user

        return form

    def save_model(self, request: HttpRequest, obj: Post, form, change: bool) -> None:  # noqa: ANN001, FBT001
        """Override the save_model method to set the author field correctly.

        This is because contributors and authors have this field set to read-only and are unable to set it correctly.
        """
        if not change and (not hasattr(obj, "author") or obj.author is None):
            obj.author = request.user

        super().save_model(request, obj, form, change)  # pragma: no cover

    def get_readonly_fields(self, request: HttpRequest, _: Post | None = None):  # noqa: ANN201
        """Limit the readonly fields based on user role.

        Args:
            request: The request object.
            _: The post object.

        Returns:
            A tuple of readonly fields.
        """
        # Superusers, Admins, Editors, can edit all fields except the `readonly_fields` above
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return self.readonly_fields

        # Create a new list of readonly fields and add the author field
        readonly = [*self.readonly_fields, "author"]

        # Restrict status field if user can't publish
        if not request.user.has_perm("djpress.can_publish_post"):
            readonly.append("status")

        return readonly

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

        # Superusers, Admins, Editors, can see all posts
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return qs

        # Others can only see their own posts
        return qs.filter(author=request.user)

    def has_change_permission(self, request: HttpRequest, obj: Post | None = None) -> bool:
        """Limit the change permission based on user role.

        Database-level `delete` permissions are assigned in `permissions.py`.
        Superusers, Admins, Editors, can change any post.
        Other users can only change their own posts.

        Args:
            request: The request object.
            obj: The post object.

        Returns:
            A boolean indicating if the user has change permission.
        """
        # First check if they have basic change permission
        if not super().has_change_permission(request, obj):
            return False

        # Superusers, Admins, Editors, can change any post
        if (
            request.user.is_superuser
            or request.user.groups.filter(name="djpress_admin").exists()
            or request.user.groups.filter(name="djpress_editor").exists()
        ):
            return True

        # If no specific object, remove the change permission
        if obj is None:
            return False

        # Others can only change their own posts
        return obj.author == request.user

    def has_delete_permission(self, request: HttpRequest, obj: Post | None = None) -> bool:
        """Limit the delete permission based on user role.

        Database-level `delete` permissions are assigned in `permissions.py`.
        Superusers, Admins, Editors, can delete any post.
        Other users cannot delete any posts.

        Args:
            request: The request object.
            obj: The post object.

        Returns:
            A boolean indicating if the user has delete permission.
        """
        # First check if they have basic delete permission
        return super().has_delete_permission(request, obj)


@admin.register(PluginStorage)
class PluginStorageAdmin(admin.ModelAdmin):
    """PluginStorage admin configuration."""

    list_display = ["plugin_name", "plugin_data"]
    list_display_links = ["plugin_name"]
    ordering = ["plugin_name"]
    search_fields = ["plugin_name"]
    list_filter = ["plugin_name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin configuration.

    Note that we do not need to configure the has_delete_permission nor has_change_permission methods since we are not
    doing any specific checks on whether the user can edit or delete their own objects. Same with the get_queryset
    method - all users can see all objects.
    """

    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "slug"]
