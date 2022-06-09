import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from local_qt_material import QtStyleTools
import logging
from pathlib import Path

log = logging.getLogger(__name__)

class ControlWindow(QWidget, QtStyleTools):

    def __init__(self, configuration):
        super().__init__()
        """ControlWindow init."""
        
        # Settings.
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.set_dark_mode()

        # Widget.
        self.controlTabWidget = QTabWidget()
        self.controlTabWidget.setTabPosition(QTabWidget.TabPosition(0))

        # Layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.controlTabWidget)
        self.setLayout(self.layout)

    def update_UI(self, newConfiguration):
        """Method to update the UI."""
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.set_size()
        self.set_dark_mode()
        log.info("Updated control window settings in UI.")
    
    def set_size(self):
        """Method to set size of window."""
        x = int(self.configuration["controlWindow"]["x"])
        y = int(self.configuration["controlWindow"]["y"])
        w = int(self.configuration["controlWindow"]["width"])
        h = int(self.configuration["controlWindow"]["height"])
        self.setGeometry(x, y, w, h)

    def set_dark_mode(self):
        """Method to set dark mode."""
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        
        # Get css directory.
        bundle_dir = Path(__file__).parents[1]
        path_to_css = os.path.abspath(os.path.join(bundle_dir,"CamLab.css"))
        with open(path_to_css) as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    def resizeEvent(self, event):
        """Override of Qt resizeEvent method."""
        self.configuration["controlWindow"]["width"] = int(self.width())
        self.configuration["controlWindow"]["height"] = int(self.height())

    def moveEvent(self, event):
        """Override of Qt moveEvent method."""
        position = self.geometry()
        self.configuration["controlWindow"]["x"] = int(position.x())
        self.configuration["controlWindow"]["y"] = int(position.y())

    def closeEvent(self, event):
        """Override of Qt closeEvent method."""
        self.configuration["controlWindow"]["visible"] = False

