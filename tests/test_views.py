import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from djpress.models import Category, Post
from djpress.views import validate_date


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
        date=timezone.make_aware(timezone.datetime(2024, 1, 1)),
    )
    post.categories.set([category])
    return post


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("djpress:index")
    response = client.get(url)
    assert response.status_code == 200
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_post_detail_view(client, create_test_post):
    url = reverse("djpress:post_detail", args=[create_test_post.permalink])
    response = client.get(url)
    assert response.status_code == 200
    assert "post" in response.context


@pytest.mark.django_db
def test_post_detail_not_exist(client):
    url = reverse("djpress:post_detail", args=["foobar-does-not-exist"])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_author_with_no_posts_view(client, user):
    url = reverse("djpress:author_posts", args=[user.username])
    response = client.get(url)
    assert response.status_code == 200
    assert "author" in response.context
    assert "posts" in response.context
    assert b"No posts available" in response.content


@pytest.mark.django_db
def test_author_with_posts_view(client, create_test_post):
    url = reverse("djpress:author_posts", args=[create_test_post.author.username])
    response = client.get(url)
    assert response.status_code == 200
    assert "author" in response.context
    assert "posts" in response.context
    assert not b"No posts available" in response.content


@pytest.mark.django_db
def test_author_with_invalid_author(client):
    url = reverse("djpress:author_posts", args=["non-existent-author"])
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
    url = reverse("djpress:category_posts", args=[category.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert "category" in response.context
    assert "posts" in response.context
    assert not b"No posts available" in response.content


@pytest.mark.django_db
def test_category_with_invalid_category(client):
    url = reverse("djpress:category_posts", args=["non-existent-category"])
    response = client.get(url)
    assert response.status_code == 404


def test_validate_date():
    # Test 1 - invalid year
    year = "0000"
    with pytest.raises(ValueError):
        validate_date(year, "", "")

    # Test 2 - invalid months
    month = "00"
    with pytest.raises(ValueError):
        validate_date("2024", month, "")
    month = "13"
    with pytest.raises(ValueError):
        validate_date("2024", month, "")

    # Test 3 - invalid days
    day = "00"
    with pytest.raises(ValueError):
        validate_date("2024", "1", day)
    day = "32"
    with pytest.raises(ValueError):
        validate_date("2024", "1", day)


@pytest.mark.django_db
def test_date_archives_year(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2024"})
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert create_test_post.title.encode() in response.content


@pytest.mark.django_db
def test_date_archives_year_invalid_year(client):
    response = client.get("/archives/0000/")
    assert response.status_code == 400


@pytest.mark.django_db
def test_date_archives_year_no_posts(client, create_test_post):
    url = reverse("djpress:archives_posts", kwargs={"year": "2023"})
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
def test_date_archives_month_invalid_month(client):
    response1 = client.get("/archives/2024/00/")
    assert response1.status_code == 400
    response2 = client.get("/archives/2024/13/")
    assert response2.status_code == 400


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
def test_date_archives_day_invalid_day(client):
    response1 = client.get("/archives/2024/01/00/")
    assert response1.status_code == 400
    response2 = client.get("/archives/2024/01/32/")
    assert response2.status_code == 400


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
