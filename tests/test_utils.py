import pytest

from djpress.utils import get_author_display_name, render_markdown, get_template_name
from django.contrib.auth.models import User
from django.template.loader import TemplateDoesNotExist


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
    markdown_text = (
        '[DJ Press](https://github.com/stuartmaxwell/djpress/ "DJ Press GitHub")'
    )
    html = render_markdown(markdown_text)

    assert (
        '<a href="https://github.com/stuartmaxwell/djpress/" title="DJ Press GitHub">DJ Press</a>'
        in html
    )


def test_render_markdown_image():
    markdown_text = (
        "![DJ Press Logo](https://github.com/stuartmaxwell/djpress/logo.png)"
    )
    html = render_markdown(markdown_text)

    assert (
        '<img alt="DJ Press Logo" src="https://github.com/stuartmaxwell/djpress/logo.png">'
        in html
    )


def test_render_markdown_image_with_title():
    markdown_text = '![DJ Press Logo](https://github.com/stuartmaxwell/djpress/logo.png "DJ Press Logo")'
    html = render_markdown(markdown_text)

    assert (
        '<img alt="DJ Press Logo" src="https://github.com/stuartmaxwell/djpress/logo.png" title="DJ Press Logo">'
        in html
    )


def test_render_markdown_python_codehilite():
    markdown_text = """
```python
print("Hello, DJ Press!")
```"""
    html = render_markdown(markdown_text)

    output = (
        '<div class="codehilite">'
        "<pre>"
        "<span></span>"
        "<code>"
        '<span class="nb">print</span>'
        '<span class="p">(</span>'
        '<span class="s2">&quot;Hello, DJ Press!&quot;</span>'
        '<span class="p">)</span>'
        "\n"
        "</code>"
        "</pre>"
        "</div>"
    )

    assert output in html


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
