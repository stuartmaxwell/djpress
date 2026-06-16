# Management Commands

DJ Press provides Django management commands for exporting content and managing user permissions.

## djpress_setup_groups

The `djpress_setup_groups` command creates or updates DJ Press user groups and assigns appropriate permissions.

### Usage

```bash
python manage.py djpress_setup_groups
```

### What It Does

This command creates four user groups with different permission levels:

- **djpress_admin**: Full permissions to all djpress models
- **djpress_editor**: Can publish posts and manage all content
- **djpress_author**: Can publish their own posts and add tags/media
- **djpress_contributor**: Can create/edit posts (but not publish) and add tags/media

### When to Use

Groups are automatically created when you run `python manage.py migrate`, so you typically don't need to run this command manually. However, it's useful for:

- Troubleshooting permission issues
- Re-creating groups after manual deletion
- Updating permissions after upgrading DJ Press

### Assigning Users to Groups

After running the command, assign users to groups via the Django admin interface or management shell:

```bash
python manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='editor_user')
>>> user.groups.add(Group.objects.get(name='djpress_editor'))
```

## djpress_export

The `djpress_export` command exports your DJ Press blog content and media files to Markdown and static asset files. By default, it packages the output into a single ZIP archive to make backups and migrations easy.

### Usage

```bash
python manage.py djpress_export [options]
```

### Options

- `-o OUTPUT`, `--output OUTPUT`, `--output-dir OUTPUT`: Destination path for the export. Defaults to `djpress_export.zip` (or `djpress_export` directory if `--no-zip` is specified). Auto-appends `.zip` suffix for ZIP exports if missing.
- `--posts-only`: Export only posts, not pages.
- `--published-only`: Export only published content (excludes drafts and future posts).
- `--no-media`: Do not include uploaded media files in the export (included by default).
- `--no-zip`: Export directly to a flat directory structure instead of packaging into a ZIP archive.

### Examples

Export all content (including drafts and media library) to a ZIP archive:

```bash
python manage.py djpress_export
```

Export only published content as a flat directory:

```bash
python manage.py djpress_export --no-zip --published-only
```

Export to a custom ZIP path (auto-appends `.zip` if omitted):

```bash
python manage.py djpress_export -o my_backup
```

Export directly to a custom directory without ZIP packaging:

```bash
python manage.py djpress_export --no-zip -o my_blog_folder
```

Export posts only, excluding media:

```bash
python manage.py djpress_export --posts-only --no-media
```

### Output Structure

By default, the command creates a ZIP file containing the directory structure. When exported as a directory (using `--no-zip`), the layout matches Hugo's content and static assets organization:

```text
output_directory/
├── content/
│   ├── posts/
│   │   ├── 2024-01-15-my-first-post.md
│   │   └── 2024-02-20-another-post.md
│   └── pages/
│       ├── about.md
│       └── contact/
│           └── _index.md
└── static/
    └── media/
        └── djpress/
            └── 2026/
                └── 06/
                    └── 16/
                        └── mg4-urban-black.png
```

### File Naming

- **Posts**: Named as `YYYY-MM-DD-slug.md` using the post's published date and slug
- **Pages**:
  - Top-level pages: `slug.md`
  - Nested pages: `parent-slug/child-slug/_index.md`

### Frontmatter

Each exported file includes YAML frontmatter with the following fields:

#### Common Fields (Posts and Pages)

- `title`: The post/page title
- `date`: Publication date in ISO format
- `lastmod`: Last modified date in ISO format
- `draft`: Boolean indicating if content is published
- `slug`: URL slug
- `author`: Author's full name or username

#### Post-Specific Fields

- `categories`: Array of category names (if any)
- `tags`: Array of tag names (if any)

#### Page-Specific Fields

- `type`: Always set to "page"
- `weight`: Menu order (if not 0)
- `parent`: Parent page slug (for nested pages)

### Example Output

**Post Example** (`2024-01-15-hello-world.md`):

```markdown
---
title: Hello World
date: 2024-01-15T10:30:00+00:00
lastmod: 2024-01-15T10:30:00+00:00
draft: false
slug: hello-world
author: John Doe
categories:
  - Technology
  - Django
tags:
  - blogging
  - web development
---

Welcome to my new blog! This is my first post using DJ Press.

## Getting Started

Here's how to get started with DJ Press...
```

**Page Example** (`about.md`):

```markdown
---
title: About Us
date: 2024-01-10T09:00:00+00:00
lastmod: 2024-01-10T09:00:00+00:00
draft: false
slug: about
author: Jane Smith
type: page
---

Learn more about our company and mission.
```

### Use Cases

#### Static Site Migration

Use this command when migrating from DJ Press to a static site generator:

```bash
python manage.py djpress_export -o my_blog_export --published-only --no-zip
```

#### Content Backup

Create a backup of all your content in a portable format:

```bash
python manage.py djpress_export -o backup_$(date +%Y%m%d)
```

#### Draft Review

Export all content including drafts for review:

```bash
python manage.py djpress_export -o review_content --no-zip
```

### Static Site Generator Compatibility

The exported format is designed to work with popular static site generators:

#### Hugo

The default output structure matches Hugo's content organization. Files can be used directly in a Hugo site.

#### Jekyll

Files are compatible with Jekyll with minimal configuration changes. You may need to adjust the frontmatter format if using Jekyll-specific features.

#### Other Generators

Most static site generators that support Markdown with YAML frontmatter should work with the exported files.

### Notes

- The command preserves your original content structure and metadata
- Draft posts are exported with `draft: true` in the frontmatter
- Categories and tags are preserved as arrays in the frontmatter
- Parent/child page relationships are maintained through directory structure and frontmatter
- All dates are exported in ISO format for maximum compatibility
- File encoding is UTF-8 to support international content
