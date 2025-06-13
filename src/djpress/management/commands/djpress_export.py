"""Management command to export DJ Press content to Hugo format."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from djpress.models import Post


class Command(BaseCommand):
    """Export DJ Press blog content to Markdown flat files."""

    help = (
        "Export DJ Press blog content to a flat-file format that should be compatible with a variety of static site"
        " generators."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "--output-dir",
            type=str,
            default="djpress_export",
            help="Directory to export DJ Press content (default: djpress_export)",
        )
        parser.add_argument(
            "--posts-only",
            action="store_true",
            help="Export only posts, not pages",
        )
        parser.add_argument(
            "--published-only",
            action="store_true",
            default=False,
            help="Export only published content (default: False)",
        )

    def handle(self, **options: Any) -> None:  # noqa: ANN401
        """Handle the export command."""
        output_dir = Path(options["output_dir"])
        posts_only = options["posts_only"]
        published_only = options["published_only"]

        # Create output directory structure
        self._create_directory_structure(output_dir)

        # Get posts and pages to export
        if published_only:
            queryset = Post.post_objects.all() if posts_only else Post.objects.all()
        elif posts_only:
            queryset = Post.admin_objects.filter(post_type="post")
        else:
            queryset = Post.admin_objects.all()

        # Export content
        posts_exported = 0
        pages_exported = 0

        for item in queryset.prefetch_related("categories", "tags", "author"):
            if item.post_type == "page":
                self._export_page(item, output_dir)
                pages_exported += 1
            else:
                self._export_post(item, output_dir)
                posts_exported += 1

        # Output summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Export completed!\n"
                f"Posts exported: {posts_exported}\n"
                f"Pages exported: {pages_exported}\n"
                f"Output directory: {output_dir.absolute()}",
            ),
        )

    def _create_directory_structure(self, output_dir: Path) -> None:
        """Create the Hugo directory structure."""
        try:
            # Create main directories
            (output_dir / "content" / "posts").mkdir(parents=True, exist_ok=True)
            (output_dir / "content" / "pages").mkdir(parents=True, exist_ok=True)

            self.stdout.write(f"Created output directory: {output_dir.absolute()}")
        except OSError as e:
            msg = f"Failed to create output directory: {e}"
            raise CommandError(msg) from e

    def _export_post(self, post: Post, output_dir: Path) -> None:
        """Export a single post to Hugo format."""
        # Create filename based on date and slug
        date_str = post.published_at.strftime("%Y-%m-%d")
        filename = f"{date_str}-{post.slug}.md"
        filepath = output_dir / "content" / "posts" / filename

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(post)

        # Write the file
        self._write_content_file(filepath, frontmatter, post.content)

    def _export_page(self, page: Post, output_dir: Path) -> None:
        """Export a single page to Hugo format."""
        # Create directory structure for nested pages
        if page.parent:
            # For nested pages, create parent directory structure
            page_path = page.full_page_path
            filepath = output_dir / "content" / "pages" / page_path / "_index.md"
        else:
            # Top-level page
            filename = f"{page.slug}.md"
            filepath = output_dir / "content" / "pages" / filename

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(page)

        # Write the file
        self._write_content_file(filepath, frontmatter, page.content)

    def _generate_frontmatter(self, content: Post) -> dict[str, Any]:
        """Generate Hugo frontmatter for a post or page."""
        frontmatter = {
            "title": content.post_title,
            "date": content.published_at.isoformat(),
            "lastmod": content.updated_at.isoformat(),
            "draft": content.is_published is False,
            "slug": content.slug,
            "author": content.author.get_full_name() or content.author.username,
        }

        # Add categories
        if content.categories.exists():
            frontmatter["categories"] = [cat.title for cat in content.categories.all()]

        # Add tags
        if content.tags.exists():
            frontmatter["tags"] = [tag.title for tag in content.tags.all()]

        # Add page-specific fields
        if content.post_type == "page":
            frontmatter["type"] = "page"
            if content.menu_order != 0:
                frontmatter["weight"] = content.menu_order
            if content.parent:
                frontmatter["parent"] = content.parent.slug

        return frontmatter

    def _format_yaml_value(self, value: Any) -> str:  # noqa: ANN401
        """Format a value for YAML output."""
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int | float):
            return str(value)
        if isinstance(value, list):
            return "\n" + "\n".join(f"  - {item}" for item in value)
        # Quote strings that contain colons or start with special characters
        value_str = str(value)
        if ":" in value_str or value_str.startswith(("-", "?")):
            return f'"{value_str}"'
        return value_str

    def _write_content_file(self, filepath: Path, frontmatter: dict[str, Any], content: str) -> None:
        """Write a content file with frontmatter and content."""
        # Create parent directories if they don't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with filepath.open("w", encoding="utf-8") as f:
                # Write YAML frontmatter
                f.write("---\n")
                for key, value in frontmatter.items():
                    formatted_value = self._format_yaml_value(value)
                    f.write(f"{key}: {formatted_value}\n")
                f.write("---\n\n")

                # Write content
                f.write(content)

            self.stdout.write(f"Exported: {filepath}")
        except OSError as e:
            self.stderr.write(f"Failed to write {filepath}: {e}")
