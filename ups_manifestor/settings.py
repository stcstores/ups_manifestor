"""Application settings for the UPS Manifestor application."""

from pathlib import Path

import toml

settings_file_path = Path.cwd() / "settings.toml"

with open(settings_file_path, "r") as f:
    SETTINGS = toml.load(f)

PROTOCOL = SETTINGS["PROTOCOL"]
DOMAIN = SETTINGS["DOMAIN"]
TOKEN = SETTINGS["TOKEN"]
SHIPMENT_DIRECTORY = SETTINGS["SHIPMENT_DIRECTORY"]
COMMODITIES_FILE_NAME = SETTINGS["COMMODITIES_FILE_NAME"]
ADDRESS_FILE_NAME = SETTINGS["ADDRESS_FILE_NAME"]
WINDOW_WIDTH = SETTINGS["WINDOW_WIDTH"]
WINDOW_HEIGHT = SETTINGS["WINDOW_HEIGHT"]
THEME = SETTINGS["THEME"]
