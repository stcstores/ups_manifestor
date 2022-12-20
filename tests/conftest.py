from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def use_test_settings():
    test_settings_path = Path(__file__).parent / "test_settings.toml"
    with mock.patch(
        "ups_manifestor.settings.Settings.settings_file_path", test_settings_path
    ):
        yield


@pytest.fixture
def load_settings(use_test_settings):
    from ups_manifestor.settings import Settings

    Settings.load_settings()
