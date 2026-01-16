import pytest

from pytest_django.asserts import assertTemplateUsed

from collections.abc import Iterable


@pytest.mark.django_db
def test_default_theme_index_view(client, test_post1, test_long_post1, test_post2, test_post3):
    url = "/"
    response = client.get(url)

    # Test that the template is index.html
    assertTemplateUsed(response, "djpress/default/index.html")

    assert response.status_code == 200
    assert "posts" in response.context


@pytest.mark.django_db
def test_simple_theme_index_view(client, settings, test_post1, test_long_post1, test_post2, test_post3):
    settings.DJPRESS_SETTINGS["THEME"] = "simple"

    url = "/"
    response = client.get(url)

    # Test that the template is index.html
    assertTemplateUsed(response, "djpress/simple/index.html")

    assert response.status_code == 200
    assert "posts" in response.context
