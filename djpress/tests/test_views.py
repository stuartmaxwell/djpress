import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from djpress.models import Category, Post
from django.conf import settings
from django.utils import timezone


@pytest.fixture
def user():
    user = User.objects.create_user(
        username="testuser",
        password="testpass",
    )
    return user


@pytest.fixture
def category():
    category = Category.objects.create(
        name="Test Category",
        slug="test-category",
    )
    return category


@pytest.fixture
def create_test_post(user, category):
    post = Post.post_objects.create(
        title="Test Post",
        slug="test-post",
        content="This is a test post.",
        author=user,
        status="published",
        post_type="post",
        date=timezone.datetime(2024, 1, 1),
    )
    post.categories.set([category])
    return post


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("djpress:index")
    response = client.get(url)
    print(response.content)
    assert response.status_code == 200
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_content_detail_view(client, create_test_post):
    settings.POST_PREFIX = ""
    url = reverse("djpress:post_detail", args=[create_test_post.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert "post" in response.context


@pytest.mark.django_db
def test_content_detail_not_exist(client):
    url = reverse("djpress:post_detail", args=["foobar-does-not-exist"])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_with_no_posts_view(client, category):
    url = reverse("djpress:category_posts", args=[category.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert "category" in response.context
    assert "posts" in response.context
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_category_with_posts_view(client, create_test_post, category):
    print(create_test_post.title)
    url = reverse("djpress:category_posts", args=[category.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert "category" in response.context
    assert "posts" in response.context
    assert not b"No posts available" in response.content


@pytest.mark.django_db
def test_date_archives_year(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2024"})
    settings.POST_PREFIX = ""
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert create_test_post.title.encode() in response.content


@pytest.mark.django_db
def test_date_archives_year_no_posts(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2023"})
    settings.POST_PREFIX = ""
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert not create_test_post.title.encode() in response.content
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_date_archives_month(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2024", "month": "01"})
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert create_test_post.title.encode() in response.content


@pytest.mark.django_db
def test_date_archives_month_no_posts(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2024", "month": "02"})
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert not create_test_post.title.encode() in response.content
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_date_archives_day(client, create_test_post):
    url = reverse(
        "djpress:archives_posts", kwargs={"year": "2024", "month": "01", "day": "01"}
    )
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert create_test_post.title.encode() in response.content


@pytest.mark.django_db
def test_date_archives_day_no_posts(client, create_test_post):
    url = reverse(
        "djpress:archives_posts", kwargs={"year": "2024", "month": "01", "day": "02"}
    )
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert not create_test_post.title.encode() in response.content
    assert b"No posts available" in response.content
