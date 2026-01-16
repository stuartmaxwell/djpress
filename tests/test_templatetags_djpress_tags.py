from djpress.conf import settings as djpress_settings
from django.utils import timezone
import pytest
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.template import Context, Template
from django.urls import reverse
from django.db import models

from djpress.models import Category, Post, Tag
from djpress.templatetags import djpress_tags
from djpress.templatetags.helpers import (
    post_read_more_link,
    categories_html,
    get_page_link,
    tags_html,
)
from djpress.utils import get_author_display_name
from djpress.exceptions import PageNotFoundError


@pytest.mark.django_db
def test_get_posts(test_post1, test_long_post1, test_post2, test_post3):
    posts = Post.objects.all().order_by("-published_at")

    assert list(djpress_tags.get_posts()) == list(posts)


@pytest.mark.django_db
def test_get_pages(test_page1, test_page2, test_page3):
    assert list(djpress_tags.get_pages()) == [test_page1, test_page2, test_page3]

    test_page1.status = "draft"
    test_page1.save()
    assert list(djpress_tags.get_pages()) == [test_page2, test_page3]

    test_page2.parent = test_page1
    test_page2.save()
    assert list(djpress_tags.get_pages()) == [test_page3]


def test_get_site_title(settings):
    """Test the get_site_title template tag.

    This can be changed on the fly.
    """
    assert settings.DJPRESS_SETTINGS["SITE_TITLE"] == "My Test DJ Press Blog"
    assert djpress_tags.get_site_title() == settings.DJPRESS_SETTINGS["SITE_TITLE"]

    # Change the title
    settings.DJPRESS_SETTINGS["SITE_TITLE"] = "My New Blog Title"
    assert settings.DJPRESS_SETTINGS["SITE_TITLE"] == "My New Blog Title"
    assert djpress_tags.get_site_title() == settings.DJPRESS_SETTINGS["SITE_TITLE"]


def test_get_site_description(settings):
    """Test the get_site_description template tag.

    This can be changed on the fly.
    """
    assert settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] == "This is a test blog."
    assert djpress_tags.get_site_description() == settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"]

    # Change the description
    settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] = "My New Blog description"
    assert settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] == "My New Blog description"
    assert djpress_tags.get_site_description() == settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"]


@pytest.mark.django_db
def test_get_categories(category1, category2, category3):
    categories = Category.objects.all().order_by("menu_order").order_by("title")
    djpress_categories = djpress_tags.get_categories()

    assert category1 in categories
    assert category2 in categories
    assert category3 in categories
    assert category1 in djpress_categories
    assert category2 in djpress_categories
    assert category3 in djpress_categories

    assert list(djpress_categories) == list(categories)  # type: ignore


@pytest.mark.django_db
def test_get_tags(tag1, tag2, tag3):
    tags = Tag.objects.get_tags().order_by("title")
    djpresstags = djpress_tags.get_tags()

    assert tag1 in tags
    assert tag2 in tags
    assert tag3 in tags
    assert tag1 in djpresstags
    assert tag2 in djpresstags
    assert tag3 in djpresstags

    assert list(djpresstags) == list(tags)


def test_site_title(settings):
    """site_title returns some configurable HTML."""
    assert settings.DJPRESS_SETTINGS["SITE_TITLE"] == "My Test DJ Press Blog"
    # Test case - no options
    expected_output = "My Test DJ Press Blog"
    assert djpress_tags.site_title() == expected_output

    # Test case - with all options
    expected_output = f'<h1 class="title"><a href="/" class="test-link-class">My Test DJ Press Blog</a></h1>'
    assert (
        djpress_tags.site_title(
            outer_tag="h1",
            outer_class="title",
            link=True,
            link_class="test-link-class",
        )
        == expected_output
    )

    # Test case - just link=True
    expected_output = f'<a href="/" class="test-link-class">My Test DJ Press Blog</a>'
    assert (
        djpress_tags.site_title(
            link=True,
            link_class="test-link-class",
        )
        == expected_output
    )

    # Test case - options but no link
    expected_output = f'<h1 class="title">My Test DJ Press Blog</h1>'
    assert (
        djpress_tags.site_title(
            outer_tag="h1",
            outer_class="title",
        )
        == expected_output
    )

    # Test case - invalid outer_tag
    expected_output = ""
    assert (
        djpress_tags.site_title(
            outer_tag="ul",
            outer_class="title",
        )
        == expected_output
    )

    # Test case - no site_title and no options
    settings.DJPRESS_SETTINGS["SITE_TITLE"] = ""
    expected_output = ""
    assert djpress_tags.site_title() == expected_output

    # Test case - no site_title and all options
    settings.DJPRESS_SETTINGS["SITE_TITLE"] = ""
    expected_output = ""
    assert (
        djpress_tags.site_title(
            outer_tag="h1",
            outer_class="title",
            link=True,
            link_class="test-link-class",
        )
        == expected_output
    )


def test_site_description(settings):
    """site_description returns some configurable HTML."""
    assert settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] == "This is a test blog."
    # Test case - no options
    expected_output = "This is a test blog."
    assert djpress_tags.site_description() == expected_output

    # Test case - with all options
    expected_output = f'<h2 class="subtitle">This is a test blog.</h2>'
    assert (
        djpress_tags.site_description(
            outer_tag="h2",
            outer_class="subtitle",
        )
        == expected_output
    )

    # Test case - invalid outer_tag
    expected_output = ""
    assert (
        djpress_tags.site_description(
            outer_tag="ul",
            outer_class="subtitle",
        )
        == expected_output
    )

    # Test case - no site_description and no options
    settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] = ""
    expected_output = ""
    assert djpress_tags.site_description() == expected_output

    # Test case - no site_description and all options
    settings.DJPRESS_SETTINGS["SITE_DESCRIPTION"] = ""
    expected_output = ""
    assert (
        djpress_tags.site_description(
            outer_tag="h2",
            outer_class="subtitle",
        )
        == expected_output
    )


@pytest.mark.django_db
def test_get_post_title_single_post(test_post1):
    context = Context({"post": test_post1})
    assert djpress_tags.get_post_title(context) == "Test Post1"

    # test with no title
    test_post1.title = ""
    test_post1.save()
    assert djpress_tags.get_post_title(context) == ""
    assert djpress_tags.get_post_title(context, include_empty=True) == "Test post1..."


def test_get_post_title_no_post_context():
    context = Context({"foo": "bar"})
    assert djpress_tags.get_post_title(context) == ""
    assert type(djpress_tags.get_post_title(context)) == str


@pytest.mark.django_db
def test_get_post_url(test_post1):
    context = Context({"post": test_post1})

    assert djpress_tags.get_post_url(context) == test_post1.url


def test_get_post_url_no_context():
    context = Context({"foo": "bar"})

    assert djpress_tags.get_post_url(context) == ""


@pytest.mark.django_db
def test_get_post_category_slugs(settings, test_post1, category2):
    """Test the `get_post_category_slugs` tempalte tag.

    test_post1 has a single category called `Test Category1` (`test-category1`).
    `category2` has a slug of `test-category2`.
    """
    assert test_post1.categories.count() == 1
    assert test_post1.categories.first().slug == "test-category1"
    assert category2.slug == "test-category2"

    # Test case: Post in the context, one category
    context = Context({"post": test_post1})
    assert djpress_tags.get_post_category_slugs(context) == ["test-category1"]

    # Test case: No post in the context, empty list
    context = Context({"foo": "bar"})
    assert djpress_tags.get_post_category_slugs(context) == []

    # Test case: Post with multiple categories
    test_post1.categories.add(category2)
    context = Context({"post": test_post1})
    assert djpress_tags.get_post_category_slugs(context) == ["test-category1", "test-category2"]


@pytest.mark.django_db
def test_get_post_categories(test_post1, category1, category2):
    """Test the `get_post_categories` tempalte tag.

    test_post1 has a single category called `Test Category1`.
    """
    assert test_post1.categories.count() == 1
    assert test_post1.categories.first() == category1

    # Test case: Post in the context, one category
    context = Context({"post": test_post1})
    assert list(djpress_tags.get_post_categories(context)) == [category1]

    # Test case: No post in the context, empty list
    context = Context({"foo": "bar"})
    assert list(djpress_tags.get_post_categories(context)) == []

    # Test case: Post with multiple categories
    test_post1.categories.add(category2)
    context = Context({"post": test_post1})
    assert list(djpress_tags.get_post_categories(context)) == [category1, category2]


@pytest.mark.django_db
def test_post_title_posts(settings, test_post1):
    """Test the post_title template tag."""
    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_post1], "post": test_post1})

    # Confirm settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"

    # this generates a URL based on the slug only - this is prefixed with the POST_PREFIX setting
    post_url = test_post1.url

    expected_output = f'<a href="{post_url}" title="{test_post1.title}" class="u-url">{test_post1.title}</a>'
    assert djpress_tags.post_title(context) == expected_output

    # disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = f'<a href="{post_url}" title="{test_post1.title}">{test_post1.title}</a>'
    assert djpress_tags.post_title(context) == expected_output


@pytest.mark.django_db
def test_post_title_no_post():
    context = Context({"post": None})

    expected_output = ""
    assert djpress_tags.post_title(context) == expected_output


@pytest.mark.django_db
def test_post_title_no_title(test_post1):
    # test with no title
    test_post1.title = ""
    test_post1.save()

    context = Context({"post": test_post1})

    assert djpress_tags.post_title(context) == ""
    assert djpress_tags.post_title(context, include_empty=True) == "Test post1..."


@pytest.mark.django_db
def test_post_title_single_post(test_post1):
    context = Context({"post": test_post1})
    expected_output = test_post1.title
    assert djpress_tags.post_title(context) == expected_output


@pytest.mark.django_db
def test_post_title_single_post_force_link(test_post1):
    context = Context({"post": test_post1})

    # this generates a URL based on the slug only - this is prefixed with the POST_PREFIX setting
    post_url = test_post1.url
    expected_output = f'<a href="{post_url}" title="{test_post1.title}" class="u-url">{test_post1.title}</a>'
    assert djpress_tags.post_title(context, force_link=True) == expected_output


@pytest.mark.django_db
def test_post_title_with_valid_tag(settings, test_post1):
    context = Context({"post": test_post1})

    # Microformats are enabled by default
    expected_output = f'<h1 class="p-name">{test_post1.title}</h1>'
    assert djpress_tags.post_title(context, outer_tag="h1") == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False

    expected_output = f"<h1>{test_post1.title}</h1>"
    assert djpress_tags.post_title(context, outer_tag="h1") == expected_output


@pytest.mark.django_db
def test_post_title_with_invalid_tag(test_post1):
    context = Context({"post": test_post1})

    assert djpress_tags.post_title(context, outer_tag="ul") == ""


@pytest.mark.django_db
def test_post_title_with_prefix(settings, test_post1):
    # Confirm settings in settings_testing.py
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"

    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_post1], "post": test_post1})

    post_url = test_post1.url

    expected_output = f'<a href="{post_url}" title="{test_post1.title}" class="u-url">{test_post1.title}</a>'
    assert djpress_tags.post_title(context) == expected_output


@pytest.mark.django_db
def test_get_post_author(test_post1):
    context = Context({"post": test_post1})

    author = test_post1.author
    output = get_author_display_name(author)
    assert djpress_tags.get_post_author(context) == output


def test_get_post_author_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.get_post_author(context) == ""
    assert type(djpress_tags.get_post_author(context)) == str


def test_post_author_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_author(context) == ""
    assert type(djpress_tags.post_author(context)) == str


@pytest.mark.django_db
def test_post_author(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"

    author = test_post1.author

    expected_output = (
        f'<span class="p-author">'
        f'<a href="/{settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"]}/testuser/" title="View all posts by '
        f'{get_author_display_name(author)}">'
        f"{get_author_display_name(author)}</a>"
        f"</span>"
    )
    assert djpress_tags.post_author(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = (
        f"<span>"
        f'<a href="/{settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"]}/testuser/" title="View all posts by '
        f'{get_author_display_name(author)}">'
        f"{get_author_display_name(author)}</a>"
        f"</span>"
    )
    assert djpress_tags.post_author(context) == expected_output

    # Test case: invalid outer tag
    expected_output = ""
    assert djpress_tags.post_author(context, outer_tag="invalid") == expected_output


@pytest.mark.django_db
def test_post_author_author_path_disabled(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"

    settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] = False

    author = test_post1.author

    expected_output = f'<span class="p-author">{get_author_display_name(author)}</span>'
    assert djpress_tags.post_author(context) == expected_output


@pytest.mark.django_db
def test_post_author_with_author_path_with_one_link_class(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"

    author = test_post1.author

    expected_output = (
        f'<span class="p-author">'
        f'<a href="/{settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"]}/testuser/" title="View all posts by '
        f'{get_author_display_name(author)}" class="class1">'
        f"{get_author_display_name(author)}</a>"
        "</span>"
    )
    assert djpress_tags.post_author(context, link_class="class1") == expected_output


@pytest.mark.django_db
def test_post_author_with_author_path_with_two_link_class(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] is True
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"

    author = test_post1.author

    expected_output = (
        '<span class="p-author">'
        f'<a href="/{settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"]}/testuser/" title="View all posts by '
        f'{get_author_display_name(author)}" class="class1 class2">'
        f"{get_author_display_name(author)}</a>"
        "</span>"
    )
    assert djpress_tags.post_author(context, link_class="class1 class2") == expected_output


def test_get_post_date_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.get_post_date(context) == ""
    assert type(djpress_tags.get_post_date(context)) == str


@pytest.mark.django_db
def test_get_post_date_with_date_archives_disabled(settings, test_post1):
    """djpress_tags.get_post_date is not impacted by the ARCHIVE_ENABLED setting."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] = False
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is False

    expected_output = test_post1.local_datetime.strftime("%b %-d, %Y")

    assert djpress_tags.get_post_date(context) == expected_output


@pytest.mark.django_db
def test_get_post_date_with_date_archives_enabled(settings, test_post1):
    """djpress_tags.get_post_date is not impacted by the ARCHIVE_ENABLED setting."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    expected_output = test_post1.local_datetime.strftime("%b %-d, %Y")

    assert djpress_tags.get_post_date(context) == expected_output


def test_post_date_no_post():
    context = Context({"foo": "bar"})

    assert djpress_tags.post_date(context) == ""
    assert type(djpress_tags.post_date(context)) == str


@pytest.mark.django_db
def test_post_date_with_date_archives_disabled(settings, test_post1):
    """Should return just the date."""
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] = False
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is False

    expected_output = test_post1.local_datetime.strftime("%b %-d, %Y")

    assert djpress_tags.post_date(context) == expected_output


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    post_date = timezone.localtime(test_post1.published_at)
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<time class="dt-published" datetime="{post_date.isoformat()}">'
        f'<a href="/test-url-archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}">{post_month_name}</a> '
        f'<a href="/test-url-archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}">{post_day_name}</a>, '
        f'<a href="/test-url-archives/{post_year}/" title="View all posts in {post_year}">{post_year}</a>, '
        f"{post_time}."
        "</time>"
    )

    assert djpress_tags.post_date(context) == expected_output

    # disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = (
        f'<a href="/test-url-archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}">{post_month_name}</a> '
        f'<a href="/test-url-archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}">{post_day_name}</a>, '
        f'<a href="/test-url-archives/{post_year}/" title="View all posts in {post_year}">{post_year}</a>, '
        f"{post_time}."
    )

    assert djpress_tags.post_date(context) == expected_output


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled_with_one_link_class(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    post_date = timezone.localtime(test_post1.published_at)
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<time class="dt-published" datetime="{post_date.isoformat()}">'
        f'<a href="/test-url-archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1">{post_month_name}</a> '
        f'<a href="/test-url-archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1">{post_day_name}</a>, '
        f'<a href="/test-url-archives/{post_year}/" title="View all posts in {post_year}" class="class1">{post_year}</a>, '
        f"{post_time}."
        "</time>"
    )

    assert djpress_tags.post_date(context, "class1") == expected_output


@pytest.mark.django_db
def test_post_date_with_date_archives_enabled_with_two_link_classes(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["ARCHIVE_ENABLED"] is True

    post_date = timezone.localtime(test_post1.published_at)
    post_year = post_date.strftime("%Y")
    post_month = post_date.strftime("%m")
    post_month_name = post_date.strftime("%b")
    post_day = post_date.strftime("%d")
    post_day_name = post_date.strftime("%-d")
    post_time = post_date.strftime("%-I:%M %p")

    expected_output = (
        f'<time class="dt-published" datetime="{post_date.isoformat()}">'
        f'<a href="/test-url-archives/{post_year}/{post_month}/" title="View all posts in {post_month_name} {post_year}" class="class1 class2">{post_month_name}</a> '
        f'<a href="/test-url-archives/{post_year}/{post_month}/{post_day}/" title="View all posts on {post_day_name} {post_month_name} {post_year}" class="class1 class2">{post_day_name}</a>, '
        f'<a href="/test-url-archives/{post_year}/" title="View all posts in {post_year}" class="class1 class2">{post_year}</a>, '
        f"{post_time}."
        "</time>"
    )

    assert djpress_tags.post_date(context, "class1 class2") == expected_output


def test_post_content_no_post():
    """If there's no post in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.post_content(context) == ""
    assert type(djpress_tags.post_content(context)) == str


@pytest.mark.django_db
def test_post_content_with_post(test_post1):
    """If there's a post in the context, return the post content."""
    context = Context({"post": test_post1})

    expected_output = f"{test_post1.content_markdown}"

    assert djpress_tags.post_content(context) == expected_output


@pytest.mark.django_db
def test_post_content_with_post_with_outer(settings, test_post1):
    """If there's a post in the context, return the post content."""
    context = Context({"post": test_post1})

    # Microformats are enabled by default
    expected_output = f'<section class="e-content">{test_post1.content_markdown}</section>'
    assert djpress_tags.post_content(context, outer_tag="section") == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    expected_output = f"<section>{test_post1.content_markdown}</section>"
    assert djpress_tags.post_content(context, outer_tag="section") == expected_output


@pytest.mark.django_db
def test_post_content_with_posts_long_post(test_long_post1):
    """If there's a posts in the context, return the truncated post content."""
    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_long_post1], "post": test_long_post1})

    assert test_long_post1.is_truncated is True

    expected_output = f"{test_long_post1.truncated_content_markdown}{post_read_more_link(test_long_post1)}"

    assert djpress_tags.post_content(context) == expected_output


@pytest.mark.django_db
def test_post_content_with_posts_short_post(test_post1):
    """If there's a posts in the context, return the truncated post content."""
    # Context should have both a posts and a post to simulate the for post in posts loop
    context = Context({"posts": [test_post1], "post": test_post1})

    assert test_post1.is_truncated is False

    assert post_read_more_link(test_post1) == ""

    assert djpress_tags.post_content(context) == test_post1.truncated_content_markdown


@pytest.mark.django_db
def test_author_name(user):
    """author_name only works if there's an author in the context."""
    context = Context({"author": user})

    # Test case 1 - no options
    expected_output = get_author_display_name(user)
    assert djpress_tags.author_name(context) == expected_output

    # Test case 2 - with options
    expected_output = f'<h1 class="title">View posts by {get_author_display_name(user)} author</h1>'
    assert (
        djpress_tags.author_name(
            context,
            outer_tag="h1",
            outer_class="title",
            pre_text="View posts by ",
            post_text=" author",
        )
        == expected_output
    )

    # Test case: invalid outer_tag
    expected_output = ""
    assert (
        djpress_tags.author_name(
            context,
            outer_tag="invalid",
            outer_class="title",
            pre_text="View posts by ",
            post_text=" author",
        )
        == expected_output
    )


def test_author_name_no_author():
    """If there's no author in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.author_name(context) == ""
    assert type(djpress_tags.author_name(context)) == str


@pytest.mark.django_db
def test_category_title(category1):
    """category_title only works if there's a category in the context."""
    context = Context({"category": category1})

    # Test case 1 - no options
    expected_output = category1.title
    assert djpress_tags.category_title(context) == expected_output

    # Test case 2 - with options
    expected_output = f'<h1 class="title">View posts in the {category1.title} category</h1>'
    assert (
        djpress_tags.category_title(
            context,
            outer_tag="h1",
            outer_class="title",
            pre_text="View posts in the ",
            post_text=" category",
        )
        == expected_output
    )

    # Test case: invalid outer_tag
    expected_output = ""
    assert (
        djpress_tags.category_title(
            context,
            outer_tag="invalid",
            outer_class="title",
            pre_text="View posts in the ",
            post_text=" category",
        )
        == expected_output
    )


def test_category_title_no_category():
    """If there's no category in the context, return an empty string."""
    context = Context({"foo": "bar"})

    assert djpress_tags.category_title(context) == ""
    assert type(djpress_tags.category_title(context)) == str


@pytest.mark.django_db
def test_post_categories(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category">Test Category1</a></li></ul>'

    assert djpress_tags.post_categories(context) == expected_output


def test_post_categories_none_post_context():
    context = Context({"post": None})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


def test_post_categories_no_post_context():
    context = Context({"foo": None})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


@pytest.mark.django_db
def test_post_categories_no_categories_context(test_post1):
    test_post1.categories.clear()
    context = Context({"post": test_post1})

    expected_output = ""
    assert djpress_tags.post_categories(context) == expected_output


@pytest.mark.django_db
def test_post_categories_ul(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category">Test Category1</a></li></ul>'

    assert djpress_tags.post_categories(context, outer_tag="ul") == expected_output


@pytest.mark.django_db
def test_post_categories_ul_class1(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1">Test Category1</a></li></ul>'

    assert djpress_tags.post_categories(context, outer_tag="ul", link_class="class1") == expected_output


@pytest.mark.django_db
def test_post_categories_ul_class1_class2(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<ul><li><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1 class2">Test Category1</a></li></ul>'

    assert djpress_tags.post_categories(context, outer_tag="ul", link_class="class1 class2") == expected_output


@pytest.mark.django_db
def test_post_categories_div(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<div><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category">Test Category1</a></div>'

    assert djpress_tags.post_categories(context, outer_tag="div") == expected_output


@pytest.mark.django_db
def test_post_categories_div_class1(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<div><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1">Test Category1</a></div>'

    assert djpress_tags.post_categories(context, outer_tag="div", link_class="class1") == expected_output


@pytest.mark.django_db
def test_post_categories_div_class1_class2(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<div><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1 class2">Test Category1</a></div>'

    assert djpress_tags.post_categories(context, outer_tag="div", link_class="class1 class2") == expected_output


@pytest.mark.django_db
def test_post_categories_span(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<span><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category">Test Category1</a></span>'

    assert djpress_tags.post_categories(context, outer_tag="span") == expected_output


@pytest.mark.django_db
def test_post_categories_span_class1(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<span><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1">Test Category1</a></span>'

    assert djpress_tags.post_categories(context, outer_tag="span", link_class="class1") == expected_output


@pytest.mark.django_db
def test_post_categories_span_class1_class2(settings, test_post1):
    context = Context({"post": test_post1})

    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"

    expected_output = f'<span><a href="/{settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"]}/test-category1/" title="View all posts in the Test Category1 category" class="p-category class1 class2">Test Category1</a></span>'

    assert djpress_tags.post_categories(context, outer_tag="span", link_class="class1 class2") == expected_output


@pytest.mark.django_db
def test_site_categories(category1, category2):
    categories = Category.objects.all()

    assert category1 in categories
    assert category2 in categories

    assert djpress_tags.site_categories() == categories_html(
        categories=categories, outer_tag="ul", outer_class="", link_class="", separator=", ", pre_text="", post_text=""
    )


@pytest.mark.django_db
def test_site_categories_no_categories():
    assert djpress_tags.site_categories() == ""


@pytest.mark.django_db
def test_site_tags(tag1, tag2):
    tags = Tag.objects.all()

    assert tag1 in tags
    assert tag2 in tags

    assert djpress_tags.site_tags() == tags_html(
        tags=tags, outer_tag="ul", outer_class="", link_class="", separator=", ", pre_text="", post_text=""
    )


@pytest.mark.django_db
def test_site_tags_no_tags():
    assert djpress_tags.site_tags() == ""


@pytest.mark.django_db
def test_tags_with_counts(test_post1, test_post2, tag1, tag2, tag3):
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    # Only tags 1 and 2 have posts, tag3 is empty
    result = djpress_tags.tags_with_counts()

    # Should only show tags with published posts
    assert tag1.title in result
    assert tag2.title in result
    assert tag3.title not in result

    # Should show post counts
    assert "(1)" in result


@pytest.mark.django_db
def test_tag_title(tag1):
    context = Context({"tags": [tag1.slug]})

    # Test with default parameters
    result = djpress_tags.tag_title(context)
    assert result == tag1.title

    # Test with outer tag and class
    result = djpress_tags.tag_title(context, outer_tag="h1", outer_class="test-class")
    assert f'<h1 class="test-class">{tag1.title}</h1>' == result

    # Test with pre and post text
    result = djpress_tags.tag_title(context, pre_text="Posts tagged with: ", post_text="!")
    assert f"Posts tagged with: {tag1.title}!" == result

    # Test case: invalid outer tag
    result = djpress_tags.tag_title(context, outer_tag="invalid")
    assert result == ""


@pytest.mark.django_db
def test_tag_title_multiple_tags(tag1, tag2):
    context = Context({"tags": [tag1.slug, tag2.slug]})

    # Test with default parameters
    result = djpress_tags.tag_title(context)
    assert result == f"{tag1.title}, {tag2.title}"

    # Test with custom separator
    result = djpress_tags.tag_title(context, separator=" | ")
    assert result == f"{tag1.title} | {tag2.title}"

    # Test with outer tag and class
    result = djpress_tags.tag_title(context, outer_tag="h1", outer_class="test-class")
    assert f'<h1 class="test-class">{tag1.title} | {tag2.title}</h1>' == result

    # Test with pre and post text
    result = djpress_tags.tag_title(context, pre_text="Posts tagged with: ", post_text="!")
    assert f"Posts tagged with: {tag1.title} | {tag2.title}!" == result


@pytest.mark.django_db
def test_site_pages_list_no_pages():
    assert djpress_tags.site_pages_list() == ""

    # Test case with include_home
    assert djpress_tags.site_pages_list(include_home=True) == '<ul><li><a href="/">Home</a></li></ul>'


@pytest.mark.django_db
def test_site_pages_list_no_children(test_page1, test_page2, test_page3):
    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}</li>"
        f"<li>{get_page_link(page=test_page2)}</li>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list() == expected_output

    # Test case with include_home
    expected_output = (
        "<ul>"
        f'<li><a href="/">Home</a></li>'
        f"<li>{get_page_link(page=test_page1)}</li>"
        f"<li>{get_page_link(page=test_page2)}</li>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list(include_home=True) == expected_output


@pytest.mark.django_db
def test_site_pages_list_no_children_with_classes(test_page1, test_page2, test_page3):
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}</li>'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}</li>'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
        )
        == expected_output
    )

    # Test case with include_home
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class"><a href="/" class="a-class">Home</a></li>'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}</li>'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}</li>'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
            include_home=True,
        )
        == expected_output
    )


@pytest.mark.django_db
def test_site_pages_list_one_child(test_page1, test_page2, test_page3):
    test_page2.parent = test_page1
    test_page2.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list() == expected_output

    # Test case with include_home
    expected_output = (
        "<ul>"
        f'<li><a href="/">Home</a></li>'
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list(include_home=True) == expected_output


@pytest.mark.django_db
def test_site_pages_list_one_child_with_classes(test_page1, test_page2, test_page3):
    test_page2.parent = test_page1
    test_page2.save()

    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
        )
        == expected_output
    )

    # Test case with include_home
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class"><a href="/" class="a-class">Home</a></li>'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
            include_home=True,
        )
        == expected_output
    )


@pytest.mark.django_db
def test_site_pages_list_two_children(test_page1, test_page2, test_page3, test_page4):
    test_page3.parent = test_page1
    test_page3.save()
    test_page4.parent = test_page2
    test_page4.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list() == expected_output

    # Test case with include_home
    expected_output = (
        "<ul>"
        f'<li><a href="/">Home</a></li>'
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list(include_home=True) == expected_output


@pytest.mark.django_db
def test_site_pages_list_two_children_with_classes(test_page1, test_page2, test_page3, test_page4):
    test_page3.parent = test_page1
    test_page3.save()
    test_page4.parent = test_page2
    test_page4.save()

    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
        )
        == expected_output
    )

    # Test case with include_home
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class"><a href="/" class="a-class">Home</a></li>'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
            include_home=True,
        )
        == expected_output
    )


@pytest.mark.django_db
def test_site_pages_list_child_grandchild(test_page1, test_page2, test_page3, test_page4):
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list() == expected_output

    # Test case with include_home
    expected_output = (
        "<ul>"
        f'<li><a href="/">Home</a></li>'
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list(include_home=True) == expected_output


@pytest.mark.django_db
def test_site_pages_list_child_grandchild_with_classes(test_page1, test_page2, test_page3, test_page4):
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()

    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
        )
        == expected_output
    )

    # Test case with include_home
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class"><a href="/" class="a-class">Home</a></li>'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
            include_home=True,
        )
        == expected_output
    )


@pytest.mark.django_db
def test_site_pages_list_child_greatgrandchild(test_page1, test_page2, test_page3, test_page4):
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page4.parent = test_page3
    test_page4.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list() == expected_output

    # Test case with include_home
    expected_output = (
        "<ul>"
        f'<li><a href="/">Home</a></li>'
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert djpress_tags.site_pages_list(include_home=True) == expected_output


@pytest.mark.django_db
def test_site_pages_list_child_greatgrandchild_with_classes(test_page1, test_page2, test_page3, test_page4):
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page4.parent = test_page3
    test_page4.save()

    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
        )
        == expected_output
    )

    # Test case with include_home
    expected_output = (
        '<ul class="ul-outer-class">'
        f'<li class="li-class"><a href="/" class="a-class">Home</a></li>'
        f'<li class="li-class">{get_page_link(page=test_page1, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page2, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page3, link_class="a-class")}'
        '<ul class="ul-child-class">'
        f'<li class="li-class">{get_page_link(page=test_page4, link_class="a-class")}</li>'
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )
    assert (
        djpress_tags.site_pages_list(
            ul_outer_class="ul-outer-class",
            li_class="li-class",
            a_class="a-class",
            ul_child_class="ul-child-class",
            include_home=True,
        )
        == expected_output
    )


@pytest.mark.django_db
def test_site_pages_list_child_change_order(test_page1, test_page2, test_page3, test_page4, test_page5):
    test_page5.menu_order = 1
    test_page5.save()
    test_page1.menu_order = 2
    test_page1.save()
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page4.parent = test_page1
    test_page4.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page5)}</li>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}</li>"
        "</ul>"
        "</li>"
        f"<li>{get_page_link(page=test_page4)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )

    assert djpress_tags.site_pages_list() == expected_output


@pytest.mark.django_db
def test_site_pages_list_child_greatgreatgrandchild(test_page1, test_page2, test_page3, test_page4, test_page5):
    test_page2.parent = test_page1
    test_page2.save()
    test_page3.parent = test_page2
    test_page3.save()
    test_page4.parent = test_page3
    test_page4.save()
    test_page5.parent = test_page4
    test_page5.save()

    expected_output = (
        "<ul>"
        f"<li>{get_page_link(page=test_page1)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page2)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page3)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page4)}"
        "<ul>"
        f"<li>{get_page_link(page=test_page5)}</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
        "</li>"
        "</ul>"
    )

    assert djpress_tags.site_pages_list() == expected_output


@pytest.mark.django_db
def test_site_pages_no_pages():
    assert djpress_tags.site_pages() == ""

    # Test case: invalid outer_tag
    assert djpress_tags.site_pages(outer_tag="invalid") == ""


@pytest.mark.django_db
def test_site_pages_one_page(test_page1):
    # Test case: no options:
    expected_output = (
        f'<div><a href="{test_page1.url}" title="View the {test_page1.title} page">{test_page1.title}</a></div>'
    )
    assert djpress_tags.site_pages() == expected_output

    # Test case: span options:
    expected_output = (
        f'<span><a href="{test_page1.url}" title="View the {test_page1.title} page">{test_page1.title}</a></span>'
    )
    assert djpress_tags.site_pages(outer_tag="span") == expected_output

    # Test case: all options:
    expected_output = f'<span class="outer-class"><a href="{test_page1.url}" title="View the {test_page1.title} page" class="link-class">{test_page1.title}</a></span>'
    assert (
        djpress_tags.site_pages(outer_tag="span", outer_class="outer-class", link_class="link-class") == expected_output
    )

    # Test case: outer_class option:
    expected_output = f'<div class="outer-class"><a href="{test_page1.url}" title="View the {test_page1.title} page">{test_page1.title}</a></div>'
    assert djpress_tags.site_pages(outer_class="outer-class") == expected_output

    # Test case: link_class option:
    expected_output = f'<div><a href="{test_page1.url}" title="View the {test_page1.title} page" class="link-class">{test_page1.title}</a></div>'
    assert djpress_tags.site_pages(link_class="link-class") == expected_output

    # Test case: separator option - no difference.:
    expected_output = f'<div><a href="{test_page1.url}" title="View the {test_page1.title} page" class="link-class">{test_page1.title}</a></div>'
    assert djpress_tags.site_pages(link_class="link-class", separator=" | ") == expected_output

    # Test case: invalid outer_tag
    assert djpress_tags.site_pages(outer_tag="invalid") == ""


@pytest.mark.django_db
def test_site_pages_multiple_pages(test_page1, test_page2):
    # Test case: no options:
    expected_output = f"<div>"
    expected_output += f'<a href="{test_page1.url}" title="View the {test_page1.title} page">{test_page1.title}</a>'
    expected_output += ", "
    expected_output += f'<a href="{test_page2.url}" title="View the {test_page2.title} page">{test_page2.title}</a>'
    expected_output += f"</div>"
    assert djpress_tags.site_pages() == expected_output

    # Test case: all options:
    expected_output = f'<span class="outer-class">'
    expected_output += (
        f'<a href="{test_page1.url}" title="View the {test_page1.title} page" class="link-class">{test_page1.title}</a>'
    )
    expected_output += " | "
    expected_output += (
        f'<a href="{test_page2.url}" title="View the {test_page2.title} page" class="link-class">{test_page2.title}</a>'
    )
    expected_output += f"</span>"
    assert (
        djpress_tags.site_pages(outer_tag="span", outer_class="outer-class", link_class="link-class", separator=" | ")
        == expected_output
    )

    # Test case: invalid outer_tag
    assert djpress_tags.site_pages(outer_tag="invalid") == ""


@pytest.mark.django_db
def test_page_title(test_post1, test_page1):
    # Test case 1 - category page
    context = Context({"category": test_post1.categories.first()})
    assert test_post1.categories.first().title == djpress_tags.page_title(context)

    # Test case 2 - author page
    context = Context({"author": test_post1.author})
    assert get_author_display_name(test_post1.author) == djpress_tags.page_title(context)

    # Test case 3 - single post
    context = Context({"post": test_post1})
    assert test_post1.title == djpress_tags.page_title(context)

    # Test case 4 - single page
    context = Context({"post": test_page1})
    assert test_page1.title == djpress_tags.page_title(context)

    # Test case 5 - no context
    context = Context()
    assert "" == djpress_tags.page_title(context)


@pytest.mark.django_db
def test_is_paginated(settings, test_post1, test_post2, test_long_post1):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Test case 1 - no paginator in context
    context = Context()
    assert djpress_tags.is_paginated(context) is False

    # Test case 2 - paginator in context
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.is_paginated(context) is True


def test_pagination_links_no_posts():
    context = Context()

    assert djpress_tags.pagination_links(context) == ""
    assert type(djpress_tags.pagination_links(context)) == str


@pytest.mark.django_db
def test_get_pagination_range(settings, test_post1, test_post2, test_long_post1):
    # Test case 1 - 1 page, i.e. 3 posts with 3 posts per page
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_range(context) == range(1, 2)

    # Test case 2 - 2 pages, i.e. 3 posts with 2 posts per page
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 2
    assert djpress_tags.get_pagination_range(context) == range(1, 3)

    # Test case 3 - 3 pages, i.e. 3 posts with 1 posts per page
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 1
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 1
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_range(context) == range(1, 4)


@pytest.mark.django_db
def test_get_pagination_range_no_posts(settings):
    # Test case 1 - no posts
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_range(context) == range(0)


@pytest.mark.django_db
def test_get_pagination_current_page(settings, test_post1, test_post2, test_long_post1):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 1
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 1

    # Test case 1 - no page number
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_current_page(context) == 1

    # Test case 2 - page number 1
    page = posts.get_page(number=1)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_current_page(context) == 1

    # Test case 3 - page number 2
    page = posts.get_page(number=2)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_current_page(context) == 2

    # Test case 4 - page number 3
    page = posts.get_page(number=3)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_current_page(context) == 3


@pytest.mark.django_db
def test_get_pagination_current_page_no_posts(settings):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    # Test case 1 - no posts
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    assert djpress_tags.get_pagination_current_page(context) == 0


@pytest.mark.django_db
def test_pagination_links_one_page(settings, test_post1, test_post2, test_long_post1):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)

    context = Context({"posts": page})

    previous_output = ""
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = ""

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output


@pytest.mark.django_db
def test_pagination_links_two_pages(settings, test_post1, test_post2, test_long_post1):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2

    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 2

    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )

    # Test case 1 - first page with no page
    page = posts.get_page(number=None)

    context = Context({"posts": page})

    previous_output = ""
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = (
        f'<span class="next">'
        f'<a href="?page={page.next_page_number()}">next</a> '
        f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
        f"</span>"
    )

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output

    # Test case 2 - first page with page number 1
    page = posts.get_page(number=1)

    context = Context({"posts": page})

    previous_output = ""
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = (
        f'<span class="next">'
        f'<a href="?page={page.next_page_number()}">next</a> '
        f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
        f"</span>"
    )

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output

    # Test case 3 - second page with page number 2
    page = posts.get_page(number=2)

    context = Context({"posts": page})

    previous_output = (
        f'<span class="previous">'
        f'<a href="?page=1">&laquo; first</a> '
        f'<a href="?page={page.previous_page_number()}">previous</a>'
        f"</span>"
    )
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = ""

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output


@pytest.mark.django_db
def test_pagination_links_three_pages(settings, test_post1, test_post2, test_long_post1):
    # Confirm settings are set according to settings_testing.py
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3

    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 1

    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 1

    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )

    # Test case 1 - first page with no page number
    page = posts.get_page(number=None)

    context = Context({"posts": page})

    previous_output = ""
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = (
        f'<span class="next">'
        f'<a href="?page={page.next_page_number()}">next</a> '
        f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
        f"</span>"
    )

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output

    # Test case 2 - first page with page number 1
    page = posts.get_page(number=1)

    context = Context({"posts": page})

    previous_output = ""
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = (
        f'<span class="next">'
        f'<a href="?page={page.next_page_number()}">next</a> '
        f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
        f"</span>"
    )

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output

    # Test case 3 - first page with page number 2
    page = posts.get_page(number=2)

    context = Context({"posts": page})

    previous_output = (
        f'<span class="previous">'
        f'<a href="?page=1">&laquo; first</a> '
        f'<a href="?page={page.previous_page_number()}">previous</a>'
        f"</span>"
    )
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = (
        f'<span class="next">'
        f'<a href="?page={page.next_page_number()}">next</a> '
        f'<a href="?page={page.paginator.num_pages}">last &raquo;</a>'
        f"</span>"
    )

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output

    # Test case 4 - first page with page number 3
    page = posts.get_page(number=3)

    context = Context({"posts": page})

    previous_output = (
        f'<span class="previous">'
        f'<a href="?page=1">&laquo; first</a> '
        f'<a href="?page={page.previous_page_number()}">previous</a>'
        f"</span>"
    )
    current_output = f'<span class="current">Page {page.number} of {page.paginator.num_pages}</span>'
    next_output = ""

    expected_output = f'<div class="pagination">{previous_output} {current_output} {next_output}</div>'

    assert djpress_tags.pagination_links(context) == expected_output


@pytest.mark.django_db
def test_page_link(test_page1):
    # Test 1 - page with a non-existent page_slug
    page_slug = ""
    assert djpress_tags.page_link(page_slug=page_slug) == ""

    # Test 2 - page with a page_slug and no options
    page_slug = test_page1.slug
    expected_output = get_page_link(page=test_page1)
    assert djpress_tags.page_link(page_slug=page_slug) == expected_output

    # Test case: page with a page_slug and div and no options
    page_slug = test_page1.slug
    outer_tag = "div"
    output = get_page_link(page=test_page1)
    expected_output = f"<div>{output}</div>"
    assert djpress_tags.page_link(page_slug=page_slug, outer_tag=outer_tag) == expected_output

    # Test case: page with a page_slug and div and all options
    page_slug = test_page1.slug
    outer_tag = "div"
    outer_class = "outer-class"
    link_class = "link-class"

    output = get_page_link(page=test_page1, link_class=link_class)
    expected_output = f'<div class="{outer_class}">{output}</div>'
    assert (
        djpress_tags.page_link(
            page_slug=page_slug,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
        )
        == expected_output
    )

    # Test 5 - page with a page_slug and span and all options
    page_slug = test_page1.slug
    outer_tag = "span"
    outer_class = "outerclass"
    link_class = "linkclass"

    output = get_page_link(page=test_page1, link_class=link_class)
    expected_output = f'<span class="{outer_class}">{output}</span>'
    assert (
        djpress_tags.page_link(
            page_slug=page_slug,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
        )
        == expected_output
    )

    # Test case: - invalid outer tag
    page_slug = test_page1.slug
    outer_tag = "invalid"

    output = get_page_link(page=test_page1)
    expected_output = ""
    assert (
        djpress_tags.page_link(
            page_slug=page_slug,
            outer_tag=outer_tag,
            outer_class=outer_class,
            link_class=link_class,
        )
        == expected_output
    )


def test_rss_url(settings):
    settings.DJPRESS_SETTINGS["RSS_ENABLED"] = True

    settings.DJPRESS_SETTINGS["RSS_PATH"] = "test-rss"
    expected_output = "/test-rss/"
    assert settings.DJPRESS_SETTINGS["RSS_PATH"] == "test-rss"
    assert settings.DJPRESS_SETTINGS["RSS_ENABLED"] is True
    assert djpress_tags.get_rss_url() == expected_output

    settings.DJPRESS_SETTINGS["RSS_PATH"] = "foobar"
    expected_output = "/foobar/"
    assert settings.DJPRESS_SETTINGS["RSS_PATH"] == "foobar"
    assert settings.DJPRESS_SETTINGS["RSS_ENABLED"] is True
    assert djpress_tags.get_rss_url() == expected_output


def test_rss_link(settings):
    settings.DJPRESS_SETTINGS["RSS_ENABLED"] = True
    settings.DJPRESS_SETTINGS["RSS_PATH"] = "test-rss"
    expected_output = f'<link rel="alternate" type="application/rss+xml" title="Latest Posts" href="/test-rss/">'
    assert djpress_tags.rss_link() == expected_output

    settings.DJPRESS_SETTINGS["RSS_ENABLED"] = False
    expected_output = ""
    assert djpress_tags.rss_link() == expected_output


@pytest.mark.django_db
def test_get_recent_posts(settings, test_post1, test_post2, test_post3):
    assert settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] == 3
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=None)
    context = Context({"posts": page})
    tag_get_recent_posts = list(djpress_tags.get_recent_posts(context))
    page_posts = list(page.object_list)
    assert tag_get_recent_posts == page_posts

    # Test case 2 - 2 pages, i.e. 3 posts with 2 posts per page
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=2)
    context = Context({"posts": page})
    tag_get_recent_posts = list(djpress_tags.get_recent_posts(context))
    page_posts = list(page.object_list)
    assert tag_get_recent_posts != page_posts

    # Test case 3 - 3 pages, i.e. 3 posts with 1 posts per page
    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 1
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(number=3)
    context = Context({"posts": page})
    tag_get_recent_posts = list(djpress_tags.get_recent_posts(context))
    page_posts = list(page.object_list)
    assert tag_get_recent_posts != page_posts


@pytest.mark.django_db
def test_post_wrapper_single_post_no_tag(settings):
    """Creates an article by default."""
    template_text = "{% load djpress_tags %}{% post_wrap %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = '<article class="h-entry"><p>This is test post 1.</p></article>'
    assert template.render(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False

    template = Template(template_text)
    expected_output = "<article><p>This is test post 1.</p></article>"
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_valid_tag(settings):
    """Create a div instead."""
    template_text = "{% load djpress_tags %}{% post_wrap tag='div' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = '<div class="h-entry"><p>This is test post 1.</p></div>'
    assert template.render(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False

    template = Template(template_text)
    expected_output = "<div><p>This is test post 1.</p></div>"
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_valid_tag_double_quotes(settings):
    """Create a div instead."""
    template_text = '{% load djpress_tags %}{% post_wrap tag="div" %}<p>This is test post 1.</p>{% end_post_wrap %}'
    context = Context({})

    template = Template(template_text)
    expected_output = '<div class="h-entry"><p>This is test post 1.</p></div>'
    assert template.render(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False

    template = Template(template_text)
    expected_output = "<div><p>This is test post 1.</p></div>"
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_invalid_tag():
    """Just returns the content."""
    template_text = "{% load djpress_tags %}{% post_wrap tag='foobar' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = "<p>This is test post 1.</p>"
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_valid_tag_arg_only():
    """Just returns the content."""
    template_text = "{% load djpress_tags %}{% post_wrap 'article' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = '<article class="h-entry"><p>This is test post 1.</p></article>'
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_invalid_tag_arg_only():
    """Just returns the content."""
    template_text = "{% load djpress_tags %}{% post_wrap 'foobar' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = "<p>This is test post 1.</p>"
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_class(settings):
    template_text = (
        "{% load djpress_tags %}{% post_wrap class='blog-post' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    )
    context = Context({})

    template = Template(template_text)
    expected_output = '<article class="h-entry blog-post"><p>This is test post 1.</p></article>'
    assert template.render(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    template = Template(template_text)
    expected_output = '<article class="blog-post"><p>This is test post 1.</p></article>'
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_wrapper_single_post_with_tag_and_class(settings):
    template_text = "{% load djpress_tags %}{% post_wrap tag='div' class='blog-post' %}<p>This is test post 1.</p>{% end_post_wrap %}"
    context = Context({})

    template = Template(template_text)
    expected_output = '<div class="h-entry blog-post"><p>This is test post 1.</p></div>'
    assert template.render(context) == expected_output

    # Disable microformats
    settings.DJPRESS_SETTINGS["MICROFORMATS_ENABLED"] = False
    template = Template(template_text)
    expected_output = '<div class="blog-post"><p>This is test post 1.</p></div>'
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_post_tags(test_post1, tag1):
    """Test post_tag."""
    # Make sure that test_post1 has a tag
    assert test_post1.tags.count() == 0
    test_post1.tags.add(tag1)
    assert test_post1.tags.count() == 1

    # Test case: no post in context
    context = Context({"foo": "bar"})
    assert djpress_tags.post_tags(context) == ""

    # Set the post in the context
    context = Context({"post": test_post1})
    tags = test_post1.tags.all()

    # Test case: invalid outer_tag
    assert djpress_tags.post_tags(context, outer_tag="invalid") == ""

    # Test case: no options - default is an unordered list
    assert djpress_tags.post_tags(context) == tags_html(
        tags, outer_tag="ul", outer_class="", link_class="", separator="", pre_text="", post_text=""
    )

    # Test case: post has no tags
    test_post1.tags.clear()
    assert test_post1.tags.count() == 0
    assert djpress_tags.post_tags(context) == ""


@pytest.mark.django_db
def test_tags_with_counts_outer_div(test_post1, test_post2, tag1, tag2):
    """Test tags_with_counts with div as outer tag."""
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    result = djpress_tags.tags_with_counts(outer_tag="div", outer_class="tag-list")

    assert '<div class="tag-list">' in result
    assert tag1.title in result
    assert tag2.title in result
    assert "(1)" in result


@pytest.mark.django_db
def test_tags_with_counts_incorrect_outer_div(test_post1, test_post2, tag1, tag2):
    """Test tags_with_counts with incorrect outer tag."""
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    result = djpress_tags.tags_with_counts(outer_tag="main", outer_class="tag-list")

    assert result == ""


@pytest.mark.django_db
def test_tags_with_counts_outer_span(test_post1, test_post2, tag1, tag2):
    """Test tags_with_counts with span as outer tag."""
    test_post1.tags.add(tag1)
    test_post2.tags.add(tag2)

    result = djpress_tags.tags_with_counts(outer_tag="span", outer_class="tag-list")

    assert '<span class="tag-list">' in result
    assert tag1.title in result
    assert tag2.title in result
    assert "(1)" in result


@pytest.mark.django_db
def test_tags_with_counts_empty():
    """Test tags_with_counts when there are no tags with published posts."""
    result = djpress_tags.tags_with_counts()
    assert result == ""


@pytest.mark.django_db
def test_tag_title_multiple_tags(rf, tag1, tag2):
    """Test tag_title with multiple tags in context."""
    # Create a request with multiple tags in context
    request = rf.get("/")
    context = Context({"tags": [tag1.slug, tag2.slug]})

    # Test with default parameters
    result = djpress_tags.tag_title(context)
    expected = f"{tag1.title}, {tag2.title}"
    assert result == expected

    # Test with pre and post text
    result = djpress_tags.tag_title(context, pre_text="Posts tagged with: ", post_text="!")
    expected = f"Posts tagged with: {tag1.title}, {tag2.title}!"
    assert result == expected


@pytest.mark.django_db
def test_tag_title_no_tags():
    """Test tag_title when there are no tags in context."""
    context = Context({})
    result = djpress_tags.tag_title(context)
    assert result == ""


@pytest.mark.django_db
def test_post_wrapper_tag_arguments(settings):
    """Test post_wrapper_tag with various argument combinations."""
    # Test with tag and class in different order
    template_text = (
        "{% load djpress_tags %}{% post_wrap class='blog-post' tag='div' %}<p>Test content</p>{% end_post_wrap %}"
    )
    context = Context({})

    template = Template(template_text)
    expected_output = '<div class="h-entry blog-post"><p>Test content</p></div>'
    assert template.render(context) == expected_output

    # Test with double quotes for arguments
    template_text = (
        '{% load djpress_tags %}{% post_wrap class="blog-post" tag="section" %}<p>Test content</p>{% end_post_wrap %}'
    )
    template = Template(template_text)
    expected_output = '<section class="h-entry blog-post"><p>Test content</p></section>'
    assert template.render(context) == expected_output

    # Test with more than two arguments (which should be ignored)
    template_text = '{% load djpress_tags %}{% post_wrap "article" "post-class" "extra-arg" %}<p>Test content</p>{% end_post_wrap %}'
    template = Template(template_text)
    expected_output = '<article class="h-entry post-class"><p>Test content</p></article>'
    assert template.render(context) == expected_output


@pytest.mark.django_db
def test_get_pagination_range_no_page_in_context():
    """Test get_pagination_range when there's no page object in the context."""
    context = Context({})
    assert djpress_tags.get_pagination_range(context) == range(0)

    # Test with non-Page object in posts
    context = Context({"posts": "not a Page object"})
    assert djpress_tags.get_pagination_range(context) == range(0)


# Tests for new hook-based template tags


def test_djpress_header_no_plugins():
    """Test djpress_header template tag when no plugins are loaded."""
    result = djpress_tags.djpress_header()
    assert result == ""
    assert isinstance(result, str)


def test_djpress_footer_no_plugins():
    """Test djpress_footer template tag when no plugins are loaded."""
    result = djpress_tags.djpress_footer()
    assert result == ""
    assert isinstance(result, str)


def test_get_search_url(settings):
    """Test search_url template tag."""
    settings.DJPRESS_SETTINGS["SEARCH_ENABLED"] = True
    settings.DJPRESS_SETTINGS["SEARCH_PREFIX"] = "search"
    settings.APPEND_SLASH = True
    assert djpress_tags.get_search_url() == "/search/"

    settings.DJPRESS_SETTINGS["SEARCH_PREFIX"] = "find"
    assert djpress_tags.get_search_url() == "/find/"

    settings.APPEND_SLASH = False
    assert djpress_tags.get_search_url() == "/find"

    settings.DJPRESS_SETTINGS["SEARCH_ENABLED"] = False
    assert djpress_tags.get_search_url() == ""


@pytest.mark.django_db
def test_search_form(settings):
    """Test search_form template tag."""
    settings.DJPRESS_SETTINGS["SEARCH_ENABLED"] = True
    settings.DJPRESS_SETTINGS["SEARCH_PREFIX"] = "search"
    settings.APPEND_SLASH = True

    context = Context({})
    result = djpress_tags.search_form(context)
    assert '<form action="/search/" method="get">' in result
    assert '<input type="search" name="q"' in result
    assert 'placeholder="Search..."' in result
    assert '<button type="submit">Search</button>' in result

    # Test with custom parameters
    result = djpress_tags.search_form(
        context,
        placeholder="Find posts...",
        button_text="Go",
        form_class="my-form",
        input_class="search-input",
        button_class="btn",
    )
    assert 'class="my-form"' in result
    assert 'class="search-input"' in result
    assert 'class="btn"' in result
    assert 'placeholder="Find posts..."' in result
    assert ">Go</button>" in result

    # Test with existing query in context
    context = Context({"search_query": "test query"})
    result = djpress_tags.search_form(context)
    assert 'value="test query"' in result

    # Test with show_button=False
    result = djpress_tags.search_form(context, show_button=False)
    assert "<button" not in result

    # Test when search is disabled
    settings.DJPRESS_SETTINGS["SEARCH_ENABLED"] = False
    result = djpress_tags.search_form(context)
    assert result == ""


@pytest.mark.django_db
def test_search_title(settings):
    """Test search_title template tag."""
    # Test with search_query in context
    context = Context({"search_query": "django"})
    result = djpress_tags.search_title(context)
    assert result == "django"

    # Test with outer tag
    result = djpress_tags.search_title(context, outer_tag="h1")
    assert result == "<h1>django</h1>"

    # Test with outer class
    result = djpress_tags.search_title(context, outer_tag="h2", outer_class="search-heading")
    assert result == '<h2 class="search-heading">django</h2>'

    # Test with pre_text and post_text
    result = djpress_tags.search_title(context, outer_tag="h1", pre_text="Results for: ", post_text="!")
    assert result == "<h1>Results for: django!</h1>"

    # Test with no search_query in context
    context = Context({})
    result = djpress_tags.search_title(context)
    assert result == ""

    # Test with invalid outer tag
    context = Context({"search_query": "test"})
    result = djpress_tags.search_title(context, outer_tag="script")
    assert result == ""

    # Test with non-string search_query
    context = Context({"search_query": 123})
    result = djpress_tags.search_title(context)
    assert result == ""


@pytest.mark.django_db
def test_search_errors(settings):
    """Test search_errors template tag."""
    # Test with errors in context
    context = Context({"search_errors": ["Error 1", "Error 2"]})
    result = djpress_tags.search_errors(context)
    assert '<div class="search-errors">' in result
    assert '<p class="error">Error 1</p>' in result
    assert '<p class="error">Error 2</p>' in result
    assert "</div>" in result

    # Test with custom parameters
    result = djpress_tags.search_errors(
        context,
        outer_tag="section",
        outer_class="alerts",
        error_tag="span",
        error_class="alert-msg",
    )
    assert '<section class="alerts">' in result
    assert '<span class="alert-msg">Error 1</span>' in result
    assert "</section>" in result

    # Test with no errors in context
    context = Context({})
    result = djpress_tags.search_errors(context)
    assert result == ""

    # Test with empty errors list
    context = Context({"search_errors": []})
    result = djpress_tags.search_errors(context)
    assert result == ""

    # Test with non-list search_errors
    context = Context({"search_errors": "not a list"})
    result = djpress_tags.search_errors(context)
    assert result == ""

    # Test with invalid outer tag (should default to div)
    context = Context({"search_errors": ["Error"]})
    result = djpress_tags.search_errors(context, outer_tag="script")
    assert result == ""

    # Test with invalid error tag (should default to p)
    result = djpress_tags.search_errors(context, error_tag="script")
    assert result == ""

    # Test with non-string items in errors list (should skip them)
    context = Context({"search_errors": ["Valid error", 123, None, "Another error"]})
    result = djpress_tags.search_errors(context)
    assert '<p class="error">Valid error</p>' in result
    assert '<p class="error">Another error</p>' in result
    assert "123" not in result


@pytest.mark.django_db
def test_pagination_links_with_query_string(settings, test_post1, test_post2, test_long_post1):
    """Test that pagination links preserve query string parameters."""
    from django.test import RequestFactory
    from django.core.paginator import Paginator

    settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"] = 2

    # Create a request with query parameters (like search)
    factory = RequestFactory()
    request = factory.get("/search/?q=test&page=2")

    # Create paginated posts
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.DJPRESS_SETTINGS["RECENT_PUBLISHED_POSTS_COUNT"],
    )
    page = posts.get_page(2)

    # Create context with request and posts
    context = Context({"request": request, "posts": page})

    result = djpress_tags.pagination_links(context)

    # Verify query string is preserved in pagination links
    assert "q=test" in result
    assert 'href="?q=test&page=1"' in result  # first page
    assert 'href="?q=test&page=1"' in result  # previous page (from page 2)
    assert 'href="?q=test&page=' in result  # next/last pages should also have q=test
    assert "Page 2 of" in result


def test_get_theme_setting(settings):
    # settings.DJPRESS_SETTINGS["THEME"] = "default"

    # # The default theme
    # assert settings.DJPRESS_SETTINGS["THEME"] == "default"

    # Test with no theme setting
    assert djpress_tags.get_theme_setting("nonexistent_setting") is None

    # Test with no theme settings and default value
    assert djpress_tags.get_theme_setting("nonexistent_setting", "default_value") == "default_value"

    settings.DJPRESS_SETTINGS["THEME_SETTINGS"] = {"default": {"test_setting": "test_value"}}

    # Test with a theme setting
    assert djpress_tags.get_theme_setting("test_setting") == "test_value"
