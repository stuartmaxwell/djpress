"""djpress admin configuration."""

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

# Register the models here.
from djpress.models import Category, PluginStorage, Post, Tag
from djpress.plugins import Hooks, registry


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
    list_display_links = ["title"]
    ordering = ["post_type", "-date"]  # Displays pages first, then sorted by date.
    list_filter = ["post_type", "date", "author"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title", "content", "slug"]
    readonly_fields = ["modified_date", "plugin_buttons"]
    fieldsets = [
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
        (
            "Plugin Actions",
            {
                "fields": ("plugin_buttons",),
                "description": "Plugins can add actions on the saved post object here.",
            },
        ),
    ]

    class Media:
        """Media class for the admin form."""

        js = ("admin/js/vendor/jquery/jquery.min.js",)

    def plugin_buttons(self, obj: Post) -> str:
        """Render buttons for plugin actions.

        Args:
            obj (Post): The post object.

        Returns:
            str: HTML for plugin action buttons.
        """
        if obj.pk is None:  # Skip for new posts
            return "Save the post first to see plugin actions."

        # Make sure plugins are loaded
        if not registry._loaded:  # noqa: SLF001
            registry.load_plugins()

        admin_post_buttons = registry.hooks.get(Hooks.ADMIN_POST_BUTTONS, [])

        # If no buttons were returned, show a message
        if not admin_post_buttons or not isinstance(admin_post_buttons, list):
            return "No plugin actions available."

        buttons_html = []
        for button in admin_post_buttons:
            if not isinstance(button, dict) or "name" not in button or "plugin_name" not in button:
                continue

            # Build the action URL
            url = reverse(
                "djpress:post_admin_button_action",
                kwargs={
                    "plugin_name": button["plugin_name"],
                    "post_id": obj.pk,
                },
            )

            # Create the button HTML
            btn_label = button.get("label", button["name"])
            btn_style = button.get("style", "primary")
            css_class = f"button button-{btn_style} plugin-action-btn"
            action_url = f"{url}?action={button['name']}"
            btn_html = (
                f'<a href="{action_url}" class="{css_class}" '
                f'data-plugin="{button["plugin_name"]}" data-action="{button["name"]}">{btn_label}</a>'
            )
            buttons_html.append(btn_html)

        # Add some simple JavaScript to handle button clicks
        js = """
        <script>
        (function($) {
            $(document).ready(function() {
                $('.plugin-action-btn').click(function(e) {
                    e.preventDefault();
                    var url = $(this).attr('href');

                    // Show loading state
                    var originalText = $(this).text();
                    $(this).text('Loading...');
                    $(this).addClass('disabled');

                    // Make the AJAX request
                    $.ajax({
                        url: url,
                        type: 'GET',
                        dataType: 'json',
                        success: function(data) {
                            if (data.success && data.result) {
                                alert(data.result);
                            } else {
                                alert('Action completed successfully!');
                            }
                        },
                        error: function(xhr) {
                            var msg = 'An error occurred';
                            if (xhr.responseJSON && xhr.responseJSON.message) {
                                msg = xhr.responseJSON.message;
                            }
                            alert(msg);
                        },
                        complete: function() {
                            // Reset button state
                            $('.plugin-action-btn').removeClass('disabled');
                            $('.plugin-action-btn').text(originalText);
                        }
                    });
                });
            });
        })(django.jQuery);
        </script>
        """

        if buttons_html:
            return mark_safe('<div class="plugin-actions">' + " ".join(buttons_html) + js + "</div>")
        return "No plugin actions available."

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
