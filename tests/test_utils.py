import pytest

from djpress.utils import get_author_display_name, render_markdown, get_template_name
from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist

from djpress.utils import extract_parts_from_path
from djpress.conf import settings
from djpress.exceptions import SlugNotFoundError


# create a parameterized fixture for a test user with first name, last name, and username
@pytest.fixture(
    params=[
        ("Sam", "Brown", "sambrown"),
        ("Sam", "", "sambrown"),
        ("", "Brown", "sambrown"),
        ("", "", "sambrown"),
    ]
)
def test_user(request):
    first_name, last_name, username = request.param
    user = User.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password="testpass",
    )

    return user


# Test the get_author_display_name function with the test_user fixture
@pytest.mark.django_db
def test_get_author_display_name(test_user):
    display_name = get_author_display_name(test_user)
    first_name = test_user.first_name
    last_name = test_user.last_name
    user_name = test_user.username

    # Assert that the display name is the first name and last name separated by a space
    if first_name and last_name:
        assert display_name == f"{first_name} {last_name}"

    if first_name and not last_name:
        assert display_name == first_name

    if not first_name and last_name:
        assert display_name == user_name

    if not first_name and not last_name:
        assert display_name == user_name


def test_render_markdown_basic():
    markdown_text = "# Heading\n\nThis is some **bold** text. And this is *italic*.\n\nAnd a paragraph."
    html = render_markdown(markdown_text)

    assert "<h1>Heading</h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html
    assert "<p>And a paragraph.</p>" in html


def test_render_markdown_link():
    markdown_text = "[DJ Press](https://github.com/stuartmaxwell/djpress/)"
    html = render_markdown(markdown_text)

    assert '<a href="https://github.com/stuartmaxwell/djpress/">DJ Press</a>' in html


def test_render_markdown_link_with_title():
    markdown_text = '[DJ Press](https://github.com/stuartmaxwell/djpress/ "DJ Press GitHub")'
    html = render_markdown(markdown_text)

    assert '<a href="https://github.com/stuartmaxwell/djpress/" title="DJ Press GitHub">DJ Press</a>' in html


def test_render_markdown_image():
    markdown_text = "![DJ Press Logo](https://github.com/stuartmaxwell/djpress/logo.png)"
    html = render_markdown(markdown_text)

    assert '<img alt="DJ Press Logo" src="https://github.com/stuartmaxwell/djpress/logo.png">' in html


def test_render_markdown_image_with_title():
    markdown_text = '![DJ Press Logo](https://github.com/stuartmaxwell/djpress/logo.png "DJ Press Logo")'
    html = render_markdown(markdown_text)

    assert (
        '<img alt="DJ Press Logo" src="https://github.com/stuartmaxwell/djpress/logo.png" title="DJ Press Logo">'
        in html
    )


def test_get_template_name():
    # Test case 1 - template exists
    templates = [
        "djpress/not-exists.html",
        "djpress/index.html",
    ]
    template_name = get_template_name(templates)
    assert template_name == "djpress/index.html"

    # Test case 2 - template does not exist
    templates = [
        "djpress/not-exists.html",
        "djpress/not-exists-2.html",
    ]
    with pytest.raises(TemplateDoesNotExist):
        get_template_name(templates)


def test_extract_slug_from_path_prefix_testing():
    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""

    # Test case 1 - path with slug
    path = "test-posts/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"

    # Test case 2 - post prefix missing
    path = "/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 3 - post prefix incorrect
    path = "foobar/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 4 - path with slug and post permalink
    path = "test-posts/2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "2024/01/01/slug"

    # Test case 5 - post permalink but no slug
    path = "test-posts/"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Remove the post prefix
    settings.POST_PREFIX = ""
    assert settings.POST_PREFIX == ""

    # Test case 5 - just a slug
    path = "slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"

    # Test case 6 - slug with post prefix
    path = "test-posts/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "test-posts/slug"

    # Test case 7 - path with slug and post permalink
    path = "2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "2024/01/01/slug"

    # Set the post prefix back to "test-posts"
    settings.POST_PREFIX = "test-posts"

    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""


def test_extract_slug_from_path_permalink_testing():
    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""

    # Test case 1 - slug with prefix and no permalink
    path = "test-posts/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"

    # Set the post permalink to "%Y/%m/%d"
    settings.POST_PERMALINK = "%Y/%m/%d"
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == "%Y/%m/%d"

    # Test case 2 - slug with prefix and permalink
    path = "test-posts/2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"

    # Test case 3 - slug with extra date parts
    path = "test-posts/2024/01/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "01/slug"

    # Test case 4 - slugn with missing date parts
    path = "test-posts/2024/01/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 5 - missing slug
    path = "test-posts/2024/01/01"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Set the post permalink to "%Y/%m"
    settings.POST_PERMALINK = "%Y/%m"
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == "%Y/%m"

    # Test case 6 - slug with prefix and permalink
    path = "test-posts/2024/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"

    # Test case 7 - slug with extra date parts
    path = "test-posts/2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "01/slug"

    # Test case 8 - slug with missing date parts
    path = "test-posts/2024/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 9 - missing slug
    path = "test-posts/2024/01"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Set the post permalink to default
    settings.POST_PERMALINK = ""

    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""


def test_extract_date_parts_from_path():
    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""

    # Set the post permalink to "%Y/%m/%d"
    settings.POST_PERMALINK = "%Y/%m/%d"
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == "%Y/%m/%d"

    # Test case 1 - slug with prefix and permalink
    path = "test-posts/2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"
    assert path_parts.year == 2024
    assert path_parts.month == 1
    assert path_parts.day == 1

    # Test case 2 - slug with extra date parts
    path = "test-posts/2024/01/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "01/slug"
    assert path_parts.year == 2024
    assert path_parts.month == 1
    assert path_parts.day == 1

    # Test case 3 - slug with missing date parts
    path = "test-posts/2024/01/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 4 - missing slug
    path = "test-posts/2024/01/01"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Set the post permalink to "%Y/%m"
    settings.POST_PERMALINK = "%Y/%m"
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == "%Y/%m"

    # Test case 5 - slug with prefix and permalink
    path = "test-posts/2024/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "slug"
    assert path_parts.year == 2024
    assert path_parts.month == 1
    assert path_parts.day is None

    # Test case 6 - slug with extra date parts
    path = "test-posts/2024/01/01/slug"
    path_parts = extract_parts_from_path(path)
    assert path_parts.slug == "01/slug"
    assert path_parts.year == 2024
    assert path_parts.month == 1
    assert path_parts.day is None

    # Test case 7 - slug with missing date parts
    path = "test-posts/2024/slug"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Test case 8 - missing slug
    path = "test-posts/2024/01"
    # Should raise an exception
    with pytest.raises(SlugNotFoundError):
        path_parts = extract_parts_from_path(path)

    # Set the post permalink to default
    settings.POST_PERMALINK = ""

    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""
