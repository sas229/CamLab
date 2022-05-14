from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QTabWidget
from views import AcquisitionTableView
import logging

log = logging.getLogger(__name__)

class DeviceConfigurationGroupBox(QGroupBox):

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(750)
        self.setFixedHeight(500)
        self.setTitle("Device Configuration")

        # Create TabWidget for configuration tables.
        self.deviceConfigurationTabWidget = QTabWidget()
        self.deviceConfigurationTabWidget.setTabPosition(QTabWidget.TabPosition(0))
        layout = QVBoxLayout()
        layout.addWidget(self.deviceConfigurationTabWidget)
        self.setLayout(layout)

