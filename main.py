import sys, os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, Qt, QModelIndex, QPoint, QThread, QTimer
from qt_material import apply_stylesheet, QtStyleTools
from src.manager import Manager
from src.widgets import CamLabToolBar, StatusGroupBox, GlobalSettingsGroupBox, DevicesGroupBox, AcquisitionGroupBox, \
    PlotWindow, ControlGroupBox, DeviceConfigurationGroupBox
from src.models import DeviceTableModel, AcquisitionTableModel, ColourPickerTableModel
from src.views import DeviceTableView, AcquisitionTableView, ControlTableView
from src.log import init_log

from src.models import ChannelsTableModel
from src.dialogs import ColourPickerDialog
from src.dialogs import RefreshDevicesDialog
import logging
import copy
from time import sleep
from random import randint

class MainWindow(QMainWindow, QtStyleTools):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamLab")
        self.width = 800
        self.height = 1008
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.refreshing = False

        # Empty dicts for storage. 
        self.deviceConfigurationLayout = {}
        self.deviceConfigurationWidget = {}
        self.acquisitionTableViews = {}
        self.controlTableViews = {}
        self.plots = {}

        # Timers.
        self.plotTimer = QTimer()

        # Instantiate the manager object and thread.
        self.manager = Manager()
        self.managerThread = QThread(parent=self)
        self.manager.moveToThread(self.managerThread)
        self.managerThread.start()

        # Extract the configuration to generate initial UI setup.
        self.configuration = self.manager.configuration

        # Main window layout.
        log.info("Assembling UI.")
        self.mainWindowLayout = QVBoxLayout()

        # Toolbar.
        self.toolbar = CamLabToolBar()
        self.mainWindowLayout.addWidget(self.toolbar)

        # Status groupbox.
        self.statusGroupBox = StatusGroupBox()
        self.mainWindowLayout.addWidget(self.statusGroupBox)

        # Global settings groupbox.
        self.globalSettingsGroupBox = GlobalSettingsGroupBox(self.configuration)
        self.mainWindowLayout.addWidget(self.globalSettingsGroupBox)

        # Device table groupbox.
        self.devicesGroupBox = DevicesGroupBox(self.configuration)
        self.mainWindowLayout.addWidget(self.devicesGroupBox)
        self.devicesGroupBox.deviceTableView.setModel(self.manager.deviceTableModel)

        # Device configuration groupbox.
        self.deviceConfigurationGroupBox = DeviceConfigurationGroupBox()
        self.mainWindowLayout.addWidget(self.deviceConfigurationGroupBox)

        # Acquisition groupbox.
        self.acquisitionGroupBox = AcquisitionGroupBox()

        # Control groupbox.
        self.controlGroupBox = ControlGroupBox()

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainWindowLayout)
        self.setCentralWidget(self.centralWidget)

        # # Set dark mode (always do this last to ensure all GUI objects are displayed correctly).
        # self.darkMode = self.configuration["global"]["darkMode"]
        # self.setDarkMode()

        # Toolbar connections.
        self.toolbar.modeButton.triggered.connect(self.toggleMode)
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

        # Global settings connections.
        self.globalSettingsGroupBox.acquisitionRateChanged.connect(self.manager.updateAcquisitionRate)
        self.globalSettingsGroupBox.controlRateChanged.connect(self.manager.updateControlRate)
        self.globalSettingsGroupBox.averageSamplesChanged.connect(self.manager.updateAverageSamples)
        self.globalSettingsGroupBox.pathChanged.connect(self.manager.updatePath)
        self.globalSettingsGroupBox.filenameChanged.connect(self.manager.updateFilename)

        # Manager connections.
        self.manager.updateUI.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.globalSettingsGroupBox.updateUI)
        self.manager.clearDeviceConfigurationTabs.connect(self.clearDeviceConfigurationTabs)
        self.manager.clearPlots.connect(self.clearPlots)
        self.manager.addDeviceConfiguration.connect(self.addDeviceConfiguration)
        self.manager.removeWidget.connect(self.removeWidgetFromLayout)
        self.manager.addControlTable.connect(self.addControlTable)
        self.manager.updateDeviceConfigurationTab.connect(self.updateDeviceConfigurationTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateDeviceConfigurationTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.timing.actualRate.connect(self.statusGroupBox.update)
        self.manager.plotWindowChannelsUpdated.connect(self.updatePlotWindows)
        self.manager.existingPlotFound.connect(self.createExistingPlot)

        # Timer connections.
        self.plotTimer.timeout.connect(self.manager.assembly.updatePlotData)

    @Slot()
    def start(self):
        self.plotTimer.start(250)
        
    @Slot()
    def end(self):
        self.plotTimer.stop()
        self.statusGroupBox.reset()

    @Slot()
    def openControlPanel(self):
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

    @Slot(str, list)
    def addDeviceConfiguration(self, name, defaultFeedbackChannel):
        # Create layout.
        self.deviceConfigurationLayout[name] = QVBoxLayout()

        # Add acquisition table label.
        acquisitionLabel = QLabel('ACQUISITION')
        self.deviceConfigurationLayout[name].addWidget(acquisitionLabel)

        # Add acquisition table to the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.setListFeedbackCombobox)
        self.manager.acquisitionModels[name].channelIndexToggled.connect(self.resetControlFeedbackComboBox)

        # Add control table label.
        conrtrolLabel = QLabel('CONTROL')
        self.deviceConfigurationLayout[name].addWidget(conrtrolLabel)

        # Add control table to the TabWidget.
        self.addControlTable(name, defaultFeedbackChannel)

        # Set layout within widget.
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

    @Slot()
    def updateDeviceConfigurationTabs(self):
        # Clear the acquisition table TabWidget.
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()

        # If enabled and status is True, add the TabWidget for this device.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.acquisitionTableViews:
                self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)

    @Slot()
    def clearDeviceConfigurationTabs(self):
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

    @Slot(str)
    def removeWidgetFromLayout(self,name):
        self.controlTableViews[name].setParent(None)

    @Slot(int)
    def resetControlFeedbackComboBox(self, row):
        tabIndex = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)
        self.manager.resetIndexFeedbackComboBox(row, name)

    @Slot(str, list)
    def addControlTable(self, name, defaultFeedbackChannel):
        # Add acquisition table to dict and update the TabWidget.
        self.controlTableViews[name] = ControlTableView(self.manager.controlModeList, self.manager.controlActuatorList, defaultFeedbackChannel)
        self.controlTableViews[name].setModel(self.manager.controlModels[name])
        self.controlTableViews[name].setFixedHeight(120)
        self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
        # self.controlTableViews[name].persistentEditorOpen()

    @Slot(dict)
    def updateUI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

        # Update icon colours as a function of the darkMode boolean.
        self.toolbar.updateIcons(self.darkMode)
        self.devicesGroupBox.deviceTableView.connectionIconDelegate.setIcon(self.darkMode)
        self.devicesGroupBox.deviceTableView.statusIconDelegate.setIcon(self.darkMode)

        # Update the UI of plot windows if they exist.
        if self.plots: 
            self.updatePlotWindows()

        log.info("Updated UI.")

    @Slot()
    def toggleMode(self):
        # Toggle between run and configuration modes by showing and hiding various UI items.
        self.statusGroupBox.setVisible(not self.statusGroupBox.isVisible())
        self.globalSettingsGroupBox.setVisible(not self.globalSettingsGroupBox.isVisible())
        self.devicesGroupBox.setVisible(not self.devicesGroupBox.isVisible())
        self.deviceConfigurationGroupBox.setVisible(not self.deviceConfigurationGroupBox.isVisible())
        if self.statusGroupBox.isVisible() == True:
            self.height = 300
            self.width = 800
        else:
            self.height = 1008
            self.width = 800
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)

    def setDarkMode(self):
        # Set the darkmode. 
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    @Slot(list)
    def addPlot(self):
        # Define a default configuration in the same format as we want it to be stored in self.manager.configuration["plots"][plotNumber].
        plotWindow = PlotWindow()
        plotNumber = str(id(plotWindow))
        plotWindow.setPlotNumber(plotNumber)

        #Store the plot windwow
        self.plots.update({plotNumber: plotWindow})

        # If the "plots" key doesn't exist in the configuration, it means no plots have been made before, so we add the key.
        # Otherwise we add the plot.
        # set colour for new plot window
        defaultProperties = {
            "invertX": False,
            "logXAxis": False,
            "invertY": False,
            "logYAxis": False,
            "setGrid": False,
            "setGridX": False,
            "setGridY": False,
            "alpha": 50,
            "opacity": 50,
            "auto": True,
            "autoX": True,
            "autoY": True,
            "manualX": False,
            "minXRange": 0,
            "maxXRange": 1,
            "manualY": False,
            "minYRange": 0,
            "maxYRange": 1,
            "lock": False,
            "channels": self.manager.getGenericChannelsData()
        }
        if "plots" not in self.manager.configuration:
            self.manager.configuration["plots"] = {plotNumber: copy.deepcopy(defaultProperties)}
        else:
            self.manager.configuration["plots"][plotNumber] = copy.deepcopy(defaultProperties)
            self.manager.setColourNewPlot(plotNumber)

        # Show the plot.
        plotWindow.show()

        # Connections.
        self.manager.configurationChanged.connect(self.plots[plotNumber].setConfiguration)
        self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updateLines)
        self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
        self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)

        # Run updatePlotWindows function to reset configuration.
        self.updatePlotWindows()
        
    @Slot()
    def updatePlotWindows(self):
        if "plots" in self.manager.configuration:
            for plotNumber in self.manager.configuration["plots"].keys():
                plotWindow = self.plots[plotNumber]
                plotWindow.setPlotNumber(plotNumber)
                plotWindow.setConfiguration(self.manager.configuration)

                # self.manager.updatePlotWindowChannelsData()
                # plotWindow.setChannelsModel(self.manager.configuration["plots"][plotNumber]["channels"])

    @Slot(QModelIndex, str)
    def updateChannelColours(self, index, colour):
        #print(colour)
        for plotNumber in self.manager.configuration["plots"].keys():
            self.plots[plotNumber].setColour(index, colour)
        self.updatePlotWindows()

    @Slot()
    def createExistingPlot(self):
        for plotNumber in self.manager.configuration["plots"].keys():
            
            plotWindow = PlotWindow()
            plotWindow.setPlotNumber(plotNumber)

            # plotWindow.setConfiguration(self.manager.configuration)
            # #plotWindow.setChannelsModel(self.manager.configuration["plots"][plotNumber]["channels"])

            self.plots.update({plotNumber: plotWindow})

            # Show the plot.
            plotWindow.show()

            # Connections.
            self.manager.configurationChanged.connect(self.plots[plotNumber].setConfiguration)
            self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updateLines)
            self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
            self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)
        self.updatePlotWindows()

    @Slot(str)
    def removePlot(self, plotNumber):
        # Pop plot from if "plots" key in dict.
        self.plots.pop(plotNumber)
        if "plots" in self.manager.configuration:
            self.manager.configuration["plots"].pop(plotNumber)
            # If plots dict in manager is empty delete the plots key.
            if self.manager.configuration["plots"] == {}:
                del self.manager.configuration["plots"]

    def clearPlots(self):
        plotList = list(self.plots.keys())
        for key in plotList:
            self.plots[key].close()

    def storePlot(self, plotWindow):
        self.plots.update({plotWindow.plotNumber: plotWindow})
        return self.plots

    def closeEvent(self, event):
        # Close all plots.
        plotList = list(self.plots.keys())
        for key in plotList:
            self.plots[key].close()

        # In the event the device list is refreshing, wait until complete before quitting all threads otherwise an error is shown, but hide the window in the meantime.
        self.setVisible(False)
        if self.manager.refreshing == True:
            log.info("Waiting for manager thread to finish refreshing the device list before closing.")
            while self.manager.refreshing == True:
                sleep(1.0)

        # Stop and quit all threads and plots and then close.
        for name in self.manager.deviceThreads:
            self.manager.deviceThreads[name].quit()
            log.info("Thread for " + name + " stopped.")
        self.manager.assemblyThread.quit()
        log.info("Assembly thread stopped.")
        self.manager.timing.stop()
        self.manager.timingThread.quit()
        log.info("Timing thread stopped.")
        self.managerThread.quit()
        log.info("Manager thread stopped.")
        log.info('Closing CamLab.')

if __name__ == '__main__':
    # Create log file instance.
    init_log()
    log = logging.getLogger(__name__)
    log.info('Log file created.')

    # Generate application instance.
    app = QApplication(sys.argv)
    app.setOrganizationName("CUED")
    app.setOrganizationDomain("Civil")
    app.setApplicationName("CamLab")
    app.setWindowIcon(QIcon("assets/NRFIS.svg"))

    # Execute main window.
    main = MainWindow()
    main.show()
    configurationPath = main.manager.configurationPath
    main.manager.loadConfiguration(configurationPath)
    log.info("Timer instantiated.")
    sys.exit(app.exec())

