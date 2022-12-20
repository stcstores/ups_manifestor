"""Application settings for the UPS Manifestor application."""

from pathlib import Path

import toml


class Settings:
    """Class for managing application settings."""

    PROTOCOL = None
    DOMAIN = None
    TOKEN = None
    SHIPMENT_DIRECTORY = None
    COMMODITIES_FILE_NAME = None
    ADDRESS_FILE_NAME = None
    WINDOW_WIDTH = None
    WINDOW_HEIGHT = None
    THEME = None

    settings_file_path = Path.cwd() / "settings.toml"

    @classmethod
    def load_settings(cls):
        """Read application settings from settings_file_path."""
        with open(cls.settings_file_path, "r") as f:
            SETTINGS = toml.load(f)
        cls.PROTOCOL = SETTINGS["PROTOCOL"]
        cls.DOMAIN = SETTINGS["DOMAIN"]
        cls.TOKEN = SETTINGS["TOKEN"]
        cls.SHIPMENT_DIRECTORY = SETTINGS["SHIPMENT_DIRECTORY"]
        cls.COMMODITIES_FILE_NAME = SETTINGS["COMMODITIES_FILE_NAME"]
        cls.ADDRESS_FILE_NAME = SETTINGS["ADDRESS_FILE_NAME"]
        cls.WINDOW_WIDTH = SETTINGS["WINDOW_WIDTH"]
        cls.WINDOW_HEIGHT = SETTINGS["WINDOW_HEIGHT"]
        cls.THEME = SETTINGS["THEME"]
