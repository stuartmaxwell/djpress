"""Helper functions for the template tags."""

from django import template
from django.db import models
from django.utils.html import conditional_escape, format_html, format_html_join
from django.utils.safestring import SafeString, mark_safe

from djpress.conf import settings as djpress_settings
from djpress.models import Category, Post, Tag
from djpress.models.post import PageNode


def wrap_in_tag(content: str | SafeString, tag: str, css_class: str = "") -> str | SafeString:
    """Wraps an HTML content snippet inside a whitelisted HTML tag with optional class.

    If tag is empty, content is returned as-is.
    If tag is not whitelisted, empty string is returned.

    Args:
        content (str | SafeString): The HTML content to wrap.
        tag (str): The HTML tag to wrap the content in.
        css_class (str, optional): The CSS class to apply to the tag. Defaults to "".

    Returns:
        str | SafeString: The wrapped HTML content, or an empty string if the tag is not whitelisted.
    """
    if not tag:
        return format_html("{}", content)

    allowed_tags = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span", "section", "article", "li", "ul"}
    if tag not in allowed_tags:
        return ""

    if css_class:
        return format_html('<{0} class="{1}">{2}</{0}>', tag, css_class, content)

    return format_html("<{0}>{1}</{0}>", tag, content)


def build_html_link(
    url: str,
    text: str,
    title: str | SafeString,
    css_class: str = "",
    microformat_class: str = "",
) -> SafeString:
    """Builds a secure HTML anchor link.

    Args:
        url (str): The URL to link to.
        text (str): The text to display.
        title (str | SafeString): The title to display.
        css_class (str, optional): The CSS class to apply to the link. Defaults to "".
        microformat_class (str, optional): The microformat class to apply to the link. Defaults to "".

    Returns:
        SafeString: The HTML for the link.
    """
    classes = []
    if microformat_class and djpress_settings.MICROFORMATS_ENABLED:
        classes.append(microformat_class)
    if css_class:
        classes.append(css_class)

    class_str = " ".join(classes)
    class_html = format_html(' class="{}"', class_str) if class_str else ""

    return format_html(
        '<a href="{}" title="{}"{}>{}</a>',
        url,
        title,
        class_html,
        text,
    )


def categories_html(
    categories: models.QuerySet,
    outer_tag: str,
    outer_class: str,
    link_class: str,
    separator: str,
    pre_text: str,
    post_text: str,
) -> str | SafeString:
    """Return the HTML for the categories.

    Note this isn't a template tag, but a helper function for the other template tags

    Args:
        categories (models.QuerySet): The categories to display.
        outer_tag (str): The HTML tag to wrap the categories in.
        outer_class (str): The CSS class to apply to the outer tag.
        link_class (str): The CSS class to apply to the category links.
        separator (str): The separator to use between category links.
        pre_text (str): The text to display before the category links.
        post_text (str): The text to display after the category links.

    Returns:
        str | SafeString: The HTML for the categories, or an empty string if no categories are provided.
    """
    if not categories:
        return ""

    if outer_tag == "ul":
        items_html = format_html_join(
            "",
            "<li>{}</li>",
            ((get_category_link(category, link_class),) for category in categories),
        )
        return wrap_in_tag(items_html, "ul", outer_class)

    escaped_separator = conditional_escape(separator)
    links = [get_category_link(category, link_class) for category in categories]
    joined_links = mark_safe(escaped_separator.join(links))

    content = format_html("{}{}{}", pre_text, joined_links, post_text)
    return wrap_in_tag(content, outer_tag, outer_class)


def tags_html(
    tags: models.QuerySet,
    outer_tag: str,
    outer_class: str,
    link_class: str,
    separator: str,
    pre_text: str,
    post_text: str,
) -> str | SafeString:
    """Return the HTML for the tags.

    Note this isn't a template tag, but a helper function for the other template tags

    Args:
        tags (models.QuerySet): The tags to display.
        outer_tag (str): The outer tag to use.
        outer_class (str): The outer tag class.
        link_class (str): The link class.
        separator (str): The separator to use between tags.
        pre_text (str): The text to display before the tags.
        post_text (str): The text to display after the tags.

    Returns:
        str | SafeString: The HTML for the tags.
    """
    if not tags:
        return ""

    if outer_tag == "ul":
        items_html = format_html_join(
            "",
            "<li>{}</li>",
            ((get_tag_link(tag, link_class),) for tag in tags),
        )
        return wrap_in_tag(items_html, "ul", outer_class)

    escaped_separator = conditional_escape(separator)
    links = [get_tag_link(tag, link_class) for tag in tags]
    joined_links = mark_safe(escaped_separator.join(links))

    content = format_html("{}{}{}", pre_text, joined_links, post_text)
    return wrap_in_tag(content, outer_tag, outer_class)


def get_category_link(category: Category, link_class: str = "") -> SafeString:
    """Return the category link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the category links.

    Args:
        category (Category): The category to link to.
        link_class (str): The link class.

    Returns:
        SafeString: The HTML for the category link.
    """
    title = format_html("View all posts in the {} category", category.title)
    return build_html_link(
        url=category.url,
        text=category.title,
        title=title,
        css_class=link_class,
        microformat_class="p-category",
    )


def get_tag_link(tag: "Tag", link_class: str = "") -> SafeString:
    """Return the tag link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the tag links.

    Args:
        tag (Tag): The tag to link to.
        link_class (str): The link class.

    Returns:
        SafeString: The HTML for the tag link.
    """
    title = format_html("View all posts tagged with {}", tag.title)
    return build_html_link(
        url=tag.url,
        text=tag.title,
        title=title,
        css_class=link_class,
        microformat_class="p-category",
    )


def get_page_link(page: Post, link_class: str = "") -> SafeString:
    """Return the page link.

    This is not intended to be used as a template tag. It is used by the other
    template tags in this module to generate the page links.

    Args:
        page (Post): The page to link to.
        link_class (str): The link class.

    Returns:
        SafeString: The HTML for the page link.
    """
    title = format_html("View the {} page", page.title)
    return build_html_link(
        url=page.url,
        text=page.title,
        title=title,
        css_class=link_class,
    )


def post_read_more_link(
    post: Post,
    link_class: str = "",
    read_more_text: str = "",
) -> str | SafeString:
    """Return the read more link for a post.

    If the post isn't truncated, return an empty string.

    Args:
        post (Post): The post to check.
        link_class (str): The link class.
        read_more_text (str): The read more text to display.

    Returns:
        str | SafeString: The HTML for the read more link.
    """
    post_read_more_text = djpress_settings.POST_READ_MORE_TEXT

    # The following line should never be true since we assign a default value.
    if not isinstance(post_read_more_text, str):  # pragma: no cover
        msg = f"Expected a string for POST_READ_MORE_TEXT, got {type(post_read_more_text).__name__}"
        raise TypeError(msg)

    if post.is_truncated is False:
        return ""

    read_more_text = read_more_text or post_read_more_text
    class_html = format_html(' class="{}"', link_class) if link_class else ""

    return format_html(
        '<p><a href="{}"{}>{}</a></p>',
        post.url,
        class_html,
        read_more_text,
    )


def get_site_pages_list(
    pages: list[PageNode],
    li_class: str = "",
    a_class: str = "",
    ul_child_class: str = "",
    levels: int = 0,
) -> str | SafeString:
    """Return the HTML for the site pages list.

    This expects to be passed the output of the get_page_tree method.

    Args:
        pages (list[PageNode]): The pages to display.
        li_class (str): The li class.
        a_class (str): The a class.
        ul_child_class (str): The ul child class.
        levels (int): The number of levels to display.

    Returns:
        str | SafeString: The HTML for the site pages list.
    """
    output = []

    for page_data in pages:
        page = page_data["page"]
        children = page_data["children"]

        page_link_html = get_page_link(page, link_class=a_class)

        children_html = ""
        if children and (levels == 0 or levels > 1):
            new_levels = levels - 1 if levels > 0 else 0
            inner_list = get_site_pages_list(
                children,
                li_class=li_class,
                a_class=a_class,
                ul_child_class=ul_child_class,
                levels=new_levels,
            )
            if ul_child_class:
                children_html = format_html('<ul class="{}">{}</ul>', ul_child_class, inner_list)
            else:
                children_html = format_html("<ul>{}</ul>", inner_list)

        if li_class:
            item_html = format_html('<li class="{}">{}{}</li>', li_class, page_link_html, children_html)
        else:
            item_html = format_html("<li>{}{}</li>", page_link_html, children_html)

        output.append(item_html)

    return mark_safe("".join(output))


class BlogPostWrapper(template.Node):
    """Wraps the blog post content.

    This is a template tag that wraps the blog post content in a configurable HTML tag with a CSS class.
    """

    def __init__(self, nodelist: template.NodeList, tag: str = "", css_class: str = "") -> None:
        """Initialize the BlogPostWrapper."""
        self.nodelist = nodelist
        self.tag = "article" if tag == "" else tag
        self.css_class = css_class

    def render(self, context: template.Context) -> str | SafeString:
        """Render the blog post content."""
        content = self.nodelist.render(context)

        # Just return the content if the tag isn't allowed
        if self.tag not in ["div", "span", "section", "article"]:
            return content

        if self.css_class:
            return format_html('<{0} class="{1}">{2}</{0}>', self.tag, self.css_class, content)
        return format_html("<{0}>{1}</{0}>", self.tag, content)


def parse_post_wrapper_params(params: list) -> tuple[str, str]:
    """Parse the parameters for the template tag."""
    tag = ""
    css_class = ""

    for num, param in enumerate(params):
        # Support keyword arguments
        if "=" in param:
            name, value = param.split("=", 1)
            value = value.strip("\"'")
            if name == "tag":
                tag = value
            elif name == "class":
                css_class = value
            else:
                # Ignore any other keyword arguments
                pass
        else:
            # Support positional arguments too
            value = param.strip("\"'")
            if num == 0:
                tag = value
            if num == 1:
                css_class = value

    return tag, css_class
