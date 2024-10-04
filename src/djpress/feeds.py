"""RSS feed for blog posts."""

from typing import TYPE_CHECKING

from django.contrib.syndication.views import Feed

from djpress.conf import settings as djpress_settings
from djpress.models import Post

if TYPE_CHECKING:  # pragma: no cover
    from django.db import models


class PostFeed(Feed):
    """RSS feed for blog posts."""

    title = djpress_settings.BLOG_TITLE
    link = f"/{djpress_settings.RSS_PATH}/"
    description = djpress_settings.BLOG_DESCRIPTION

    def items(self: "PostFeed") -> "models.QuerySet":
        """Return the most recent posts."""
        return Post.post_objects.get_recent_published_posts()

    def item_title(self: "PostFeed", item: Post) -> str:
        """Return the title of the post."""
        return item.title

    def item_description(self: "PostFeed", item: Post) -> str:
        """Return the description of the post.

        This is taken from the truncated content of the post converted to HTML from
        Markdown.
        """
        description = item.truncated_content_markdown
        if item.is_truncated:
            description += f'<p><a href="{self.item_link(item)}">Read more</a></p>'
        return description

    def item_link(self: "PostFeed", item: Post) -> str:
        """Return the link to the post."""
        return item.url
