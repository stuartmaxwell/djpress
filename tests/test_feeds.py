import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from djpress.conf import settings as djpress_settings
from djpress.models import Post
from djpress.url_utils import get_rss_url


@pytest.mark.django_db
def test_latest_posts_feed(client, user):
    Post.post_objects.create(title="Post 1", content="Content of post 1.", author=user, status="published")
    Post.post_objects.create(title="Post 2", content="Content of post 2.", author=user, status="published")

    url = get_rss_url()
    print(f"URL: {url}")
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/rss+xml; charset=utf-8"

    feed = response.content.decode("utf-8")
    assert f"<title>{djpress_settings.BLOG_TITLE}</title>" in feed
    assert f"<link>http://testserver/{djpress_settings.RSS_PATH}/</link>" in feed
    assert f"<description>{djpress_settings.BLOG_DESCRIPTION}</description>" in feed
    assert "<item>" in feed
    assert "<title>Post 1</title>" in feed
    assert "<description>&lt;p&gt;Content of post 1.&lt;/p&gt;</description>" in feed
    assert "<title>Post 2</title>" in feed
    assert "<description>&lt;p&gt;Content of post 2.&lt;/p&gt;</description>" in feed


@pytest.mark.django_db
def test_truncated_posts_feed(client, user):
    # Confirm the truncate tag is set according to settings_testing.py
    truncate_tag = "<!--test-more-->"
    assert djpress_settings.TRUNCATE_TAG == truncate_tag
    post_prefix = "test-posts"
    assert djpress_settings.POST_PREFIX == post_prefix

    Post.post_objects.create(
        title="Post 1",
        content=f"Content of post 1.{truncate_tag}Truncated content",
        author=user,
        status="published",
    )

    url = get_rss_url()
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/rss+xml; charset=utf-8"

    feed = response.content.decode("utf-8")
    assert f"<title>{djpress_settings.BLOG_TITLE}</title>" in feed
    assert f"<link>http://testserver/{djpress_settings.RSS_PATH}/</link>" in feed
    assert f"<description>{djpress_settings.BLOG_DESCRIPTION}</description>" in feed
    assert "<item>" in feed
    assert "<title>Post 1</title>" in feed
    assert "Truncated content" not in feed
    assert f'&lt;a href="/{post_prefix}/post-1"&gt;Read more&lt;/a&gt;&lt;/p&gt;' in feed
