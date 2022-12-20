import csv
from pathlib import Path
from unittest import mock

import pytest

from ups_manifestor.models import ShipmentFileManager


@pytest.fixture
def shipment_directory(tmpdir):
    return tmpdir


@pytest.fixture
def comodities_file_name():
    return "commoditites.csv"


@pytest.fixture
def address_file_name():
    return "address.csv"


@pytest.fixture
def rows():
    return [
        ["Col 1", "Col 2", "Col 3"],
        ["1", "A", "B"],
        ["2", "C", "D"],
        ["3", "E", "F"],
    ]


@pytest.fixture
def export_id():
    return 132


@pytest.fixture
def csv_file(shipment_directory, rows):
    path = Path(shipment_directory) / "test.csv"
    with open(path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return path


@pytest.fixture(autouse=True)
def mock_settings(shipment_directory, comodities_file_name, address_file_name):
    with mock.patch("ups_manifestor.models.Settings") as mock_settings:
        mock_settings.SHIPMENT_DIRECTORY = str(shipment_directory)
        mock_settings.COMMODITIES_FILE_NAME = comodities_file_name
        mock_settings.ADDRESS_FILE_NAME = address_file_name
        yield mock_settings


@pytest.fixture
def mock_read_csv(rows):
    with mock.patch(
        "ups_manifestor.models.ShipmentFileManager.read_csv"
    ) as mock_read_csv:
        mock_read_csv.return_value = rows
        yield mock_read_csv


@pytest.fixture
def mock_get_file_status():
    with mock.patch(
        "ups_manifestor.models.ShipmentFileManager.get_file_status"
    ) as mock_get_file_status:
        yield mock_get_file_status


@pytest.fixture
def mock_update_comodities_file():
    with mock.patch(
        "ups_manifestor.models.ShipmentFileManager.update_comodities_file"
    ) as mock_update_comodities_file:
        yield mock_update_comodities_file


@pytest.fixture
def mock_update_address_file():
    with mock.patch(
        "ups_manifestor.models.ShipmentFileManager.update_address_file"
    ) as mock_update_address_file:
        yield mock_update_address_file


@pytest.fixture
def mock_update_file():
    with mock.patch(
        "ups_manifestor.models.ShipmentFileManager.update_file"
    ) as mock_update_file:
        yield mock_update_file


@pytest.fixture
def test_file_contents():
    return "contents".encode()


@pytest.fixture
def mock_download_file_request_class(test_file_contents):
    mock_request = mock.Mock()
    mock_request.return_value.request.return_value.iter_content.return_value = [
        test_file_contents
    ]
    return mock_request


def test_sets_shipment_directory(shipment_directory):
    assert ShipmentFileManager().shipment_directory == shipment_directory


def test_sets_commodities_file_path(shipment_directory, comodities_file_name):
    expected = shipment_directory / comodities_file_name
    assert ShipmentFileManager().commodities_file_path == expected


def test_sets_address_file_path(shipment_directory, address_file_name):
    expected = shipment_directory / address_file_name
    assert ShipmentFileManager().address_file_path == expected


def test_get_file_status_returns_missing_file_file_does_not_exist(shipment_directory):
    returned_value = ShipmentFileManager().get_file_status(
        Path(shipment_directory / "test.csv"), 0, 0, 0
    )
    assert returned_value == "Missing"


@pytest.mark.parametrize(
    "order_number_column,start_row,end_row,expected",
    [
        (0, 0, None, "1, 2, 3, Col 1"),
        (0, 1, -1, "1, 2"),
        (1, 0, None, "A, C, Col 2, E"),
    ],
)
def test_get_file_status(
    order_number_column, start_row, end_row, expected, mock_read_csv
):
    returned_value = ShipmentFileManager().get_file_status(
        Path(__file__), order_number_column, start_row, end_row
    )
    assert returned_value == expected


def test_get_file_status_error_response(mock_read_csv):
    mock_read_csv.side_effect = Exception
    returned_value = ShipmentFileManager().get_file_status(Path(__file__), 0, 0, None)
    assert returned_value == "Invalid"


def test_get_commodities_file_status(mock_get_file_status):
    shipment_file_manager = ShipmentFileManager()
    shipment_file_manager.get_commodities_file_status()
    mock_get_file_status.assert_called_once_with(
        shipment_file_manager.commodities_file_path,
        shipment_file_manager.COMMODITIES_ORDER_NUMBER_COLUMN,
        shipment_file_manager.COMMODITIES_START_ROW,
        shipment_file_manager.COMMODITES_END_ROW,
    )


def test_get_address_file_status(mock_get_file_status):
    shipment_file_manager = ShipmentFileManager()
    shipment_file_manager.get_address_file_status()
    mock_get_file_status.assert_called_once_with(
        shipment_file_manager.address_file_path,
        shipment_file_manager.ADDRESS_ORDER_NUMBER_COLUMN,
        shipment_file_manager.ADDRESS_START_ROW,
        shipment_file_manager.ADDRESS_END_ROW,
    )


def test_read_csv(csv_file, rows):
    assert ShipmentFileManager().read_csv(csv_file) == rows


def test_update_shipping_files(
    mock_update_comodities_file, mock_update_address_file, export_id
):
    ShipmentFileManager().update_shipping_files(export_id)
    mock_update_comodities_file.assert_called_once_with(export_id=export_id)
    mock_update_address_file.asser_called_once_with(export_id=export_id)


def test_update_comodites_file(mock_api_requests, mock_update_file, export_id):
    shipment_file_manager = ShipmentFileManager()
    shipment_file_manager.update_comodities_file(export_id)
    mock_update_file.assert_called_once_with(
        export_id=export_id,
        request_class=mock_api_requests.DownloadShipmentFile,
        target_path=shipment_file_manager.commodities_file_path,
    )


def test_update_address_file(mock_api_requests, mock_update_file, export_id):
    shipment_file_manager = ShipmentFileManager()
    shipment_file_manager.update_address_file(export_id)
    mock_update_file.assert_called_once_with(
        export_id=export_id,
        request_class=mock_api_requests.DownloadAddressFile,
        target_path=shipment_file_manager.address_file_path,
    )


def test_update_file_makes_request(
    shipment_directory, export_id, mock_download_file_request_class
):
    ShipmentFileManager().update_file(
        export_id,
        mock_download_file_request_class,
        Path(shipment_directory) / "test.csv",
    )
    mock_download_file_request_class.assert_called_once_with()
    mock_download_file_request_class.return_value.request.assert_called_once_with(
        export_id=export_id
    )


def test_update_file_writes_file(
    shipment_directory, export_id, mock_download_file_request_class, test_file_contents
):
    path = Path(shipment_directory) / "test.csv"
    ShipmentFileManager().update_file(
        export_id,
        mock_download_file_request_class,
        path,
    )
    assert path.is_file()
    with open(path, "rb") as f:
        assert f.read() == test_file_contents
