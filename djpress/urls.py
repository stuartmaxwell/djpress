"""djpress URLs file."""

from django.conf import settings
from django.urls import path, re_path

from djpress.feeds import PostFeed
from djpress.views import (
    archives_posts,
    author_posts,
    category_posts,
    index,
    post_detail,
)

regex_path = r"^(?P<path>[0-9A-Za-z/_-]*)$"
regex_archives = r"(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"

if settings.APPEND_SLASH:
    regex_path = regex_path[:-1] + "/$"
    regex_archives = regex_archives[:-1] + "/$"

app_name = "djpress"

urlpatterns = []

if settings.CATEGORY_PATH_ENABLED and settings.CATEGORY_PATH:
    urlpatterns += [
        path(
            f"{settings.CATEGORY_PATH}/<slug:slug>/",
            category_posts,
            name="category_posts",
        ),
    ]

if settings.AUTHOR_PATH_ENABLED and settings.AUTHOR_PATH:
    urlpatterns += [
        path(
            f"{settings.AUTHOR_PATH}/<str:author>/",
            author_posts,
            name="author_posts",
        ),
    ]

if settings.ARCHIVES_PATH_ENABLED and settings.ARCHIVES_PATH:
    urlpatterns += [
        re_path(
            settings.ARCHIVES_PATH + "/" + regex_archives,
            archives_posts,
            name="archives_posts",
        ),
    ]

if settings.RSS_ENABLED and settings.RSS_PATH:
    urlpatterns += [
        path(
            f"{settings.RSS_PATH}/",
            PostFeed(),
            name="rss_feed",
        ),
    ]

urlpatterns += [
    path("", index, name="index"),
    re_path(
        regex_path,
        post_detail,
        name="post_detail",
    ),
]
