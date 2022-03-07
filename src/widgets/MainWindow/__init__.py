import os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QDialog
from PySide6.QtGui import QScreen
from PySide6.QtCore import Signal, Slot, QThread, QTimer, Qt
from src.local_qt_material import apply_stylesheet, QtStyleTools
from src.widgets.MainWindow._TabUtilities import TabUtilities
from src.widgets.MainWindow._PlotUtilities import PlotUtilities
from src.widgets.MainWindow._ControlUtilities import ControlUtilities
from src.widgets.MainWindow._ConfigurationUtilities import ConfigurationUtilities
from src.manager import Manager
from src.widgets.ToolBar import ToolBar
from src.widgets.TabInterface import TabInterface
from src.widgets.ConfigurationTab import ConfigurationTab
from src.widgets.SequencesTab import SequencesTab
from src.widgets.StatusTab import StatusTab
from src.widgets.StatusGroupBox import StatusGroupBox
from src.dialogs import BusyDialog
from src.log import init_log
import logging
from time import sleep

log = logging.getLogger(__name__)

class MainWindow(TabUtilities, PlotUtilities, ControlUtilities, ConfigurationUtilities, QtStyleTools, QMainWindow):
    running = Signal(bool)
    renameWindow = Signal(str)
    emitRefreshDevices = Signal()
    
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
        x = self.manager.configuration["mainWindow"]["x"]
        y = self.manager.configuration["mainWindow"]["y"]
        self.move(x, y)

        # Extract the configuration to generate initial UI setup.
        self.configuration = self.manager.configuration
        self.setTheme()

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
        self.sequencesTab = SequencesTab()

        # Status tab.
        self.statusTab = StatusTab()

        self.tabs.addPersistentTab(self.configurationTab, "Configuration")
        self.tabs.addPersistentTab(self.sequencesTab, "Sequences")
        self.tabs.addPersistentTab(self.statusTab, "Status")

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
        self.toolbar.extensionButton.triggered.connect(self.openExtension)
        self.toolbar.refreshButton.triggered.connect(self.refreshDevices)
        self.toolbar.loadConfiguration.connect(self.manager.loadConfiguration)
        self.toolbar.saveConfiguration.connect(self.manager.saveConfiguration)
        self.toolbar.clearConfigButton.triggered.connect(self.manager.clearConfiguration)
        self.toolbar.newFileButton.triggered.connect(self.manager.assembly.newFile)
        self.toolbar.autozeroButton.triggered.connect(self.manager.assembly.autozero)
        self.toolbar.clearPlotsButton.triggered.connect(self.manager.assembly.clearPlotData)
        self.toolbar.darkModeButton.triggered.connect(self.updateDarkMode)

        # Tab interface connections.
        self.tabs.tabToWindow.connect(self.tabToWindow)

        # Configuration tab connections.
        self.configurationTab.globalSettingsGroupBox.skipSamplesChanged.connect(self.manager.updateSkipSamples)
        self.configurationTab.globalSettingsGroupBox.controlRateChanged.connect(self.manager.updateControlRate)
        self.configurationTab.globalSettingsGroupBox.averageSamplesChanged.connect(self.manager.updateAverageSamples)
        self.configurationTab.globalSettingsGroupBox.pathChanged.connect(self.manager.updatePath)
        self.configurationTab.globalSettingsGroupBox.filenameChanged.connect(self.manager.updateFilename)
        self.configurationTab.configurationWindowClosed.connect(self.windowToTab)

        # Sequences tab connections.
        self.sequencesTab.sequencesWindowClosed.connect(self.windowToTab)

        # Status tab connections.
        self.statusTab.statusWindowClosed.connect(self.windowToTab)

        # Manager connections.
        self.manager.configurationChanged.connect(self.updateUI)
        self.manager.clearDeviceConfigurationTabs.connect(self.clearDeviceConfigurationTabs)
        self.manager.closePlots.connect(self.closePlots)
        self.manager.clearControlTabs.connect(self.clearControlTabs)
        self.manager.deviceAdded.connect(self.addDeviceConfigurationTab)
        self.manager.deviceToggled.connect(self.updateDeviceConfigurationTab)
        # self.manager.removeControlTable.connect(self.removeControlTable)
        # self.manager.addControlTable.connect(self.addControlTable)
        # self.manager.updateFeedbackChannelList.connect(self.updateFeedbackChannelList)
        # self.manager.updateDeviceConfigurationTab.connect(self.updateDeviceConfigurationTabs)
        # self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateDeviceConfigurationTabs)

        self.manager.timing.actualRate.connect(self.statusGroupBox.update)
        self.manager.plotWindowChannelsUpdated.connect(self.updatePlots)
        self.manager.existingPlotsFound.connect(self.createExistingPlots)
        self.manager.outputText.connect(self.statusGroupBox.setOutputText)

        self.tabs.removePlot.connect(self.removePlot)

        self.emitRefreshDevices.connect(self.manager.refreshDevices)
        self.manager.finishedRefreshingDevices.connect(self.closeBusyDialog)

        # Timer connections.
        self.updateTimer.timeout.connect(self.manager.assembly.updatePlotData)
        self.updateUI(self.manager.configuration)

    def moveEvent(self, event):
        position = self.geometry()
        self.configuration["mainWindow"]["x"] = int(position.x())
        self.configuration["mainWindow"]["y"] = int(position.y())
        return

    @Slot()
    def refreshDevices(self):
        self.emitRefreshDevices.emit()
        self.busy = BusyDialog(self)
        self.busy.open()

    @Slot()
    def closeBusyDialog(self):
        self.busy.accept()
        
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

        # Update other GUI items.
        self.configurationTab.globalSettingsGroupBox.updateUI(self.configuration)

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