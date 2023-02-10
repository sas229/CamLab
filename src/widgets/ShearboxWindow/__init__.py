import os, sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QDialog, QPushButton
from PySide6.QtGui import QScreen
from PySide6.QtCore import Signal, Slot, QThread, QTimer
from local_qt_material import QtStyleTools
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

class ShearboxWindow(QMainWindow, QtStyleTools):
    configurationChanged = Signal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shear Box")
        # self.setMinimumSize(800, 600)
        # self.resize(1000,800)

        # Extract the configuration to generate initial UI setup.
        # self.configuration = self.manager.configuration
        # self.set_theme()

        self.button = QPushButton("Push here")
        self.button.clicked.connect(self.pressed)
        self.setCentralWidget(self.button)


    def set_theme(self):
        """Method to set the theme and apply the qt-material stylesheet."""
        self.darkMode = self.configuration["global"]["darkMode"]
        # Set the darkmode. 
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        
        # Get css directory.
        bundle_dir = Path(__file__).parents[2]
        path_to_css = os.path.abspath(os.path.join(bundle_dir,"CamLab.css"))
        with open(path_to_css) as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))
        
    def pressed(self, checked):
        log.info("Shearbox button pressed.")

    def set_configuration(self, configuration):
        # Set the configuration.
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.set_theme()
    
    def update_configuration(self):
        self.configurationChanged.emit(self.configuration)

    def closeEvent(self, event):
        return super().closeEvent(event)