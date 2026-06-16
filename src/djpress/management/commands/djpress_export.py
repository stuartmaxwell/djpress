"""Management command to export DJ Press content to Markdown flat files."""

import shutil
import tempfile
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from djpress.models import Media, Post


class Command(BaseCommand):
    """Export DJ Press blog content to Markdown flat files."""

    help = (
        "Export DJ Press blog content to a flat-file format that should be compatible with a variety of static site"
        " generators."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments."""
        parser.add_argument(
            "-o",
            "--output",
            "--output-dir",
            dest="output",
            type=str,
            default=None,
            help="Destination path for the export (ZIP file by default, or directory if --no-zip is set)",
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
        parser.add_argument(
            "--no-media",
            action="store_true",
            default=False,
            help="Do not include uploaded media files in the export",
        )
        parser.add_argument(
            "--no-zip",
            action="store_true",
            default=False,
            help="Export as a directory instead of a ZIP archive",
        )

    def handle(self, **options: Any) -> None:  # noqa: ANN401
        """Handle the export command."""
        output_opt = options.get("output")
        posts_only = options.get("posts_only", False)
        published_only = options.get("published_only", False)
        no_media = options.get("no_media", False)
        no_zip = options.get("no_zip", False)

        include_media = not no_media
        is_zip = not no_zip

        if is_zip:
            # Determine ZIP path
            if output_opt:
                zip_path = Path(output_opt)
                if zip_path.suffix != ".zip":
                    zip_path = zip_path.with_suffix(".zip")
            else:
                zip_path = Path("djpress_export.zip")

            # Ensure parent directory of ZIP file exists
            try:
                zip_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                msg = f"Failed to create output directory: {e}"
                raise CommandError(msg) from e

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                posts_exported, pages_exported, media_exported = self._run_export(
                    temp_path,
                    posts_only=posts_only,
                    published_only=published_only,
                    include_media=include_media,
                )

                # Package the temp_dir into a zip archive
                zip_base = zip_path.with_suffix("")
                try:
                    shutil.make_archive(str(zip_base), "zip", root_dir=temp_path)
                except OSError as e:
                    msg = f"Failed to create ZIP archive: {e}"
                    raise CommandError(msg) from e

            # Output ZIP summary
            summary = f"Export completed!\nPosts exported: {posts_exported}\nPages exported: {pages_exported}\n"
            if include_media:
                summary += f"Media items exported: {media_exported}\n"
            summary += f"Output ZIP archive: {zip_path.absolute()}"
            self.stdout.write(self.style.SUCCESS(summary))
        else:
            output_dir = Path(output_opt) if output_opt else Path("djpress_export")
            posts_exported, pages_exported, media_exported = self._run_export(
                output_dir,
                posts_only=posts_only,
                published_only=published_only,
                include_media=include_media,
            )
            # Output directory summary
            summary = f"Export completed!\nPosts exported: {posts_exported}\nPages exported: {pages_exported}\n"
            if include_media:
                summary += f"Media items exported: {media_exported}\n"
            summary += f"Output directory: {output_dir.absolute()}"
            self.stdout.write(self.style.SUCCESS(summary))

    def _run_export(
        self,
        target_dir: Path,
        *,
        posts_only: bool,
        published_only: bool,
        include_media: bool,
    ) -> tuple[int, int, int]:
        """Run the actual export process to target_dir."""
        # Create output directory structure
        self._create_directory_structure(target_dir, include_media=include_media)

        # Get posts and pages to export
        if published_only:
            queryset = Post.post_objects.all() if posts_only else Post.objects.all()
        elif posts_only:
            queryset = Post.admin_objects.filter(post_type="post")
        else:
            queryset = Post.admin_objects.all()

        posts_exported = 0
        pages_exported = 0
        media_exported = 0

        # Export posts & pages
        for item in queryset.prefetch_related("categories", "tags", "author"):
            if item.post_type == "page":
                self._export_page(item, target_dir)
                pages_exported += 1
            else:
                self._export_post(item, target_dir)
                posts_exported += 1

        # Export media items if requested
        if include_media:
            for media in Media.objects.all():
                if self._export_media(media, target_dir):
                    media_exported += 1

        return posts_exported, pages_exported, media_exported

    def _create_directory_structure(self, output_dir: Path, *, include_media: bool = False) -> None:
        """Create the Hugo directory structure."""
        try:
            # Create main directories
            (output_dir / "content" / "posts").mkdir(parents=True, exist_ok=True)
            (output_dir / "content" / "pages").mkdir(parents=True, exist_ok=True)

            if include_media:
                media_url = getattr(settings, "MEDIA_URL", "/media/")
                media_dir_name = media_url.strip("/")
                if media_dir_name:
                    (output_dir / "static" / media_dir_name).mkdir(parents=True, exist_ok=True)
                else:
                    (output_dir / "static").mkdir(parents=True, exist_ok=True)

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

    def _export_media(self, media: Media, output_dir: Path) -> bool:
        """Export a single media file to the static directory."""
        if not media.file or not media.file.name:
            self.stderr.write(f"Skipping media '{media.title}': No file associated.")
            return False

        media_url = getattr(settings, "MEDIA_URL", "/media/")
        media_dir_name = media_url.strip("/")

        # Construct target filepath: output_dir / "static" / media_dir_name / media.file.name
        # Note: if media_dir_name is empty, we just export to output_dir / "static" / media.file.name
        if media_dir_name:
            filepath = output_dir / "static" / media_dir_name / media.file.name
        else:
            filepath = output_dir / "static" / media.file.name

        try:
            # Create parent directories
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with media.file.open("rb") as src, filepath.open("wb") as dest:
                for chunk in src.chunks():
                    dest.write(chunk)
        except OSError as e:
            self.stderr.write(f"Failed to write media file {filepath}: {e}")
            return False
        else:
            self.stdout.write(f"Exported media: {filepath}")
            return True
