"""Run the UPS Manifestor application."""

from .application import Application, ErrorWindow


def main():
    """Run the UPS Manifestor application."""
    try:
        Application()
    except Exception as e:
        ErrorWindow(e)


if __name__ == "__main__":
    main()
