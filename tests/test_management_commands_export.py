"""Tests for management commands."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from djpress.management.commands.djpress_export import Command
from djpress.models import Category, Post, Tag


@pytest.fixture
def draft_post(user):
    """Create a draft post for testing."""
    return Post.admin_objects.create(
        title="Draft Post",
        slug="draft-post",
        content="This is a draft post.",
        author=user,
        status="draft",
        post_type="post",
    )


@pytest.fixture
def future_post(user):
    """Create a future post for testing."""
    return Post.admin_objects.create(
        title="Future Post",
        slug="future-post",
        content="This is a future post.",
        author=user,
        status="published",
        post_type="post",
        published_at=timezone.now() + timezone.timedelta(days=1),
    )


@pytest.fixture
def test_page(user):
    """Create a page for testing."""
    return Post.admin_objects.create(
        title="Test Page",
        slug="test-page",
        content="This is a test page.",
        author=user,
        status="published",
        post_type="page",
        menu_order=10,
    )


@pytest.fixture
def child_page(user, test_page):
    """Create a child page for testing."""
    return Post.admin_objects.create(
        title="Child Page",
        slug="child-page",
        content="This is a child page.",
        author=user,
        status="published",
        post_type="page",
        parent=test_page,
        menu_order=5,
    )


@pytest.fixture
def post_with_categories_and_tags(user, category1, tag1, tag2):
    """Create a post with categories and tags."""
    post = Post.admin_objects.create(
        title="Post with Categories and Tags",
        slug="post-with-categories-and-tags",
        content="This post has categories and tags.",
        author=user,
        status="published",
        post_type="post",
    )
    post.categories.set([category1])
    post.tags.set([tag1, tag2])
    return post


@pytest.fixture
def post_without_title(user):
    """Create a post without a title."""
    return Post.admin_objects.create(
        title="",
        slug="post-without-title",
        content="# This is a markdown header\n\nThis post has no title but has content.",
        author=user,
        status="published",
        post_type="post",
    )


@pytest.mark.django_db
class TestExportToHugoCommand:
    """Test the djpress_export management command."""

    def test_command_help(self):
        """Test that the command help is displayed correctly."""
        command = Command()
        assert (
            "Export DJ Press blog content to a flat-file format that should be compatible with a variety of static site generators."
            in command.help
        )

    def test_add_arguments(self):
        """Test that command arguments are added correctly."""
        command = Command()
        parser = Mock()
        command.add_arguments(parser)

        # Verify parser.add_argument was called with correct parameters
        assert parser.add_argument.call_count == 3

        # Check the arguments were added
        calls = parser.add_argument.call_args_list
        assert any("--output-dir" in str(call) for call in calls)
        assert any("--posts-only" in str(call) for call in calls)
        assert any("--published-only" in str(call) for call in calls)

    def test_basic_export_published_only(self, test_post1, test_page, draft_post):
        """Test basic export with published content only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            call_command("djpress_export", output_dir=temp_dir, published_only=True)

            # Check directory structure
            content_dir = Path(temp_dir) / "content"
            posts_dir = content_dir / "posts"
            pages_dir = content_dir / "pages"

            assert content_dir.exists()
            assert posts_dir.exists()
            assert pages_dir.exists()

            # Check exported files
            post_files = list(posts_dir.glob("*.md"))
            page_files = list(pages_dir.glob("*.md"))

            assert len(post_files) == 1  # Only published post
            assert len(page_files) == 1  # Only published page

            # Check file naming
            post_file = post_files[0]
            assert test_post1.slug in post_file.name
            assert str(test_post1.published_at.year) in post_file.name

    def test_export_posts_only(self, test_post1, test_page):
        """Test export with posts-only option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            call_command("djpress_export", output_dir=temp_dir, posts_only=True)

            posts_dir = Path(temp_dir) / "content" / "posts"
            pages_dir = Path(temp_dir) / "content" / "pages"

            # Check that only posts are exported
            post_files = list(posts_dir.glob("*.md"))
            page_files = list(pages_dir.glob("*.md"))

            assert len(post_files) == 1
            assert len(page_files) == 0

    def test_export_all_content_including_drafts(self, test_post1, draft_post, test_page, test_page1):
        """Test export including draft content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            call_command("djpress_export", output_dir=temp_dir, published_only=False)

            posts_dir = Path(temp_dir) / "content" / "posts"
            post_files = list(posts_dir.glob("*.md"))

            pages_dir = Path(temp_dir) / "content" / "pages"
            page_files = list(pages_dir.glob("*.md"))

            # Should include both published and draft posts
            assert len(post_files) == 2
            assert len(page_files) == 2  # Only one page

    def test_frontmatter_generation_complete(self, post_with_categories_and_tags):
        """Test complete frontmatter generation with all fields."""
        command = Command()
        frontmatter = command._generate_frontmatter(post_with_categories_and_tags)

        expected_keys = {"title", "date", "lastmod", "draft", "slug", "author", "categories", "tags"}
        assert set(frontmatter.keys()) == expected_keys

        assert frontmatter["title"] == post_with_categories_and_tags.title
        assert frontmatter["slug"] == post_with_categories_and_tags.slug
        assert frontmatter["draft"] is False
        assert frontmatter["author"] == "Test User"
        assert len(frontmatter["categories"]) == 1
        assert len(frontmatter["tags"]) == 2

    def test_frontmatter_generation_page_with_parent(self, child_page):
        """Test frontmatter generation for page with parent and menu order."""
        command = Command()
        frontmatter = command._generate_frontmatter(child_page)

        assert "type" in frontmatter
        assert frontmatter["type"] == "page"
        assert "weight" in frontmatter
        assert frontmatter["weight"] == child_page.menu_order
        assert "parent" in frontmatter
        assert frontmatter["parent"] == child_page.parent.slug

    def test_frontmatter_generation_draft_post(self, draft_post):
        """Test frontmatter generation for draft post."""
        command = Command()
        frontmatter = command._generate_frontmatter(draft_post)

        assert frontmatter["draft"] is True

    def test_frontmatter_generation_no_categories_tags(self, user):
        """Test frontmatter generation when post has no categories or tags."""
        # Create a post without categories or tags
        post = Post.admin_objects.create(
            title="Post without categories or tags",
            slug="post-no-cat-tags",
            content="This post has no categories or tags.",
            author=user,
            status="published",
            post_type="post",
        )

        command = Command()
        frontmatter = command._generate_frontmatter(post)

        # Should not include categories/tags if empty
        assert "categories" not in frontmatter or not frontmatter.get("categories")
        assert "tags" not in frontmatter or not frontmatter.get("tags")

    def test_export_post_filename_format(self, test_post1):
        """Test that exported post files have correct filename format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = Command()
            command._export_post(test_post1, Path(temp_dir))

            posts_dir = Path(temp_dir) / "content" / "posts"
            post_files = list(posts_dir.glob("*.md"))

            assert len(post_files) == 1
            filename = post_files[0].name

            # Should be in format YYYY-MM-DD-slug.md
            date_str = test_post1.published_at.strftime("%Y-%m-%d")
            expected_filename = f"{date_str}-{test_post1.slug}.md"
            assert filename == expected_filename

    def test_export_page_top_level(self, test_page):
        """Test export of top-level page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = Command()
            command._export_page(test_page, Path(temp_dir))

            pages_dir = Path(temp_dir) / "content" / "pages"
            page_file = pages_dir / f"{test_page.slug}.md"

            assert page_file.exists()

    def test_export_page_nested(self, child_page):
        """Test export of nested page."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = Command()
            command._export_page(child_page, Path(temp_dir))

            # Should create nested directory structure
            expected_path = (
                Path(temp_dir) / "content" / "pages" / f"{child_page.parent.slug}" / f"{child_page.slug}" / "_index.md"
            )
            assert expected_path.exists()

    def test_write_content_file_format(self, test_post1):
        """Test that content files are written with correct format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = Command()
            filepath = Path(temp_dir) / "test.md"
            frontmatter = {"title": "Test", "draft": False}
            content = "Test content"

            command._write_content_file(filepath, frontmatter, content)

            assert filepath.exists()
            file_content = filepath.read_text(encoding="utf-8")

            # Check YAML frontmatter structure
            assert file_content.startswith("---\n")
            assert "---\n\n" in file_content
            assert "Test content" in file_content

            # Verify frontmatter content without parsing YAML
            lines = file_content.split("\n")
            frontmatter_lines = []
            in_frontmatter = False
            for line in lines:
                if line == "---":
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        break
                if in_frontmatter:
                    frontmatter_lines.append(line)

            frontmatter_text = "\n".join(frontmatter_lines)
            assert "title: Test" in frontmatter_text
            assert "draft: false" in frontmatter_text

    def test_post_with_no_title_uses_content(self, post_without_title):
        """Test that posts without titles generate titles from content."""
        command = Command()
        frontmatter = command._generate_frontmatter(post_without_title)

        # Should generate title from markdown header
        assert frontmatter["title"] == "Post without title..."

    def test_user_without_full_name(self, user):
        """Test author handling when user has no full name."""
        # Clear the user's name
        user.first_name = ""
        user.last_name = ""
        user.save()

        post = Post.admin_objects.create(
            title="Test Post",
            slug="test-post",
            content="Content",
            author=user,
            status="published",
            post_type="post",
        )

        command = Command()
        frontmatter = command._generate_frontmatter(post)

        # Should fall back to username
        assert frontmatter["author"] == user.username

    @patch("djpress.management.commands.djpress_export.Path.mkdir")
    def test_directory_creation_error(self, mock_mkdir):
        """Test handling of directory creation errors."""
        mock_mkdir.side_effect = OSError("Permission denied")

        command = Command()
        with pytest.raises(CommandError, match="Failed to create output directory"):
            command._create_directory_structure(Path("/fake/path"))

    def test_file_write_error(self):
        """Test handling of file write errors."""
        command = Command()

        # Mock both mkdir and open to fail after mkdir succeeds
        with (
            patch.object(Path, "mkdir"),
            patch("builtins.open", side_effect=OSError("Permission denied")),
            patch.object(command, "stderr") as mock_stderr,
        ):
            command._write_content_file(Path("/fake/file.md"), {}, "content")
            mock_stderr.write.assert_called_once()
            assert "Failed to write" in mock_stderr.write.call_args[0][0]

    def test_export_with_custom_output_dir(self, test_post1):
        """Test export with custom output directory."""
        with tempfile.TemporaryDirectory() as base_temp_dir:
            custom_dir = Path(base_temp_dir) / "my_blog_export"
            call_command("djpress_export", output_dir=str(custom_dir))

            assert custom_dir.exists()
            assert (custom_dir / "content" / "posts").exists()

    def test_command_output_summary(self, test_post1, test_page, draft_post):
        """Test that command outputs correct summary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Capture command output
            with patch("sys.stdout") as mock_stdout:
                call_command("djpress_export", output_dir=temp_dir, verbosity=1)

                # Get the output
                output_calls = [call.args[0] for call in mock_stdout.write.call_args_list]
                output_text = "".join(output_calls)

                assert "Export completed!" in output_text
                assert "Pages exported: 1" in output_text
                assert "Posts exported: 2" in output_text

    def test_page_with_zero_menu_order(self, user):
        """Test page with default menu order (0) doesn't include weight."""
        page = Post.admin_objects.create(
            title="Page with default order",
            slug="page-default-order",
            content="Content",
            author=user,
            status="published",
            post_type="page",
            menu_order=0,  # Default value
        )

        command = Command()
        frontmatter = command._generate_frontmatter(page)

        # Should not include weight for default menu order
        assert "weight" not in frontmatter

    def test_handle_method_flow(self, test_post1, test_page):
        """Test the complete handle method flow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            command = Command()

            # Mock stdout to verify output
            with patch.object(command, "stdout") as mock_stdout:
                command.handle(
                    output_dir=temp_dir,
                    posts_only=False,
                    published_only=True,
                )

                # Verify directory creation message
                mock_stdout.write.assert_any_call(f"Created output directory: {Path(temp_dir).absolute()}")

                # Verify export completion message
                success_calls = [call for call in mock_stdout.write.call_args_list if "Export completed!" in str(call)]
                assert len(success_calls) > 0

    @pytest.mark.django_db
    def test_with_multiple_categories_and_tags(self, user):
        """Test post with multiple categories and tags."""
        cat1 = Category.objects.create(title="Category 1", slug="cat1")
        cat2 = Category.objects.create(title="Category 2", slug="cat2")
        tag1 = Tag.objects.create(title="Tag 1", slug="tag1")
        tag2 = Tag.objects.create(title="Tag 2", slug="tag2")
        tag3 = Tag.objects.create(title="Tag 3", slug="tag3")

        post = Post.admin_objects.create(
            title="Multi Categories Tags Post",
            slug="multi-cat-tag-post",
            content="Content with multiple categories and tags",
            author=user,
            status="published",
            post_type="post",
        )
        post.categories.set([cat1, cat2])
        post.tags.set([tag1, tag2, tag3])

        command = Command()
        frontmatter = command._generate_frontmatter(post)

        assert len(frontmatter["categories"]) == 2
        assert len(frontmatter["tags"]) == 3
        assert "Category 1" in frontmatter["categories"]
        assert "Category 2" in frontmatter["categories"]
        assert "Tag 1" in frontmatter["tags"]
        assert "Tag 2" in frontmatter["tags"]
        assert "Tag 3" in frontmatter["tags"]

    def test_export_posts_only_including_drafts(self, test_post1, draft_post, test_page):
        """Test export with posts-only option including drafts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            call_command("djpress_export", output_dir=temp_dir, posts_only=True, published_only=False)

            posts_dir = Path(temp_dir) / "content" / "posts"
            pages_dir = Path(temp_dir) / "content" / "pages"

            # Check that only posts (including drafts) are exported
            post_files = list(posts_dir.glob("*.md"))
            page_files = list(pages_dir.glob("*.md"))

            assert len(post_files) == 2  # published + draft posts
            assert len(page_files) == 0  # no pages
