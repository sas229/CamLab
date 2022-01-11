from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QTabWidget
from src.views import AcquisitionTableView
import logging

log = logging.getLogger(__name__)

class ControlGroupBox(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(70)
        self.setTitle("Control")

        # Create TabWidget for acquisition tables.
        self.controlTabWidget = QTabWidget()
        self.controlTabWidget.setTabPosition(QTabWidget.TabPosition(0))
        layout = QVBoxLayout()
        layout.addWidget(self.controlTabWidget)
        self.setLayout(layout)