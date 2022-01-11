import sys, os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, \
    QPushButton, QLabel, QTableView, QHeaderView, QTabWidget, QGridLayout, QLineEdit, QFrame, QCheckBox, QColorDialog
from PySide6.QtGui import QIcon, QDoubleValidator, QCursor
from PySide6.QtCore import Signal, Slot, Qt, QObject, QAbstractTableModel, QModelIndex, QLocale, QPoint, QThread, QTimer
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

        self.deviceConfigurationLayout = {}
        self.deviceConfigurationWidget = {}
        self.acquisitionTableViews = {}
        self.controlTableViews = {}
        self.plots = {}

        # Timers.
        self.plotTimer = QTimer()
        self.displayTimer = QTimer()
        self.sampleTimer = QTimer()

        # Instantiate the manager object and thread.
        self.manager = Manager()
        self.managerThread = QThread(parent=self)
        self.manager.moveToThread(self.managerThread)
        self.managerThread.start()

        # Extract the configuration to generate initial UI setup.
        self.configuration = self.manager.configuration

        # Set dark mode.
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

        # Main window layout.
        log.info("Assembling UI.")
        self.mainWindowLayout = QVBoxLayout()

        # Toolbar.
        self.toolbar = CamLabToolBar(self.configuration)
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

        # Device Configuration groupbox
        self.deviceConfigurationGroupBox = DeviceConfigurationGroupBox()
        self.mainWindowLayout.addWidget(self.deviceConfigurationGroupBox)

        # Acquisition groupbox.
        self.acquisitionGroupBox = AcquisitionGroupBox()
        #self.mainWindowLayout.addWidget(self.acquisitionGroupBox)

        # control groupbox.
        self.controlGroupBox = ControlGroupBox()
        #self.mainWindowLayout.addWidget(self.controlGroupBox)

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainWindowLayout)
        self.setCentralWidget(self.centralWidget)

        # Connections.
        self.toolbar.modeButton.triggered.connect(self.toggleMode)
        self.toolbar.refreshButton.triggered.connect(self.manager.refreshDevices)
        self.toolbar.loadConfiguration.connect(self.manager.loadConfiguration)
        self.toolbar.saveConfiguration.connect(self.manager.saveConfiguration)
        self.toolbar.clearConfigButton.triggered.connect(self.manager.clearConfiguration)
        self.toolbar.darkModeChanged.connect(self.manager.updateDarkMode)
        self.toolbar.configure.connect(self.manager.configure)
        self.toolbar.run.connect(self.manager.run)
        self.toolbar.addPlotButton.triggered.connect(self.addPlot)
        self.toolbar.run.connect(self.statusGroupBox.setInitialTime)
        self.toolbar.clearPlotsButton.triggered.connect(self.manager.assembly.clearPlotData)
        self.toolbar.autozeroButton.triggered.connect(self.manager.assembly.autozero)

        self.globalSettingsGroupBox.acquisitionRateChanged.connect(self.manager.updateAcquisitionRate)
        self.globalSettingsGroupBox.controlRateChanged.connect(self.manager.updateControlRate)
        self.globalSettingsGroupBox.averageSamplesChanged.connect(self.manager.updateAverageSamples)
        self.globalSettingsGroupBox.pathChanged.connect(self.manager.updatePath)
        self.globalSettingsGroupBox.filenameChanged.connect(self.manager.updateFilename)

        self.manager.updateUI.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.updateUI)
        self.manager.configurationChanged.connect(self.globalSettingsGroupBox.updateUI)
        #self.manager.addAcquisitionTable.connect(self.addAcquisitionTable)
        self.manager.clearAcquisitionTabs.connect(self.clearAcquisitionTabs)
        #self.manager.updateAcquisitionTabs.connect(self.updateAcquisitionTabs)
        self.manager.addDeviceConfiguration.connect(self.addDeviceConfiguration)
        self.manager.removeWidget.connect(self.removeWidgetFromLayout)
        self.manager.addControlTable.connect(self.addControlTable)
        #self.manager.updateControlTabs.connect(self.updateControlTabs)
        self.manager.clearControlTabs.connect(self.clearControlTabs)
        self.manager.updateDeviceConfigurationTab.connect(self.updateDeviceConfigurationTabs)
        #self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateAcquisitionTabs)
        #self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateControlTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateDeviceConfigurationTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.startTimers.connect(self.start)
        self.manager.endTimers.connect(self.end)
        self.manager.assembly.samplesCount.connect(self.statusGroupBox.updateSamplesCount)
        self.manager.connectSampleTimer.connect(self.connectSampleTimerToDevice)
        self.manager.plotWindowChannelsUpdated.connect(self.updatePlotWindows)
        self.manager.existingPlotFound.connect(self.createExistingPlot)
        #self.acquisitionGroupBox.acquisitionTabWidget.currentChanged.connect(self.updateControlTabs)
        #self.controlGroupBox.controlTabWidget.currentChanged.connect(self.updateAcquisitionTabs)


        self.plotTimer.timeout.connect(self.manager.assembly.updatePlotData)
        self.displayTimer.timeout.connect(self.statusGroupBox.updateTimes)

    @Slot(str)
    def connectSampleTimerToDevice(self, name):
        self.sampleTimer.timeout.connect(self.manager.devices[name].readValues)

    @Slot()
    def start(self):
        self.plotTimer.start(250)
        self.displayTimer.start(1000)
        self.sampleTimer.start(1)

    @Slot()
    def end(self):
        self.plotTimer.stop()
        self.displayTimer.stop()
        self.sampleTimer.stop()

    @Slot(str, list)
    def addDeviceConfiguration(self, name, item3):

        self.deviceConfigurationLayout[name] = QVBoxLayout()
        acquisitionLabel = QLabel('ACQUISITION')

        self.deviceConfigurationLayout[name].addWidget(acquisitionLabel)
        self.addAcquisitionTable(name)

        #self.acquisitionTableViews[name].setFixedHeight(230)
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])
        conrtrolLabel = QLabel('CONTROL')
        self.deviceConfigurationLayout[name].addWidget(conrtrolLabel)
        self.addControlTable(name, item3)
        # self.controlTableViews[name].setFixedHeight(120)
        # self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

    @Slot()
    def updateDeviceConfigurationTabs(self):
        # Clear the acquisition table TabWidget.
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()
        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        # If enabled and available, add the TabWidget.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.acquisitionTableViews:
                self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)

    @Slot(str)
    def removeWidgetFromLayout(self,name):
        self.controlTableViews[name].setParent(None)

    @Slot(int)
    def resetControlFeedbackComboBox(self, row):
        tabIndex = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)
        # print(name)
        self.manager.resetIndexFeedbackComboBox(row, name)

    def addAcquisitionTable(self, name):
        # Add acquisition table to dict and update the TabWidget.
        #self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(
            self.manager.setListFeedbackCombobox)
        self.manager.acquisitionModels[name].channelIndexToggled.connect(
            self.resetControlFeedbackComboBox)

    @Slot()
    def clearAcquisitionTabs(self):
        # Clear the acqusition table TabWidget.
        self.acquisitionGroupBox.acquisitionTabWidget.clear()

    @Slot()
    def updateAcquisitionTabs(self):

        # Clear the acquisition table TabWidget.
        self.acquisitionGroupBox.acquisitionTabWidget.clear()
        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        # If enabled and available, add the TabWidget.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.acquisitionTableViews:
                self.acquisitionGroupBox.acquisitionTabWidget.addTab(self.acquisitionTableViews[name], name)

    @Slot(str)
    def removeAcquisitionTable(self, name):
        indexTab = self.acquisitionGroupBox.acquisitionTabWidget.indexOf(self.acquisitionTableViews[name])
        self.acquisitionGroupBox.acquisitionTabWidget.removeTab(indexTab)


    @Slot(str, list)
    def addControlTable(self, name, item3):
        # Add acquisition table to dict and update the TabWidget.
        self.controlTableViews[name] = ControlTableView(self.manager.item1, self.manager.item2, item3)
        self.controlTableViews[name].setModel(self.manager.controlModels[name])
        self.controlTableViews[name].setFixedHeight(120)
        self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
        #self.controlTableViews[name].persistentEditorOpen()

    @Slot()
    def clearControlTabs(self):
        # Clear the Control table TabWidget.
        self.controlGroupBox.controlTabWidget.clear()

    @Slot()
    def updateControlTabs(self):
        # Clear the acquisition table TabWidget.
        self.controlGroupBox.controlTabWidget.clear()
        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        indexAcquistionTab = self.acquisitionGroupBox.acquisitionTabWidget.currentIndex()
        # If enabled and available, add the TabWidget.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.controlTableViews:
                self.controlGroupBox.controlTabWidget.addTab(self.controlTableViews[name], name)
                self.controlGroupBox.controlTabWidget.setCurrentIndex(indexAcquistionTab)

    @Slot(dict)
    def updateUI(self, newConfiguration):
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()
        self.updateToolBarIcons()
        self.updateTableIcons()
        #log.info("Updated main window settings in UI.")

    @Slot()
    def toggleMode(self):
        self.statusGroupBox.setVisible(not self.statusGroupBox.isVisible())
        self.globalSettingsGroupBox.setVisible(not self.globalSettingsGroupBox.isVisible())
        self.devicesGroupBox.setVisible(not self.devicesGroupBox.isVisible())
        self.deviceConfigurationGroupBox.setVisible(not self.deviceConfigurationGroupBox.isVisible())
        #self.acquisitionGroupBox.setVisible(not self.acquisitionGroupBox.isVisible())
        #self.controlGroupBox.setVisible(not self.controlGroupBox.isVisible())
        if self.statusGroupBox.isVisible() == True:
            self.height = 300
            self.width = 800
        else:
            self.height = 1008
            self.width = 800
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)

    def setDarkMode(self):
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    def updateToolBarIcons(self):
        self.toolbar.updateIcons(self.darkMode)

    def updateTableIcons(self):
        # Workaround to change icon style in device table delegates.
        self.devicesGroupBox.deviceTableView.connectionIconDelegate.setIcon(self.darkMode)
        self.devicesGroupBox.deviceTableView.statusIconDelegate.setIcon(self.darkMode)

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
        # self.manager.configuration["plots"][plotNumber]["channels"] = copy.deepcopy(self.manager.getGenericChannelsData())

        # Update the configuration in the PlotWindow object.
        self.plots[plotNumber].setConfiguration(self.manager.configuration)
        #self.plots[plotNumber].setChannelsModel(self.manager.configuration["plots"][plotNumber]["channels"])

        # Show the plot.
        plotWindow.show()

        # Connections.
        self.manager.configurationChanged.connect(self.plots[plotNumber].updateUI)
        self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updateLines)
        self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
        self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)

    @Slot()
    def updatePlotWindows(self):

        for plotNumber in self.manager.configuration["plots"].keys():
            plotWindow = self.plots[plotNumber]
            plotWindow.setPlotNumber(plotNumber)
            plotWindow.setConfiguration(self.manager.configuration)
            #plotWindow.setChannelsModel(self.manager.configuration["plots"][plotNumber]["channels"])


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

            plotWindow.setConfiguration(self.manager.configuration)
            #plotWindow.setChannelsModel(self.manager.configuration["plots"][plotNumber]["channels"])

            self.plots.update({plotNumber: plotWindow})

            plotWindow.show()

            self.manager.configurationChanged.connect(self.plots[plotNumber].updateUI)
            self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].updateLines)
            self.plots[plotNumber].plotWindowClosed.connect(self.removePlot)
            self.plots[plotNumber].colourUpdated.connect(self.updateChannelColours)

    @Slot(str)
    def removePlot(self, plotNumber):

        self.plots.pop(plotNumber)
        self.manager.configuration["plots"].pop(plotNumber)

        if self.manager.configuration["plots"] == {}:
            del self.manager.configuration["plots"]

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

        # Quit all threads and plots and then close.
        for name in self.manager.deviceThread:
            self.manager.deviceThread[name].quit()
            log.info("Thread for " + name + " stopped.")
        self.manager.assemblyThread.quit()
        log.info("Assembly thread stopped.")
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

