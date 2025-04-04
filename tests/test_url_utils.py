import pytest


from djpress.url_utils import (
    regex_post,
    regex_archives,
    regex_category,
    regex_author,
    get_path_regex,
    get_author_url,
    get_category_url,
    get_tag_url,
    get_archives_url,
    get_page_url,
    get_post_url,
    get_rss_url,
)


@pytest.mark.django_db
def test_basic_year_month_day(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    expected_regex = r"(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_basic_year_month_day_no_spaces(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{year}}/{{month}}/{{day}}"
    expected_regex = r"(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_basic_year_month_day_mixed_spaces(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{y e a r}}/{{m onth}}/{{day }}"
    expected_regex = r"(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_with_static_prefix(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "posts/{{ year }}/{{ month }}"
    expected_regex = r"posts/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_year_only(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}"
    expected_regex = r"(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_static_only(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "posts/all"
    expected_regex = r"posts/all/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_mixed_order(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ month }}/{{ year }}/posts/{{ day }}"
    expected_regex = r"(?P<month>\d{2})/(?P<year>\d{4})/posts/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_with_regex_special_chars(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "posts+{{ year }}[{{ month }}]"
    expected_regex = r"posts\+(?P<year>\d{4})\[(?P<month>\d{2})\]/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_empty_prefix(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = ""
    expected_regex = r"(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_unknown_placeholder(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ unknown }}/{{ year }}"
    expected_regex = r"\{\{ unknown \}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_no_slashes(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "posts{{ year }}{{ month }}"
    expected_regex = r"posts(?P<year>\d{4})(?P<month>\d{2})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_weird_order(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ month }}/{{ year }}/post"
    expected_regex = r"(?P<month>\d{2})/(?P<year>\d{4})/post/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_nested_curly_braces(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ outer {{ inner }} }}/{{ year }}"
    expected_regex = r"\{\{ outer \{\{ inner \}\} \}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_empty_placeholder(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{}}/{{ year }}"
    expected_regex = r"\{\{\}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_bad_prefix_no_closing_brackets(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month"
    expected_regex = r"(?P<year>\d{4})/\{\{ month/(?P<slug>[\w-]+)"

    regex = regex_post()
    assert regex == expected_regex


@pytest.mark.django_db
def test_archives_year_only(settings):
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    expected_regex = r"(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?"

    regex = regex_archives()
    assert regex == expected_regex


@pytest.mark.django_db
def test_archives_with_prefix(settings):
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = "archives"
    expected_regex = r"archives/(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?"

    regex = regex_archives()
    assert regex == expected_regex


@pytest.mark.django_db
def test_archives_empty_prefix(settings):
    settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] = ""
    expected_regex = r"(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?"

    regex = regex_archives()
    assert regex == expected_regex


@pytest.mark.django_db
def test_category_with_prefix(settings):
    settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] = "category"
    expected_regex = r"category/(?P<slug>[\w-]+)"

    regex = regex_category()
    assert regex == expected_regex


@pytest.mark.django_db
def test_author_with_prefix(settings):
    settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] = "author"
    expected_regex = r"author/(?P<author>[\w-]+)"

    regex = regex_author()
    assert regex == expected_regex


@pytest.mark.django_db
def test_author_empty_prefix(settings):
    settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] = ""
    expected_regex = r"(?P<author>[\w-]+)"

    regex = regex_author()
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_path_regex_post(settings):
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    expected_regex = r"^test\-posts/(?P<slug>[\w-]+)/$"

    regex = get_path_regex("post")
    assert regex == expected_regex

    settings.APPEND_SLASH = False
    expected_regex = r"^test\-posts/(?P<slug>[\w-]+)$"

    regex = get_path_regex("post")
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_path_regex_archives(settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    expected_regex = r"^test\-url\-archives/(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?/$"

    regex = get_path_regex("archives")
    assert regex == expected_regex

    settings.APPEND_SLASH = False
    expected_regex = r"^test\-url\-archives/(?P<year>\d{4})(/(?P<month>\d{2}))?(/(?P<day>\d{2}))?$"

    regex = get_path_regex("archives")
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_path_regex_page(settings):
    expected_regex = r"^(?P<path>([\w-]+/)*[\w-]+)/$"

    regex = get_path_regex("page")
    assert regex == expected_regex

    settings.APPEND_SLASH = False
    expected_regex = r"^(?P<path>([\w-]+/)*[\w-]+)$"

    regex = get_path_regex("page")
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_path_regex_category(settings):
    assert settings.DJPRESS_SETTINGS["CATEGORY_PREFIX"] == "test-url-category"
    expected_regex = r"^test\-url\-category/(?P<slug>[\w-]+)/$"

    regex = get_path_regex("category")
    assert regex == expected_regex

    settings.APPEND_SLASH = False
    expected_regex = r"^test\-url\-category/(?P<slug>[\w-]+)$"

    regex = get_path_regex("category")
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_path_regex_author(settings):
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"
    expected_regex = r"^test\-url\-author/(?P<author>[\w-]+)/$"

    regex = get_path_regex("author")
    assert regex == expected_regex

    settings.APPEND_SLASH = False
    expected_regex = r"^test\-url\-author/(?P<author>[\w-]+)$"

    regex = get_path_regex("author")
    assert regex == expected_regex


@pytest.mark.django_db
def test_get_author_url(settings, user):
    assert settings.DJPRESS_SETTINGS["AUTHOR_PREFIX"] == "test-url-author"
    assert settings.APPEND_SLASH is True
    expected_url = f"/test-url-author/{user.username}/"

    url = get_author_url(user)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = f"/test-url-author/{user.username}"

    url = get_author_url(user)
    assert url == expected_url


@pytest.mark.django_db
def test_get_category_url(settings, category1):
    assert settings.APPEND_SLASH is True
    expected_url = f"/{category1.permalink}/"

    url = get_category_url(category1)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = f"/{category1.permalink}"

    url = get_category_url(category1)
    assert url == expected_url


@pytest.mark.django_db
def test_get_tag_url(settings, tag1):
    assert settings.APPEND_SLASH is True
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == "test-url-tag"
    expected_url = f"/test-url-tag/{tag1.slug}/"
    url = get_tag_url(tag1)
    assert url == expected_url

    assert settings.APPEND_SLASH is True
    settings.DJPRESS_SETTINGS["TAG_PREFIX"] = ""
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == ""
    expected_url = f"/{tag1.slug}/"
    url = get_tag_url(tag1)
    assert url == expected_url

    settings.APPEND_SLASH = False
    settings.DJPRESS_SETTINGS["TAG_PREFIX"] = "test-url-tag"
    assert settings.DJPRESS_SETTINGS["TAG_PREFIX"] == "test-url-tag"
    expected_url = f"/test-url-tag/{tag1.slug}"
    url = get_tag_url(tag1)
    assert url == expected_url


def test_get_archives_url_year(settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    assert settings.APPEND_SLASH is True
    expected_url = "/test-url-archives/2024/"

    url = get_archives_url(2024)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = "/test-url-archives/2024"

    url = get_archives_url(2024)
    assert url == expected_url


def test_get_archives_url_year_month(settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    assert settings.APPEND_SLASH is True
    expected_url = "/test-url-archives/2024/09/"

    url = get_archives_url(2024, 9)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = "/test-url-archives/2024/09"

    url = get_archives_url(2024, 9)
    assert url == expected_url


def test_get_archives_url_year_month_day(settings):
    assert settings.DJPRESS_SETTINGS["ARCHIVE_PREFIX"] == "test-url-archives"
    assert settings.APPEND_SLASH is True
    expected_url = "/test-url-archives/2024/09/24/"

    url = get_archives_url(2024, 9, 24)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = "/test-url-archives/2024/09/24"

    url = get_archives_url(2024, 9, 24)
    assert url == expected_url


@pytest.mark.django_db
def test_get_page_url(settings, test_page1):
    assert settings.APPEND_SLASH is True
    expected_url = f"/{test_page1.slug}/"

    url = get_page_url(test_page1)
    assert url == expected_url

    settings.APPEND_SLASH = False
    expected_url = f"/{test_page1.slug}"

    url = get_page_url(test_page1)
    assert url == expected_url


@pytest.mark.django_db
def test_get_page_url_parent(settings, test_page1, test_page2):
    assert settings.APPEND_SLASH is True
    expected_url = f"/{test_page2.slug}/{test_page1.slug}/"

    test_page1.parent = test_page2
    test_page1.save()

    url = get_page_url(test_page1)
    assert url == expected_url


@pytest.mark.django_db
def test_get_post_url(settings, test_post1):
    assert settings.DJPRESS_SETTINGS["POST_PREFIX"] == "test-posts"
    assert settings.APPEND_SLASH is True
    expected_url = f"/test-posts/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = ""
    expected_url = f"/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.date.strftime('%d')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{year}}/{{month}}/{{day}}"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.date.strftime('%d')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{y e a r}}/{{m onth}}/{{day }}"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.date.strftime('%d')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "post/{{ year }}/{{ month }}/{{ day }}"
    expected_url = f"/post/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.date.strftime('%d')}/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}/post"
    expected_url = f"/{test_post1.date.strftime('%Y')}/{test_post1.date.strftime('%m')}/{test_post1.date.strftime('%d')}/post/{test_post1.slug}/"
    url = get_post_url(test_post1)
    assert url == expected_url

    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "test-posts"
    settings.APPEND_SLASH = False
    expected_url = f"/test-posts/{test_post1.slug}"
    url = get_post_url(test_post1)
    assert url == expected_url


def test_get_rss_url(settings):
    with pytest.raises(KeyError):
        assert settings.DJPRESS_SETTINGS["RSS_ENABLED"] == "True"
    assert settings.DJPRESS_SETTINGS["RSS_PATH"] == "test-rss"
    assert settings.APPEND_SLASH is True
    expected_url = "/test-rss/"
    url = get_rss_url()
    assert url == expected_url

    settings.DJPRESS_SETTINGS["RSS_PATH"] = None
    with pytest.raises(TypeError):
        url = get_rss_url()

    settings.DJPRESS_SETTINGS["RSS_PATH"] = "test-rss"
    settings.APPEND_SLASH = False
    expected_url = "/test-rss"
    url = get_rss_url()
    assert url == expected_url
