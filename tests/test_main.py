from unittest import mock

import pytest

from main import main


@pytest.fixture(autouse=True)
def mock_application():
    with mock.patch("main.Application") as mock_application:
        yield mock_application


@pytest.fixture(autouse=True)
def mock_error_window():
    with mock.patch("main.ErrorWindow") as mock_error_window:
        yield mock_error_window


@pytest.fixture(autouse=True)
def mock_settings():
    with mock.patch("main.Settings") as mock_settings:
        yield mock_settings


def test_loads_settings(mock_settings):
    main()
    mock_settings.load_settings.assert_called_once_with()


def test_runs_application(mock_application):
    main()
    mock_application.assert_called_once_with()


def test_handles_errors(mock_application, mock_error_window):
    mock_application.side_effect = Exception
    main()
    mock_error_window.assert_called_once
