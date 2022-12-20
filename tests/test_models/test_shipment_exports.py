import pytest

from ups_manifestor.models import ShipmentExports


@pytest.fixture
def export():
    return {
        "id": 154,
        "description": "shipment description text",
        "order_numbers": "AAA1554",
        "destinations": "shipment destination",
        "package_count": 5,
        "shipment_count": 2,
        "created_at": "22 Dec 2022",
    }


def test_update_method_makes_request(mock_api_requests):
    ShipmentExports().update()
    mock_api_requests.ShipmentExportsRequest.assert_called_once_with()
    mock_api_requests.ShipmentExportsRequest.return_value.request.assert_called_once_with()


def test_update_method_sets_exports(mock_api_requests):
    current_shipments = ShipmentExports()
    current_shipments.update()
    assert (
        current_shipments.exports
        == mock_api_requests.ShipmentExportsRequest.return_value.request.return_value[
            "exports"
        ]
    )


def test_get_display_rows_method(export):
    current_shipments = ShipmentExports()
    current_shipments.exports = [export]
    expected = [
        [
            "shipment description text",
            "shipment destination",
            2,
            5,
            "22 Dec 2022",
            "AAA1554",
        ]
    ]
    assert current_shipments.get_display_rows() == expected
