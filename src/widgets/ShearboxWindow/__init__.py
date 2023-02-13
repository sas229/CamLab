import os, sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog, QPushButton, QLabel, QSpacerItem, QSpinBox
from PySide6.QtGui import QScreen, QAction
from PySide6.QtCore import Signal, Slot, QThread, QTimer
from local_qt_material import QtStyleTools
from widgets.ShearboxWindow.Tabs import TabInterface
from widgets.ShearboxWindow.ToolBar import ToolBar
import logging
from time import sleep
from pathlib import Path

log = logging.getLogger(__name__)

class ShearboxWindow(QMainWindow, QtStyleTools):
    configurationChanged = Signal(dict)
    def __init__(self, configuration):
        super().__init__()
        self.setWindowTitle("Shear Box")
        self.setMinimumSize(800, 600)

        self.configuration = configuration

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
        # for i in range(1,5):
        #     if i <= self.configuration["shearbox"]["Number of Specimens"]:
        #         self.tabs.setTabEnabled(i-1, True)
        #     else:
        #         self.tabs.setTabEnabled(i-1, False)

        self.Layout.addWidget(self.topbar,0)
        self.Layout.addWidget(self.tabs,2)

        self.specimens.valueChanged.connect(self.specimens_number)


        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.Layout)
        self.setCentralWidget(self.centralWidget)


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
        
    def specimens_number(self):
        self.specimens.lineEdit().deselect()
        self.configuration["shearbox"]["Number of specimens"] = self.specimens.value()
        # for i in range(1,5):
        #     if i <= self.configuration["shearbox"]["Number of Specimens"]:
        #         self.tabs.setTabEnabled(i-1, True)
        #     else:
        #         self.tabs.setTabEnabled(i-1, False)
        self.update_configuration()

    def set_configuration(self, configuration):
        # Set the configuration.
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]

        self.set_theme()
        self.move(self.configuration["shearbox"]["x"], self.configuration["shearbox"]["y"])
        self.resize(self.configuration["shearbox"]["width"], self.configuration["shearbox"]["height"])
    
    def update_configuration(self):
        self.configurationChanged.emit(self.configuration)

    def closeEvent(self, event):
        self.configuration["shearbox"]["x"] = self.frameGeometry().x()
        self.configuration["shearbox"]["y"] = self.frameGeometry().y()
        self.configuration["shearbox"]["width"] = self.frameGeometry().width()
        self.configuration["shearbox"]["height"] = self.frameGeometry().height()

        self.update_configuration()

        return super().closeEvent(event)