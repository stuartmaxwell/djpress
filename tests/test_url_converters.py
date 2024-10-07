import re
import pytest


def test_regex_append_slash(converter):
    # Valid paths
    valid_paths = [
        "valid-path/",
        "valid_path/",
        "valid/path/",
        "valid123/",
        "valid-123_path/",
        "valid/path/123/",
    ]
    for path in valid_paths:
        assert re.match(converter.regex, path), f"Regex should match valid path: {path}"

    # Invalid paths
    invalid_paths = [
        "invalid path",  # space
        "invalid@path",  # special character
        "invalid#path",  # special character
        "invalid?path",  # special character
    ]
    for path in invalid_paths:
        assert not re.match(converter.regex, path), f"Regex should not match invalid path: {path}"


def test_regex_no_append_slash(settings, converter):
    settings.APPEND_SLASH = False
    # Valid paths
    valid_paths = [
        "valid-path",
    ]
    for path in valid_paths:
        assert re.match(converter.regex, path), f"Regex should match valid path: {path}"


def test_to_python(converter):
    assert converter.to_python("test-value") == "test-value"
    assert converter.to_python("123") == "123"
    assert converter.to_python("valid/path") == "valid/path"


def test_to_url(converter):
    assert converter.to_url("test-value") == "test-value"
    assert converter.to_url("123") == "123"
    assert converter.to_url("valid/path") == "valid/path"
