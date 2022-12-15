"""Exception classes for the UPS Manifestor application."""


class CloseProgramRequest(Exception):
    """Raised when the application should close."""

    pass


class HTTPRequestError(Exception):
    """Raised when an HTTP request fails."""

    def __init__(self, url, response):
        """Initialise self."""
        message = f"Error making request to {url}."
        if response is not None:
            message = f"{message} Status {response.status_code}."
        super().__init__(message)
