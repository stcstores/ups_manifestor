"""HTTP requesters for the UPS Manifestor application."""

import requests

from . import exceptions
from .settings import Settings


class BaseRequest:
    """Base class for HTTP requests."""

    def make_url(self, path):
        """Return the request URL."""
        return f"{Settings.PROTOCOL}://{Settings.DOMAIN}/{path}"

    def request_data(self, *args, **kwargs):
        """Return request data."""
        return {"token": Settings.TOKEN}

    def make_request(self, *args, **kwargs):
        """Make an HTTP request and return the response."""
        url = self.make_url(self.PATH)
        data = self.request_data(*args, **kwargs)
        response = None
        try:
            response = requests.post(url, data)
            response.raise_for_status()
        except Exception:
            raise exceptions.HTTPRequestError(url, response)
        else:
            return response

    def process_response(self, response, *args, **kwargs):
        """Return the response JSON."""
        return response.json()

    def request(self, *args, **kwargs):
        """Make and process an HTTP request."""
        response = self.make_request(*args, **kwargs)
        return self.process_response(response, *args, **kwargs)


class CurrentShipmentsRequest(BaseRequest):
    """Request for getting currently open shipments."""

    PATH = "fba/api/current_shipments"


class ShipmentExportsRequest(BaseRequest):
    """Request for getting recent shipment exports."""

    PATH = "fba/api/shipment_exports"


class BaseFileDownloadRequest(BaseRequest):
    """Base class for file download requests."""

    def request_data(self, *args, **kwargs):
        """Return the request data."""
        data = super().request_data(*args, **kwargs)
        data["export_id"] = kwargs["export_id"]
        return data

    def process_response(self, response, *args, **kwargs):
        """Return the response object."""
        return response


class DownloadShipmentFile(BaseFileDownloadRequest):
    """Request for downloading an exported shipment file."""

    PATH = "fba/api/download_shipment_file"


class DownloadAddressFile(BaseFileDownloadRequest):
    """Request for downloading a exported address file."""

    PATH = "fba/api/download_address_file"


class CloseShipment(BaseRequest):
    """Request to close open shipments."""

    PATH = "fba/api/close_shipment"

    def request_data(self, *args, **kwargs):
        """Return the request data."""
        data = super().request_data(*args, **kwargs)
        data["shipment_id"] = kwargs["shipment_id"]
        return data
