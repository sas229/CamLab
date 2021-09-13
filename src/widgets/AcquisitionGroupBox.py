from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QTabWidget
from src.views import AcquisitionTableView
import logging

log = logging.getLogger(__name__)

class AcquisitionGroupBox(QGroupBox):

    def __init__(self):
        super().__init__() 
        self.setFixedHeight(335)
        self.setTitle("Acquisition")

        # Create TabWidget for acquisition tables.
        self.acquisitionTabWidget = QTabWidget()
        self.acquisitionTabWidget.setTabPosition(QTabWidget.TabPosition(0))
        layout = QVBoxLayout()
        layout.addWidget(self.acquisitionTabWidget)
        self.setLayout(layout)
        