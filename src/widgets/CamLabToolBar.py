from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal
import logging

log = logging.getLogger(__name__)

class CamLabToolBar(QToolBar):
    configure = Signal() 
    run = Signal() 
    loadConfiguration = Signal(str)
    saveConfiguration = Signal(str)
    darkModeChanged = Signal(bool)
    
    def __init__(self, configuration):
        super().__init__()
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.running = False

        # Mode QAction.
        self.modeButton = QAction(parent=None)
        self.modeButton.setIcon(QIcon("assets/play_circle_white_24dp.svg" if self.darkMode else "assets/play_circle_black_24dp.svg"))
        self.modeButton.setToolTip("Click to run acquisition and control.")
        self.addAction(self.modeButton)

        self.addSeparator()

        # Add plot QAction.
        self.addPlotButton = QAction()
        self.addPlotButton.setIcon(QIcon("assets/stacked_line_chart_white_24dp.svg" if self.darkMode else "assets/stacked_line_chart_black_24dp.svg"))
        self.addPlotButton.setToolTip("Click to add plot.")
        self.addAction(self.addPlotButton)

        # Open control pannel  QAction.
        self.controlPanelButton = QAction()
        self.controlPanelButton.setIcon(QIcon("assets/videogame_asset_white_24dp.svg" if self.darkMode else "assets/videogame_asset_black_24dp.svg"))
        self.controlPanelButton.setToolTip("Click to open control panel.")
        self.addAction(self.controlPanelButton)

        # Open camera QAction.
        self.cameraButton = QAction()
        self.cameraButton.setIcon(QIcon("assets/camera_white_24dp.svg" if self.darkMode else "assets/camera_black_24dp.svg"))
        self.cameraButton.setToolTip("Click to open camera.")
        self.addAction(self.cameraButton)

        # Open extension QAction.
        self.extensionButton = QAction()
        self.extensionButton.setIcon(QIcon("assets/extension_white_24dp.svg" if self.darkMode else "assets/extension_black_24dp.svg"))
        self.extensionButton.setToolTip("Click to open extension.")
        self.addAction(self.extensionButton)

        self.addSeparator()

        # Refresh devices QAction.
        self.refreshButton = QAction()
        self.refreshButton.setIcon(QIcon("assets/restart_alt_white_24dp.svg" if self.darkMode else "assets/restart_alt_black_24dp.svg"))
        self.refreshButton.setToolTip("Refresh device list.")
        self.refreshButton.setVisible(True)
        self.addAction(self.refreshButton)

        # Load configuration QAction.
        self.loadConfigButton = QAction()
        self.loadConfigButton.setIcon(QIcon("assets/file_upload_white_24dp.svg" if self.darkMode else "assets/file_upload_black_24dp.svg"))
        self.loadConfigButton.setToolTip("Click to load a configuration.")
        self.loadConfigButton.setVisible(True)
        self.addAction(self.loadConfigButton)

        # Save configuration QAction.
        self.saveConfigButton = QAction()
        self.saveConfigButton.setIcon(QIcon("assets/file_download_white_24dp.svg" if self.darkMode else "assets/file_download_black_24dp.svg"))
        self.saveConfigButton.setToolTip("Click to save the current configuration.")
        self.saveConfigButton.setVisible(True)
        self.addAction(self.saveConfigButton)

        # Clear configuration QAction.
        self.clearConfigButton = QAction()
        self.clearConfigButton.setIcon(QIcon("assets/clear_white_24dp.svg" if self.darkMode else "assets/clear_black_24dp.svg"))
        self.clearConfigButton.setToolTip("Click to clear the current configuration.")
        self.clearConfigButton.setVisible(True)
        self.addAction(self.clearConfigButton)

        # Add calculated variable QAction.
        self.addCalculatedVariableButton = QAction()
        self.addCalculatedVariableButton.setIcon(QIcon("assets/calculate_white_24dp.svg" if self.darkMode else "assets/calculate_black_24dp.svg"))
        self.addCalculatedVariableButton.setToolTip("Click to add a calculated variable.")
        self.addCalculatedVariableButton.setVisible(True)
        self.addAction(self.addCalculatedVariableButton)

        # New file QAction.
        self.newFileButton = QAction()
        self.newFileButton.setIcon(QIcon("assets/restore_page_white_24dp.svg" if self.darkMode else "assets/restore_page_black_24dp.svg"))
        self.newFileButton.setToolTip("Click to start a new output file.")
        self.newFileButton.setVisible(False)
        self.addAction(self.newFileButton)

        # Autozero QAction.
        self.autozeroButton = QAction()
        self.autozeroButton.setIcon(QIcon("assets/exposure_zero_white_24dp.svg" if self.darkMode else "assets/exposure_zero_black_24dp.svg"))
        self.autozeroButton.setToolTip("Click to zero selected channels.")
        self.autozeroButton.setVisible(False)
        self.addAction(self.autozeroButton)

        # Clear plots QAction.
        self.clearPlotsButton = QAction()
        self.clearPlotsButton.setIcon(QIcon("assets/clear_all_white_24dp.svg" if self.darkMode else "assets/clear_all_black_24dp.svg"))
        self.clearPlotsButton.setToolTip("Click to clear the plots.")
        self.clearPlotsButton.setVisible(False)
        self.addAction(self.clearPlotsButton)

        # Spacer to fill toolbar.
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        self.addWidget(spacer)

        # Dark mode QAction.
        self.darkModeButton = QAction()
        self.darkModeButton.setIcon(QIcon("assets/light_mode_white_24dp.svg" if self.darkMode else "assets/dark_mode_black_24dp.svg"))
        self.darkModeButton.setToolTip("Click for light mode." if self.darkMode else "Click for dark mode.")
        self.addAction(self.darkModeButton)

        # Connections.
        self.modeButton.triggered.connect(self.changeMode)
        self.darkModeButton.triggered.connect(self.emitDarkModeChanged)
        self.loadConfigButton.triggered.connect(self.emitLoadConfiguration)
        self.saveConfigButton.triggered.connect(self.emitSaveConfiguration)

    def changeMode(self):
        # Toggle running property, modeButton ToolTip and icon and visible state for all other ToolButtons as required.
        log.info("Acquisition and control mode enabled." if self.running else "Configuration mode enabled")
        self.running = not self.running
        if self.darkMode == True:
            self.modeButton.setIcon(QIcon("assets/settings_white_24px.svg" if self.running else "assets/play_circle_white_24dp.svg"))
        else:
            self.modeButton.setIcon(QIcon("assets/settings_black_24px.svg" if self.running else "assets/play_circle_black_24dp.svg"))
        self.modeButton.setToolTip("Click to run acquisition and control." if self.running else "Click to configure.")
        self.refreshButton.setVisible(not self.refreshButton.isVisible())
        self.loadConfigButton.setVisible(not self.loadConfigButton.isVisible())
        self.saveConfigButton.setVisible(not self.saveConfigButton.isVisible())
        self.clearConfigButton.setVisible(not self.clearConfigButton.isVisible())
        self.addCalculatedVariableButton.setVisible(not self.addCalculatedVariableButton.isVisible())
        self.newFileButton.setVisible(not self.newFileButton.isVisible())
        self.autozeroButton.setVisible(not self.autozeroButton.isVisible())
        self.clearPlotsButton.setVisible(not self.clearPlotsButton.isVisible())
        if self.running == True:    
            self.run.emit()
        else:
            self.configure.emit()

    def updateIcons(self, darkMode):
        # Change appearance between light and dark modes.
        self.darkMode = darkMode
        self.modeButton.setIcon(QIcon("assets/play_circle_white_24dp.svg" if self.darkMode else "assets/play_circle_black_24dp.svg"))
        self.addPlotButton.setIcon(QIcon("assets/stacked_line_chart_white_24dp.svg" if self.darkMode else "assets/stacked_line_chart_black_24dp.svg"))
        self.controlPanelButton.setIcon(QIcon("assets/videogame_asset_white_24dp.svg" if self.darkMode else "assets/videogame_asset_black_24dp.svg"))
        self.cameraButton.setIcon(QIcon("assets/camera_white_24dp.svg" if self.darkMode else "assets/camera_black_24dp.svg"))
        self.extensionButton.setIcon(QIcon("assets/extension_white_24dp.svg" if self.darkMode else "assets/extension_black_24dp.svg"))
        self.newFileButton.setIcon(QIcon("assets/restore_page_white_24dp.svg" if self.darkMode else "assets/restore_page_black_24dp.svg"))
        self.autozeroButton.setIcon(QIcon("assets/exposure_zero_white_24dp.svg" if self.darkMode else "assets/exposure_zero_black_24dp.svg"))
        self.clearPlotsButton.setIcon(QIcon("assets/clear_all_white_24dp.svg" if self.darkMode else "assets/clear_all_black_24dp.svg"))
        self.addCalculatedVariableButton.setIcon(QIcon("assets/calculate_white_24dp.svg" if self.darkMode else "assets/calculate_black_24dp.svg"))
        self.refreshButton.setIcon(QIcon("assets/restart_alt_white_24dp.svg" if self.darkMode else "assets/restart_alt_black_24dp.svg"))
        self.loadConfigButton.setIcon(QIcon("assets/file_upload_white_24dp.svg" if self.darkMode else "assets/file_upload_black_24dp.svg"))
        self.saveConfigButton.setIcon(QIcon("assets/file_download_white_24dp.svg" if self.darkMode else "assets/file_download_black_24dp.svg"))
        self.clearConfigButton.setIcon(QIcon("assets/clear_white_24dp.svg" if self.darkMode else "assets/clear_black_24dp.svg"))
        self.darkModeButton.setIcon(QIcon("assets/light_mode_white_24dp.svg" if self.darkMode else "assets/dark_mode_black_24dp.svg"))
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