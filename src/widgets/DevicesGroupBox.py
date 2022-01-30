from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from src.views import DeviceTableView
import logging

log = logging.getLogger(__name__)

class DevicesGroupBox(QGroupBox):

    def __init__(self, configuration):
        super().__init__() 
        self.configuration = configuration
        self.setFixedHeight(163)
        self.setTitle("Devices")

        # Create device table view.
        self.deviceTableView = DeviceTableView(self.configuration)

        # Create layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.deviceTableView)
        self.setLayout(self.layout)
        