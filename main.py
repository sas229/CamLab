import sys, os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QTabWidget
from PySide6.QtGui import QIcon, QScreen
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QPoint, QThread, QTimer, QDir
from src.local_qt_material import apply_stylesheet, QtStyleTools
from src.manager import Manager
from src.widgets import CamLabToolBar, TabInterface, StatusGroupBox, GlobalSettingsGroupBox, DevicesGroupBox, ConfigurationGroupBox, PlotWindow, ControlWindow, LinearAxis
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
    running = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamLab")
        self.width = 800
        self.height = 955
        # self.setFixedWidth(self.width)
        # self.setFixedHeight(self.height)
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
        self.setGeometry(x, y, self.width, self.height)

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

        # # Status groupbox.
        self.statusGroupBox = StatusGroupBox()
        # self.mainWindowLayout.addWidget(self.statusGroupBox)

        self.configurationWidget = QWidget()

        # Global settings groupbox.
        self.globalSettingsGroupBox = GlobalSettingsGroupBox(self.configuration)
        
        # Device table groupbox.
        self.devicesGroupBox = DevicesGroupBox(self.configuration)
        self.devicesGroupBox.deviceTableView.setModel(self.manager.deviceTableModel)

        # # Device configuration groupbox.
        self.configurationGroupBox = ConfigurationGroupBox()

        self.configurationLayout = QGridLayout()
        self.configurationLayout.setRowStretch(0, 1)
        self.configurationLayout.addWidget(self.globalSettingsGroupBox, 1, 0, 1, 1)
        self.configurationLayout.addWidget(self.devicesGroupBox, 2, 0, 1, 1)
        self.configurationLayout.addWidget(self.configurationGroupBox, 1, 1, 2, 1)
        self.configurationLayout.setRowStretch(self.configurationLayout.rowCount(), 1)

        self.configurationWidget.setLayout(self.configurationLayout)
        self.tabs.addPersistentTab(self.configurationWidget, "Configuration")
        self.tabs.addPersistentTab(QWidget(), "Sequences")
        self.tabs.addPersistentTab(QWidget(), "Dashboard")

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

    @Slot()
    def windowToTab(self, widget):
        if self.tabs.indexOf(widget) == -1:
            widget.setWindowFlags(Qt.Widget)
            # If not a PlotWindow, insert in order.
            if not isinstance(widget, PlotWindow):
                controlDevice, channel = widget.controlName.split(' ')
                devices = self.manager.deviceTableModel.enabledDevices()
                #  For each device get a list of enabled control channels.
                index = 3
                for device in devices:
                    deviceName = device["name"]
                    controls = self.manager.controlTableModels[deviceName].enabledControls()
                    for control in controls:
                        controlChannel = control["channel"]
                        controlChannelName = control["name"]
                        controlName = deviceName + " " + controlChannel
                        if deviceName == controlDevice and controlChannel == channel:
                            self.tabs.insertPersistentTab(index, widget, widget.windowTitle())
                        index += 1
            # Otherwise append on end of tab bar.
            else:
                self.tabs.addTab(widget, widget.windowTitle())    

    @Slot()
    def tabToWindow(self, widget, index):
        if index != -1:
            text = self.tabs.tabText(index)
            self.tabs.removeTab(index)
            widget.setWindowFlags(Qt.Window)
            widget.setWindowTitle(text)
            widget.show()

    @Slot()
    def clearControls(self):
        # Remove all control tabs.
        tabs = self.tabs.count()
        for index in reversed(range(tabs)):
            widget = self.tabs.widget(index)
            text = self.tabs.tabText(index)
            if not isinstance(widget, PlotWindow):
                if text != "Dashboard" and text != "Configuration" and text != "Sequences":
                    self.tabs.removeTab(index)

    @Slot() 
    def updateControlTabs(self):
        # Method to update control tab widgets.
        self.clearControls()
        devices = self.manager.deviceTableModel.enabledDevices()
        #  For each device get a list of enabled control channels.
        index = 3
        for device in devices:
            deviceName = device["name"]
            controls = self.manager.controlTableModels[deviceName].enabledControls()
            for control in controls:
                controlChannel = control["channel"]
                controlChannelName = control["name"]
                controlName = deviceName + " " + controlChannel

                #  Create control widget.
                if control["control"] == 0:
                    controlWidget = LinearAxis(controlName)

                    # Connections.
                    controlWidget.enable.connect(self.manager.devices[deviceName].setEnable)
                    controlWidget.secondarySetPointChanged.connect(self.manager.devices[deviceName].setSpeed)
                    controlWidget.positiveJogEnabled.connect(self.manager.devices[deviceName].jogPositiveOn)
                    controlWidget.positiveJogDisabled.connect(self.manager.devices[deviceName].jogPositiveOff)
                    controlWidget.negativeJogEnabled.connect(self.manager.devices[deviceName].jogNegativeOn)
                    controlWidget.negativeJogDisabled.connect(self.manager.devices[deviceName].jogNegativeOff)
                    controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[deviceName].updatePositionLeftLimit)
                    controlWidget.primaryRightLimitChanged.connect(self.manager.devices[deviceName].updatePositionRightLimit)
                    controlWidget.primarySetPointChanged.connect(self.manager.devices[deviceName].moveToPosition)
                    controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackLeftLimit)
                    controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackRightLimit)
                    controlWidget.feedbackSetPointChanged.connect(self.manager.devices[deviceName].setFeedbackSetPoint)
                    controlWidget.zeroPosition.connect(self.manager.devices[deviceName].zeroPosition)
                    controlWidget.stopCommand.connect(self.manager.devices[deviceName].stopCommand)
                    controlWidget.PIDControl.connect(self.manager.devices[deviceName].setPIDControl)
                    controlWidget.KPChanged.connect(self.manager.devices[deviceName].setKP)
                    controlWidget.KIChanged.connect(self.manager.devices[deviceName].setKI)
                    controlWidget.KDChanged.connect(self.manager.devices[deviceName].setKD)
                    controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[deviceName].setPoM)
                    controlWidget.axisWindowClosed.connect(self.windowToTab)
                    self.checkTimer.timeout.connect(self.manager.devices[deviceName].checkConnection)
                    self.running.connect(self.manager.devices[deviceName].setRunning)
                    self.manager.devices[deviceName].updateRunningIndicator.connect(controlWidget.setRunningIndicator)
                    if control["channel"] == "C1":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC1)
                        self.manager.devices[deviceName].updateLimitIndicatorC1.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC1.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC1.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC1.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC1.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC1.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC1.connect(controlWidget.setFeedbackProcessVariable)
                    elif control["channel"] == "C2":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC2)
                        self.manager.devices[deviceName].updateLimitIndicatorC2.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC2.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC2.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC2.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC2.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC2.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC2.connect(controlWidget.setFeedbackProcessVariable)
                else:
                    controlWidget = QWidget()

                # Check configuration for previous settings, otherwise take defaults.
                if controlName not in self.manager.configuration["controlWindow"]:
                    self.defaultControlSettings = {
                        "name": controlChannelName,
                        "device": deviceName,
                        "channel": controlChannel,
                        "primaryMinimum": -100.00,
                        "primaryMaximum": 100.00,
                        "primaryLeftLimit": -80.00,
                        "primaryRightLimit": 80.00,
                        "primarySetPoint": 0.00,
                        "primaryProcessVariable": 0.00,
                        "primaryUnit": "(mm)",
                        "secondarySetPoint": 3.000,
                        "secondaryUnit": "(mm/s)",
                        "feedbackMinimum": -20.00,
                        "feedbackMaximum": 100.00,
                        "feedbackLeftLimit": -10.00,
                        "feedbackRightLimit": 90.00,
                        "feedbackSetPoint": 0.00,
                        "feedbackProcessVariable": 0.00,
                        "feedbackUnit": "(N)",
                        "feedbackChannel": "N/A",
                        "KP": 1.00,
                        "KI": 1.00,
                        "KD": 1.00,
                        "proportionalOnMeasurement": False
                    }
                    self.manager.configuration["controlWindow"][controlName] = copy.deepcopy(self.defaultControlSettings)

                # Check for feedback channel.
                if control["feedback"] == 0:
                    self.manager.configuration["controlWindow"][controlName]["enablePIDControl"] = False
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "N/A"
                else:
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "AIN" + str(control["feedback"])
                #  Update control name.
                self.manager.configuration["controlWindow"][controlName]["name"] = controlChannelName
                
                # Set the configuration.
                controlWidget.setConfiguration(configuration=self.manager.configuration)
                self.manager.devices[deviceName].checkConnection()
                self.manager.devices[deviceName].setPosition(controlChannel, self.manager.configuration["controlWindow"][controlName]["primaryProcessVariable"])
                
                # Add to tab bar.
                self.tabs.insertPersistentTab(index, controlWidget, controlChannelName)
                index += 1

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
        self.running.emit(False)
        self.updateTimer.stop()
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

    @Slot(str, list)
    def addDeviceConfigurationTab(self, name, defaultFeedbackChannel):
        # Create layout.
        self.deviceConfigurationLayout[name] = QVBoxLayout()

        # Add acquisition table label.
        acquisitionLabel = QLabel('Acquisition')
        self.deviceConfigurationLayout[name].addWidget(acquisitionLabel)

        # Add acquisition table to the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.setListFeedbackCombobox)
        self.manager.acquisitionModels[name].acquisitionChannelToggled.connect(self.resetControlFeedbackComboBox)

        # Add control table label.
        controlLabel = QLabel('Control')
        self.deviceConfigurationLayout[name].addWidget(controlLabel)

        # Add control table to the TabWidget.
        self.addControlTable(name, defaultFeedbackChannel)
        self.manager.controlTableModels[name].controlChannelNameChanged.connect(self.manager.updatePlotWindowChannelsData)

        # Set layout within widget.
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

    @Slot()
    def updateDeviceConfigurationTabs(self):
        # Clear the acquisition table TabWidget.
        self.configurationGroupBox.deviceConfigurationTabWidget.clear()

        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()

        # If enabled and status is True, add the TabWidget for this device.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.acquisitionTableViews:
                self.configurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)

    @Slot()
    def clearDeviceConfigurationTabs(self):
        self.configurationGroupBox.deviceConfigurationTabWidget.clear()

    @Slot(str)
    def removeControlTable(self,name):
        self.controlTableViews[name].setParent(None)

    @Slot(int)
    def resetControlFeedbackComboBox(self, row):
        # Method receives the row of the acquisition channel toggled and then gets the name of the channel and sends it to manager.
        tabIndex = self.configurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.configurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)
        self.manager.resetIndexFeedbackComboBox(row, name)

    @Slot(str, list)
    def addControlTable(self, name, defaultFeedbackChannel):
        # Add acquisition table to dict, update the TabWidget and connect to control widget generation method.
        self.controlTableViews[name] = ControlTableView(self.manager.controlModeList, self.manager.controlActuatorList, defaultFeedbackChannel)
        self.controlTableViews[name].setModel(self.manager.controlTableModels[name])
        self.controlTableViews[name].setFixedHeight(89)
        self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
        self.manager.controlTableModels[name].controlChannelToggled.connect(self.updateControlTabs)
        self.updateControlTabs()

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

    @Slot(list)
    def addPlot(self):
        # Define a default configuration in the same format as we want it to be stored in self.manager.configuration["plots"][plotNumber].
        plotWindow = PlotWindow()
        plotNumber = str(id(plotWindow))
        plotWindow.setPlotNumber(plotNumber)

        # Store the plot windwow.
        self.plots.update({plotNumber: plotWindow})

        # Defaults.
        width = 1200
        height = 800
        x = self.screenSize.width()/2 - width/2
        y = self.screenSize.height()/2 - height/2
        defaultProperties = {
            "alpha": 50,
            "auto": True,
            "autoCommonAxis": True,
            "autoSelectedAxis": True,
            "height": height,
            "width": width,
            "invertCommonAxis": False,
            "invertSelectedAxis": False,
            "lock": False,
            "lockCommonAxis": False,
            "lockSelectedAxis": False,
            "logCommonAxis": False,
            "logSelectedAxis": False,          
            "manualCommonAxis": False,
            "manualSelectedAxis": False,
            "minCommonAxisRange": 0,
            "minSelectedAxisRange": 0,
            "maxCommonAxisRange": 1,
            "maxSelectedAxisRange": 1,
            "minCommonAxisRangeLock": 0,
            "minSelectedAxisRangeLock": 0,
            "maxCommonAxisRangeLock": 1,
            "maxSelectedAxisRangeLock": 1,
            "opacity": 50,
            "setGrid": False,
            "swap": False,
            "x": x,
            "y": y,
            "channels": self.manager.getGenericChannelsData()
        }

        # If the "plots" key doesn't exist in the configuration, it means no plots have been made before, so we add the key.
        # Otherwise we add the plot and set the colour for the new plot window.        
        if "plots" not in self.manager.configuration:
            self.manager.configuration["plots"] = {plotNumber: copy.deepcopy(defaultProperties)}
        else:
            self.manager.configuration["plots"][plotNumber] = copy.deepcopy(defaultProperties)
        self.manager.setColourNewPlot(plotNumber)

        # Show the plot.
        plotWindow.setConfiguration(self.manager.configuration)
        self.tabs.addTab(self.plots[plotNumber], "Plot")

        # Connections.
        self.manager.configurationChanged.connect(self.plots[plotNumber].setConfiguration)
        self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updatePlotData)
        # self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
        self.plots[plotNumber].plotWindowClosed.connect(self.windowToTab)
        self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)

        # Update all plot windows to reset configuration.
        self.updatePlots()

    @Slot()
    def createExistingPlots(self):
        # For all plots in self.manager.configuration["plots"][plotNumber], create a plot window.
        for plotNumber in self.manager.configuration["plots"].keys():
            # Create plot window object and set the plot number.
            plotWindow = PlotWindow()
            plotWindow.setPlotNumber(plotNumber)

            # Store plot window object in plots dict.
            self.plots.update({plotNumber: plotWindow})

            # Show the plot.
            plotWindow.setConfiguration(self.manager.configuration)
            self.tabs.addTab(self.plots[plotNumber], "Plot")

            # Connections.
            self.manager.configurationChanged.connect(self.plots[plotNumber].setConfiguration)
            self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updatePlotData)
            # self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
            self.plots[plotNumber].plotWindowClosed.connect(self.windowToTab)
            self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)
        
        # Update all plot windows to reset configuration.
        self.updatePlots()
        
    @Slot()
    def updatePlots(self):
        # If plots exist update the configuration.
        if "plots" in self.manager.configuration:
            for plotNumber in self.manager.configuration["plots"].keys():
                plotWindow = self.plots[plotNumber]
                plotWindow.setPlotNumber(plotNumber)
                plotWindow.setConfiguration(self.manager.configuration)
                
    @Slot(str)
    def removePlot(self, plotNumber):
        # Pop plot from if "plots" key in dict.
        if plotNumber in self.plots:
            self.plots.pop(plotNumber)
        if "plots" in self.manager.configuration:
            self.manager.configuration["plots"].pop(plotNumber)
            # If plots dict in manager is empty delete the plots key.
            if self.manager.configuration["plots"] == {}:
                del self.manager.configuration["plots"]
    
    def closePlots(self):
        # Remove plot tabs.
        tabs = self.tabs.count()
        for index in reversed(range(tabs)):
            widget = self.tabs.widget(index)
            text = self.tabs.tabText(index)
            if isinstance(widget, PlotWindow):
                self.tabs.removeTab(index)
        self.plots = {}

    @Slot(QModelIndex, str)
    def updateChannelColours(self, index, colour):
        # Update colours of channels in all plots.
        for plotNumber in self.manager.configuration["plots"].keys():
            self.plots[plotNumber].setColour(index, colour)
        self.updatePlots()

    def closeEvent(self, event):
        # Close all plots.
        self.closePlots()

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

