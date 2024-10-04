import pytest
from copy import deepcopy
from example.config import settings_testing
from djpress.models import Category, Post
from django.contrib.auth.models import User

# Take a static snapshot of DJPRESS_SETTINGS from settings_test.py
CLEAN_DJPRESS_SETTINGS = deepcopy(settings_testing.DJPRESS_SETTINGS)


@pytest.fixture(autouse=True)
def reset_djpress_settings(settings):
    """Reset DJPress settings for each test based on a clean, static state."""

    # Reset to the known clean state
    settings.DJPRESS_SETTINGS.clear()
    settings.DJPRESS_SETTINGS.update(CLEAN_DJPRESS_SETTINGS)

    yield  # Run the test

    # Ensure everything is cleared again after the test (extra cleanup)
    settings.DJPRESS_SETTINGS.clear()
    settings.DJPRESS_SETTINGS.update(CLEAN_DJPRESS_SETTINGS)


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def category1():
    return Category.objects.create(title="Test Category1", slug="test-category1")


@pytest.fixture
def category2():
    return Category.objects.create(title="Test Category2", slug="test-category2")


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


@pytest.fixture
def test_post2(user, category1):
    post = Post.objects.create(
        title="Test Post2",
        slug="test-post2",
        content="This is test post 2.",
        author=user,
        status="published",
        post_type="post",
    )

    return post


@pytest.fixture
def test_page1(user):
    return Post.objects.create(
        title="Test Page1",
        slug="test-page1",
        content="This is test page 1.",
        author=user,
        status="published",
        post_type="page",
    )


@pytest.fixture
def test_page2(user):
    return Post.objects.create(
        title="Test Page2",
        slug="test-page2",
        content="This is test page 2.",
        author=user,
        status="published",
        post_type="page",
    )
