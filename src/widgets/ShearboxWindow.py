import os, sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QDialog, QPushButton
from PySide6.QtGui import QScreen
from PySide6.QtCore import Signal, Slot, QThread, QTimer
from manager import Manager
from widgets.ToolBar import ToolBar
from widgets.TabInterface import TabInterface
from widgets.ConfigurationTab import ConfigurationTab
from widgets.SequenceTab import SequenceTab
from widgets.StatusTab import StatusTab
from widgets.StatusGroupBox import StatusGroupBox
from dialogs import BusyDialog
import logging
from time import sleep
from pathlib import Path

log = logging.getLogger(__name__)

class ShearboxWindow(QMainWindow):
    shearboxWindowClosed = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self.button = QPushButton("Push here")
        self.button.clicked.connect(self.pressed)
        self.setCentralWidget(self.button)

    def pressed(self, checked):
        log.info("Shearbox button pressed.")

    def set_configuration(self, configuration):
        # Set the configuration.
        self.configuration = configuration
        if "shearbox" in self.configuration:
            pass

    def closeEvent(self, event):
        return super().closeEvent(event)