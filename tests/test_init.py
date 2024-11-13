import importlib
import sys
from unittest.mock import mock_open, patch

import pytest


def test_tomllib_import_error():
    mock_toml_content = """
    [project]
    version = "1.0.0"
    """

    with patch.dict("sys.modules", {"tomllib": None}):
        with patch("pathlib.Path.open", mock_open(read_data=mock_toml_content)):
            if sys.version_info < (3, 11):
                # tomli only installed for Python 3.10 and below
                with patch("tomli.load") as mock_load:
                    mock_load.return_value = {"project": {"version": "1.0.0"}}
                    import djpress

                    importlib.reload(djpress)  # Reload the module to apply the mock
                    assert djpress.__version__ == "1.0.0"
            else:
                with pytest.raises((ImportError, TypeError)):  # TypeError for VS Code?
                    import djpress

                    importlib.reload(djpress)
