from collections.abc import Iterable

import pytest

from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from djpress.url_utils import get_archives_url, get_author_url, get_category_url


@pytest.mark.django_db
def test_index_view(client):
    url = reverse("djpress:index")
    response = client.get(url)
    assert response.status_code == 200
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_single_post_view(client, test_post1):
    url = test_post1.url
    response = client.get(url)
    assert response.status_code == 200
    assert "post" in response.context
    assert not isinstance(response.context["post"], Iterable)


@pytest.mark.django_db
def test_single_post_view_with_date(client, settings, test_post1):
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    dt = datetime.now()
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    url = f"/{year}/{month}/{day}/{test_post1.slug}/"
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_single_post_view_wrong_date(client, settings, test_post1):
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    url = f"/1999/01/01/{test_post1.slug}/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_single_post_not_exist(client, settings):
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    url = "/test-posts/foobar-does-not-exist/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_single_page_view(client, test_page1):
    url = test_page1.url
    response = client.get(url)
    assert response.status_code == 200
    assert "post" in response.context
    assert not isinstance(response.context["post"], Iterable)


@pytest.mark.django_db
def test_author_with_no_posts_view(client, user):
    url = get_author_url(user)
    print(url)
    response = client.get(url)
    assert response.status_code == 200
    assert "author" in response.context
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_author_with_posts_view(client, test_post1):
    url = get_author_url(test_post1.author)
    response = client.get(url)
    assert response.status_code == 200
    assert "author" in response.context
    assert b"No posts available" not in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_author_with_invalid_author(client, settings):
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"
    url = "/test-url-author/non-existent-author/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_author_with_author_enabled_false(client, settings):
    """This will try to get a page from the database that does not exist."""
    assert settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] == True
    settings.DJPRESS_SETTINGS["AUTHOR_ENABLED"] = False
    url = "/test-url-author/non-existent-author/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_with_no_posts_view(client, category1):
    url = get_category_url(category1)
    response = client.get(url)
    assert response.status_code == 200
    assert "category" in response.context
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_category_with_posts_view(client, category1, test_post1):
    test_post1.categories.add(category1)
    url = get_category_url(category1)
    response = client.get(url)
    assert response.status_code == 200
    assert "category" in response.context
    assert b"No posts available" not in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_category_with_invalid_category(client, settings):
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"
    url = "/test-url-category/non-existent-category/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_with_category_enabled_false(client, settings):
    """This will try to get a page from the database that does not exist."""
    assert settings.DJPRESS_SETTINGS["CATEGORY_ENABLED"] == True
    settings.DJPRESS_SETTINGS["CATEGORY_ENABLED"] = False
    url = "/test-url-category/non-existent-category/"
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_date_archives_year(client, test_post1):
    url = get_archives_url(test_post1.date.year)
    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_date_archives_year_invalid_year(client, settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    url = "/test-url-archives/0000/"
    response = client.get(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_date_archives_year_no_posts(client, test_post1):
    url = get_archives_url(test_post1.date.year - 1)
    response = client.get(url)
    assert response.status_code == 200
    assert not test_post1.title.encode() in response.content
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_date_archives_month(client, test_post1):
    url = get_archives_url(test_post1.date.year, test_post1.date.month)
    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_date_archives_month_invalid_month(client, settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    response1 = client.get("/test-url-archives/2024/00/")
    assert response1.status_code == 400
    response2 = client.get("/test-url-archives/2024/13/")
    assert response2.status_code == 400


@pytest.mark.django_db
def test_date_archives_month_no_posts(client, test_post1):
    url = get_archives_url(test_post1.date.year - 1, test_post1.date.month)
    response = client.get(url)
    assert response.status_code == 200
    assert not test_post1.title.encode() in response.content
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_date_archives_day(client, test_post1):
    url = get_archives_url(test_post1.date.year, test_post1.date.month, test_post1.date.day)
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert test_post1.title.encode() in response.content


@pytest.mark.django_db
def test_date_archives_day_invalid_day(client, settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    response1 = client.get("/test-url-archives/2024/01/00/")
    assert response1.status_code == 400
    response2 = client.get("/test-url-archives/2024/01/32/")
    assert response2.status_code == 400


@pytest.mark.django_db
def test_date_archives_day_no_posts(client, test_post1):
    url = get_archives_url(test_post1.date.year - 1, test_post1.date.month, test_post1.date.day)
    response = client.get(url)
    assert response.status_code == 200
    assert not test_post1.title.encode() in response.content
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)
