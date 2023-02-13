from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog, QToolButton, QMenu, QGridLayout, QPushButton
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, Slot
import logging

log = logging.getLogger(__name__)

class ToolBar(QToolBar):
    configure = Signal() 
    run = Signal() 
    loadConfiguration = Signal(str)
    saveConfiguration = Signal(str)
    
    def __init__(self):
        super().__init__()

        self.addSeparator()

        # Run test.
        self.runButton = QAction()
        self.runButton.setToolTip("Run test.")
        self.runButton.setVisible(True)
        self.addAction(self.runButton)

        self.addSeparator()

        # Show test results.
        self.resultsButton = QAction()
        self.resultsButton.setToolTip("Show test results.")
        self.resultsButton.setVisible(True)
        self.addAction(self.resultsButton)

    @Slot()
    def enableModeButton(self):
        self.modeButton.setEnabled(True)
        self.modeButton.setToolTip("Click to stop and configure." if self.running else "Click to run acquisition and control.")

    @Slot()
    def disableModeButton(self):
        self.modeButton.setEnabled(False)
        self.modeButton.setToolTip("Add devices to enable.")


    def changeMode(self):
        # Toggle running property, modeButton ToolTip and icon and visible state for all other ToolButtons as required.
        log.info("Acquisition and control mode enabled." if self.running else "Configuration mode enabled")
        self.running = not self.running
        self.modeButton.setIcon(QIcon("icon:/secondaryText/stop.svg" if self.running else "icon:/secondaryText/play_circle.svg"))
        self.modeButton.setToolTip("Click to stop and configure." if self.running else "Click to run acquisition and control.")
        self.refreshButton.setVisible(not self.refreshButton.isVisible())
        self.loadConfigButton.setVisible(not self.loadConfigButton.isVisible())
        self.saveConfigButton.setVisible(not self.saveConfigButton.isVisible())
        self.clearConfigButton.setVisible(not self.clearConfigButton.isVisible())
        self.newFileButton.setVisible(not self.newFileButton.isVisible())
        self.autozeroButton.setVisible(not self.autozeroButton.isVisible())
        self.clearPlotsButton.setVisible(not self.clearPlotsButton.isVisible())
        if self.running == True:    
            self.run.emit()
        else:
            self.configure.emit()

    @Slot()
    def updateIcons(self, darkMode):
        # Change appearance between light and dark modes.
        self.darkMode = darkMode
        self.modeButton.setIcon(QIcon("icon:/secondaryText/stop.svg" if self.running else "icon:/secondaryText/play_circle.svg"))
        self.addPlotButton.setIcon(QIcon("icon:/secondaryText/stacked_line_chart.svg"))
        self.extensionButton.setIcon(QIcon("icon:/secondaryText/extension.svg"))
        self.refreshButton.setIcon(QIcon("icon:/secondaryText/restart_alt.svg"))
        self.loadConfigButton.setIcon(QIcon("icon:/secondaryText/file_upload.svg"))
        self.saveConfigButton.setIcon(QIcon("icon:/secondaryText/file_download.svg"))
        self.clearConfigButton.setIcon(QIcon("icon:/secondaryText/clear.svg"))
        self.newFileButton.setIcon(QIcon("icon:/secondaryText/restore_page.svg"))
        self.autozeroButton.setIcon(QIcon("icon:/secondaryText/exposure_zero.svg"))
        self.clearPlotsButton.setIcon(QIcon("icon:/secondaryText/clear_all.svg"))
        self.darkModeButton.setIcon(QIcon("icon:/secondaryText/light_mode.svg" if self.darkMode else "icon:/secondaryText/dark_mode.svg"))
        self.darkModeButton.setToolTip("Click for light mode." if self.darkMode else "Click for dark mode.")

    def emitLoadConfiguration(self):
        # Method to select a configuration file to load and emit it as a signal.
        filename, _ = QFileDialog.getOpenFileName(self,"Open CamLab configuration file", "","Yaml files (*.yaml)")
        self.loadConfiguration.emit(filename)

    def emitSaveConfiguration(self):
        # Method to select a configuration file to save to and emit it as a signal.
        filename, _ = QFileDialog.getSaveFileName(self,"Save CamLab configuration file", "","Yaml files (*.yaml)")
        self.saveConfiguration.emit(filename)

    def emitDarkModeChanged(self):
        # Method to emit a signal indicating that the dark mode boolean has been toggled.
        self.darkModeChanged.emit(not self.darkMode)