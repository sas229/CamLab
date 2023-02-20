import os, sys
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, Slot
from local_qt_material import QtStyleTools
from widgets.ShearboxWindow._TabUtilities import TabUtilities
from widgets.ShearboxWindow.Tabs import TabInterface
from widgets.ShearboxWindow.ToolBar import ToolBar
import logging
from time import sleep
from pathlib import Path

log = logging.getLogger(__name__)

class ShearboxWindow(QMainWindow, TabUtilities, QtStyleTools):
    configurationChanged = Signal(dict)
    def __init__(self, configuration):
        """Main window containing shear box setup

        Arguments:
            configuration -- configuration for initial setup
        """
        super().__init__()
        self.setWindowTitle("Shear Box")
        self.setMinimumSize(800, 600)

        self.configuration = configuration
        self.running = False

        self.Layout = QVBoxLayout()
        self.toolbar = ToolBar()

        self.specimens = QSpinBox()
        self.specimens.setMinimum(1)
        self.specimens.setMaximum(4)
        self.specimens.lineEdit().setReadOnly(True)
        self.specimens.setValue(self.configuration["shearbox"]["Number of Specimens"])

        self.topbar = QWidget()
        self.topbarlayout = QHBoxLayout()
        self.topbarlayout.addWidget(QLabel("Number of Specimens"),0)
        self.topbarlayout.addWidget(self.specimens,0)
        self.topbarlayout.addStretch(2)
        self.topbarlayout.addWidget(self.toolbar,0)
        self.topbar.setLayout(self.topbarlayout)


        self.tabs = TabInterface()

        self.addItemstoComboboxes()

        self.Layout.addWidget(self.topbar,0)
        self.Layout.addWidget(self.tabs,2)

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.Layout)
        self.setCentralWidget(self.centralWidget)

        self.set_theme()

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

    def updateIcons(self, darkMode):
        """Change appearance between light and dark modes.

        Arguments:
            darkMode -- if dark mode is selected
        """
        self.darkMode = darkMode
        self.toolbar.runButton.setIcon(QIcon("icon:/secondaryText/pause_circle.svg" if self.running else "icon:/secondaryText/play_circle.svg"))
        self.toolbar.loadConfigButton.setIcon(QIcon("icon:/secondaryText/file_upload.svg"))
        self.toolbar.saveConfigButton.setIcon(QIcon("icon:/secondaryText/file_download.svg"))

    @Slot(int)    
    def specimens_number(self, num):
        """Change number of specimens by one

        Arguments:
            num -- new number of specimens
        """
        if num < self.configuration["shearbox"]["Number of Specimens"]:
            self.tabs.specimen.tabs.close_tab(num)
        else:
            specimen = f"Specimen {num}"
            self.tabs.specimen.tabs.add_persistent_tab(self.tabs.specimen.tabs.specimens[specimen]["widget"], specimen)
        self.configuration["shearbox"]["Number of Specimens"] = num
        self.configurationChanged.emit(self.configuration)

    @Slot(dict)
    def set_configuration(self, configuration):
        """Set the configuration

        Arguments:
            configuration -- the configuration to be set
        """
        
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]

        self.set_theme()
        self.updateIcons(self.darkMode)

        self.move(self.configuration["shearbox"]["x"], self.configuration["shearbox"]["y"])
        self.resize(self.configuration["shearbox"]["width"], self.configuration["shearbox"]["height"])

    def closeEvent(self, event):
        self.remove_connections()

        if "shearbox" in self.configuration.keys():
            self.configuration["shearbox"]["x"] = self.frameGeometry().x()
            self.configuration["shearbox"]["y"] = self.frameGeometry().y()
            self.configuration["shearbox"]["width"] = self.frameGeometry().width()
            self.configuration["shearbox"]["height"] = self.frameGeometry().height()

            self.configurationChanged.emit(self.configuration)

        log.info("Closing ShearBox")
        return super().closeEvent(event)