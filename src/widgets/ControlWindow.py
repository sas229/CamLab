import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from src.local_qt_material import apply_stylesheet, QtStyleTools
import logging

log = logging.getLogger(__name__)

class ControlWindow(QWidget, QtStyleTools):

    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

        self.controlTabWidget = QTabWidget()
        self.controlTabWidget.setTabPosition(QTabWidget.TabPosition(0))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.controlTabWidget)
        self.setLayout(self.layout)

    def updateUI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setSize()
        self.setDarkMode()
        log.info("Updated control window settings in UI.")
    
    def setSize(self):
        x = int(self.configuration["controlWindow"]["x"])
        y = int(self.configuration["controlWindow"]["y"])
        w = int(self.configuration["controlWindow"]["width"])
        h = int(self.configuration["controlWindow"]["height"])
        self.setGeometry(x, y, w, h)

    def setDarkMode(self):
        # Set dark mode.
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('src/CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    def resizeEvent(self, event):
        # Save updated size in configuration.
        self.configuration["controlWindow"]["width"] = int(self.width())
        self.configuration["controlWindow"]["height"] = int(self.height())

    def moveEvent(self, event):
        # Save updated position in configuration.
        position = self.geometry()
        self.configuration["controlWindow"]["x"] = int(position.x())
        self.configuration["controlWindow"]["y"] = int(position.y())

    def closeEvent(self, event):
        self.configuration["controlWindow"]["visible"] = False

