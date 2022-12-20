"""Run the UPS Manifestor application."""

from ups_manifestor.application import Application, ErrorWindow
from ups_manifestor.settings import Settings


def main():
    """Run the UPS Manifestor application."""
    Settings.load_settings()
    try:
        Application()
    except Exception as e:
        ErrorWindow(e)


if __name__ == "__main__":
    main()
