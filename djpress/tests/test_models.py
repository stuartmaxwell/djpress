import pytest
from django.utils.text import slugify
from django.contrib.auth.models import User
from djpress.models import Category, Post
from django.utils import timezone
from django.http import Http404

from django.conf import settings


@pytest.mark.django_db
def test_category_model():
    category = Category.objects.create(name="Test Category", slug="test-category")
    assert category.name == "Test Category"
    assert category.slug == "test-category"
    assert str(category) == "Test Category"


@pytest.mark.django_db
def test_content_model():
    user = User.objects.create_user(username="testuser", password="testpass")
    category = Category.objects.create(name="Test Category", slug="test-category")
    content = Post.post_objects.create(
        title="Test Content",
        slug="test-content",
        content="This is a test content.",
        author=user,
        status="published",
        post_type="post",
    )
    content.categories.add(category)
    assert content.title == "Test Content"
    assert content.slug == "test-content"
    assert content.author == user
    assert content.status == "published"
    assert content.post_type == "post"
    assert content.categories.count() == 1
    assert str(content) == "Test Content"


@pytest.mark.django_db
def test_content_methods():
    user = User.objects.create_user(username="testuser", password="testpass")
    category1 = Category.objects.create(name="Category 1", slug="category-1")
    category2 = Category.objects.create(name="Category 2", slug="category-2")
    Post.post_objects.create(
        title="Test Post 1",
        slug="test-post-1",
        content="This is test post 1.",
        author=user,
        status="published",
        post_type="post",
    ).categories.add(category1)
    Post.post_objects.create(
        title="Test Post 2",
        slug="test-post-2",
        content="This is test post 2.",
        author=user,
        status="draft",
        post_type="post",
    )
    assert Post.post_objects.all().count() == 2
    assert (
        Post.post_objects.get_published_post_by_slug("test-post-1").title
        == "Test Post 1"
    )
    assert Post.post_objects.get_published_posts_by_category(category1).count() == 1
    assert Post.post_objects.get_published_posts_by_category(category2).count() == 0


@pytest.mark.django_db
def test_get_published_content_with_future_date():
    user = User.objects.create_user(username="testuser", password="testpass")
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
    assert Post.post_objects._get_published_posts().count() == 1


@pytest.mark.django_db
def test_get_published_content_ordering():
    user = User.objects.create_user(username="testuser", password="testpass")
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
def test_get_published_post_by_slug_with_future_date():
    user = User.objects.create_user(username="testuser", password="testpass")
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
def test_get_published_content_by_category_with_future_date():
    user = User.objects.create_user(username="testuser", password="testpass")
    category = Category.objects.create(name="Test Category", slug="test-category")
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
def test_post_slug_generation():
    user = User.objects.create_user(username="testuser", password="testpass")

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
def test_category_save_slug_generation():
    """Test that the slug is correctly generated when saving a Category."""
    category = Category(name="Test Category")
    category.save()

    assert category.slug == slugify("Test Category")


@pytest.mark.django_db
def test_category_save_slug_uniqueness():
    """Test that an error is raised when trying to save a Category with a duplicate slug."""
    category1 = Category(name="Test Category")
    category1.save()

    category2 = Category(name="Test Category")

    with pytest.raises(ValueError) as excinfo:
        category2.save()

    assert (
        str(excinfo.value)
        == f"A category with the slug {category2.slug} already exists."
    )


@pytest.mark.django_db
def test_category_save_invalid_name():
    """Test that an error is raised when trying to save a Category with an invalid name."""
    category = Category(name="-")

    with pytest.raises(ValueError) as excinfo:
        category.save()

    assert str(excinfo.value) == "Invalid name. Unable to generate a valid slug."


@pytest.mark.django_db
def test_markdown_rendering():
    user = User.objects.create_user(username="testuser", password="testpass")

    # Test case 1: Render markdown with basic formatting
    post1 = Post.post_objects.create(
        title="Post with Markdown",
        content="# Heading\n\nThis is a paragraph with **bold** and *italic* text.",
        author=user,
    )
    expected_html = "<h1>Heading</h1>\n<p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>"
    assert post1.content_markdown == expected_html

    # Test case 2: Render markdown with code block
    post2 = Post.post_objects.create(
        title="Post with Code Block",
        content='```python\nprint("Hello, World!")\n```',
        author=user,
    )
    expected_html = '<div class="codehilite"><pre><span></span><code><span class="nb">print</span><span class="p">(</span><span class="s2">&quot;Hello, World!&quot;</span><span class="p">)</span>\n</code></pre></div>'
    assert post2.content_markdown == expected_html

    # Test case 3: Render markdown with fenced code block
    post3 = Post.post_objects.create(
        title="Post with Fenced Code Block",
        content="```\nThis is a fenced code block.\n```",
        author=user,
    )
    expected_html = '<div class="codehilite"><pre><span></span><code>This is a fenced code block.\n</code></pre></div>'
    assert post3.content_markdown == expected_html


@pytest.mark.django_db
def test_truncated_content_markdown():
    user = User.objects.create_user(username="testuser", password="testpass")

    # Test case 1: Content with "read more" tag
    post1 = Post.post_objects.create(
        title="Post with Read More",
        content="This is the intro.\n\n<!--more-->\n\nThis is the rest of the content.",
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
def test_is_truncated_property():
    user = User.objects.create_user(username="testuser", password="testpass")

    # Test case 1: Content with truncate tag
    post1 = Post.post_objects.create(
        title="Post with Truncate Tag",
        content=f"This is the intro.{settings.TRUNCATE_TAG}This is the rest of the content.",
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
        content=f"{settings.TRUNCATE_TAG}This is the content.",
        author=user,
    )
    assert post3.is_truncated is True

    # Test case 4: Content with truncate tag at the end
    post4 = Post.post_objects.create(
        title="Post with Truncate Tag at the End",
        content=f"This is the content.{settings.TRUNCATE_TAG}",
        author=user,
    )
    assert post4.is_truncated is True


@pytest.mark.django_db
def test_category_slug_auto_generation():
    # Test case 1: Slug auto-generated when not provided
    category1 = Category.objects.create(name="Test Category")
    assert category1.slug == slugify(category1.name)

    # Test case 2: Slug not overridden when provided
    category2 = Category.objects.create(name="Another Category", slug="custom-slug")
    assert category2.slug == "custom-slug"

    # Test case 3: Slug auto-generated with special characters
    category3 = Category.objects.create(name="Special !@#$%^&*() Category")
    assert category3.slug == "special-category"

    # Test case 4: Slug auto-generated with non-ASCII characters
    category4 = Category.objects.create(name="Non-ASCII áéíóú Category")
    assert category4.slug == "non-ascii-aeiou-category"

    # Test case 5: Slug auto-generated with leading/trailing hyphens
    category5 = Category.objects.create(name="--Leading/Trailing Hyphens--")
    assert category5.slug == "leadingtrailing-hyphens"

    # Test case 6: Raise ValueError for invalid name
    with pytest.raises(ValueError) as exc_info:
        Category.objects.create(name="!@#$%^&*()")
    assert str(exc_info.value) == "Invalid name. Unable to generate a valid slug."


@pytest.mark.django_db
def test_post_permalink():
    post = Post(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=User.objects.create_user(username="testuser", password="testpass"),
        date=timezone.datetime(2024, 1, 1),
        status="published",
        post_type="post",
    )
    settings.POST_PREFIX = ""
    settings.POST_PERMALINK = ""
    assert post.permalink == "test-post"
    settings.POST_PERMALINK = settings.DAY_SLUG
    assert post.permalink == "2024/01/01/test-post"
    settings.POST_PERMALINK = settings.MONTH_SLUG
    assert post.permalink == "2024/01/test-post"
    settings.POST_PERMALINK = settings.YEAR_SLUG
    assert post.permalink == "2024/test-post"

    settings.POST_PREFIX = "posts"
    settings.POST_PERMALINK = ""
    assert post.permalink == "posts/test-post"
    settings.POST_PERMALINK = settings.DAY_SLUG
    assert post.permalink == "posts/2024/01/01/test-post"
    settings.POST_PERMALINK = settings.MONTH_SLUG
    assert post.permalink == "posts/2024/01/test-post"
    settings.POST_PERMALINK = settings.YEAR_SLUG
    assert post.permalink == "posts/2024/test-post"


@pytest.mark.django_db
def test_page_permalink():
    page = Post(
        title="Test Page",
        slug="test-page",
        content="This is a test page.",
        author=User.objects.create_user(username="testuser", password="testpass"),
        date=timezone.now(),
        status="published",
        post_type="page",
    )

    assert page.permalink == "test-page"
