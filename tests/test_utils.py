import pytest

from djpress.utils import get_author_display_name, get_markdown_renderer, get_template_name
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


def test_get_template_name(settings):
    # Test case 1 - template exists
    templates = [
        "djpress/not-exists.html",
        "djpress/default/index.html",
    ]
    template_name = get_template_name(templates)
    assert template_name == "djpress/default/index.html"

    # Test case 2 - template does not exist - fall back to default
    templates = [
        "djpress/not-exists.html",
        "djpress/not-exists-2.html",
    ]
    template_name = get_template_name(templates)
    assert template_name == "djpress/default/index.html"

    # Test case 3 - default template file does not exist
    settings.DJPRESS_SETTINGS["THEME"] = "not-exists"

    with pytest.raises(TemplateDoesNotExist):
        get_template_name(templates)
