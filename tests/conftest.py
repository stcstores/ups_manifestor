from unittest import mock

import pytest


@pytest.fixture()
def mock_settings():
    with mock.patch("ups_manifestor.api_requests.settings") as settings:
        settings.PROTOCOL = "https"
        settings.DOMAIN = "test.com"
        settings.TOKEN = "TEST_TOKEN"
        yield settings
