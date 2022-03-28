from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from src.views import DeviceTableView
import logging

log = logging.getLogger(__name__)

class DevicesGroupBox(QGroupBox):

    def __init__(self, configuration):
        super().__init__() 
        self.configuration = configuration
        self.setMinimumWidth(750)
        self.setFixedHeight(295)
        self.setTitle("Devices")

        # Create device table view.
        self.deviceTableView = DeviceTableView()
        self.deviceTableView.setColumnWidth(0, 50)
        self.deviceTableView.setColumnWidth(1, 50)
        self.deviceTableView.setColumnWidth(2, 30)
        self.deviceTableView.setColumnWidth(3, 50)
        self.deviceTableView.setColumnWidth(4, 150)
        self.deviceTableView.setColumnWidth(5, 50)

        # Create layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.deviceTableView)
        self.setLayout(self.layout)
        