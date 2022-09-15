import os, sys
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QDialog
from PySide6.QtGui import QScreen
from PySide6.QtCore import Signal, Slot, QThread, QTimer
from local_qt_material import QtStyleTools
from widgets.MainWindow._TabUtilities import TabUtilities
from widgets.MainWindow._PlotUtilities import PlotUtilities
from widgets.MainWindow._ControlUtilities import ControlUtilities
from widgets.MainWindow._ConfigurationUtilities import ConfigurationUtilities
from widgets.MainWindow._CameraUtilities import CameraUtilities
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

class MainWindow(TabUtilities, PlotUtilities, ControlUtilities, ConfigurationUtilities, CameraUtilities, QtStyleTools, QMainWindow):
    running = Signal(bool)
    renameWindow = Signal(str)
    emitRefreshDevices = Signal()
    startCameraPreview = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamLab")
        self.refreshing = False
        self.screenSize = QScreen.availableGeometry(QApplication.primaryScreen())

        # Empty dicts for storage. 
        self.deviceConfigurationLayout = {}
        self.deviceConfigurationWidget = {}
        self.acquisitionTableViews = {}
        self.controlTableViews = {}
        self.plots = {}
        self.controls = {}
        self.previews = {}

        # Timers.
        self.updateTimer = QTimer()
        self.checkTimer = QTimer()
        self.checkTimer.start(1000)
        self.previewTimer = QTimer()
        self.previewTimer.start(100)

        # Instantiate the manager object and thread.
        self.manager = Manager()
        self.managerThread = QThread(parent=self)
        self.manager.moveToThread(self.managerThread)
        self.managerThread.start()

        # Set position.
        x = self.manager.configuration["mainWindow"]["x"]
        y = self.manager.configuration["mainWindow"]["y"]
        self.move(x, y)

        # Extract the configuration to generate initial UI setup.
        self.configuration = self.manager.configuration
        self.set_theme()

        # Main window layout.
        log.info("Assembling UI.")
        self.mainWindowLayout = QVBoxLayout()

        # Toolbar.
        self.toolbar = ToolBar()
        self.mainWindowLayout.addWidget(self.toolbar)
        
        # Tab interface.
        self.tabs = TabInterface()
        self.mainWindowLayout.addWidget(self.tabs)

        # Status GroupBox.
        self.statusGroupBox = StatusGroupBox()

        # Configuration tab.
        self.configurationTab = ConfigurationTab(self.configuration)
        self.configurationTab.devicesGroupBox.deviceTableView.setModel(self.manager.deviceTableModel)

        # Sequences tab.
        self.sequenceTab = SequenceTab()

        # Status tab.
        self.statusTab = StatusTab()

        self.tabs.add_persistent_tab(self.configurationTab, "Configuration")
        self.tabs.add_persistent_tab(self.sequenceTab, "Sequence")
        self.tabs.add_persistent_tab(self.statusTab, "Status")

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainWindowLayout)
        self.setCentralWidget(self.centralWidget)

        # Toolbar connections.
        self.toolbar.configure.connect(self.manager.configure)
        self.toolbar.configure.connect(self.manager.timing.stop)
        self.toolbar.configure.connect(self.end_acquisition)
        self.toolbar.run.connect(self.manager.run)
        self.toolbar.run.connect(self.start_acquisition)
        self.toolbar.run.connect(self.statusGroupBox.setInitialTimeDate)
        self.toolbar.addPlotButton.triggered.connect(self.add_plot)
        self.toolbar.extensionButton.triggered.connect(self.open_extension)
        self.toolbar.refreshButton.triggered.connect(self.refresh_devices)
        self.toolbar.loadConfiguration.connect(self.manager.loadConfiguration)
        self.toolbar.saveConfiguration.connect(self.manager.saveConfiguration)
        self.toolbar.clearConfigButton.triggered.connect(self.manager.clearConfiguration)
        self.toolbar.newFileButton.triggered.connect(self.manager.assembly.new_file)
        self.toolbar.autozeroButton.triggered.connect(self.manager.assembly.autozero)
        self.toolbar.clearPlotsButton.triggered.connect(self.manager.assembly.clear_plot_data)
        self.toolbar.darkModeButton.triggered.connect(self.update_dark_mode)

        # Tab interface connections.
        self.tabs.tabToWindow.connect(self.tab_to_window)

        # Configuration tab connections.
        self.configurationTab.configurationWindowClosed.connect(self.window_to_tab)

        # Sequences tab connections.
        self.sequenceTab.sequenceWindowClosed.connect(self.window_to_tab)

        # Status tab connections.
        self.statusTab.statusWindowClosed.connect(self.window_to_tab)

        # Manager connections.
        self.manager.configurationChanged.connect(self.set_configuration)
        self.manager.clear_device_configuration_tabs.connect(self.clear_device_configuration_tabs)
        self.manager.close_plots.connect(self.close_plots)
        self.manager.clear_tabs.connect(self.clear_tabs)
        self.manager.deviceAdded.connect(self.add_device_configuration_tab)
        self.manager.deviceToggled.connect(self.update_device_configuration_tab)
        self.manager.deviceToggled.connect(self.update_control_visibility)
        self.manager.deviceToggled.connect(self.upate_preview_visibility)
        self.manager.deviceTableModel.numberDevicesEnabled.connect(self.update_mode_enable)

        self.manager.timing.actualRate.connect(self.statusGroupBox.update)
        self.manager.plotWindowChannelsUpdated.connect(self.update_plots)
        self.manager.existingPlotsFound.connect(self.create_existing_plots)
        self.manager.outputText.connect(self.statusGroupBox.setOutputText)

        self.tabs.remove_plot.connect(self.remove_plot)

        self.emitRefreshDevices.connect(self.manager.refresh_devices)
        self.manager.finishedRefreshingDevices.connect(self.close_busy_dialog)

        # Timer connections.
        self.updateTimer.timeout.connect(self.manager.assembly.update_output_data)

        # Set initial configuration.
        self.set_configuration(self.manager.configuration)      
        self.manager.checkForPreviousConfiguration()

    @Slot(int)
    def update_mode_enable(self, number):
        """Method to update the mode button enable state based on the number of enabled devices."""
        if number > 0:
            self.toolbar.enableModeButton()
        elif number == 0:
            self.toolbar.disableModeButton()

    @Slot()
    def refresh_devices(self):
        """Method to refresh device list."""
        self.emitRefreshDevices.emit()
        self.busy = BusyDialog(self)
        self.busy.open()

    @Slot()
    def close_busy_dialog(self):
        """Method to close the busy dialog."""
        self.busy.accept()
        
    @Slot()
    def start_acquisition(self):
        """Method to start the acquisition mode."""
        self.updateTimer.start(100)
        self.running.emit(True)
        # Hide the configuration and sequences tabs.
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == "Configuration":
                self.tabs.setTabVisible(index, False)
            if self.tabs.tabText(index) == "Sequences":
                self.tabs.setTabVisible(index, False)
        
    @Slot()
    def end_acquisition(self):
        """Method to end the acquisiton mode."""
        self.updateTimer.stop()
        self.running.emit(False)
        self.statusGroupBox.reset()
        # Show the configuration and sequences tabs.
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == "Configuration":
                self.tabs.setTabVisible(index, True)
            if self.tabs.tabText(index) == "Sequences":
                self.tabs.setTabVisible(index, True)

    @Slot()
    def open_extension(self):
        """Method to open an extension."""
        log.info("Extension button clicked.")

    @Slot()
    def update_dark_mode(self):
        """Method to update the darkMode state."""
        # Toggle darkMode boolean in the configuration.
        self.manager.configuration["global"]["darkMode"] = not self.darkMode

        # Update the local darkMode variable.
        self.darkMode = self.manager.configuration["global"]["darkMode"]

        # Update the UI
        self.set_configuration(self.manager.configuration)
        log.info("Dark mode changed.")

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

    @Slot(dict)
    def set_configuration(self, newConfiguration):
        """Method to forcibly update the UI."""
        self.configuration = newConfiguration
        self.configurationTab.globalSettingsGroupBox.set_configuration(self.configuration)
        self.darkMode = self.configuration["global"]["darkMode"]
        self.set_theme()

        # Update icon colours as a function of the darkMode boolean.
        self.toolbar.updateIcons(self.darkMode)
        self.sequenceTab.update_tab()

        # Update press configuration if device present.
        self.update_press_configuration()

        # Update the UI of plot windows if they exist.
        if self.plots and "plots" in self.manager.configuration: 
            self.update_plots()

    def moveEvent(self, event):
        """Method to store the current main window position i the configuration after a move event using a Qt moveEvent overide."""
        position = self.geometry()
        self.configuration["mainWindow"]["x"] = int(position.x())
        self.configuration["mainWindow"]["y"] = int(position.y())
        return

    def closeEvent(self, event):
        """Close CamLab using a Qt closeEvent override."""
        # Close all plots.
        self.close_plots()

        # In the event the device list is refreshing, wait until complete before quitting all threads otherwise an error is shown, but hide the window in the meantime.
        self.setVisible(False)
        if self.manager.refreshing == True:
            log.info("Waiting for manager thread to finish refreshing the device list before closing.")
            while self.manager.refreshing == True:
                sleep(1.0)

        # Stop and quit all threads and plots and then close. Short delays required to stop premature quitting.
        self.manager.timing.stop()
        sleep(0.2)
        self.manager.timingThread.quit()
        sleep(0.2)
        log.info("Timing thread stopped.")
        for name in self.manager.deviceThreads:
            self.manager.deviceThreads[name].quit()
            log.info("Thread for " + name + " stopped.") 
        sleep(0.2)
        self.manager.assemblyThread.quit()
        log.info("Assembly thread stopped.")
        sleep(0.2)
        self.managerThread.quit()
        log.info("Manager thread stopped.")
        log.info('Closing CamLab.')
        handlers = log.handlers[:]
        for handler in handlers:
            handler.close()
            log.removeHandler(handler)