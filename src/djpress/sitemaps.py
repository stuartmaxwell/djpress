"""Sitemap classes for DJ Press."""

from datetime import datetime
from typing import Any

from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet

from djpress.conf import settings as djpress_settings
from djpress.models import Category, Post


class PostSitemap(Sitemap):
    """Sitemap for blog posts."""

    changefreq = "monthly"
    protocol = "https"

    def items(self) -> QuerySet:
        """Return all published posts."""
        return Post.post_objects.all()

    def lastmod(self, obj: Post) -> datetime:
        """Return the last modified date of the post."""
        return obj.updated_at

    def location(self, obj: Post) -> str:
        """Return the URL of the post."""
        return obj.url


class PageSitemap(Sitemap):
    """Sitemap for static pages."""

    changefreq = "monthly"
    protocol = "https"

    def items(self) -> QuerySet:
        """Return all published pages."""
        return Post.page_objects.get_published_pages()

    def lastmod(self, obj: Post) -> datetime:
        """Return the last modified date of the page."""
        return obj.updated_at

    def location(self, obj: Post) -> str:
        """Return the URL of the page."""
        return obj.url


class CategorySitemap(Sitemap):
    """Sitemap for category archives."""

    changefreq = "daily"
    protocol = "https"

    def items(self) -> QuerySet:
        """Return all categories that have published posts."""
        return Category.objects.get_categories_with_published_posts()

    def lastmod(self, obj: Category) -> datetime | None:
        """Return the last modified date of the most recent post in the category."""
        return obj.last_modified

    def location(self, obj: Category) -> str:
        """Return the URL of the category."""
        return obj.url


class DateBasedSitemap(Sitemap):
    """Sitemap for date-based archives."""

    changefreq = "daily"
    protocol = "https"

    def items(self) -> list[dict[str, Any]]:
        """Return all date-based archives that have posts.

        Returns a list of dictionaries containing:
        - year: The year
        - month: The month (optional)
        - day: The day (optional)
        - latest_modified: The latest modified date of posts in this period
        """
        if djpress_settings.ARCHIVE_ENABLED is False:
            return []

        archives: list[dict] = []

        # Get all unique years
        years = Post.post_objects.get_years()
        for year in years:
            archives.append(
                {
                    "year": year.year,
                    "latest_modified": Post.post_objects.get_year_last_modified(year.year),
                },
            )

            # Get all months in this year
            months = Post.post_objects.get_months(year.year)
            for month in months:
                archives.append(
                    {
                        "year": year.year,
                        "month": month.month,
                        "latest_modified": Post.post_objects.get_month_last_modified(year.year, month.month),
                    },
                )

                # Get all days in this month
                days = Post.post_objects.get_days(year.year, month.month)
                for day in days:
                    archives.append(  # noqa: PERF401
                        {
                            "year": year.year,
                            "month": month.month,
                            "day": day.day,
                            "latest_modified": Post.post_objects.get_day_last_modified(year.year, month.month, day.day),
                        },
                    )

        return archives

    def lastmod(self, obj: dict[str, Any]) -> datetime:
        """Return the last modified date of posts in this archive."""
        return obj["latest_modified"]

    def location(self, obj: dict[str, Any]) -> str:
        """Return the URL of the archive."""
        from djpress.url_utils import get_archives_url

        return get_archives_url(obj["year"], obj.get("month"), obj.get("day"))
