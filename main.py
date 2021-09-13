import sys, os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QDialog, QPushButton, QLabel, QTableView, QHeaderView, QTabWidget, QGridLayout, QLineEdit, QFrame, QCheckBox, QColorDialog
from PySide6.QtGui import QIcon, QDoubleValidator, QCursor
from PySide6.QtCore import Signal, Slot, Qt, QObject, QAbstractTableModel, QModelIndex, QLocale, QPoint, QThread, QTimer
from qt_material import apply_stylesheet, QtStyleTools
from src.manager import Manager
from src.widgets import CamLabToolBar, StatusGroupBox, GlobalSettingsGroupBox, DevicesGroupBox, AcquisitionGroupBox, PlotWindow
from src.models import DeviceTableModel, AcquisitionTableModel
from src.views import DeviceTableView, AcquisitionTableView
from src.log import init_log
from src.dialogs import RefreshDevicesDialog
import logging
import copy 
from time import sleep

class MainWindow(QMainWindow, QtStyleTools):
    def __init__(self):
        super().__init__()  
        self.setWindowTitle("CamLab")
        self.width = 800
        self.height = 850
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)
        self.refreshing = False

        self.acquisitionTableViews = {}
        self.plotWindows = []

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

        # Acquisition groupbox.
        self.acquisitionGroupBox = AcquisitionGroupBox()
        self.mainWindowLayout.addWidget(self.acquisitionGroupBox)

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainWindowLayout)
        self.setCentralWidget(self.centralWidget)   

        self.channelsData = [   
            {"plot": False, "name": "Time", "device": "[ALL]", "colour": "#35e3e3", "value": "0.00", "unit": "s"},
            {"plot": True, "name": "LC1", "device": "[AMY]", "colour": "#35e3e3", "value": "243.32", "unit": "mm"},
            {"plot": False, "name": "LC2", "device": "[AMY]", "colour": "#414168", "value": "219.12", "unit": "kPa"},
            {"plot": False, "name": "PPT1", "device": "[DOT]", "colour": "#ffd035", "value": "1.22", "unit": "V"},
            {"plot": False, "name": "PPT2", "device": "[DOT]", "colour": "#b2df8a", "value": "1.32", "unit": "V"},
            {"plot": False, "name": "PPT3", "device": "[DOT]", "colour": "#a6cee3", "value": "1.44", "unit": "V"},
            {"plot": False, "name": "PPT4", "device": "[DOT]", "colour": "#a42f3b", "value": "2.35", "unit": "V"},
            {"plot": False, "name": "VDisp", "device": "[EVE]", "colour": "#cc9245", "value": "100.35", "unit": "V"},
            {"plot": False, "name": "HDisp", "device": "[EVE]", "colour": "#cab2d6", "value": "25.64", "unit": "V"}      
        ]
        
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
        self.manager.addAcquisitionTable.connect(self.addAcquisitionTable)
        self.manager.clearAcquisitionTabs.connect(self.clearAcquisitionTabs)
        self.manager.updateAcquisitionTabs.connect(self.updateAcquisitionTabs)
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.updateAcquisitionTabs)
        self.manager.startTimers.connect(self.start)
        self.manager.endTimers.connect(self.end)
        self.manager.assembly.samplesCount.connect(self.statusGroupBox.updateSamplesCount)
        self.manager.connectSampleTimer.connect(self.connectSampleTimerToDevice)

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

    @Slot(str)
    def addAcquisitionTable(self, name):
        # Add acquisition table to dict and update the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
    
    @Slot()
    def clearAcquisitionTabs(self):
        # Clear the acqusition table TabWidget.
        self.acquisitionGroupBox.acquisitionTabWidget.clear()
        
    @Slot()
    def updateAcquisitionTabs(self):
        # Clear the acqusition table TabWidget.
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
        index = self.acquisitionGroupBox.acquisitionTabWidget.indexOf(self.acquisitionTableViews[name])
        self.acquisitionGroupBox.acquisitionTabWidget.removeTab(index)

    @Slot(dict)
    def updateUI(self, newConfiguration):
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()
        self.updateToolBarIcons()
        self.updateTableIcons()
        # log.info("Updated main window settings in UI.")

    @Slot()
    def toggleMode(self):
        self.statusGroupBox.setVisible(not self.statusGroupBox.isVisible()) 
        self.globalSettingsGroupBox.setVisible(not self.globalSettingsGroupBox.isVisible())
        self.devicesGroupBox.setVisible(not self.devicesGroupBox.isVisible())
        self.acquisitionGroupBox.setVisible(not self.acquisitionGroupBox.isVisible()) 
        if self.statusGroupBox.isVisible() == True:
            self.height = 300
            self.width = 800
        else:
            self.height = 850
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

    def addPlot(self):
        # Function required here to generate the channelsData object, or load it from the configuration...
        channelsData = copy.deepcopy(self.channelsData)
        plotNumber = len(self.plotWindows)
        plotWindow = PlotWindow(plotNumber, self.darkMode, channelsData)
        self.plotWindows.append(plotWindow)
        plotWindow.show()
        
        # Connections.
        self.manager.configurationChanged.connect(self.plotWindows[plotNumber].updateUI)
        self.manager.assembly.plotDataChanged.connect(self.plotWindows[plotNumber].updateLines)
        self.plotWindows[plotNumber].plotWindowClosed.connect(self.removePlot)

    def removePlot(self, plotNumber):
        self.plotWindows.pop(plotNumber)

    def closeEvent(self, event):
        # Close all plots.
        for plot in self.plotWindows:
            plot.close()

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
    