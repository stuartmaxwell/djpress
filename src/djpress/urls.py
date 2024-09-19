"""djpress URLs file."""

from django.urls import path, re_path

from djpress.conf import settings
from djpress.feeds import PostFeed
from djpress.views import (
    archives_posts,
    author_posts,
    category_posts,
    index,
    post_detail,
)


def regex_path() -> str:
    """Generate the regex path for the post detail view.

    The following regex is used to match the path. It is used to match the
    any path that contains letters, numbers, underscores, hyphens, and slashes.
    """
    regex = r"^(?P<path>[0-9A-Za-z/_-]*)$"
    if settings.APPEND_SLASH:
        return regex[:-1] + "/$"
    return regex


def regex_archives() -> str:
    """Generate the regex path for the archives view.

    The following regex is used to match the archives path. It is used to match
    the following patterns:
    - 2024
    - 2024/01
    - 2024/01/01
    There will always be a year.
    If there is a month, there will always be a year.
    If there is a day, there will always be a month and a year.
    """
    regex = r"(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"
    if settings.APPEND_SLASH:
        return regex[:-1] + "/$"
    return regex


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

if settings.AUTHOR_PATH_ENABLED:
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
            settings.ARCHIVES_PATH + "/" + regex_archives(),
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
        regex_path(),
        post_detail,
        name="post_detail",
    ),
]
