from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog, QToolButton, QMenu
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
        self.darkMode = True
        self.running = False

        # Mode QAction.
        self.modeButton = QAction(parent=None)
        self.modeButton.setToolTip("Add devices to enable.")
        self.modeButton.setEnabled(False)
        self.addAction(self.modeButton)

        self.addSeparator()

        # Add plot QAction.
        self.addPlotButton = QAction()
        self.addPlotButton.setToolTip("Click to add plot.")
        self.addAction(self.addPlotButton)

        # Set up extensions menu
        self.extensionsMenu = QMenu()
        self.extensionsMenu.addAction("ShearBox")

        # Open extension QToolButton.
        self.extensionButton = QToolButton()
        self.extensionButton.setToolTip("Click to open extension.")
        self.extensionButton.setMenu(self.extensionsMenu)
        self.extensionButton.setPopupMode(QToolButton.InstantPopup)
        self.addWidget(self.extensionButton)

        self.addSeparator()

        # Refresh devices QAction.
        self.refreshButton = QAction()
        self.refreshButton.setToolTip("Refresh device list.")
        self.refreshButton.setVisible(True)
        self.addAction(self.refreshButton)

        # Load configuration QAction.
        self.loadConfigButton = QAction()
        self.loadConfigButton.setToolTip("Click to load a configuration.")
        self.loadConfigButton.setVisible(True)
        self.addAction(self.loadConfigButton)

        # Save configuration QAction.
        self.saveConfigButton = QAction()
        self.saveConfigButton.setToolTip("Click to save the current configuration.")
        self.saveConfigButton.setVisible(True)
        self.addAction(self.saveConfigButton)

        # Clear configuration QAction.
        self.clearConfigButton = QAction()
        self.clearConfigButton.setToolTip("Click to clear the current configuration.")
        self.clearConfigButton.setVisible(True)
        self.addAction(self.clearConfigButton)

        # New file QAction.
        self.newFileButton = QAction()
        self.newFileButton.setToolTip("Click to start a new output file.")
        self.newFileButton.setVisible(False)
        self.addAction(self.newFileButton)

        # Autozero QAction.
        self.autozeroButton = QAction()
        self.autozeroButton.setToolTip("Click to zero selected channels.")
        self.autozeroButton.setVisible(False)
        self.addAction(self.autozeroButton)

        # Clear plots QAction.
        self.clearPlotsButton = QAction()
        self.clearPlotsButton.setToolTip("Click to clear the plots.")
        self.clearPlotsButton.setVisible(False)
        self.addAction(self.clearPlotsButton)

        # Spacer to fill toolbar.
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.addWidget(spacer)

        # Dark mode QAction.
        self.darkModeButton = QAction()
        self.darkModeButton.setToolTip("Click for light mode." if self.darkMode else "Click for dark mode.")
        self.addAction(self.darkModeButton)

        # Connections.
        self.modeButton.triggered.connect(self.changeMode)
        self.loadConfigButton.triggered.connect(self.emitLoadConfiguration)
        self.saveConfigButton.triggered.connect(self.emitSaveConfiguration)

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