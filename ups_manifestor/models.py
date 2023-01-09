"""Models for the UPS Manifestor application."""

import csv
from pathlib import Path

from . import api_requests
from .settings import Settings


class CurrentShipments:
    """Manages currently open shipments."""

    ID = "id"
    DESCRIPTION = "description"
    ORDER_NUMBER = "order_number"
    DESTINATION = "destination"
    PACKAGE_COUNT = "package_count"
    WEIGHT = "weight"
    VALUE = "value"
    shipment_keys = (
        DESCRIPTION,
        DESTINATION,
        PACKAGE_COUNT,
        WEIGHT,
        VALUE,
        ORDER_NUMBER,
    )

    def update(self):
        """Get currently open shipments from the server."""
        data = api_requests.CurrentShipmentsRequest().request()
        self.shipments = data["shipments"]

    def get_display_rows(self):
        """Return contents for the table display."""
        return [
            [shipment.get(col) for col in self.shipment_keys]
            for shipment in self.shipments
        ]

    def close_shipment(self, shipment_id):
        """Close all currently open shipments and return the ID of the created export."""
        data = api_requests.CloseShipment().request(shipment_id=shipment_id)
        return data["export_id"]


class ShipmentExports:
    """Manages existing shipment exports."""

    ID = "id"
    DESCRIPTION = "description"
    ORDER_NUMBERS = "order_numbers"
    DESTINATIONS = "destinations"
    PACKAGE_COUNT = "package_count"
    SHIPMENT_COUNT = "shipment_count"
    CREATED_AT = "created_at"

    export_keys = (
        DESCRIPTION,
        DESTINATIONS,
        SHIPMENT_COUNT,
        PACKAGE_COUNT,
        CREATED_AT,
        ORDER_NUMBERS,
    )

    def update(self):
        """Update the list of shipment exports."""
        data = api_requests.ShipmentExportsRequest().request()
        self.exports = data["exports"]

    def get_display_rows(self):
        """Return contents for the table display."""
        return [
            [export.get(col) for col in self.export_keys] for export in self.exports
        ]


class ShipmentFileManager:
    """Manage the UPS shipment files."""

    COMMODITIES_ORDER_NUMBER_COLUMN = 0
    COMMODITIES_START_ROW = 1
    COMMODITES_END_ROW = -1
    ADDRESS_ORDER_NUMBER_COLUMN = 17
    ADDRESS_START_ROW = 1
    ADDRESS_END_ROW = None

    def __init__(self):
        """Get file paths."""
        self.shipment_directory = Path(Settings.SHIPMENT_DIRECTORY)
        self.commodities_file_path = (
            self.shipment_directory / Settings.COMMODITIES_FILE_NAME
        )
        self.address_file_path = self.shipment_directory / Settings.ADDRESS_FILE_NAME

    def get_file_status(self, file_path, order_number_column, start_row, end_row):
        """Return a string representation of the status of a file."""
        if not file_path.is_file():
            return "Missing"
        else:
            try:
                data = self.read_csv(file_path)
                order_ids = [
                    row[order_number_column] for row in data[start_row:end_row]
                ]
                order_ids = sorted(list(set(order_ids)))
                return ", ".join(order_ids)
            except Exception:
                return "Invalid"

    def get_commodities_file_status(self):
        """Return a string representation of the comodities file."""
        return self.get_file_status(
            self.commodities_file_path,
            self.COMMODITIES_ORDER_NUMBER_COLUMN,
            self.COMMODITIES_START_ROW,
            self.COMMODITES_END_ROW,
        )

    def get_address_file_status(self):
        """Return a string representation of the address file."""
        return self.get_file_status(
            self.address_file_path,
            self.ADDRESS_ORDER_NUMBER_COLUMN,
            self.ADDRESS_START_ROW,
            self.ADDRESS_END_ROW,
        )

    def read_csv(self, path):
        """Return the contents of a .csv file."""
        with open(path, "r") as f:
            reader = csv.reader(f)
            data = list(reader)
        return data

    def update_shipping_files(self, export_id):
        """Replace the current shipping files."""
        self.update_comodities_file(export_id=export_id)
        self.update_address_file(export_id=export_id)

    def update_comodities_file(self, export_id):
        """Replace the comodities file."""
        self.update_file(
            export_id=export_id,
            request_class=api_requests.DownloadShipmentFile,
            target_path=self.commodities_file_path,
        )

    def update_address_file(self, export_id):
        """Replace the address file."""
        self.update_file(
            export_id=export_id,
            request_class=api_requests.DownloadAddressFile,
            target_path=self.address_file_path,
        )

    def update_file(self, export_id, request_class, target_path):
        """Download a .csv file and save it to target path."""
        response = request_class().request(export_id=export_id)
        with open(target_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
            file.flush()
