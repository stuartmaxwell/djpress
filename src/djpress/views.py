"""DJ Press views file.

There are two type of views - those that return a collection of posts, and then a view
that returns a single post.
"""

import logging
import re

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from djpress.conf import settings as djpress_settings
from djpress.exceptions import PageNotFoundError, PostNotFoundError
from djpress.feeds import PostFeed
from djpress.models import Category, Post
from djpress.url_utils import get_path_regex
from djpress.utils import get_template_name, validate_date_parts

logger = logging.getLogger(__name__)


def dispatcher(request: HttpRequest, path: str) -> HttpResponse | None:  # noqa: C901, PLR0911
    """Dispatch the request to the appropriate view based on the path."""
    # 1. Check for special URLs first
    if djpress_settings.RSS_ENABLED and (path in (djpress_settings.RSS_PATH, f"{djpress_settings.RSS_PATH}/")):
        return PostFeed()(request)

    # 2. Check if it matches the single post or the archives regex
    post_match = re.fullmatch(get_path_regex("post"), path)
    archives_match = re.fullmatch(get_path_regex("archives"), path)
    if post_match:
        # Does the post exist?
        post_groups = post_match.groupdict()
        post = get_post(**post_groups)

        # If so, return the single post view
        if post:
            return single_post(request, post)

        # If it doesn't look like an archive post, then it's a 404 - otherwise continue to the next step
        if not archives_match:
            msg = "Post not found"
            raise Http404(msg)

    # 3. Check if it matches the archives regex
    if archives_match:
        archives_groups = archives_match.groupdict()
        return archive_posts(request, **archives_groups)

    # 4. Check if it matches the category regex
    if djpress_settings.CATEGORY_ENABLED and djpress_settings.CATEGORY_PREFIX:
        category_match = re.fullmatch(get_path_regex("category"), path)
        if category_match:
            category_slug = category_match.group("slug")
            return category_posts(request, slug=category_slug)

    # 5. Check if it matches the tag regex
    if djpress_settings.TAG_ENABLED and djpress_settings.TAG_PREFIX:
        tag_match = re.fullmatch(get_path_regex("tag"), path)
        if tag_match:
            tag_slug = tag_match.group("slug")
            return tag_posts(request, slug=tag_slug)

    # 6. Check if it matches the author regex
    if djpress_settings.AUTHOR_ENABLED and djpress_settings.AUTHOR_PREFIX:
        author_match = re.fullmatch(get_path_regex("author"), path)
        if author_match:
            author_username = author_match.group("author")
            return author_posts(request, author=author_username)

    # 7. Any other path is considered a page
    page_match = re.fullmatch(get_path_regex("page"), path)
    page_path = page_match.group("path")
    return single_page(request, path=page_path)


def entry(
    request: HttpRequest,
    path: str = "",
) -> HttpResponse:
    """The main entry point.

    This takes a path and returns the appropriate view.
    """
    # Just echo the path receeived for now
    return dispatcher(request, path)


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
    template: str = get_template_name("index")

    posts = Paginator(
        Post.post_objects.get_published_posts(),
        djpress_settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page},
    )


def archive_posts(
    request: HttpRequest,
    year: str,
    month: str = "",
    day: str = "",
) -> HttpResponse:
    """View for the date-based archives pages.

    There will always be a year at least.

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
    template: str = get_template_name(view_name="archive_posts")

    try:
        date_parts = validate_date_parts(year=year, month=month, day=day)
    except ValueError:
        msg = "Invalid date"
        return HttpResponseBadRequest(msg)

    filtered_posts = Post.post_objects.get_published_posts().filter(date__year=date_parts["year"])
    if "month" in date_parts:
        filtered_posts = filtered_posts.filter(date__month=date_parts["month"])
    if "day" in date_parts:
        filtered_posts = filtered_posts.filter(date__day=date_parts["day"])

    posts = Paginator(filtered_posts, djpress_settings.RECENT_PUBLISHED_POSTS_COUNT)
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
    template: str = get_template_name(view_name="category_posts")

    try:
        category: Category = Category.objects.get_category_by_slug(slug=slug)
    except ValueError as exc:
        msg = "Category not found"
        raise Http404(msg) from exc

    posts = Paginator(
        Post.post_objects.get_published_posts_by_category(category),
        djpress_settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page, "category": category},
    )


def tag_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View for posts by tag.

    Tags differ from categories in that they can be concatenated together to return posts that have all the tags.

    The slug that is passed to this view is either a single tag, or a list of tags separated by a "+".

    Args:
        request (HttpRequest): The request object.
        slug (str): The tag slug.

    Returns:
        HttpResponse: The response.

    Context:
        posts (Page): The published posts for the tag as a Page object.
        tag (Tag): The tag object.
    """
    template: str = get_template_name(view_name="tag_posts")

    # Create a list of slugs from the slug
    slugs = slug.split("+")

    try:
        posts = Paginator(
            Post.post_objects.get_published_posts_by_tags(slugs),
            djpress_settings.RECENT_PUBLISHED_POSTS_COUNT,
        )
    except ValueError as exc:
        # Get the message from the exception
        msg = exc.args[0]
        raise Http404(msg) from exc

    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page, "tags": slugs},
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
    template: str = get_template_name(view_name="author_posts")

    try:
        user: User = User.objects.get(username=author)
    except User.DoesNotExist as exc:
        msg = "Author not found"
        raise Http404(msg) from exc

    posts = Paginator(
        Post.post_objects.get_published_posts_by_author(user),
        djpress_settings.RECENT_PUBLISHED_POSTS_COUNT,
    )
    page_number = request.GET.get("page")
    page = posts.get_page(page_number)

    return render(
        request=request,
        template_name=template,
        context={"posts": page, "author": user},
    )


def get_post(
    slug: str,
    year: str | None = None,
    month: str | None = None,
    day: str | None = None,
) -> None | Post:
    """Try to get a post by slug and date parts.

    Args:
        slug (str): The post slug.
        year (str | None): The year.
        month (str | None): The month.
        day (str | None): The day.

    Returns:
        None | Post: The post object, or None if not found.
    """
    try:
        date_parts = validate_date_parts(year=year, month=month, day=day)
        return Post.post_objects.get_published_post_by_slug(slug=slug, **date_parts)
    except (PostNotFoundError, ValueError):
        # A PageNotFoundError means we were able to parse the path, but the page was not found
        # A ValueError means we were not able to parse the path
        return None


def single_post(
    request: HttpRequest,
    post: Post,
) -> HttpResponse:
    """View for a single post.

    The single_post view is different to the others in that it doesn't look for a post since this is done in the
    dispatcher function. This view is only called if a post is found.

    Args:
        request (HttpRequest): The request object.
        post (Post): The post object.

    Returns:
        HttpResponse: The response.

    Context:
        post (Post): The post object.
    """
    context: dict = {"post": post}
    template: str = get_template_name(view_name="single_post")

    return render(
        request=request,
        context=context,
        template_name=template,
    )


def single_page(request: HttpRequest, path: str) -> HttpResponse:
    """View for a single page.

    Args:
        request (HttpRequest): The request object.
        path (str): The page path.

    Returns:
        HttpResponse: The response.

    Context:
        post (Post): The page object.

    Raises:
        Http404: If the page is not found.
    """
    try:
        post = Post.page_objects.get_published_page_by_path(path)
        context: dict = {"post": post}
    except (PageNotFoundError, ValueError) as exc:
        msg = "Page not found"
        raise Http404(msg) from exc

    template: str = get_template_name(view_name="single_page")

    return render(
        request=request,
        template_name=template,
        context=context,
    )
