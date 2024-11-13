import importlib
from unittest.mock import mock_open, patch

import pytest


def test_version_loading():
    mock_toml_content = """
    [project]
    version = "1.0.0"
    """

    with patch("pathlib.Path.open", mock_open(read_data=mock_toml_content)):
        with patch("tomllib.load") as mock_load:
            mock_load.return_value = {"project": {"version": "1.0.0"}}

            import djpress

            importlib.reload(djpress)  # Reload the module to apply the mock

            assert djpress.__version__ == "1.0.0"


def test_version_loading_error():
    with patch("pathlib.Path.open", mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()

        with pytest.raises(FileNotFoundError):
            import djpress

            importlib.reload(djpress)  # Reload the module to apply the mock


def test_tomllib_import_error():
    mock_toml_content = """
    [project]
    version = "1.0.0"
    """

    with patch.dict("sys.modules", {"tomllib": None}):
        with patch("pathlib.Path.open", mock_open(read_data=mock_toml_content)):
            with patch("tomli.load") as mock_load:
                mock_load.return_value = {"project": {"version": "1.0.0"}}

                import djpress

                importlib.reload(djpress)  # Reload the module to apply the mock

                assert djpress.__version__ == "1.0.0"
