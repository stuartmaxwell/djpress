import pytest

from django.urls import reverse
from django.contrib.auth.models import User

from djpress.conf import settings
from djpress import url_utils
from djpress.models import Category, Post


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def category1():
    return Category.objects.create(title="Test Category1", slug="test-category1")


@pytest.fixture
def test_post1(user, category1):
    post = Post.objects.create(
        title="Test Post1",
        slug="test-post1",
        content="This is test post 1.",
        author=user,
        status="published",
        post_type="post",
    )
    return post


@pytest.mark.django_db
def test_url_author_enabled(test_post1):
    """Test the author URL."""

    # Confirm settings are set according to settings_testing.py
    assert settings.AUTHOR_ENABLED is True
    assert settings.AUTHOR_PREFIX == "test-url-author"

    author_url = url_utils.get_author_url(test_post1.author)

    assert author_url == f"/{settings.AUTHOR_PREFIX}/testuser/"


@pytest.mark.django_db
def test_url_category_enabled(category1):
    """Test the category URL."""

    # Confirm settings are set according to settings_testing.py
    assert settings.CATEGORY_ENABLED is True
    assert settings.CATEGORY_PREFIX == "test-url-category"

    category_url = url_utils.get_category_url(category1)

    assert category_url == f"/{settings.CATEGORY_PREFIX}/test-category1/"
