# URL Structure

This document explains how URLs are organised in DJ Press and how to customise them for your site's needs.

## Types of Content

DJ Press manages three main types of content, each with their own URL structure:

- [Pages](#page) - Static content like "About Us" or "Contact"
- [Posts](#post) - Blog entries organised chronologically
- [Index pages](#index) - Collections of posts organised by date, category, tag, or author

## Page

A page is standalone content with a `post_type` of `page`. Pages:

- Don't belong to categories or tags
- Can have a hierarchical structure with parent pages
- Have simple URLs based on their slug
- Can be used for static content like "About", "Contact", etc.

## Post

A post is a blog entry with a `post_type` of `post`. Posts:

- Belong to categories and can have tags
- Are organised chronologically
- Have URLs that typically include date information
- Form the primary content of your blog

## Index

Index pages display collections of posts filtered by specific criteria:

- Date-based archives (yearly, monthly, daily)
- Category archives
- Tag archives
- Author archives

Index pages include pagination and typically display truncated post content.

## URL Patterns

### Single Post

Post URLs follow this pattern:

```text
/{{ POST_PREFIX }}/{{ post_slug }}
```

The `POST_PREFIX` setting can include date placeholders and static text:

| Example `POST_PREFIX`                        | Sample URL            |
|----------------------------------------------|-----------------------|
| `{{ year }}/{{ month }}/{{ day }}` (default) | `/2024/05/20/my-post` |
| `{{ year }}/{{ month }}`                     | `/2024/05/my-post`    |
| `blog/{{ year }}`                            | `/blog/2024/my-post`  |
| `articles`                                   | `/articles/my-post`   |
| *(empty string)*                             | `/my-post`            |

### Single Page

Page URLs follow a hierarchical pattern:

```text
/{{ parent_slug }}/{{ parent_slug }}/{{ page_slug }}
```

Pages can have unlimited nesting levels, with each level represented by its slug:

| Page Structure                    | URL                      |
|-----------------------------------|--------------------------|
| Page: "About"                     | `/about`                 |
| Page: "Team" (parent: About)      | `/about/team`            |
| Page: "Leadership" (parent: Team) | `/about/team/leadership` |

### Archive Page

Archive URLs display posts from a specific time period:

```text
/{{ ARCHIVE_PREFIX }}/{{ year }}/{{ month }}/{{ day }}
```

The `ARCHIVE_PREFIX` is optional (default is empty):

| Example       | URL              | Content                     |
|---------------|------------------|-----------------------------|
| Year archive  | `/2024`          | All posts from 2024         |
| Month archive | `/2024/05`       | All posts from May 2024     |
| Day archive   | `/2024/05/20`    | All posts from May 20, 2024 |
| With prefix   | `/archives/2024` | All posts from 2024         |

Enable/disable with `ARCHIVE_ENABLED` (default: `True`).

### Category Page

Category URLs follow this pattern:

```text
/{{ CATEGORY_PREFIX }}/{{ category_slug }}
```

The `CATEGORY_PREFIX` is required (default is "category"):

| Example       | URL              | Content                          |
|---------------|------------------|----------------------------------|
| Default       | `/category/news` | All posts in the "News" category |
| Custom prefix | `/topics/news`   | All posts in the "News" category |

Enable/disable with `CATEGORY_ENABLED` (default: `True`).

### Author Page

Author URLs follow this pattern:

```text
/{{ AUTHOR_PREFIX }}/{{ username }}
```

The `AUTHOR_PREFIX` is required (default is "author"):

| Example       | URL               | Content                     |
|---------------|-------------------|-----------------------------|
| Default       | `/author/johndoe` | All posts by user "johndoe" |
| Custom prefix | `/writer/johndoe` | All posts by user "johndoe" |

Enable/disable with `AUTHOR_ENABLED` (default: `True`).

### Tag Page

Tag URLs follow this pattern:

```text
/{{ TAG_PREFIX }}/{{ tag_slug }}
```

For multiple tags:

```text
/{{ TAG_PREFIX }}/{{ tag_slug }}+{{ tag_slug }}
```

The `TAG_PREFIX` is required (default is "tag"):

| Example       | URL                  | Content                                      |
|---------------|----------------------|----------------------------------------------|
| Single tag    | `/tag/python`        | Posts tagged with "python"                   |
| Multiple tags | `/tag/python+django` | Posts tagged with both "python" and "django" |
| Custom prefix | `/topics/python`     | Posts tagged with "python"                   |

Enable/disable with `TAG_ENABLED` (default: `True`).

### Special URLs

These special URLs serve specific purposes:

| URL Pattern       | Description              | Setting                     |
|-------------------|--------------------------|-----------------------------|
| `/{{ RSS_PATH }}` | RSS feed of recent posts | `RSS_PATH` (default: "rss") |

## URL Resolution Priority

When a user visits a URL, DJ Press determines what content to display using this resolution order:

1. **Special URLs** (highest priority)
   - RSS feed (`/rss` by default)
   - Any other special URLs configured by plugins

2. **Explicit URL patterns with prefixes** (second priority)
   - Single post matching post prefix pattern
   - Archive pages matching date patterns
   - Category pages matching category prefix
   - Tag pages matching tag prefix
   - Author pages matching author prefix

3. **Pages** (lowest priority)
   - Any URL not matching the above patterns is treated as a page URL

### Conflict Resolution

When URL patterns could match multiple content types, the above priority order determines which content is shown. For
example:

```text
/news/
```

Could potentially be:

- A post with slug "news" (if POST_PREFIX is empty)
- A page with slug "news"

In this case, the post would be displayed because posts have higher priority than pages in URL resolution.

To avoid conflicts, use distinctive prefixes for your content types:

```python
DJPRESS_SETTINGS = {
    "POST_PREFIX": "blog",     # Posts: /blog/my-post
    "CATEGORY_PREFIX": "topic", # Categories: /topic/news
    "TAG_PREFIX": "tagged",    # Tags: /tagged/python
}
```

## SEO Considerations

### URL Structure Best Practices

1. **Use descriptive slugs**
   - Good: `/blog/django-template-guide`
   - Avoid: `/blog/post-12345`

2. **Keep URLs consistent**
   - Once you define your URL structure, avoid changing it to prevent broken links
   - If you must change URLs, implement proper 301 redirects

3. **Keep URLs short**
   - Consider using `POST_PREFIX` with just the year or year/month instead of full dates
   - Example: `/2024/django-template-guide` vs. `/2024/05/20/django-template-guide`

4. **Use hyphens for word separation**
   - Good: `/blog/seo-best-practices`
   - Avoid: `/blog/seo_best_practices` or `/blog/seobestpractices`

5. **Leverage canonical URLs**
   - DJ Press automatically adds canonical URLs to prevent duplicate content issues
   - For posts accessible via multiple URLs (like date archives), the single post URL is canonical

### Recommended Configurations

For a blog focused on SEO:

```python
DJPRESS_SETTINGS = {
    "POST_PREFIX": "{{ year }}/{{ month }}",  # Shorter URLs with just year/month
    "CATEGORY_PREFIX": "category",            # Clear content type in URL
    "TAG_PREFIX": "tag",                      # Clear content type in URL
    "AUTHOR_PREFIX": "author",                # Clear content type in URL
}
```

For a documentation site:

```python
DJPRESS_SETTINGS = {
    "POST_PREFIX": "docs",                   # Simple prefix without dates
    "CATEGORY_PREFIX": "section",            # Represents documentation sections
    "TAG_PREFIX": "topic",                   # Represents documentation topics
    "ARCHIVE_ENABLED": False,                # Disable date-based archives
}
```
