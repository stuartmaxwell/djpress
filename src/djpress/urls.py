"""djpress URLs file."""

from django.urls import path, re_path

from djpress.conf import settings
from djpress.feeds import PostFeed
from djpress.url_utils import post_prefix_to_regex, regex_archives, regex_page
from djpress.views import archive_posts, author_posts, category_posts, index, single_page, single_post

app_name = "djpress"

urlpatterns = []

# 1. Resolve special URLs first
if settings.RSS_ENABLED and settings.RSS_PATH:
    urlpatterns += [
        path(
            f"{settings.RSS_PATH}/",
            PostFeed(),
            name="rss_feed",
        ),
    ]

# 2. Resolve the single post URLs
urlpatterns += [
    # Single post - using the pre-calculated regex
    re_path(post_prefix_to_regex(settings.POST_PREFIX), single_post, name="single_post"),
]

# 3. Resolve the archives URLs
if settings.ARCHIVE_ENABLED:
    urlpatterns += [
        re_path(
            regex_archives(),
            archive_posts,
            name="archive_posts",
        ),
    ]

# 4. Resolve the category URLs
if settings.CATEGORY_ENABLED and settings.CATEGORY_PREFIX:
    urlpatterns += [
        path(
            f"{settings.CATEGORY_PREFIX}/<slug:slug>/",
            category_posts,
            name="category_posts",
        ),
    ]

# 5. Resolve the author URLs
if settings.AUTHOR_ENABLED and settings.AUTHOR_PREFIX:
    urlpatterns += [
        path(
            f"{settings.AUTHOR_PREFIX}/<str:author>/",
            author_posts,
            name="author_posts",
        ),
    ]

# 6. Resolve the page URLs
urlpatterns += [
    re_path(
        regex_page(),
        single_page,
        name="single_page",
    ),
]

# 7. Resolve the index URL
urlpatterns += [
    path("", index, name="index"),
]
