from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
import numpy as np
import logging

log = logging.getLogger(__name__)

class PicoW_FHA_Settings(QWidget):

    def __init__(self, name, *args, **kwargs):
        """PicoW_FHA_Settings init."""
        super().__init__(*args, **kwargs)


        self.label = QLabel("THIS TAB IS LEFT BLANK INTENTIONALLY TO BE DEVELOPED")


        # Settings layout.
        self.settingsLayout = QGridLayout()

        self.settingsLayout.addWidget(self.label, 0, 0)
        self.settingsLayout.setRowStretch(self.settingsLayout.rowCount(), 1)
        self.settingsLayout.setColumnStretch(self.settingsLayout.columnCount(), 1)

        self.setLayout(self.settingsLayout)