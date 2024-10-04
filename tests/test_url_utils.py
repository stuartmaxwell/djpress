import pytest


from djpress.url_utils import regex_post, regex_archives, regex_page


@pytest.mark.django_db
def test_basic_year_month_day(settings):
    settings.DJPRESS_SETTINGS["POST_PREFIX"] = "{{ year }}/{{ month }}/{{ day }}"
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
    expected_regex = "(?P<slug>[\w-]+)"

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
