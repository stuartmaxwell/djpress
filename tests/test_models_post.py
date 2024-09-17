import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from djpress.conf import settings
from djpress.models import Category, Post


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


@pytest.mark.django_db
def test_post_model(test_post1, user, category1):
    test_post1.categories.add(category1)
    assert test_post1.title == "Test Post1"
    assert test_post1.slug == "test-post1"
    assert test_post1.author == user
    assert test_post1.status == "published"
    assert test_post1.post_type == "post"
    assert test_post1.categories.count() == 1
    assert str(test_post1) == "Test Post1"


@pytest.mark.django_db
def test_post_methods(test_post1, test_post2, category1, category2):
    test_post1.categories.add(category1)

    assert Post.post_objects.all().count() == 2
    assert (
        Post.post_objects.get_published_post_by_slug("test-post1").title == "Test Post1"
    )
    assert Post.post_objects.get_published_posts_by_category(category1).count() == 1
    assert Post.post_objects.get_published_posts_by_category(category2).count() == 0


@pytest.mark.django_db
def test_get_published_content_with_future_date(user):
    Post.post_objects.create(
        title="Past Post",
        slug="past-post",
        content="This is a past post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    )
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    )
    assert Post.post_objects.all().count() == 2
    assert Post.post_objects.get_published_posts().count() == 1


@pytest.mark.django_db
def test_get_published_content_ordering(user):
    Post.post_objects.create(
        title="Older Post",
        slug="older-post",
        content="This is an older post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=2),
    )
    Post.post_objects.create(
        title="Newer Post",
        slug="newer-post",
        content="This is a newer post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    )
    posts = Post.post_objects.all()
    assert posts[0].title == "Newer Post"
    assert posts[1].title == "Older Post"


@pytest.mark.django_db
def test_get_published_post_by_slug_with_future_date(user):
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    )
    with pytest.raises(ValueError):
        Post.post_objects.get_published_post_by_slug("future-post")


@pytest.mark.django_db
def test_get_published_content_by_category_with_future_date(user):
    category = Category.objects.create(title="Test Category", slug="test-category")
    Post.post_objects.create(
        title="Past Post",
        slug="past-post",
        content="This is a past post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() - timezone.timedelta(days=1),
    ).categories.add(category)
    Post.post_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.now() + timezone.timedelta(days=1),
    ).categories.add(category)
    assert Post.post_objects.get_published_posts_by_category(category).count() == 1


@pytest.mark.django_db
def test_post_slug_generation(user):
    # Test case 1: Slug generated from title
    post1 = Post.post_objects.create(
        title="My First Blog Post",
        content="This is the content of my first blog post.",
        author=user,
    )
    assert post1.slug == "my-first-blog-post"

    # Test case 2: Slug not overridden when provided
    post2 = Post.post_objects.create(
        title="My Second Blog Post",
        slug="custom-slug",
        content="This is the content of my second blog post.",
        author=user,
    )
    assert post2.slug == "custom-slug"

    # Test case 3: Slug generated with special characters
    post3 = Post.post_objects.create(
        title="My Third Blog Post!",
        content="This is the content of my third blog post.",
        author=user,
    )
    assert post3.slug == "my-third-blog-post"

    # Test case 4: Slug generated with non-ASCII characters
    post4 = Post.post_objects.create(
        title="My Post with 😊 Emoji",
        content="This is the content of the post with an emoji in the title.",
        author=user,
    )
    assert post4.slug == "my-post-with-emoji"

    # Test case 5: Raise error for invalid title
    with pytest.raises(ValueError) as exc_info:
        Post.post_objects.create(
            title="!@#$%^&*()",
            content="This is the content of the post with an invalid title.",
            author=user,
        )
    assert str(exc_info.value) == "Invalid title. Unable to generate a valid slug."


@pytest.mark.django_db
def test_post_markdown_rendering(user):
    assert settings.MARKDOWN_EXTENSIONS == []

    # Test case 1: Render markdown with basic formatting
    post1 = Post.post_objects.create(
        title="Post with Markdown",
        content="# Heading\n\nThis is a paragraph with **bold** and *italic* text.",
        author=user,
    )
    expected_html = "<h1>Heading</h1>\n<p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>"
    assert post1.content_markdown == expected_html


@pytest.mark.django_db
def test_post_truncated_content_markdown(user):
    # Confirm the truncate tag is set according to settings_testing.py
    truncate_tag = "<!--test-more-->"
    assert settings.TRUNCATE_TAG == truncate_tag

    # Test case 1: Content with "read more" tag
    post1 = Post.post_objects.create(
        title="Post with Read More",
        content=f"This is the intro.\n\n{truncate_tag}\n\nThis is the rest of the content.",
        author=user,
    )
    expected_truncated_content = "<p>This is the intro.</p>"
    assert post1.truncated_content_markdown == expected_truncated_content

    # Test case 2: Content without "read more" tag
    post2 = Post.post_objects.create(
        title="Post without Read More",
        content="This is the entire content.",
        author=user,
    )
    expected_truncated_content = "<p>This is the entire content.</p>"
    assert post2.truncated_content_markdown == expected_truncated_content


@pytest.mark.django_db
def test_post_is_truncated_property(user):
    # Confirm the truncate tag is set according to settings_testing.py
    truncate_tag = "<!--test-more-->"
    assert settings.TRUNCATE_TAG == truncate_tag

    # Test case 1: Content with truncate tag
    post1 = Post.post_objects.create(
        title="Post with Truncate Tag",
        content=f"This is the intro.{truncate_tag}This is the rest of the content.",
        author=user,
    )
    assert post1.is_truncated is True

    # Test case 2: Content without truncate tag
    post2 = Post.post_objects.create(
        title="Post without Truncate Tag",
        content="This is the entire content.",
        author=user,
    )
    assert post2.is_truncated is False

    # Test case 3: Content with truncate tag at the beginning
    post3 = Post.post_objects.create(
        title="Post with Truncate Tag at the Beginning",
        content=f"{truncate_tag}This is the content.",
        author=user,
    )
    assert post3.is_truncated is True

    # Test case 4: Content with truncate tag at the end
    post4 = Post.post_objects.create(
        title="Post with Truncate Tag at the End",
        content=f"This is the content.{truncate_tag}",
        author=user,
    )
    assert post4.is_truncated is True


@pytest.mark.django_db
def test_post_permalink(user):
    post = Post(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        date=timezone.datetime(2024, 1, 1),
        status="published",
        post_type="post",
    )

    # Confirm the post prefix and permalink settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"
    assert settings.POST_PERMALINK == ""

    assert post.permalink == "test-posts/test-post"
    settings.set("POST_PERMALINK", settings.DAY_SLUG)
    assert post.permalink == "test-posts/2024/01/01/test-post"
    settings.set("POST_PERMALINK", settings.MONTH_SLUG)
    assert post.permalink == "test-posts/2024/01/test-post"
    settings.set("POST_PERMALINK", settings.YEAR_SLUG)
    assert post.permalink == "test-posts/2024/test-post"

    settings.set("POST_PREFIX", "")
    settings.set("POST_PERMALINK", "")
    assert post.permalink == "test-post"
    settings.set("POST_PERMALINK", settings.DAY_SLUG)
    assert post.permalink == "2024/01/01/test-post"
    settings.set("POST_PERMALINK", settings.MONTH_SLUG)
    assert post.permalink == "2024/01/test-post"
    settings.set("POST_PERMALINK", settings.YEAR_SLUG)
    assert post.permalink == "2024/test-post"

    # Set back to defaults
    settings.set("POST_PREFIX", "test-posts")
    settings.set("POST_PERMALINK", "")


@pytest.mark.django_db
def test_get_published_posts_by_author(user):
    # Create some published posts by the test user
    post1 = Post.post_objects.create(
        title="Post 1",
        content="Content of post 1.",
        author=user,
        status="published",
    )
    post2 = Post.post_objects.create(
        title="Post 2",
        content="Content of post 2.",
        author=user,
        status="published",
    )

    # Create a draft post by the test user
    draft_post = Post.post_objects.create(
        title="Draft Post",
        content="Content of draft post.",
        author=user,
        status="draft",
    )

    # Create a future post by the test user
    future_post = Post.post_objects.create(
        title="Future Post",
        content="Content of future post.",
        author=user,
        status="published",
        date=timezone.now() + timezone.timedelta(days=1),
    )

    # Call the method being tested
    published_posts = Post.post_objects.get_published_posts_by_author(user)

    # Assert that only the published posts by the test user are returned
    assert post1 in published_posts
    assert post2 in published_posts
    assert draft_post not in published_posts
    assert future_post not in published_posts


@pytest.mark.django_db
def test_page_permalink(user):
    page = Post(
        title="Test Page",
        slug="test-page",
        content="This is a test page.",
        author=user,
        date=timezone.now(),
        status="published",
        post_type="page",
    )

    assert page.permalink == "test-page"


@pytest.mark.django_db
def test_get_recent_published_posts(user):
    """Test that the get_recent_published_posts method returns the correct posts."""
    # Confirm settings are set according to settings_testing.py
    assert settings.CACHE_RECENT_PUBLISHED_POSTS is False
    assert settings.RECENT_PUBLISHED_POSTS_COUNT == 3

    # Create some published posts
    post1 = Post.objects.create(title="Post 1", status="published", author=user)
    post2 = Post.objects.create(title="Post 2", status="published", author=user)
    post3 = Post.objects.create(title="Post 3", status="published", author=user)

    # Call the method being tested
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post3, post2, post1]

    # Test case 2: Limit the number of posts returned
    settings.set("RECENT_PUBLISHED_POSTS_COUNT", 2)

    assert settings.CACHE_RECENT_PUBLISHED_POSTS is False
    assert settings.RECENT_PUBLISHED_POSTS_COUNT == 2

    # Call the method being tested again
    recent_posts = Post.post_objects.get_recent_published_posts()

    # Assert that the correct posts are returned
    assert list(recent_posts) == [post3, post2]
    assert post1 not in recent_posts

    # Set back to defaults
    settings.set("RECENT_PUBLISHED_POSTS_COUNT", 3)
    assert settings.RECENT_PUBLISHED_POSTS_COUNT == 3


@pytest.mark.django_db
def test_get_published_post_by_path(user):
    """Test that the get_published_post_by_path method returns the correct post."""

    # Confirm settings are set according to settings_testing.py
    assert settings.POST_PREFIX == "test-posts"

    # Create a post
    post = Post.objects.create(title="Test Post", status="published", author=user)

    # Test case 1: POST_PREFIX is set and path starts with POST_PREFIX
    post_path = f"test-posts/{post.slug}"
    assert post == Post.post_objects.get_published_post_by_path(post_path)

    # Test case 2: POST_PREFIX is set but path does not start with POST_PREFIX
    post_path = f"/incorrect-path/{post.slug}"
    # Should raise a ValueError
    with pytest.raises(ValueError):
        Post.post_objects.get_published_post_by_path(post_path)

    # Test case 3: POST_PREFIX is not set but path starts with POST_PREFIX
    settings.set("POST_PREFIX", "")
    post_path = f"test-posts/non-existent-slug"
    # Should raise a ValueError
    with pytest.raises(ValueError):
        Post.post_objects.get_published_post_by_path(post_path)

    # Set back to default
    settings.set("POST_PREFIX", "test-posts")


@pytest.mark.django_db
def test_get_published_page_by_slug(test_page1):
    """Test that the get_published_page_by_slug method returns the correct page."""
    assert test_page1 == Post.page_objects.get_published_page_by_slug("test-page1")

    with pytest.raises(ValueError):
        Post.page_objects.get_published_page_by_slug("non-existent-page")


@pytest.mark.django_db
def test_get_published_pages(test_page1, test_page2):
    """Test that the get_published_pages method returns the correct pages."""
    assert list(Post.page_objects.get_published_pages()) == [test_page2, test_page1]


@pytest.mark.django_db
def test_get_published_page_by_path(test_page1: Post):
    """Test that the get_published_page_by_path method returns the correct page."""

    # Test case 1: pages can only be at the top level
    page_path = f"test-pages/{test_page1.slug}"
    with pytest.raises(expected_exception=ValueError):
        Post.page_objects.get_published_page_by_path(page_path)

    # Test case 2: pages at the top level
    page_path: str = test_page1.slug
    assert test_page1 == Post.page_objects.get_published_page_by_path(page_path)

    # Test case 3: pages doesn't exist
    page_path = "non-existent-page"
    with pytest.raises(expected_exception=ValueError):
        Post.page_objects.get_published_page_by_path(page_path)
