import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
# from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QFont
# from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QEvent, QLocale
from qt_material import apply_stylesheet, QtStyleTools
import logging

log = logging.getLogger(__name__)

class ControlWindow(QWidget, QtStyleTools):

    def __init__(self):
        super().__init__()
        self.darkMode = True
        self.setDarkMode()

        self.controlTabWidget = QTabWidget()
        self.controlTabWidget.setTabPosition(QTabWidget.TabPosition(0))

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.controlTabWidget)
        self.setLayout(self.layout)
        
    def setDarkMode(self):
        # Set dark mode.
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    # def resizeEvent(self, event):
        # Save updated size in configuration.
        # self.configuration["plots"][self.plotNumber]["width"] = int(self.width())
        # self.configuration["plots"][self.plotNumber]["height"] = int(self.height())

    # def moveEvent(self, event):
        # Save updated position in configuration.
        # position = self.geometry()
        # self.configuration["plots"][self.plotNumber]["x"] = int(position.x())
        # self.configuration["plots"][self.plotNumber]["y"] = int(position.y())

