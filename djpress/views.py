"""DJ Press views file.

There are two type of views - those that return a collection of posts, and then a view
that returns a single post.
"""

import logging

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from djpress.conf import settings
from djpress.models import Category, Post
from djpress.utils import get_template_name, validate_date

logger = logging.getLogger(__name__)


def index(
    request: HttpRequest,
) -> HttpResponse:
    """View for the index page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response.

    Context:
        posts (Page): The published posts as a Page object.
    """
    template_names: list[str] = [
        "djpress/home.html",
        "djpress/index.html",
    ]

    template: str = get_template_name(templates=template_names)

    posts = Paginator(
        Post.post_objects.get_published_posts(),
        settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page},
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

    Returns:
        HttpResponse: The response.

    Context:
        posts (Page): The published posts for the date as a Page object.
    """
    template_names: list[str] = [
        "djpress/archives.html",
        "djpress/index.html",
    ]
    template: str = get_template_name(templates=template_names)

    try:
        validate_date(year, month, day)
    except ValueError:
        msg = "Invalid date"
        return HttpResponseBadRequest(msg)

    published_posts = Post.post_objects.get_published_posts()

    # Django converts strings to integers when they are passed to the filter
    if day:
        filtered_posts = published_posts.filter(
            date__year=year,
            date__month=month,
            date__day=day,
        )

    elif month:
        filtered_posts = published_posts.filter(
            date__year=year,
            date__month=month,
        )

    elif year:
        filtered_posts = published_posts.filter(
            date__year=year,
        )

    posts = Paginator(filtered_posts, settings.RECENT_PUBLISHED_POSTS_COUNT)
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page},
    )


def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View for posts by category.

    Args:
        request (HttpRequest): The request object.
        slug (str): The category slug.

    Returns:
        HttpResponse: The response.

    Context:
        posts (Page): The published posts for the category as a Page object.
        category (Category): The category object.
    """
    template_names: list[str] = [
        "djpress/category.html",
        "djpress/index.html",
    ]
    template: str = get_template_name(templates=template_names)

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
        request=request,
        template_name=template,
        context={"posts": page, "category": category},
    )


def author_posts(request: HttpRequest, author: str) -> HttpResponse:
    """View for posts by author.

    Args:
        request (HttpRequest): The request object.
        author (str): The author username.

    Returns:
        HttpResponse: The response.

    Context:
        posts (Page): The published posts by the author as a Page object.
        author (User): The author as a User object.
    """
    template_names: list[str] = [
        "djpress/author.html",
        "djpress/index.html",
    ]
    template: str = get_template_name(templates=template_names)

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
        request=request,
        template_name=template,
        context={"posts": page, "author": user},
    )


def post_detail(request: HttpRequest, path: str) -> HttpResponse:
    """View for a single post.

    Args:
        request (HttpRequest): The request object.
        path (str): The path to the post.

    Returns:
        HttpResponse: The response.

    Context:
        post (Post): The post object.
    """
    template_names: list[str] = [
        "djpress/single.html",
        "djpress/index.html",
    ]

    try:
        page: Post = Post.page_objects.get_published_page_by_path(path)
        context: dict = {"post": page}
        # If the page is found, use the page template
        template_names.insert(0, "djpress/page.html")
    except ValueError:
        try:
            post = Post.post_objects.get_published_post_by_path(path)
            context: dict = {"post": post}
        except ValueError as exc:
            msg = "Post not found"
            raise Http404(msg) from exc

    template: str = get_template_name(templates=template_names)
    return render(
        request=request,
        context=context,
        template_name=template,
    )
