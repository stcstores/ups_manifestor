from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def mock_api_requests():
    with mock.patch("ups_manifestor.models.api_requests") as mock_api_requests:
        yield mock_api_requests
