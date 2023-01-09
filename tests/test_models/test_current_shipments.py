import pytest

from ups_manifestor.models import CurrentShipments


@pytest.fixture
def shipment():
    return {
        "id": 154,
        "description": "shipment description text",
        "order_number": "AAA1554",
        "destination": "shipment destination",
        "package_count": 5,
        "weight": 250,
        "value": "25.60",
    }


@pytest.fixture
def shipment_id():
    return 12


def test_update_method_makes_request(mock_api_requests):
    CurrentShipments().update()
    mock_api_requests.CurrentShipmentsRequest.assert_called_once_with()
    mock_api_requests.CurrentShipmentsRequest.return_value.request.assert_called_once_with()


def test_update_method_sets_shipments(mock_api_requests):
    current_shipments = CurrentShipments()
    current_shipments.update()
    assert (
        current_shipments.shipments
        == mock_api_requests.CurrentShipmentsRequest.return_value.request.return_value[
            "shipments"
        ]
    )


def test_get_display_rows_method(shipment):
    current_shipments = CurrentShipments()
    current_shipments.shipments = [shipment]
    expected = [
        [
            "shipment description text",
            "shipment destination",
            5,
            250,
            "25.60",
            "AAA1554",
        ]
    ]
    assert current_shipments.get_display_rows() == expected


def test_close_shipments_method_makes_request(mock_api_requests, shipment_id):
    CurrentShipments().close_shipment(shipment_id=shipment_id)
    mock_api_requests.CloseShipment.assert_called_once_with()
    mock_api_requests.CloseShipment.return_value.request.assert_called_once_with(
        shipment_id=shipment_id
    )


def test_close_shipments_method_returns_export_id(mock_api_requests, shipment_id):
    returned_value = CurrentShipments().close_shipment(shipment_id=shipment_id)
    assert (
        returned_value
        == mock_api_requests.CloseShipment.return_value.request.return_value[
            "export_id"
        ]
    )
