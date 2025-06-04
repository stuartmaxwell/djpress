import pytest

from djpress.markdown_renderer import default_renderer


def test_invalid_markdown_extensions(settings):
    """Test default renderer with no extensions."""
    settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] = None
    with pytest.raises(TypeError) as exc_info:
        default_renderer("# Hello World")
    assert "Expected list for MARKDOWN_EXTENSIONS" in str(exc_info.value)

    settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] = "not a list"
    with pytest.raises(TypeError) as exc_info:
        default_renderer("# Hello World")
    assert "Expected list for MARKDOWN_EXTENSIONS" in str(exc_info.value)

    settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] = {"not": "a list"}
    with pytest.raises(TypeError) as exc_info:
        default_renderer("# Hello World")
    assert "Expected list for MARKDOWN_EXTENSIONS" in str(exc_info.value)

    settings.DJPRESS_SETTINGS["MARKDOWN_EXTENSIONS"] = 99
    with pytest.raises(TypeError) as exc_info:
        default_renderer("# Hello World")
    assert "Expected list for MARKDOWN_EXTENSIONS" in str(exc_info.value)
