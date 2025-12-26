from unittest.mock import patch
import pytest

from djpress.utils import (
    get_author_display_name,
    get_markdown_renderer,
    get_template_name,
    get_templates,
    validate_date_parts,
)
from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist


render_markdown = get_markdown_renderer()


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


def test_validate_date_parts():
    """This function validates the date parts.

    They are passed as strings, then a date object is tried to be created from them.

    If the date object is valid, then the parts are returned as a dict.
    """
    # Valid tests
    assert validate_date_parts("2025", None, None) == {"year": 2025}
    assert validate_date_parts("2025", "01", None) == {"year": 2025, "month": 1}
    assert validate_date_parts("2025", "1", None) == {"year": 2025, "month": 1}
    assert validate_date_parts("2025", "01", "01") == {"year": 2025, "month": 1, "day": 1}
    assert validate_date_parts("2025", "1", "1") == {"year": 2025, "month": 1, "day": 1}

    # Invalid tests
    with pytest.raises(ValueError):
        validate_date_parts(None, "01", None)
    with pytest.raises(ValueError):
        validate_date_parts(None, None, "01")
    with pytest.raises(ValueError):
        validate_date_parts("Foobar", None, None)
    with pytest.raises(ValueError):
        validate_date_parts("-2025", None, None)
    with pytest.raises(ValueError):
        validate_date_parts("2025", "13", "1")
    with pytest.raises(ValueError):
        validate_date_parts("2025", "1", "32")


def test_render_markdown_does_not_exist(settings):
    settings.DJPRESS_SETTINGS["MARKDOWN_RENDERER"] = "djpress.not_exists"
    from django.core.exceptions import ImproperlyConfigured

    with pytest.raises(ImproperlyConfigured):
        get_markdown_renderer()


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


def test_get_templates(settings):
    """Make sure the get_templates function returns the correct list of templates."""
    settings.DJPRESS_SETTINGS["THEME"] = "test-theme"

    # Test case - index view
    templates = get_templates("index")
    assert templates == [
        "djpress/test-theme/home.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - archive_posts view
    templates = get_templates("archive_posts")
    assert templates == [
        "djpress/test-theme/archives.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - category_posts view
    templates = get_templates("category_posts")
    assert templates == [
        "djpress/test-theme/category.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - tag_posts view
    templates = get_templates("tag_posts")
    assert templates == [
        "djpress/test-theme/tag.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - author_posts view
    templates = get_templates("author_posts")
    assert templates == [
        "djpress/test-theme/author.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - single_post view
    templates = get_templates("single_post")
    assert templates == [
        "djpress/test-theme/single.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - single_page view
    templates = get_templates("single_page")
    assert templates == [
        "djpress/test-theme/page.html",
        "djpress/test-theme/index.html",
    ]

    # Test case - non-existent view
    templates = get_templates("non_existent")
    assert templates == [
        "djpress/test-theme/index.html",
    ]


def test_get_template_name_default_theme(settings):
    """These only return index.html because that's the only template that exists in the default theme."""
    # Test case 1 - template for view exists
    template_name = get_template_name("index")
    assert template_name == "djpress/default/index.html"

    # Test case 2 - template for home view does not exist, defaults to index
    template_name = get_template_name("single_page")
    assert template_name == "djpress/default/index.html"

    # Test case 3 - template for new view does not exist, defaults to index
    template_name = get_template_name("foobar")
    assert template_name == "djpress/default/index.html"


def test_get_template_name_non_existent_theme(settings):
    # Theme is set to a non-existent theme, therefore the template will not be found
    settings.DJPRESS_SETTINGS["THEME"] = "test-theme"
    with pytest.raises(TemplateDoesNotExist, match="No template found for view 'index'"):
        get_template_name("index")


def test_get_template_name_testing_theme(settings):
    """These only return index.html because that's the only template that exists in the default theme."""
    settings.DJPRESS_SETTINGS["THEME"] = "testing"

    # Test case 1 - template for index view when category.html exists
    template_name = get_template_name("index")
    assert template_name == "djpress/testing/home.html"

    # Test case 2 - template for category_posts view when category.html exists
    template_name = get_template_name("category_posts")
    assert template_name == "djpress/testing/category.html"

    # Test case 3 - template for author_posts view when author.html exists
    template_name = get_template_name("author_posts")
    assert template_name == "djpress/testing/author.html"

    # Test case 4 - template for tag_posts view when tag.html exists
    template_name = get_template_name("tag_posts")
    assert template_name == "djpress/testing/tag.html"

    # Test case 5 - template for single_post view when single.html exists
    template_name = get_template_name("single_post")
    assert template_name == "djpress/testing/single.html"

    # Test case 6 - template for single_page view when page.html exists
    template_name = get_template_name("single_page")
    assert template_name == "djpress/testing/page.html"

    # Test case 7 - template for archive_posts view when archives.html exists
    template_name = get_template_name("archive_posts")
    assert template_name == "djpress/testing/archives.html"
