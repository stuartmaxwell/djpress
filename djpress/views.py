"""djpress views file."""

import logging

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.timezone import datetime

from djpress.conf import settings
from djpress.models import Category, Post

logger = logging.getLogger(__name__)


def index(
    request: HttpRequest,
) -> HttpResponse:
    """View for the index page."""
    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)
    return render(
        request,
        "djpress/index.html",
        {"_posts": page},
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
        validate_date(year, month, day)

    except ValueError:
        msg = "Invalid date"
        return HttpResponseBadRequest(msg)

    published_posts = Post.post_objects.get_published_posts()

    # Django converts strings to integers when they are passed to the filter
    if day:
        logger.debug(f"{year}/{month}/{day}")
        filtered_posts = published_posts.filter(
            date__year=year,
            date__month=month,
            date__day=day,
        )

    elif month:
        logger.debug(f"{year}/{month}")
        filtered_posts = published_posts.filter(date__year=year, date__month=month)

    elif year:
        logger.debug(f"{year}")
        filtered_posts = published_posts.filter(date__year=year)

    posts = Paginator(filtered_posts, settings.RECENT_PUBLISHED_POSTS_COUNT)
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request,
        "djpress/index.html",
        {"_posts": page},
    )


def validate_date(year: str, month: str, day: str) -> None:
    """Test the date values.

    Convert the date values to integers and test if they are valid dates.

    The regex that gets the date values checks for the following:
    - year: four digits
    - month: two digits
    - day: two digits

    Args:
        year (str): The year.
        month (str | None): The month.
        day (str | None): The day.

    Raises:
        ValueError: If the date is invalid.

    Returns:
        None
    """
    int_year: int = int(year)
    int_month: int | None = int(month) if month else None
    int_day: int | None = int(day) if day else None

    if int_month == 0 or int_day == 0:
        msg = "Invalid date"
        raise ValueError(msg)

    try:
        if int_month and int_day:
            datetime(int_year, int_month, int_day)

        elif int_month:
            datetime(int_year, int_month, 1)

        else:
            datetime(int_year, 1, 1)

    except ValueError as exc:
        msg = "Invalid date"
        raise ValueError(msg) from exc


def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View for posts by category."""
    try:
        category: Category = Category.objects.get_category_by_slug(slug=slug)
    except ValueError as exc:
        msg = "Category not found"
        raise Http404(msg) from exc

    posts = Paginator(
        Post.post_objects.get_published_posts_by_category(category),
        settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request,
        "djpress/index.html",
        {"_posts": page, "category": category},
    )


def author_posts(request: HttpRequest, author: str) -> HttpResponse:
    """View for posts by author."""
    try:
        user: User = User.objects.get(username=author)
    except User.DoesNotExist as exc:
        msg = "Author not found"
        raise Http404(msg) from exc

    posts = Paginator(
        Post.post_objects.get_published_posts_by_author(user),
        settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request,
        "djpress/index.html",
        {"_posts": page, "author": user},
    )


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
        {"_post": post},
    )
