import sys, os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QTabWidget
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QPoint, QThread, QTimer, QDir
from src.local_qt_material import apply_stylesheet, QtStyleTools
from src.widgets.MainWindow._utilities._TabUtilities import TabUtilities
from src.widgets.MainWindow._utilities._PlotUtilities import PlotUtilities
from src.widgets.MainWindow._utilities._ControlUtilities import ControlUtilities
from src.widgets.MainWindow._utilities._ConfigurationUtilities import ConfigurationUtilities
from src.manager import Manager
from src.widgets.CamLabToolBar import CamLabToolBar
from src.widgets.TabInterface import TabInterface
from src.widgets.StatusGroupBox import StatusGroupBox
from src.widgets.GlobalSettingsGroupBox import GlobalSettingsGroupBox
from src.widgets.DevicesGroupBox import DevicesGroupBox
from src.widgets.DeviceConfigurationGroupBox import DeviceConfigurationGroupBox
from src.log import init_log
import logging
import copy
from time import sleep
from random import randint

log = logging.getLogger(__name__)

class MainWindow(QMainWindow, QtStyleTools, TabUtilities, PlotUtilities, ControlUtilities, ConfigurationUtilities):
    running = Signal(bool)
    
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

        # Timers.
        self.updateTimer = QTimer()
        self.checkTimer = QTimer()
        self.checkTimer.start(1000)

        # Instantiate the manager object and thread.
        self.manager = Manager()
        self.managerThread = QThread(parent=self)
        self.manager.moveToThread(self.managerThread)
        self.managerThread.start()

        # Set position.
        x = self.manager.configuration["configurationWindow"]["x"]
        y = self.manager.configuration["configurationWindow"]["y"]
        self.move(x, y)

        # Extract the configuration to generate initial UI setup.
        self.configuration = self.manager.configuration
        self.setTheme()

        # Main window layout.
        log.info("Assembling UI.")
        self.mainWindowLayout = QVBoxLayout()

        # Toolbar.
        self.toolbar = CamLabToolBar()
        self.mainWindowLayout.addWidget(self.toolbar)
        
        # Tab interface.
        self.tabs = TabInterface()
        self.mainWindowLayout.addWidget(self.tabs)

        # Status GroupBox.
        self.statusGroupBox = StatusGroupBox()

        # Global settings GroupBox.
        self.globalSettingsGroupBox = GlobalSettingsGroupBox(self.configuration)
        
        # Device table GroupBox.
        self.devicesGroupBox = DevicesGroupBox(self.configuration)
        self.devicesGroupBox.deviceTableView.setModel(self.manager.deviceTableModel)

        # Device configuration Groupbox.
        self.deviceConfigurationGroupBox = DeviceConfigurationGroupBox()

        self.configurationLayout = QGridLayout()
        self.configurationLayout.setRowStretch(0, 1)
        self.configurationLayout.addWidget(self.globalSettingsGroupBox, 1, 0, 1, 1)
        self.configurationLayout.addWidget(self.devicesGroupBox, 2, 0, 1, 1)
        self.configurationLayout.addWidget(self.deviceConfigurationGroupBox, 1, 1, 2, 1)
        self.configurationLayout.setRowStretch(self.configurationLayout.rowCount(), 1)
        
        self.configurationWidget = QWidget()
        self.configurationWidget.setLayout(self.configurationLayout)
        self.tabs.addPersistentTab(self.configurationWidget, "Configuration")
        self.tabs.addPersistentTab(QWidget(), "Sequences")
        self.tabs.addPersistentTab(self.statusGroupBox, "Status")

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainWindowLayout)
        self.setCentralWidget(self.centralWidget)

        # Toolbar connections.
        self.toolbar.configure.connect(self.manager.configure)
        self.toolbar.configure.connect(self.manager.timing.stop)
        self.toolbar.configure.connect(self.end)
        self.toolbar.run.connect(self.manager.run)
        self.toolbar.run.connect(self.start)
        self.toolbar.run.connect(self.statusGroupBox.setInitialTimeDate)
        self.toolbar.addPlotButton.triggered.connect(self.addPlot)
        self.toolbar.controlPanelButton.triggered.connect(self.openControlPanel)
        self.toolbar.cameraButton.triggered.connect(self.openCamera)
        self.toolbar.extensionButton.triggered.connect(self.openExtension)
        self.toolbar.refreshButton.triggered.connect(self.manager.refreshDevices)
        self.toolbar.loadConfiguration.connect(self.manager.loadConfiguration)
        self.toolbar.saveConfiguration.connect(self.manager.saveConfiguration)
        self.toolbar.clearConfigButton.triggered.connect(self.manager.clearConfiguration)
        self.toolbar.newFileButton.triggered.connect(self.manager.assembly.newFile)
        self.toolbar.autozeroButton.triggered.connect(self.manager.assembly.autozero)
        self.toolbar.clearPlotsButton.triggered.connect(self.manager.assembly.clearPlotData)
        self.toolbar.darkModeButton.triggered.connect(self.updateDarkMode)

        # Tab interface connections.
        self.tabs.tabToWindow.connect(self.tabToWindow)

        # Global settings connections.
        self.globalSettingsGroupBox.skipSamplesChanged.connect(self.manager.updateSkipSamples)
        self.globalSettingsGroupBox.controlRateChanged.connect(self.manager.updateControlRate)
        self.globalSettingsGroupBox.averageSamplesChanged.connect(self.manager.updateAverageSamples)
        self.globalSettingsGroupBox.pathChanged.connect(self.manager.updatePath)
        self.globalSettingsGroupBox.filenameChanged.connect(self.manager.updateFilename)

        # Manager connections.
        self.manager.updateUI.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.globalSettingsGroupBox.updateUI)
        self.manager.clearDeviceConfigurationTabs.connect(self.clearDeviceConfigurationTabs)
        self.manager.closePlots.connect(self.closePlots)
        self.manager.clearControls.connect(self.clearControls)
        self.manager.deviceConfigurationAdded.connect(self.addDeviceConfigurationTab)
        self.manager.removeControlTable.connect(self.removeControlTable)
        self.manager.addControlTable.connect(self.addControlTable)
        self.manager.updateDeviceConfigurationTab.connect(self.updateDeviceConfigurationTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.manager.manageDeviceThreads)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateDeviceConfigurationTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.timing.actualRate.connect(self.statusGroupBox.update)
        self.manager.plotWindowChannelsUpdated.connect(self.updatePlots)
        self.manager.existingPlotsFound.connect(self.createExistingPlots)
        self.manager.outputText.connect(self.statusGroupBox.setOutputText)

        # Timer connections.
        self.updateTimer.timeout.connect(self.manager.assembly.updatePlotData)
        self.updateUI(self.manager.configuration)

    def moveEvent(self, event):
        position = self.geometry()
        self.configuration["configurationWindow"]["x"] = int(position.x())
        self.configuration["configurationWindow"]["y"] = int(position.y())
        return

    @Slot()
    def start(self):
        self.updateTimer.start(100)
        self.running.emit(True)
        # Hide the configuration and sequences tabs.
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == "Configuration":
                self.tabs.setTabVisible(index, False)
            if self.tabs.tabText(index) == "Sequences":
                self.tabs.setTabVisible(index, False)
        
    @Slot()
    def end(self):
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
    def openControlPanel(self):
        self.controlWindow.show()
        self.configuration["controlWindow"]["visible"] = True
        log.info("Control panel opened.")

    @Slot()
    def openCamera(self):
        log.info("Camera opened.")

    @Slot()
    def openExtension(self):
        log.info("Extension opened.")

    @Slot()
    def updateDarkMode(self):
        # Toggle darkMode boolean in the configuration.
        self.manager.configuration["global"]["darkMode"] = not self.darkMode

        # Update the local darkMode variable.
        self.darkMode = self.manager.configuration["global"]["darkMode"]

        # Update the UI
        self.updateUI(self.manager.configuration)
        log.info("Dark mode changed.")

    def setTheme(self):
        self.darkMode = self.configuration["global"]["darkMode"]
        # Set the darkmode. 
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    @Slot(dict)
    def updateUI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setTheme()
        # Update icon colours as a function of the darkMode boolean.
        self.toolbar.updateIcons(self.darkMode)

        # Update the UI of plot windows if they exist.
        if self.plots and "plots" in self.manager.configuration: 
            self.updatePlots()

        # self.controlWindow.updateUI(self.configuration)
        log.info("Updated UI.")

    def closeEvent(self, event):
        # Close all plots.
        self.closePlots()

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