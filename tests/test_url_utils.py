import pytest

from djpress.url_utils import post_prefix_to_regex, regex_archives, regex_page
from djpress.conf import settings


def test_basic_year_month_day():
    prefix = "{{ year }}/{{ month }}/{{ day }}"
    expected_regex = r"(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_with_static_prefix():
    prefix = "posts/{{ year }}/{{ month }}"
    expected_regex = r"posts/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_year_only():
    prefix = "{{ year }}"
    expected_regex = r"(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_static_only():
    prefix = "posts/all"
    expected_regex = r"posts/all/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_mixed_order():
    prefix = "{{ month }}/{{ year }}/posts/{{ day }}"
    expected_regex = r"(?P<month>\d{2})/(?P<year>\d{4})/posts/(?P<day>\d{2})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_with_regex_special_chars():
    prefix = "posts+{{ year }}[{{ month }}]"
    expected_regex = r"posts\+(?P<year>\d{4})\[(?P<month>\d{2})\]/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_empty_prefix():
    prefix = ""
    expected_regex = "(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_unknown_placeholder():
    prefix = "{{ unknown }}/{{ year }}"
    expected_regex = r"\{\{ unknown \}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_no_slashes():
    prefix = "posts{{ year }}{{ month }}"
    expected_regex = r"posts(?P<year>\d{4})(?P<month>\d{2})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_weird_order():
    prefix = "{{ month }}/{{ year }}/post"
    expected_regex = r"(?P<month>\d{2})/(?P<year>\d{4})/post/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_nested_curly_braces():
    prefix = "{{ outer {{ inner }} }}/{{ year }}"
    expected_regex = r"\{\{ outer \{\{ inner \}\} \}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_empty_placeholder():
    prefix = "{{}}/{{ year }}"
    expected_regex = r"\{\{\}\}/(?P<year>\d{4})/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_bad_prefix_no_closing_brackets():
    prefix = "{{ year }}/{{ month"
    expected_regex = r"(?P<year>\d{4})/\{\{ month/(?P<slug>[\w-]+)"

    regex = post_prefix_to_regex(prefix)
    assert regex == expected_regex


def test_regex_page():
    """Test that the URL is correctly set when APPEND_SLASH is True."""
    # Default value is True
    assert settings.APPEND_SLASH is True

    # Test that the URL is correctly set
    assert regex_page() == r"^(?P<path>[0-9A-Za-z/_-]*)/$"

    settings.set("APPEND_SLASH", False)
    assert settings.APPEND_SLASH is False

    # Test that the URL is correctly set
    assert regex_page() == r"^(?P<path>[0-9A-Za-z/_-]*)$"

    # Set back to default value
    settings.set("APPEND_SLASH", True)
    assert settings.APPEND_SLASH is True


def test_regex_archives():
    """Test that the URL is correctly set when APPEND_SLASH is True."""
    # Default value is True
    assert settings.APPEND_SLASH is True
    assert settings.ARCHIVE_PREFIX == "test-url-archives"

    # Test that the URL is correctly set
    assert regex_archives() == r"test-url-archives/(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?/$"

    settings.set("APPEND_SLASH", False)
    assert settings.APPEND_SLASH is False

    # Test that the URL is correctly set
    assert regex_archives() == r"test-url-archives/(?P<year>\d{4})(?:/(?P<month>\d{2})(?:/(?P<day>\d{2}))?)?$"

    # Set back to default value
    settings.set("APPEND_SLASH", True)
    assert settings.APPEND_SLASH is True
