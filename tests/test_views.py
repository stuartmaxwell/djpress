from collections.abc import Iterable

import pytest

from datetime import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from djpress.models import Post
from djpress.url_utils import get_archives_url, get_author_url, get_category_url, get_tag_url


@pytest.mark.django_db
def test_index_view_no_posts(client):
    url = reverse("djpress:index")
    response = client.get(url)
    assert response.status_code == 200
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_index_view_multiple_posts(client, test_post1, test_post2, test_post3):
    url = "/"
    response = client.get(url)
    assert response.status_code == 200
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)
    assert (
        f'<h1 class="p-name"><a href="/test-posts/test-post1/" title="Test Post1" class="u-url">Test Post1</a></h1>'
        in response.content.decode()
    )
    assert f'<article class="h-entry">' in response.content.decode()


@pytest.mark.django_db
def test_single_post_view(client, test_post1):
    url = test_post1.url
    response = client.get(url)
    assert response.status_code == 200
    assert "post" in response.context
    assert not isinstance(response.context["post"], Iterable)
    assert f'<h1 class="p-name">{test_post1.title}</h1>' in response.content.decode()


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
def test_tag_with_no_posts_view(client, tag1):
    url = get_tag_url(tag1)
    print(url)
    response = client.get(url)
    assert response.status_code == 200
    assert "tags" in response.context
    assert b"No posts available" in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_tag_with_posts_view(client, test_post1, tag1):
    test_post1.tags.add(tag1)
    url = get_tag_url(tag1)
    print(url)
    response = client.get(url)
    assert response.status_code == 200
    assert "tags" in response.context
    assert b"No posts available" not in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_tag_with_tag_enabled_false(client, settings, tag1):
    """This will try to get a page when TAG_ENABLED is false."""
    assert settings.DJPRESS_SETTINGS["TAG_ENABLED"] == True

    url = "/test-url-tag/" + tag1.slug + "/"

    settings.DJPRESS_SETTINGS["TAG_ENABLED"] = False
    response = client.get(url)
    assert response.status_code == 404

    settings.DJPRESS_SETTINGS["TAG_ENABLED"] = True
    response = client.get(url)
    assert response.status_code == 200

    settings.DJPRESS_SETTINGS["TAG_PREFIX"] = ""
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_date_archives_year(client, settings, test_post1):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    url = get_archives_url(test_post1.date.year)
    assert url == f"/test-url-archives/{test_post1.date.year}/"
    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)
    assert "Test Post1" in response.content.decode()

    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    url = get_archives_url(test_post1.date.year)
    assert url == f"/{test_post1.date.year}/"

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
def test_date_archives_month(client, settings, test_post1):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    url = get_archives_url(test_post1.date.year, test_post1.date.month)
    assert url == f"/test-url-archives/{test_post1.date.year}/{test_post1.date.month:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)

    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    url = get_archives_url(test_post1.date.year, test_post1.date.month)
    assert url == f"/{test_post1.date.year}/{test_post1.date.month:02}/"

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
def test_date_archives_day(client, settings, test_post1):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    url = get_archives_url(test_post1.date.year, test_post1.date.month, test_post1.date.day)
    assert url == f"/test-url-archives/{test_post1.date.year}/{test_post1.date.month:02}/{test_post1.date.day:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)

    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    url = get_archives_url(test_post1.date.year, test_post1.date.month, test_post1.date.day)
    assert url == f"/{test_post1.date.year}/{test_post1.date.month:02}/{test_post1.date.day:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)

    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    url = get_archives_url(test_post1.date.year, test_post1.date.month, test_post1.date.day)
    assert url == f"/{test_post1.date.year}/{test_post1.date.month:02}/{test_post1.date.day:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_conflict_day_archives_and_single_post(client, settings, test_post1):
    """Change the POST_PREFIX to match the same format as the day archives.

    For example, with POST_PREFIX = "{{ year }}/{{ month }}", either of the following two URLs could be valid posts:

    - /2024/01/31/ - This could be a day archive, or a post with the slug "31" in the year 2024 and month 01.
    - /2024/01/test-post1/

    The first URL will try to get a post and if that doesn't exist, it will try to get a day archive, but only if the
    POST_PREFIX matches the day archive format.
    """
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}"
    url = get_archives_url(test_post1.date.year, test_post1.date.month, test_post1.date.day)
    assert url == f"/{test_post1.date.year}/{test_post1.date.month:02}/{test_post1.date.day:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_conflict_month_archives_and_single_post(client, settings, test_post1):
    """Similar concept to test_conflict_day_archives_and_single_post.

    With POST_PREFIX = "{{ year }}", either of the following two URLs could be valid posts:

    - /2024/12/ - This could be a month archive, or a post with the slug "12" in the year 2024.
    - /2024/test-post1/
    """
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}"
    url = get_archives_url(test_post1.date.year, test_post1.date.month)
    assert url == f"/{test_post1.date.year}/{test_post1.date.month:02}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)


@pytest.mark.django_db
def test_conflict_year_archives_and_single_post(client, settings, test_post1):
    """Similar concept to test_conflict_day_archives_and_single_post and test_conflict_month_archives_and_single_post.

    With POST_PREFIX = "", either of the following two URLs could be valid posts:

    - /2024/ - This could be a year archive, or a post with the slug "2024".
    - /test-post1/
    """
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = ""
    url = get_archives_url(test_post1.date.year)
    assert url == f"/{test_post1.date.year}/"

    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "posts" in response.context
    assert isinstance(response.context["posts"], Iterable)

    # If the post slug is 2024, then the post will be returned.
    test_post1.slug = str(test_post1.date.year)
    test_post1.save()
    response = client.get(url)
    assert response.status_code == 200
    assert test_post1.title.encode() in response.content
    assert "post" in response.context
    assert isinstance(response.context["post"], Post)


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
