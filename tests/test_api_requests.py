from unittest import mock

import pytest

from ups_manifestor import api_requests, exceptions


@pytest.fixture(autouse=True)
def mock_requests():
    with mock.patch("ups_manifestor.api_requests.requests") as mock_requests:
        yield mock_requests


@pytest.fixture
def mock_make_request():
    with mock.patch(
        "ups_manifestor.api_requests.BaseRequest.make_request"
    ) as mock_make_request:
        yield mock_make_request


@pytest.fixture
def mock_process_response():
    with mock.patch(
        "ups_manifestor.api_requests.BaseRequest.process_response"
    ) as mock_process_response:
        yield mock_process_response


@pytest.fixture
def mock_make_url():
    with mock.patch(
        "ups_manifestor.api_requests.BaseRequest.make_url"
    ) as mock_make_url:
        yield mock_make_url


@pytest.fixture
def mock_request_data():
    with mock.patch(
        "ups_manifestor.api_requests.BaseRequest.request_data"
    ) as mock_request_data:
        yield mock_request_data


@pytest.fixture
def base_request():
    request = api_requests.BaseRequest()
    request.PATH = "page"
    return request


def test_make_url(load_settings):
    assert api_requests.BaseRequest().make_url("page") == "https://test.com/page"


def test_request_data(load_settings):
    assert api_requests.BaseRequest().request_data() == {"token": "TEST_TOKEN"}


def test_process_response():
    response = mock.Mock(json=mock.Mock())
    returned_value = api_requests.BaseRequest().process_response(response)
    response.json.assert_called_once()
    assert returned_value == response.json.return_value


def test_request_method(mock_make_request, mock_process_response):
    api_requests.BaseRequest().request()
    mock_make_request.assert_called_once()
    mock_process_response.assert_called_once_with(mock_make_request.return_value)


def test_make_request_calls_make_url(mock_make_url, mock_request_data, base_request):
    base_request.make_request()
    mock_make_url.assert_called_once_with("page")


def test_make_request_calls_request_data(
    mock_make_url, mock_request_data, base_request
):
    base_request.make_request("ONE", two=2)
    mock_request_data.assert_called_once_with("ONE", two=2)


def test_make_request_makes_request(
    mock_requests, mock_make_url, mock_request_data, base_request
):
    base_request.make_request()
    mock_requests.post.assert_called_once_with(
        mock_make_url.return_value, mock_request_data.return_value
    )


def test_make_request_checks_status_code(
    mock_requests, mock_make_url, mock_request_data, base_request
):
    base_request.make_request()
    mock_requests.post.return_value.raise_for_status.assert_called_once_with()


def test_make_request_raises_exception_if_request_fails(
    mock_requests, mock_make_url, mock_request_data, base_request
):
    mock_requests.post.side_effect = Exception
    with pytest.raises(exceptions.HTTPRequestError):
        base_request.make_request()


def test_make_request_raises_exception_for_exception_status_code(
    mock_requests, mock_make_url, mock_request_data, base_request
):
    mock_requests.post.return_value.raise_for_status.side_effect = Exception
    with pytest.raises(exceptions.HTTPRequestError):
        base_request.make_request()


def test_make_request_returns_response(
    mock_requests, mock_make_url, mock_request_data, base_request
):
    assert base_request.make_request() == mock_requests.post.return_value


class TestBaseFileDownloadRequest:
    def test_request_data(self, load_settings):
        export_id = 11
        assert api_requests.BaseFileDownloadRequest().request_data(
            export_id=export_id
        ) == {
            "token": "TEST_TOKEN",
            "export_id": export_id,
        }

    def test_process_response(self):
        response = mock.Mock()
        returned_value = api_requests.BaseFileDownloadRequest().process_response(
            response
        )
        assert returned_value == response
