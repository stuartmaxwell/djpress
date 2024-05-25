"""djpress views file."""

import logging

from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.timezone import datetime

from djpress.models import Category, Post

logger = logging.getLogger(__name__)


def index(
    request: HttpRequest,
) -> HttpResponse:
    """View for the index page."""
    posts = Post.post_objects.get_recent_published_posts()

    return render(
        request,
        "djpress/index.html",
        {"posts": posts},
    )


def archives_posts(
    request: HttpRequest,
    year: str,
    month: str = "",
    day: str = "",
) -> HttpResponse:
    """View for the date-based archives pages.

    Args:
        request (HttpRequest): The request object.
        year (str): The year.
        month (str): The month.
        day (str): The day.
    """
    try:
        test_dates(year, month, day)

    except ValueError as exc:
        msg = "Invalid date"
        raise Http404(msg) from exc

    posts = Post.post_objects._get_published_posts()  # noqa: SLF001

    # Django converts strings to integers when they are passed to the filter
    if day:
        logger.debug(f"{year}/{month}/{day}")
        posts = posts.filter(
            date__year=year,
            date__month=month,
            date__day=day,
        )

    elif month:
        logger.debug(f"{year}/{month}")
        posts = posts.filter(date__year=year, date__month=month)

    elif year:
        logger.debug(f"{year}")
        posts = posts.filter(date__year=year)

    return render(
        request,
        "djpress/index.html",
        {"posts": posts},
    )


def test_dates(year: str, month: str | None, day: str | None) -> None:
    """Test the date values.

    Convert the date values to integers and test if they are valid dates.

    Args:
        year (str): The year.
        month (str | None): The month.
        day (str | None): The day.
    """
    try:
        int_year = int(year)
        int_month = int(month) if month else None
        int_day = int(day) if day else None

        if int_month and int_day:
            datetime(int_year, int_month, int_day)

        elif int_month:
            datetime(int_year, int_month, 1)

        else:
            datetime(int_year, 1, 1)

    except ValueError as exc:
        msg = "Invalid date"
        raise ValueError(msg) from exc


def post_detail(request: HttpRequest, path: str) -> HttpResponse:
    """View for a single post.

    Args:
        request (HttpRequest): The request object.
        path (str): The path to the post.
    """
    try:
        post = Post.post_objects.get_published_post_by_path(path)
    except ValueError as exc:
        msg = "Post not found"
        raise Http404(msg) from exc

    return render(
        request,
        "djpress/index.html",
        {"post": post},
    )


def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View for posts by category."""
    try:
        category: Category = Category.objects.get_category_by_slug(slug=slug)
    except ValueError as exc:
        msg = "Category not found"
        raise Http404(msg) from exc

    posts = Post.post_objects.get_published_posts_by_category(category)

    return render(
        request,
        "djpress/index.html",
        {"posts": posts, "category": category},
    )


def author_posts(request: HttpRequest, author: str) -> HttpResponse:
    """View for posts by author."""
    try:
        user: User = User.objects.get(username=author)
    except User.DoesNotExist as exc:
        msg = "Author not found"
        raise Http404(msg) from exc

    posts = Post.post_objects.get_published_posts_by_author(user)

    return render(
        request,
        "djpress/index.html",
        {"posts": posts, "author": user},
    )
