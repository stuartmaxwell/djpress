import pytest
from django.contrib.auth.models import User
from djpress.models import Post


@pytest.mark.django_db
def test_get_published_posts_by_author():
    # Create a test user
    user = User.objects.create_user(username="testuser", password="testpass")

    # Create some published posts by the test user
    post1 = Post.post_objects.create(
        title="Post 1", content="Content of post 1.", author=user, status="published"
    )
    post2 = Post.post_objects.create(
        title="Post 2", content="Content of post 2.", author=user, status="published"
    )

    # Create a draft post by the test user
    draft_post = Post.post_objects.create(
        title="Draft Post",
        content="Content of draft post.",
        author=user,
        status="draft",
    )

    # Call the method being tested
    published_posts = Post.post_objects.get_published_posts_by_author(user)

    # Assert that only the published posts by the test user are returned
    assert post1 in published_posts
    assert post2 in published_posts
    assert draft_post not in published_posts
