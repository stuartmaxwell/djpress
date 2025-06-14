import os
import pytest
from copy import deepcopy
from io import BytesIO

from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from djpress.url_converters import SlugPathConverter
from djpress.models import Category, Media, Post, Tag
from djpress.plugins import DJPressPlugin
from djpress.plugins.plugin_registry import PluginRegistry
from djpress.plugins.hook_registry import POST_RENDER_CONTENT, PRE_RENDER_CONTENT, DJ_HEADER, DJ_FOOTER, POST_SAVE_POST

from example.config import settings_testing

# Take a static snapshot of DJPRESS_SETTINGS from settings_test.py
CLEAN_DJPRESS_SETTINGS = deepcopy(settings_testing.DJPRESS_SETTINGS)


def pytest_configure(config):
    test_tz = os.environ.get("TEST_TIME_ZONE")
    if test_tz:
        settings.TIME_ZONE = test_tz


def pytest_report_header(config):
    current_tz = settings.TIME_ZONE
    return f"Django TIME_ZONE for tests: {current_tz}"


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
def converter():
    return SlugPathConverter()


@pytest.fixture
def mock_timezone_now(monkeypatch):
    current_time = timezone.now()
    monkeypatch.setattr(timezone, "now", lambda: current_time)
    return current_time


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        password="testpass",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def category1():
    return Category.objects.create(title="Test Category1", slug="test-category1")


@pytest.fixture
def category2():
    return Category.objects.create(title="Test Category2", slug="test-category2")


@pytest.fixture
def category3():
    category = Category.objects.create(title="Development", slug="dev")
    return category


@pytest.fixture
def tag1():
    return Tag.objects.create(title="Test Tag1", slug="test-tag1")


@pytest.fixture
def tag2():
    return Tag.objects.create(title="Test Tag2", slug="test-tag2")


@pytest.fixture
def tag3():
    return Tag.objects.create(title="Test Tag3", slug="test-tag3")


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
    post.categories.set([category1])

    return post


@pytest.fixture
def test_post2(user, category2):
    post = Post.objects.create(
        title="Test Post2",
        slug="test-post2",
        content="This is test post 2.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category2])
    return post


@pytest.fixture
def test_post3(user, category1):
    post = Post.objects.create(
        title="Test Post3",
        slug="test-post3",
        content="This is test post 3.",
        author=user,
        status="published",
        post_type="post",
    )

    return post


@pytest.fixture
def test_long_post1(user, settings, category1):
    truncate_tag = settings.DJPRESS_SETTINGS["TRUNCATE_TAG"]
    post = Post.post_objects.create(
        title="Test Long Post1",
        slug="test-long-post1",
        content=f"This is the truncated content.\n\n{truncate_tag}\n\nThis is the rest of the post.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category1])
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


@pytest.fixture
def test_page3(user):
    return Post.objects.create(
        title="Test Page3",
        slug="test-page3",
        content="This is test page 3.",
        author=user,
        status="published",
        post_type="page",
    )


@pytest.fixture
def test_page4(user):
    return Post.objects.create(
        title="Test Page4",
        slug="test-page4",
        content="This is test page 4.",
        author=user,
        status="published",
        post_type="page",
    )


@pytest.fixture
def test_page5(user):
    return Post.objects.create(
        title="Test Page5",
        slug="test-page5",
        content="This is test page 5.",
        author=user,
        status="published",
        post_type="page",
    )


@pytest.fixture
def registry():
    """Provides a fresh, empty PluginRegistry instance for each test."""
    registry = PluginRegistry()
    # Reset before test
    registry.hooks = {}
    registry.plugins = []
    registry._loaded = False

    yield registry

    # Reset after test
    registry.hooks = {}
    registry.plugins = []
    registry._loaded = False


@pytest.fixture
def bad_plugin_registry(registry):
    """Create a registry with a plugin that uses an unknown hook."""

    class BadPlugin(DJPressPlugin):
        name = "bad_plugin"

        def setup(self, registry):
            registry.register_hook("foobar", lambda x: x)

    # Manually create and setup the plugin
    plugin = BadPlugin({})
    plugin.setup(registry)

    return registry


@pytest.fixture
def content_transformer_plugin():
    class ContentTransformerPlugin(DJPressPlugin):
        """A simple plugin that modifies content."""

        name = "content_modifier"
        hooks = [
            (PRE_RENDER_CONTENT, "add_prefix"),
            (POST_RENDER_CONTENT, "add_suffix"),
        ]

        def add_prefix(self, content: str) -> str:
            return f"prefixed_{content}"

        def add_suffix(self, content: str) -> str:
            return f"{content}_suffixed"

    return ContentTransformerPlugin({})


@pytest.fixture
def content_provider_plugin():
    class ContentProviderPlugin(DJPressPlugin):
        """A simple plugin that provides content."""

        name = "content_provider"
        hooks = [
            (DJ_HEADER, "add_header"),
            (DJ_FOOTER, "add_suffix"),
        ]

        def add_header(self) -> str:
            return "header"

        def add_suffix(self) -> str:
            return "footer"

    return ContentProviderPlugin({})


@pytest.fixture
def object_provider_plugin():
    class ObjectProviderPlugin(DJPressPlugin):
        """A simple plugin that provides an object."""

        name = "object_provider"
        hooks = [
            (POST_SAVE_POST, "do_nothing"),
        ]

        def do_nothing(self, object):
            return None

    return ObjectProviderPlugin({})


@pytest.fixture
def superuser() -> User:
    return User.objects.create_superuser(username="admin", password="adminpass")  # type: ignore


@pytest.fixture
def test_media_file_1(user):
    """Fixture to create a test media file."""
    file_content = b"Test file content"
    test_file = SimpleUploadedFile(
        name="test_file.txt",
        content=file_content,
        content_type="text/plain",
    )
    # Create test media objects
    media = Media.objects.create(
        title="Test Document",
        file=test_file,
        media_type="document",
        description="A test document",
        uploaded_by=user,
    )

    yield media

    # Clean up the file after the test
    if media.file and os.path.isfile(media.file.path):
        os.unlink(media.file.path)
    media.delete()


@pytest.fixture
def test_media_image_1(user):
    """Fixture to create a test media image."""
    image_content = BytesIO()
    image_content.write(b"Test image content")
    image_content.seek(0)
    test_image = SimpleUploadedFile(
        name="test_image.jpg",
        content=image_content.read(),
        content_type="image/jpeg",
    )

    media = Media.objects.create(
        title="Test Image",
        file=test_image,
        media_type="image",
        alt_text="Test image alt text",
        description="A test image",
        uploaded_by=user,
    )

    yield media

    # Clean up the file after the test
    if media.file and os.path.isfile(media.file.path):
        os.unlink(media.file.path)
    media.delete()
