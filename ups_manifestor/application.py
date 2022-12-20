"""The main application."""

import PySimpleGUI as sg

from . import exceptions, models
from .settings import Settings


class Application:
    """The UPS Manifestor application."""

    TITLE = "UPS Manifestor"

    CREATE_SHIPMENT_EXPORT = "Create Shipment Export"
    REPROCESSS_SHIPMENT = "Reprocess Shipment"
    CURRENT_SHIPMENT_CANCEL = "current_shipment_cancel"
    CURRENT_SHIPMENT_TABLE = "current_shipment_table"
    SHIPMENT_EXPORT_TABLE = "shipment_export_table"
    SHIPMENT_EXPORT_CANCEL = "shipment_export_cancel"
    COMMODOTIES_FILE_STATUS = "comodities_file_status"
    ADDRESS_FILE_STATUS = "address_file_status"

    def __init__(self):
        """Initialise the application."""
        self.initialise_models()
        self.next_page = MainMenu
        self.current_page = MainMenu
        sg.theme(Settings.THEME)
        self.window = sg.Window(
            self.TITLE,
            layout=self.layout(),
            size=(Settings.WINDOW_WIDTH, Settings.WINDOW_HEIGHT),
        )
        self.mainloop()
        self.window.close()

    def initialise_models(self):
        """Load models."""
        self.current_shipments = models.CurrentShipments()
        self.shipment_exports = models.ShipmentExports()
        self.shipment_file_manager = models.ShipmentFileManager()
        self.current_shipments.update()
        self.shipment_exports.update()

    def change_page(self):
        """Swap columns to change the page layout."""
        self.window[f"column-{self.current_page.name}"].update(visible=False)
        self.window[f"column-{self.next_page.name}"].update(visible=True)
        self.next_page.update(self)
        self.update()
        self.current_page = self.next_page

    def mainloop(self):
        """Process the main application loop."""
        while True:
            try:
                self.current_page.mainloop(self)
            except exceptions.CloseProgramRequest:
                return
            self.change_page()

    def update(self):
        """Run between page changes."""
        self.update_shipment_file_status()

    def layout(self):
        """Return the application layout."""
        return [
            [
                sg.Column(
                    MainMenu.layout(), visible=True, key=f"column-{MainMenu.name}"
                ),
                sg.Column(
                    CurrentShipments.layout(),
                    visible=False,
                    key=f"column-{CurrentShipments.name}",
                ),
                sg.Column(
                    ShipmentExports.layout(),
                    visible=False,
                    key=f"column-{ShipmentExports.name}",
                ),
            ],
            [
                sg.Text("Comodities File:"),
                sg.Text(
                    self.shipment_file_manager.get_commodities_file_status(),
                    key=self.COMMODOTIES_FILE_STATUS,
                ),
            ],
            [
                sg.Text("Address File:"),
                sg.Text(
                    self.shipment_file_manager.get_address_file_status(),
                    key=self.ADDRESS_FILE_STATUS,
                ),
            ],
        ]

    def update_shipment_file_status(self):
        """Update the display of the current shipment files."""
        commodities_status_text = (
            self.shipment_file_manager.get_commodities_file_status()
        )
        self.window[self.COMMODOTIES_FILE_STATUS].update(value=commodities_status_text)
        address_status_text = self.shipment_file_manager.get_address_file_status()
        self.window[self.ADDRESS_FILE_STATUS].update(value=address_status_text)

    def update_current_shipments(self):
        """Update the current shipments page."""
        self.current_shipments.update()
        shipment_table_data = self.current_shipments.get_display_rows()
        self.window[self.CURRENT_SHIPMENT_TABLE].update(values=shipment_table_data)
        if len(shipment_table_data) == 0:
            self.window[self.CREATE_SHIPMENT_EXPORT].update(disabled=True)

    def update_shipment_exports(self):
        """Update the shipment exports page."""
        self.shipment_exports.update()
        shipment_table_data = self.shipment_exports.get_display_rows()
        self.window[self.SHIPMENT_EXPORT_TABLE].update(values=shipment_table_data)

    def update_shipping_files(self, export_index):
        """Replace the shipping files with one selected on the shipment exports page."""
        export = self.shipment_exports.exports[export_index]
        export_id = export[self.shipment_exports.ID]
        self.shipment_file_manager.update_shipping_files(export_id=export_id)

    def close_shipments(self):
        """Close open shipments and update the shipping files."""
        export_id = self.current_shipments.close_shipments()
        self.shipment_file_manager.update_shipping_files(export_id)


class ApplicationPage:
    """Base class for application pages."""

    @staticmethod
    def update(application):
        """Run before page is diplayed."""
        pass


class MainMenu(ApplicationPage):
    """Application main menu page."""

    name = "Main Menu"

    @staticmethod
    def layout():
        """Return the page layout."""
        return [
            [sg.Button(CurrentShipments.name)],
            [sg.Button(ShipmentExports.name)],
        ]

    @staticmethod
    def mainloop(application):
        """Process the main menu."""
        while True:
            event, _ = application.window.read()
            if event == CurrentShipments.name:
                application.next_page = CurrentShipments
                break
            if event == ShipmentExports.name:
                application.next_page = ShipmentExports
                break
            if event == sg.WIN_CLOSED:
                raise exceptions.CloseProgramRequest()


class CurrentShipments:
    """The current shipments page."""

    name = "Current Shipments"

    @staticmethod
    def mainloop(application):
        """Process the current shipments page."""
        while True:
            event, _ = application.window.read()
            if event == application.CREATE_SHIPMENT_EXPORT:
                application.close_shipments()
                application.next_page = MainMenu
                break
            if event == application.CURRENT_SHIPMENT_CANCEL:
                application.next_page = MainMenu
                break
            if event == sg.WIN_CLOSED:
                raise exceptions.CloseProgramRequest()

    @classmethod
    def layout(cls):
        """Return the page layout."""
        return [
            [sg.Text(CurrentShipments.name)],
            [cls.create_table()],
            [
                sg.Button(Application.CREATE_SHIPMENT_EXPORT),
                sg.Button("Cancel", key=Application.CURRENT_SHIPMENT_CANCEL),
            ],
        ]

    @classmethod
    def create_table(cls):
        """Return the page's table element."""
        headings = [
            "Shipment Order",
            "Destination",
            "Package Count",
            "Weight (Kg)",
            "Value",
            "Order Number",
        ]
        return sg.Table(
            values=[[]],
            headings=headings,
            auto_size_columns=False,
            col_widths=(35, 20, 10, 12, 10, 20),
            num_rows=22,
            key=Application.CURRENT_SHIPMENT_TABLE,
            enable_events=False,
            justification="left",
        )

    @staticmethod
    def update(application):
        """Update the current shipment list."""
        application.update_current_shipments()


class ShipmentExports:
    """The Shipment Exports page."""

    name = "Shipment Exports"

    @staticmethod
    def mainloop(application):
        """Process the shipment exports page."""
        while True:
            event, values = application.window.read()
            if event == application.SHIPMENT_EXPORT_TABLE:
                if len(values[application.SHIPMENT_EXPORT_TABLE]) == 1:
                    application.window[application.REPROCESSS_SHIPMENT].update(
                        disabled=False
                    )
                else:
                    application.window[application.REPROCESSS_SHIPMENT].update(
                        disabled=True
                    )
            if event == application.SHIPMENT_EXPORT_CANCEL:
                application.next_page = MainMenu
                break
            if event == application.REPROCESSS_SHIPMENT:
                export_index = values[application.SHIPMENT_EXPORT_TABLE][0]
                application.update_shipping_files(export_index=export_index)
                application.next_page = MainMenu
                break
            if event == sg.WIN_CLOSED:
                raise exceptions.CloseProgramRequest()

    @classmethod
    def layout(cls):
        """Return the page layout."""
        return [
            [sg.Text(CurrentShipments.name)],
            [cls.create_table()],
            [
                sg.Button(Application.REPROCESSS_SHIPMENT, disabled=True),
                sg.Button("Cancel", key=Application.SHIPMENT_EXPORT_CANCEL),
            ],
        ]

    @classmethod
    def create_table(cls):
        """Return the page's table element."""
        headings = [
            "Shipment Orders",
            "Destinations",
            "Shipment Count",
            "Package Count",
            "Created At",
            "Order Numbers",
        ]
        return sg.Table(
            values=[[]],
            headings=headings,
            auto_size_columns=False,
            col_widths=(40, 15, 12, 12, 15, 20),
            num_rows=22,
            key=Application.SHIPMENT_EXPORT_TABLE,
            enable_events=True,
            justification="left",
        )

    @staticmethod
    def update(application):
        """Update the shipment exports list."""
        application.update_shipment_exports()


class ErrorWindow:
    """Window to display errors."""

    TITLE = "UPS Manifestor Error"
    OK = "Ok"

    def __init__(self, exception):
        """Initialise the window."""
        self.exception = exception
        self.message = str(self.exception)
        self.window = sg.Window(self.TITLE, layout=self.layout(), size=(640, 480))
        self.mainloop()

    def mainloop(self):
        """Raise an exception when the window is closed."""
        while True:
            event, values = self.window.read()
            if event == self.OK:
                break
            if event == sg.WIN_CLOSED:
                break
        self.window.close()
        raise self.exception

    def layout(self):
        """Return the window layout."""
        return [[sg.Text("ERROR")], [sg.Text(self.message)], [sg.Button(self.OK)]]
