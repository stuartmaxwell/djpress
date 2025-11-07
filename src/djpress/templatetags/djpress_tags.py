"""Template tags for djpress."""

from django import template
from django.contrib.auth.models import User
from django.core.paginator import Page
from django.db import models
from django.template import Context
from django.urls import reverse
from django.utils.safestring import mark_safe

from djpress import url_utils
from djpress.conf import settings as djpress_settings
from djpress.exceptions import PageNotFoundError
from djpress.models import Category, Post, Tag
from djpress.plugins import registry
from djpress.plugins.hook_registry import DJ_FOOTER, DJ_HEADER
from djpress.templatetags import helpers
from djpress.utils import get_author_display_name

register = template.Library()


# Tags starting with `get_` are used to get data from the database.


@register.simple_tag(takes_context=True)
def get_recent_posts(context: Context) -> models.QuerySet[Post]:
    """Return the recent posts.

    This returns the most recent published posts, and tries to be efficient by checking if there's a `posts` object we
    can use.
    """
    posts: Page | None = context.get("posts")

    if isinstance(posts, Page) and posts.number == 1:
        return posts.object_list

    return Post.post_objects.get_recent_published_posts()


@register.simple_tag
def get_posts() -> models.QuerySet[Post]:
    """Return all published posts as a queryset.

    Returns:
        models.QuerySet[Post]: All posts.
    """
    return Post.post_objects.get_published_posts()


@register.simple_tag
def get_pages() -> models.QuerySet[Post]:
    """Return all published pages as a queryset.

    Returns:
        models.QuerySet[Post]: All pages.
    """
    return Post.page_objects.get_published_pages()


@register.simple_tag
def get_categories() -> models.QuerySet[Category] | None:
    """Return all categories as a queryset.

    Returns:
        models.QuerySet[Category]: All categories.
    """
    return Category.objects.get_categories().order_by("menu_order", "title")


@register.simple_tag
def get_tags() -> models.QuerySet[Tag]:
    """Return all tags as a queryset.

    Returns:
        models.QuerySet[Tag]: All tags.
    """
    return Tag.objects.get_tags().order_by("title")


@register.simple_tag
def site_title() -> str:
    """Return the site title.

    Returns:
        str: The site title.
    """
    site_title = djpress_settings.SITE_TITLE
    if not isinstance(site_title, str):  # pragma: no cover
        msg = f"Expected SITE_TITLE to be a string, got {type(site_title).__name__}"
        raise TypeError(msg)
    return site_title


@register.simple_tag
def site_title_link(link_class: str = "") -> str:
    """Return the site title.

    Args:
        link_class: The CSS class(es) for the link.

    Returns:
        str: The site title.
    """
    link_class_html = f' class="{link_class}"' if link_class else ""

    output = f'<a href="{reverse("djpress:index")}"{link_class_html}>{djpress_settings.SITE_TITLE}</a>'

    return mark_safe(output)


@register.simple_tag
def blog_categories(
    outer_tag: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the categories of the blog.

    Args:
        outer_tag: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The categories of the blog.
    """
    categories = Category.objects.all()
    if not categories:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(
        helpers.categories_html(
            categories=categories,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
        ),
    )


@register.simple_tag
def blog_tags(
    outer_tag: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the tags of the blog.

    Args:
        outer_tag: The outer HTML tag for the tags.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The tags of the blog.
    """
    tags = Tag.objects.get_tags().order_by("title")
    if not tags:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(helpers.tags_html(tags=tags, outer_tag=outer_tag, outer_class=outer_class, link_class=link_class))


@register.simple_tag
def tags_with_counts(
    outer_tag: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the tags of the blog with post counts.

    Each tag shows the tag name followed by the number of posts in parentheses.
    Only tags that have published posts are included.

    Args:
        outer_tag: The outer HTML tag for the tags: "ul", "div", or "span".
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The tags of the blog with post counts.
    """
    tags = Tag.objects.get_tags_with_published_posts().order_by("title")

    if not tags:
        return ""

    # If outer_tag is not one of the allowed tags, return an empty string.
    if outer_tag not in ["ul", "div", "span"]:
        return ""

    output = ""
    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer_tag == "ul":
        output += f"<ul{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"<li>{helpers.tag_link(tag, link_class)} ({count})</li>"
        output += "</ul>"

    if outer_tag == "div":
        output += f"<div{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"{helpers.tag_link(tag, link_class)} ({count}), "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer_tag == "span":
        output += f"<span{outer_class_html}>"
        for tag in tags:
            count = tag.posts.count()
            output += f"{helpers.tag_link(tag, link_class)} ({count}), "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return mark_safe(output)


@register.simple_tag
def site_pages_list(ul_outer_class: str = "", li_class: str = "", a_class: str = "", ul_child_class: str = "") -> str:
    """Returns an HTML list of the site's pages.

    The pages are sorted by menu order and then by title. Pages that have children have a nested list of children.

    The default output with no arguments is an unordered list with no classes. CSS classes can be added to the output by
    specifying the arguments shown below.

    ```
    <ul class="ul_outer_class">
        <li class="li_class">
            <a href="/page1/" class="a_class">Page 1</a>
        </li>
        <li class="li_class">
            <a href="/page2/" class="a_class">Page 2</a>
        </li>
        <li class="li_parent_class">
            <a href="/page3/" class="a_class">Page 3</a>
            <ul class="ul_child_class">
                <li class="li_class">
                    <a href="/page3/child1/" class="a_class">Child 1</a>
                </li>
                <li class="li_class">
                    <a href="/page3/child2/" class="a_class">Child 2</a>
                </li>
            </ul>
        </li>
    </ul>
    ```

    Args:
        ul_outer_class (str): The CSS class(es) for the outer unordered list.
        li_class (str): The CSS class(es) for the
        a_class (str): The CSS class(es) for the anchor tags.
        ul_child_class (str): The CSS class(es) for the nested unordered lists.

    Returns:
        str: The HTML list of the blog pages.
    """
    pages = Post.page_objects.get_page_tree()

    output = ""

    if not pages:
        return output

    if ul_outer_class:
        ul_outer_class = f' class="{ul_outer_class}"'

    output += f"<ul{ul_outer_class}>"
    output += helpers.get_site_pages_list(pages, li_class=li_class, a_class=a_class, ul_child_class=ul_child_class)
    output += "</ul>"

    return mark_safe(output)


@register.simple_tag
def site_pages(
    outer: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the pages of the site.

    Args:
        outer: The outer HTML tag for the pages.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The pages of the site.
    """
    pages = Post.page_objects.get_published_pages()

    if not pages:
        return ""

    output = ""

    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    if outer == "ul":
        output += f"<ul{outer_class_html}>"
        for page in pages:
            output += f"<li>{helpers.get_page_link(page=page, link_class=link_class)}</li>"
        output += "</ul>"

    if outer == "div":
        output += f"<div{outer_class_html}>"
        for page in pages:
            output += f"{helpers.get_page_link(page=page, link_class=link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</div>"

    if outer == "span":
        output += f"<span{outer_class_html}>"
        for page in pages:
            output += f"{helpers.get_page_link(page=page, link_class=link_class)}, "
        output = output[:-2]  # Remove the trailing comma and space
        output += "</span>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def page_title(
    context: Context,
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the page title.

    Args:
        context: The context.
        pre_text: The text to prepend to the page title.
        post_text: The text to append to the page title.

    Returns:
        str: The page title.
    """
    category: Category | None = context.get("category")
    author: User | None = context.get("author")
    post: Post | None = context.get("post")

    if category:
        title = category.title

    elif author:
        title = get_author_display_name(author)

    elif post:
        title = post.title
    else:
        title = ""

    if title:
        title = f"{pre_text}{title}{post_text}"

    return title


@register.simple_tag(takes_context=True)
def have_posts(context: Context) -> list[Post | None] | Page:
    """Return the posts in the context.

    If there's a `post` in the context, then we return a list with that post.

    If there's a `posts` in the context, then we return the posts. The `posts` should
    be a Page object.

    Args:
        context: The context.

    Returns:
        list[Post]: The posts in the context.
    """
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    if post:
        return [post]
    if posts:
        return posts

    return []


@register.simple_tag(takes_context=True)
def get_post_title(context: Context, *, include_empty: bool = False) -> str:
    """Return the title of a post.

    This is just the title of the post from the current context with no further HTML.

    If `include_empty` is set to `True`, then the title will be returned from the `post_title` property of the Post.

    Args:
        context: The context.
        include_empty: Whether to include the title if it is empty.

    Returns:
        str: The title of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    if include_empty:
        return post.post_title

    return post.title


@register.simple_tag(takes_context=True)
def get_post_url(context: Context) -> str:
    """Return the URL of a post.

    This is just the URL of the post from the current context with no further HTML.

    Args:
        context: The context.

    Returns:
        str: The URL of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    return post.url


@register.simple_tag(takes_context=True)
def post_title(
    context: Context,
    *,
    outer_tag: str = "",
    link_class: str = "",
    force_link: bool = False,
    include_empty: bool = False,
) -> str:
    """Return the title link for a post.

    If the post is part of a posts collection, then return the title and a link to the post. If the post is a single
    post, then return just the title of the post with no link. But this behavior can be overridden by setting
    `force_link` to `True`.

    The outer tag can be any of the following: "h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span". If the outer tag
    is not one of these, then the title will be returned with no outer tag.

    If the outer tag is one of the allowed tags, and if Microformats are enabled, then the outer tag will have the class
    "p-name".

    If the post doesn't have a title, return an empty string, but if `include_empty` is set to `True`, then the title
    will be returned from the `post_title` property of the Post.


    Otherwise return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the title.
        link_class: The CSS class(es) for the link.
        force_link: Whether to force the link to be displayed.
        include_empty: Whether to include the title if it is empty.

    Returns:
        str: The title link for the post.
    """
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    # If there's no post in the context, return an empty string.
    if not post:
        return ""

    # If there's no title, return an empty string.
    if not post.title and not include_empty:
        return ""

    # Get the title of the post
    output = post.post_title if include_empty else post.title

    # If there's a posts in the context, or if the link is forced, then we need to display the link.
    if posts or force_link:
        # Build the classes for the link
        link_classes = ""

        # Add p-category if microformats are enabled
        if djpress_settings.MICROFORMATS_ENABLED:
            link_classes += "u-url "

        # Add the user-defined link class
        link_classes += link_class

        # Trim any trailing spaces
        link_classes = link_classes.strip()

        link_class_html = f' class="{link_classes}"' if link_classes else ""

        output = f'<a href="{post.url}" title="{output}"{link_class_html}>{output}</a>'

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    if outer_tag in ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]:
        # If Microformats are enabled, use p-name with the outer tag.
        mf = ' class="p-name"' if djpress_settings.MICROFORMATS_ENABLED else ""

        output = f"<{outer_tag}{mf}>{output}</{outer_tag}>"

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def get_post_author(context: Context) -> str:
    """Return the author display name.

    Tries to display the first name and last name if available, otherwise falls back to
    the username.

    Args:
        context: The context.

    Returns:
        str: The author display name.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    author = post.author

    return get_author_display_name(author)


@register.simple_tag(takes_context=True)
def post_author(context: Context, link_class: str = "") -> str:
    """Return the author link for a post.

    Args:
        context: The context.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The author link.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    author = post.author
    author_display_name = get_author_display_name(author)

    mf = ' class="p-author"' if djpress_settings.MICROFORMATS_ENABLED else ""

    author_html = f"<span{mf}>{author_display_name}</span>"

    if not djpress_settings.AUTHOR_ENABLED:
        return author_html

    author_url = url_utils.get_author_url(user=author)

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{author_url}" title="View all posts by {author_display_name}"{link_class_html}>{author_html}</a>'
    )

    return mark_safe(output)


@register.simple_tag
def post_category_link(category: Category, link_class: str = "") -> str:
    """Return the category links for a post.

    TODO: do we need this?

    Args:
        category: The category of the post.
        link_class: The CSS class(es) for the link.
    """
    if not djpress_settings.CATEGORY_ENABLED:
        return category.title

    return mark_safe(helpers.category_link(category, link_class))


@register.simple_tag(takes_context=True)
def get_post_date(context: Context) -> str:
    """Return the date of a post.

    Args:
        context: The context.

    Returns:
        str: The date of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    output_date = post.local_datetime
    return output_date.strftime("%b %-d, %Y")


@register.simple_tag(takes_context=True)
def post_date(context: Context, link_class: str = "") -> str:
    """Return the date link for a post.

    Args:
        context: The context.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The date link for the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""
    output_date = post.local_datetime

    if not djpress_settings.ARCHIVE_ENABLED:
        return mark_safe(output_date.strftime("%b %-d, %Y"))

    post_year = output_date.strftime("%Y")
    post_month = output_date.strftime("%m")
    post_month_name = output_date.strftime("%b")
    post_day = output_date.strftime("%d")
    post_day_name = output_date.strftime("%-d")
    post_time = output_date.strftime("%-I:%M %p")

    year_url = url_utils.get_archives_url(year=int(post_year))
    month_url = url_utils.get_archives_url(year=int(post_year), month=int(post_month))
    day_url = url_utils.get_archives_url(year=int(post_year), month=int(post_month), day=int(post_day))

    link_class_html = f' class="{link_class}"' if link_class else ""

    output = (
        f'<a href="{month_url}" title="View all posts in {post_month_name} {post_year}"'
        f"{link_class_html}>{post_month_name}</a> "
        f'<a href="{day_url}" title="View all posts on {post_day_name} '
        f'{post_month_name} {post_year}"{link_class_html}>{post_day_name}</a>, '
        f'<a href="{year_url}" title="View all posts in {post_year}"{link_class_html}>'
        f"{post_year}</a>, "
        f"{post_time}."
    )

    # If Microformats are enabled, use dt-published with the date.
    if djpress_settings.MICROFORMATS_ENABLED:
        output = f'<time class="dt-published" datetime="{output_date.isoformat()}">{output}</time>'

    return mark_safe(output)


@register.simple_tag(takes_context=True)
def post_content(
    context: Context,
    *,
    outer_tag: str = "",
    read_more_link_class: str = "",
    read_more_text: str = "",
) -> str:
    """Return the content of a post.

    If the post is part of a posts collection, then we return the truncated content of
    the post with the read more link.

    If the post is a single post, return the full content of the post.

    The outer tag can be any one of the following: "section", "div", "article", "p", "span". If the outer tag is not one
    of these, then the content will be returned with no outer tag.

    If there's an outer tag, and if microformats are enabled, then the outer tag will have the class "e-content".

    If there's no post, return an empty string.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the content.
        read_more_link_class: The CSS class(es) for the read more link.
        read_more_text: The text for the read more link.

    Returns:
        str: The content of the post.
    """
    # Check if there's a post or posts in the context.
    post: Post | None = context.get("post")
    posts: Page | None = context.get("posts")

    # If there's no post, return an empty string.
    if not post:
        return ""

    # If there's a posts in the context, then we need to display the truncated content.
    if posts:
        content = post.truncated_content_markdown
        if post.is_truncated:
            content += helpers.post_read_more_link(post, read_more_link_class, read_more_text)
    else:
        content = post.content_markdown

    # If the outer tag is one of the allowed tags, then wrap the output in the outer tag.
    if outer_tag in ["section", "div", "article", "p", "span"]:
        # If Microformats are enabled, use e-content with the outer tag.
        mf = ' class="e-content"' if djpress_settings.MICROFORMATS_ENABLED else ""

        content = f"<{outer_tag}{mf}>{content}</{outer_tag}>"

    return mark_safe(content)


@register.simple_tag(takes_context=True)
def category_title(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of a category.

    Expects there to be an `category` in the context set to a Category object. If
    there's no category in the context or category is not a Category object, then return
    an empty string.


    Args:
        context: The context.
        outer: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category title.
        post_text: The text to append to the category title.

    Returns:
        str: The title of the category formatted with the outer tag and class if
        provided.
    """
    category: Category | None = context.get("category")

    if not category or not isinstance(category, Category):
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = category.title

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class}>{output}</{outer}>")

    return output


@register.simple_tag(takes_context=True)
def tag_title(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of the current tag.

    Expects there to be 'tags' in the context set to a list of tag slugs. In the tag views,
    this will show the tag or tags being displayed. If there's no tags in the context,
    returns an empty string.

    Args:
        context: The context.
        outer: The outer HTML tag for the tag title.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the tag title.
        post_text: The text to append to the tag title.

    Returns:
        str: The title of the tag formatted with the outer tag and class if
        provided.
    """
    tag_slugs: list | None = context.get("tags")

    if not tag_slugs:
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class_html = f' class="{outer_class}"' if outer_class else ""

    # Get tag titles from the slugs
    tags = [Tag.objects.get_tag_by_slug(slug) for slug in tag_slugs]
    tag_titles = [tag.title for tag in tags]

    # Join multiple tags with commas
    output = ", ".join(tag_titles) if len(tag_titles) > 1 else tag_titles[0]

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class_html}>{output}</{outer}>")

    return output


@register.simple_tag(takes_context=True)
def author_name(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the name of an author.

    Expects there to be an `author` in the context set to a user object. If there's no
    author in the context or author is not a User object, then return an empty string.

    Args:
        context: The context.
        outer: The outer HTML tag for the author.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the author name.
        post_text: The text to append to the author name.

    Returns:
        str: The name of the author formatted with the outer tag and class if
        provided.
    """
    author: User | None = context.get("author")

    if not author or not isinstance(author, User):
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = get_author_display_name(author)

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class}>{output}</{outer}>")

    return output


@register.simple_tag(takes_context=True)
def post_categories(
    context: Context,
    outer_tag: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the categories of a post.

    Each category is a link to the category page.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the categories.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The categories of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    categories = post.categories.all()
    if not categories:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(
        helpers.categories_html(
            categories=categories,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
        ),
    )


@register.simple_tag(takes_context=True)
def post_tags(
    context: Context,
    outer_tag: str = "ul",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the tags of a post.

    Each tag is a link to the tag page.

    Args:
        context: The context.
        outer_tag: The outer HTML tag for the tags.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The tags of the post.
    """
    post: Post | None = context.get("post")
    if not post:
        return ""

    tags = post.tags.all()
    if not tags:
        return ""

    # Explicitly pass outer_tag parameter for clarity
    return mark_safe(helpers.tags_html(tags=tags, outer_tag=outer_tag, outer_class=outer_class, link_class=link_class))


@register.simple_tag(takes_context=True)
def is_paginated(context: Context) -> bool:
    """Return whether the posts are paginated.

    Args:
        context: The context.

    Returns:
        bool: Whether the posts are paginated.
    """
    posts: Page | None = context.get("posts")
    if not posts or not isinstance(posts, Page):  # noqa: SIM103
        return False

    return True


@register.simple_tag(takes_context=True)
def get_pagination_range(context: Context) -> range:
    """Return the range of pagination pages.

    Args:
        context: The context.

    Returns:
        range: The pagination pages.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return range(0)

    return page.paginator.page_range


@register.simple_tag(takes_context=True)
def get_pagination_current_page(context: Context) -> int:
    """Return the current page number.

    Args:
        context: The context.

    Returns:
        int: The current page number.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return 0

    return page.number


@register.simple_tag(takes_context=True)
def pagination_links(
    context: Context,
) -> str:
    """Return the previous and next post links.

    This checks if there is a Page object in the context. If there is, then we return
    the previous and next post links. If there is no Page object in the context, then
    we return an empty string.

    Args:
        context: The context.

    Returns:
        str: The previous and next post links.
    """
    page: Page | None = context.get("posts")
    if not page or not isinstance(page, Page):
        return ""

    # Get the request to preserve query string parameters
    request = context.get("request")

    def build_pagination_url(page_number: int) -> str:
        """Build URL with preserved query string parameters."""
        if request and hasattr(request, "GET"):
            params = request.GET.copy()
            params["page"] = page_number
            return f"?{params.urlencode()}"
        return f"?page={page_number}"

    if page.has_previous():
        previous_output = (
            f'<span class="previous">'
            f'<a href="{build_pagination_url(1)}">&laquo; first</a> '
            f'<a href="{build_pagination_url(page.previous_page_number())}">previous</a>'
            f"</span>"
        )
    else:
        previous_output = ""

    if page.has_next():
        next_output = (
            f'<span class="next">'
            f'<a href="{build_pagination_url(page.next_page_number())}">next</a> '
            f'<a href="{build_pagination_url(page.paginator.num_pages)}">last &raquo;</a>'
            f"</span>"
        )
    else:
        next_output = ""

    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'

    return mark_safe(
        f'<div class="pagination">{previous_output} {current_output} {next_output}</div>',
    )


@register.simple_tag()
def page_link(
    page_slug: str,
    outer: str = "div",
    outer_class: str = "",
    link_class: str = "",
) -> str:
    """Return the link to a page.

    Args:
        page_slug: The slug of the page.
        outer: The outer HTML tag for the page link.
        outer_class: The CSS class(es) for the outer tag.
        link_class: The CSS class(es) for the link.

    Returns:
        str: The link to the page.
    """
    try:
        page: Post | None = Post.page_objects.get_published_page_by_slug(page_slug)
    except PageNotFoundError:
        return ""

    output = helpers.get_page_link(page, link_class=link_class)

    if outer == "li":
        return mark_safe(f"<li{outer_class}>{output}</li>")

    if outer == "span":
        return mark_safe(f"<span{outer_class}>{output}</span>")

    if outer == "div":
        return mark_safe(f"<div{outer_class}>{output}</div>")

    return mark_safe(output)


@register.simple_tag
def get_rss_url() -> str:
    """Return the URL to the RSS feed.

    Returns:
        str: The URL to the RSS feed.
    """
    return url_utils.get_rss_url()


@register.simple_tag
def rss_link() -> str:
    """Return an HTML link to the RSS feed.

    If the RSS feed is enabled, then return an HTML link tag that points to the RSS feed. Otherwise, return an empty
    string.

    Example:
        ```django
        {% rss_link %}
        ```

        ```html
        <link rel="alternate" type="application/rss+xml" title="Latest Posts" href="/rss/">
        ```

    Returns:
        str: The HTML link to the RSS feed.
    """
    if not djpress_settings.RSS_ENABLED:
        return ""

    rss_url = url_utils.get_rss_url()

    return mark_safe(f'<link rel="alternate" type="application/rss+xml" title="Latest Posts" href="{rss_url}">')


@register.tag(name="post_wrap")
def post_wrapper_tag(parser: template.base.Parser, token: template.base.Token) -> helpers.BlogPostWrapper:
    """Parse the blog post wrapper tag.

    This is a template tag that wraps the blog post content in a configurable HTML tag with a CSS class.

    Example usage:
        {% post_wrap "article" "post" %}<p>Post content</p>{% end_post_wrap %}

    Args:
        parser: The template parser.
        token: The template token.

    Returns:
        BlogPostWrapper: The blog post wrapper tag.
    """
    params = token.split_contents()[1:]  # skip the tag name

    tag, css_class = helpers.parse_post_wrapper_params(params)

    # If microformats are enabled, add the h-entry class before the css class
    if djpress_settings.MICROFORMATS_ENABLED:
        css_class = f"h-entry {css_class}" if css_class else "h-entry"

    if css_class:
        css_class = f' class="{css_class}"'

    nodelist = parser.parse(("end_post_wrap",))
    parser.delete_first_token()

    return helpers.BlogPostWrapper(nodelist, tag, css_class)


# Plugin hook template tags


@register.simple_tag()
def dj_header() -> str:
    """Return HTML content from plugins registered to the dj_header hook.

    This allows plugins to inject HTML content into the <head> section of templates.
    Plugins can register callbacks for the DJ_HEADER hook to add meta tags, styles,
    scripts, or other head content.

    Returns:
        str: HTML content from all registered dj_header hook callbacks, marked as safe.
    """
    content = registry.run_hook(DJ_HEADER)
    return mark_safe(content or "")


@register.simple_tag()
def dj_footer() -> str:
    """Return HTML content from plugins registered to the dj_footer hook.

    This allows plugins to inject HTML content near the end of HTML documents,
    typically before the closing </body> tag or within <footer> elements.
    Plugins can register callbacks for the DJ_FOOTER hook to add analytics,
    scripts, or other footer content.

    Returns:
        str: HTML content from all registered dj_footer hook callbacks, marked as safe.
    """
    content = registry.run_hook(DJ_FOOTER)
    return mark_safe(content or "")


@register.simple_tag(takes_context=True)
def search_title(
    context: Context,
    outer: str = "",
    outer_class: str = "",
    pre_text: str = "",
    post_text: str = "",
) -> str:
    """Return the title of a search query.

    Expects there to be an `search_query` in the context set to a string. If there's no search_query in the context or
    search_query is not a string, then return an empty string.


    Args:
        context: The context.
        outer: The outer HTML tag for the category.
        outer_class: The CSS class(es) for the outer tag.
        pre_text: The text to prepend to the category title.
        post_text: The text to append to the category title.

    Returns:
        str: The title of the search query formatted with the outer tag and class if provided.
    """
    search_query: str | None = context.get("search_query")

    if not search_query or not isinstance(search_query, str):
        return ""

    allowed_outer_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"]
    outer_class = f' class="{outer_class}"' if outer_class else ""

    output = search_query

    if pre_text:
        output = f"{pre_text}{output}"

    if post_text:
        output = f"{output}{post_text}"

    if outer in allowed_outer_tags:
        return mark_safe(f"<{outer}{outer_class}>{output}</{outer}>")

    return output


@register.simple_tag
def search_url() -> str:
    """Return the search URL.

    Returns:
        str: The search URL path, or empty string if search is disabled.

    Example:
        <form action="{% search_url %}" method="get">
            <input type="search" name="q" placeholder="Search...">
            <button type="submit">Search</button>
        </form>
    """
    return url_utils.get_search_url()


@register.simple_tag(takes_context=True)
def search_form(  # noqa: PLR0913
    context: Context,
    *,
    placeholder: str = "Search...",
    button_text: str = "Search",
    form_class: str = "",
    input_class: str = "",
    button_class: str = "",
    show_button: bool = True,
) -> str:
    """Return a search form as HTML.

    For a custom search form, use the {% search_url %} tag instead.

    Args:
        context: The template context - this is added automatically by Django.
        placeholder: Placeholder text for the search input.
        button_text: Text for the submit button.
        form_class: CSS class(es) for the form element.
        input_class: CSS class(es) for the input element.
        button_class: CSS class(es) for the button element.
        show_button: Whether to show the submit button.

    Returns:
        str: The search form HTML, or empty string if search is disabled.

    Example:
        {% search_form %}
        {% search_form placeholder="Search posts..." button_text="Go" form_class="my-form" %}
    """
    url = url_utils.get_search_url()

    if not url:
        return ""

    current_query = context.get("search_query", "")

    # Build the HTML
    form_class_attr = f' class="{form_class}"' if form_class else ""
    input_class_attr = f' class="{input_class}"' if input_class else ""
    button_class_attr = f' class="{button_class}"' if button_class else ""

    html = f'<form action="{url}" method="get"{form_class_attr}>'
    html += '<input type="search" name="q" '
    html += f'value="{current_query}" placeholder="{placeholder}" aria-label="Search"{input_class_attr}>'

    if show_button:
        html += f'<button type="submit"{button_class_attr}>{button_text}</button>'

    html += "</form>"

    return mark_safe(html)


@register.simple_tag(takes_context=True)
def search_errors(
    context: Context,
    outer: str = "div",
    outer_class: str = "search-errors",
    error_tag: str = "p",
    error_class: str = "error",
) -> str:
    """Return search validation errors as HTML.

    Expects there to be a `search_errors` list in the context. If there are no errors,
    returns an empty string.

    Args:
        context: The template context.
        outer: The outer HTML tag to wrap all errors (div, section, etc).
        outer_class: The CSS class(es) for the outer tag.
        error_tag: The HTML tag for each individual error message.
        error_class: The CSS class(es) for each error tag.

    Returns:
        str: The error messages HTML, or empty string if no errors.

    Example:
        {% search_errors %}
        {% search_errors outer="section" outer_class="alert alert-danger" %}
    """
    errors: list | None = context.get("search_errors")

    if not errors or not isinstance(errors, list):
        return ""

    allowed_outer_tags = ["div", "section", "aside", "article"]
    allowed_error_tags = ["p", "span", "div", "li"]

    if outer not in allowed_outer_tags:
        outer = "div"

    if error_tag not in allowed_error_tags:
        error_tag = "p"

    outer_class_attr = f' class="{outer_class}"' if outer_class else ""
    error_class_attr = f' class="{error_class}"' if error_class else ""

    html = f"<{outer}{outer_class_attr}>"

    for error in errors:
        if isinstance(error, str):
            html += f"<{error_tag}{error_class_attr}>{error}</{error_tag}>"

    html += f"</{outer}>"

    return mark_safe(html)
