import pytest

from django.contrib.auth.models import User

from djpress.conf import settings
from djpress.models import Category, Post, Tag
from djpress.templatetags.helpers import (
    categories_html,
    get_category_link,
    post_read_more_link,
    parse_post_wrapper_params,
    tags_html,
    get_page_link,
    wrap_in_tag,
)


@pytest.mark.django_db
def test_categories_html(category1, category2, category3):
    assert settings.CATEGORY_PREFIX == "test-url-category"

    categories = Category.objects.all()
    assert list(categories) == [category1, category2, category3]

    # Test case 1
    outer = "ul"
    outer_class = "categories"
    link_class = "category"
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        '<ul class="categories">'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case 2
    outer = "ul"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        "<ul>"
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a></li>'
        f'<li><a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a></li>'
        "</ul>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case 3
    outer = "div"
    outer_class = "categories"
    link_class = "category"
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        '<div class="categories">'
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a>'
        "</div>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case 4
    outer = "div"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        "<div>"
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a>'
        "</div>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case 5
    outer = "span"
    outer_class = "categories"
    link_class = "category"
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        '<span class="categories">'
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category {link_class}">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category {link_class}">{category3.title}</a>'
        "</span>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case 6
    outer = "span"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        "<span>"
        f'<a href="/{settings.CATEGORY_PREFIX}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category2.slug}/" title="View all posts in the {category2.title} category" class="p-category">{category2.title}</a>, '
        f'<a href="/{settings.CATEGORY_PREFIX}/{category3.slug}/" title="View all posts in the {category3.title} category" class="p-category">{category3.title}</a>'
        "</span>"
    )
    assert (
        categories_html(
            categories,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )


def test_categories_html_no_categories():
    categories = Category.objects.none()
    assert (
        categories_html(
            categories,
            outer_tag="outer",
            outer_class="outer_class",
            link_class="link_class",
            separator="|",
            pre_text="pre_text",
            post_text="post_text",
        )
        == ""
    )


@pytest.mark.django_db
def test_tags_html(settings, tag1, tag2, tag3):
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == "test-url-tag"

    tags = Tag.objects.get_tags()
    assert list(tags) == [tag1, tag2, tag3]

    # Test case - ul with options: pre_text, post_text, and spearator are ignored
    outer = "ul"
    outer_class = "tags"
    link_class = "tag"
    separator = " * "
    pre_text = "this will be ignored"
    post_text = "this will be ignored"
    expected_output = (
        '<ul class="tags">'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a></li>'
        "</ul>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case: ul with no options
    outer = "ul"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        "<ul>"
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category">{tag1.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category">{tag2.title}</a></li>'
        f'<li><a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category">{tag3.title}</a></li>'
        "</ul>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case: div with basic options
    outer = "div"
    outer_class = "tags"
    link_class = "tag"
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        '<div class="tags">'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a>'
        "</div>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case:: div with all options
    outer = "div"
    outer_class = "tags"
    link_class = "tag"
    separator = " | "
    pre_text = "Pre text"
    post_text = "Post text"
    expected_output = (
        '<div class="tags">Pre text'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category {link_class}">{tag1.title}</a> | '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category {link_class}">{tag2.title}</a> | '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category {link_class}">{tag3.title}</a>'
        "Post text</div>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case: span with no options
    outer = "span"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        "<span>"
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="p-category">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="p-category">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="p-category">{tag3.title}</a>'
        "</span>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case: no microformats or link_class
    outer = "span"
    outer_class = ""
    link_class = ""
    separator = ", "
    pre_text = ""
    post_text = ""
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = (
        "<span>"
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}">{tag3.title}</a>'
        "</span>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )

    # Test case: no microformats with link class
    outer = "span"
    outer_class = "tags"
    link_class = "tag"
    separator = ", "
    pre_text = ""
    post_text = ""
    expected_output = (
        '<span class="tags">'
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag1.slug}/" title="View all posts tagged with {tag1.title}" class="{link_class}">{tag1.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag2.slug}/" title="View all posts tagged with {tag2.title}" class="{link_class}">{tag2.title}</a>, '
        f'<a href="/{settings.DJPRESS_SETTINGS["TAG_PREFIX"]}/{tag3.slug}/" title="View all posts tagged with {tag3.title}" class="{link_class}">{tag3.title}</a>'
        "</span>"
    )
    assert (
        tags_html(
            tags,
            outer_tag=outer,
            outer_class=outer_class,
            link_class=link_class,
            separator=separator,
            pre_text=pre_text,
            post_text=post_text,
        )
        == expected_output
    )


def test_tags_html_no_tags():
    tags = Tag.objects.none()
    assert (
        tags_html(
            tags,
            outer_tag="outer",
            outer_class="outer_class",
            link_class="link_class",
            separator="|",
            pre_text="pre_text",
            post_text="post_text",
        )
        == ""
    )


@pytest.mark.django_db
def test_get_category_link(settings, category1):
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    # Test case 1 - no link class
    link_class = ""
    expected_output = f'<a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category">{category1.title}</a>'
    assert get_category_link(category1, link_class) == expected_output

    # Test case 2 - with link class
    link_class = "category-class"
    expected_output = f'<a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/{category1.slug}/" title="View all posts in the {category1.title} category" class="p-category {link_class}">{category1.title}</a>'
    assert get_category_link(category1, link_class) == expected_output

    # Test case 3 - microformats disabled
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    link_class = ""
    expected_output = f'<a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/{category1.slug}/" title="View all posts in the {category1.title} category">{category1.title}</a>'
    assert get_category_link(category1, link_class) == expected_output


@pytest.mark.django_db
def test_post_read_more_link(test_post1, test_long_post1):
    assert settings.POST_READ_MORE_TEXT == "Test read more..."
    assert settings.POST_PREFIX == "test-posts"

    # Test case 1 - use the app settings for the read more text
    link_class = ""
    read_more_text = ""
    expected_output = f'<p><a href="{test_long_post1.url}">{settings.POST_READ_MORE_TEXT}</a></p>'
    assert post_read_more_link(test_long_post1, link_class, read_more_text) == expected_output

    # Test case 2 - use all options
    link_class = "read-more"
    read_more_text = "Continue reading"
    expected_output = f'<p><a href="{test_long_post1.url}" class="{link_class}">{read_more_text}</a></p>'
    assert post_read_more_link(test_long_post1, link_class, read_more_text) == expected_output

    # Test case: a post with no truncation returns an empty string
    assert post_read_more_link(test_post1) == ""


def test_parse_post_wrapper_params():
    # Test case 1
    params = ['tag="div"', 'class="blog-post"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 2
    params = ['class="blog-post"']
    expected_output = ("", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 3
    params = ['"div"', '"blog-post"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 4
    params = ['"blog-post"']
    expected_output = ("blog-post", "")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 5
    params = ['""', '"blog-post"']
    expected_output = ("", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output

    # Test case 6
    params = ['tag="div"', 'class="blog-post"', 'extra="extra"']
    expected_output = ("div", "blog-post")
    assert parse_post_wrapper_params(params) == expected_output


@pytest.mark.django_db
def test_get_page_link_xss(test_post1, test_page1):
    """Test that the page title in the get_page_link tag is escaped."""
    bad_string = '<script>alert("evil")</script>'
    escaped_string = "&lt;script&gt;alert(&quot;evil&quot;)&lt;/script&gt;"

    test_post1.title = bad_string
    test_post1.save()
    test_page1.title = bad_string
    test_page1.save()

    assert bad_string not in get_page_link(test_post1)
    assert escaped_string in get_page_link(test_post1)

    assert bad_string not in get_page_link(test_page1)
    assert escaped_string in get_page_link(test_page1)


def test_wrap_in_tag():
    """Test that wrap_in_tag returns the expected HTML."""
    result = wrap_in_tag(content="This is the content", tag="div", css_class="blog-post")
    assert result == '<div class="blog-post">This is the content</div>'

    result = wrap_in_tag(content="This is the content", tag="div")
    assert result == "<div>This is the content</div>"

    result = wrap_in_tag(content="This is the content", tag="", css_class="blog-post")
    assert result == "This is the content"

    result = wrap_in_tag(content="This is the content", tag="foobar", css_class="blog-post")
    assert result == ""
