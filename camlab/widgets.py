import os
from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QFrame, QFileDialog, QComboBox, QSlider
from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QIntValidator, QFont
from PySide6.QtCore import Signal, Slot, Qt, QTime, QDate
from qt_material import apply_stylesheet, QtStyleTools
from camlab.models import ChannelsTableModel, ColourPickerTableModel
from camlab.views import ChannelsTableView, ColourPickerTableView
from camlab.dialogs import ColourPickerDialog
import logging
import pyqtgraph as pg
import numpy as np
from datetime import datetime
from qtrangeslider import QRangeSlider

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
        self.refreshButton.setIcon(QIcon("assets/restart_alt_white_24dp.svg" if self.darkMode else "assets/restart_alt_black_24dp.svg"))
        self.loadConfigButton.setIcon(QIcon("assets/file_upload_white_24dp.svg" if self.darkMode else "assets/file_upload_black_24dp.svg"))
        self.saveConfigButton.setIcon(QIcon("assets/file_download_white_24dp.svg" if self.darkMode else "assets/file_download_black_24dp.svg"))
        self.clearConfigButton.setIcon(QIcon("assets/clear_white_24dp.svg" if self.darkMode else "assets/clear_black_24dp.svg"))
        self.darkModeButton.setIcon(QIcon("assets/light_mode_white_24dp.svg" if self.darkMode else "assets/dark_mode_black_24dp.svg"))
        self.darkModeButton.setToolTip("Click for light mode." if self.darkMode else "Click for dark mode.")
        # log.info("Dark mode enabled." if self.darkMode else "Light mode enabled")

    def emitLoadConfiguration(self):
        filename, _ = QFileDialog.getOpenFileName(self,"Open CamLab configuration file", "","Yaml files (*.yaml)")
        self.loadConfiguration.emit(filename)

    def emitSaveConfiguration(self):
        filename, _ = QFileDialog.getSaveFileName(self,"Save CamLab configuration file", "","Yaml files (*.yaml)")
        self.saveConfiguration.emit(filename)

    def emitDarkModeChanged(self):
        self.darkModeChanged.emit(not self.darkMode)


class StatusGroupBox(QGroupBox):

    def __init__(self):
        super().__init__() 
        self.setTitle("Status")
        self.setVisible(False)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 5)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        self.initialTime = datetime.now()
        self.currentTime = datetime.now()
        date = QDate.currentDate()

        self.dateLabel = QLabel()
        self.dateLabel.setText("Date:")
        self.layout.addWidget(self.dateLabel, 0, 0)

        self.timeLabel = QLabel()
        self.timeLabel.setText("Current time:")
        self.layout.addWidget(self.timeLabel, 0, 1)

        self.elapsedLabel = QLabel()
        self.elapsedLabel.setText("Elapsed time:")
        self.layout.addWidget(self.elapsedLabel, 0, 2)

        self.date = QLabel()
        self.date.setFont(QFont("Arial", 25))
        self.date.setText(date.toString(Qt.ISODate))
        self.layout.addWidget(self.date, 1, 0)
        
        self.clock = QLabel()
        self.clock.setFont(QFont("Arial", 25))
        self.clock.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        self.layout.addWidget(self.clock, 1, 1)

        self.outputLabel = QLabel()
        self.outputLabel.setText("Output:")
        self.layout.addWidget(self.outputLabel, 2, 0, 1, 3)

        self.output = QLabel()
        self.output.setFont(QFont("Arial", 15))
        self.output.setText("{path}/{date}_{hours:02}:{minutes:02}:{seconds:02}.txt".format(path="/home/data", date=date.toString(Qt.ISODate), hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        self.layout.addWidget(self.output, 3, 0, 1, 3)
        
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)
        self.elapsed = QLabel()
        self.elapsed.setFont(QFont("Arial", 25))
        self.elapsed.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second))
        self.layout.addWidget(self.elapsed, 1, 2)
        self.setLayout(self.layout)

    def setInitialTime(self):
        self.initialTime = datetime.now()

    def updateTimes(self):
        self.currentTime = datetime.now()
        self.clock.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)
        self.elapsed.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second))


class GlobalSettingsGroupBox(QGroupBox):
    darkModeChanged = Signal(bool)
    acquisitionRateChanged = Signal(str)
    controlRateChanged = Signal(str)
    averageSamplesChanged = Signal(str)
    pathChanged = Signal(str)
    filenameChanged = Signal(str)

    def __init__(self, configuration):
        super().__init__() 
        self.configuration = configuration
        self.setTitle("Global Settings")

        # Set path inputs.
        self.setPathLabel = QLabel("Output")
        self.setPathButton = QPushButton("Set Path")
        self.setPathAddressLabel = QLineEdit()
        self.setPathAddressLabel.setText(self.configuration["global"]["path"])
        self.setPathAddressLabel.setEnabled(False)
        self.setFilenameLineEdit = QLineEdit()
        self.setFilenameLineEdit.setText(self.configuration["global"]["filename"])

        # Set path layout.
        self.setPathLayout = QHBoxLayout()
        self.setPathLayout.addWidget(self.setPathButton)
        self.setPathLayout.addWidget(self.setPathAddressLabel, 4)
        self.setPathLayout.addWidget(self.setFilenameLineEdit)

        # Control rate input and validator.
        self.controlRateLabel = QLabel("Control Rate (Hz)")
        self.controlRateLineEdit = QLineEdit()
        self.controlRateValidator = QDoubleValidator(bottom = 0.10, top = 1000.00, decimals=2)
        self.controlRateLineEdit.setValidator(self.controlRateValidator)
        self.controlRateLineEdit.setText(str(self.configuration["global"]["controlRate"]))

        # Acquisition rate input and validator.
        self.acquisitionRateLabel = QLabel("Acquisition Rate (Hz)")
        self.acquisitionRateLineEdit = QLineEdit()
        self.acquisitionRateValidator = QDoubleValidator(bottom = 0.01, top = 100.00, decimals=2)
        self.acquisitionRateLineEdit.setValidator(self.acquisitionRateValidator)
        self.acquisitionRateLineEdit.setText(str(self.configuration["global"]["acquisitionRate"]))

        # Sample averaging and validator.
        self.averageSamplesLabel = QLabel("Samples to average (-)")
        self.averageSamplesLineEdit = QLineEdit()
        self.averageSamplesValidator = QIntValidator(bottom = 1, top = 100)
        self.averageSamplesLineEdit.setValidator(self.averageSamplesValidator)
        self.averageSamplesLineEdit.setText(str(self.configuration["global"]["averageSamples"]))

        # Rates layout.
        self.ratesLayout = QGridLayout()
        self.ratesLayout.addWidget(self.controlRateLabel, 0, 0)
        self.ratesLayout.addWidget(self.controlRateLineEdit, 1, 0)
        self.ratesLayout.addWidget(self.acquisitionRateLabel, 0, 1)
        self.ratesLayout.addWidget(self.acquisitionRateLineEdit, 1, 1)
        self.ratesLayout.addWidget(self.averageSamplesLabel, 0, 2)
        self.ratesLayout.addWidget(self.averageSamplesLineEdit, 1, 2)

        # Horizontal separator.
        self.horizontalSeparator = QFrame()
        self.horizontalSeparator.setFrameShape(QFrame.HLine)
        self.horizontalSeparator.setFixedHeight(4)
        self.horizontalSeparator.setFrameShadow(QFrame.Sunken)

        # Verical separator.
        self.verticalSeparator = QFrame()
        self.verticalSeparator.setFrameShape(QFrame.VLine)
        self.verticalSeparator.setFixedHeight(2)
        self.verticalSeparator.setFrameShadow(QFrame.Sunken)
        
        # Assemble nested layouts.
        self.globalSettingsVLayout = QVBoxLayout()
        self.globalSettingsVLayout.addLayout(self.ratesLayout)
        self.globalSettingsVLayout.addWidget(self.horizontalSeparator)
        self.globalSettingsVLayout.addWidget(self.setPathLabel)
        self.globalSettingsVLayout.addLayout(self.setPathLayout)

        # Set global settings groupbox layout.
        self.setLayout(self.globalSettingsVLayout)

        # Connections.
        self.acquisitionRateLineEdit.editingFinished.connect(self.emitAcquisitionRate)
        self.controlRateLineEdit.editingFinished.connect(self.emitControlRate)
        self.averageSamplesLineEdit.editingFinished.connect(self.emitAverageSamples)
        self.setPathButton.clicked.connect(self.emitPath)
        self.setFilenameLineEdit.editingFinished.connect(self.emitFilename)
    
    @Slot()
    def updateUI(self, newConfiguration):
        self.configuration = newConfiguration
        self.acquisitionRateLineEdit.setText(str(self.configuration["global"]["acquisitionRate"]))
        self.controlRateLineEdit.setText(str(self.configuration["global"]["controlRate"]))
        self.averageSamplesLineEdit.setText(str(self.configuration["global"]["averageSamples"]))
        self.setPathAddressLabel.setText(self.configuration["global"]["path"])
        self.setFilenameLineEdit.setText(self.configuration["global"]["filename"])
        # log.info("Updated global settings in UI.")

    def emitAcquisitionRate(self):
        newAcquisitionRate =self.acquisitionRateLineEdit.text()
        self.acquisitionRateChanged.emit(newAcquisitionRate)

    def emitControlRate(self):
        newControlRate =self.controlRateLineEdit.text()
        self.controlRateChanged.emit(newControlRate)
    
    def emitAverageSamples(self):
        newAverageSamples =self.averageSamplesLineEdit.text()
        self.averageSamplesChanged.emit(newAverageSamples)

    def emitPath(self):
        loadPath = QFileDialog.getExistingDirectory(self, 'Select the directory in which to save data')
        self.setPathAddressLabel.setText(loadPath)
        self.pathChanged.emit(loadPath)

    def emitFilename(self):
        newFilename =self.setFilenameLineEdit.text()
        self.filenameChanged.emit(newFilename)

class PlotWindow(QWidget, QtStyleTools):
    plotWindowClosed = Signal(int)

    def __init__(self, plotNumber, darkMode, channelsData):
        super().__init__() 
        self.plotNumber = plotNumber
        self.darkMode = darkMode
        self.channelsData = channelsData
        self.width = 1200
        self.height = 800
        self.alpha = 50
        self.history = 100
        self.resize(self.width, self.height)
        self.commonChannel = 0
        

        self.colourPickerDialog = ColourPickerDialog(self)

        self.plot = pg.PlotWidget(self)
        styles = {'color':os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size':'16px'}
        self.plot.setLabel('left', 'Selected channels', **styles)
        self.plot.setLabel('bottom', 'Common channel', **styles)
        # self.plot.setMenuEnabled(enableMenu=False)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

        self.plotWindowLayout = QHBoxLayout()
        self.plotWindowLayout.addWidget(self.plot)   

        # Channels data model.
        self.channelsModel = ChannelsTableModel(self.channelsData)


        # self.createPens()
        self.createLines()

        self.selectedChannelsLabel = QLabel("Selected channels:")

        self.selectedChannelsTableView = ChannelsTableView()
        self.selectedChannelsTableView.setModel(self.channelsModel)
        self.selectedChannelsTableView.setColumnWidth(0,30)
        self.selectedChannelsTableView.setColumnWidth(1,25)
        self.selectedChannelsTableView.setColumnWidth(2,60)
        self.selectedChannelsTableView.setColumnWidth(3,55)
        self.selectedChannelsTableView.setColumnWidth(4,60)
        self.selectedChannelsTableView.setColumnWidth(5,30)

        self.commonChannelLabel = QLabel("Common channel:")
        self.commonChannelComboBox = QComboBox()
        
        self.commonChannelGroupBox = QGroupBox("Common Channel")
        self.commonChannelLayout = QVBoxLayout()
        self.commonChannelLayout.addWidget(self.commonChannelComboBox)
        self.commonChannelGroupBox.setLayout(self.commonChannelLayout)

        self.selectedChannelsTableGroupBox = QGroupBox("Selected Channels")
        self.selectedChannelsTableLayout = QVBoxLayout()
        self.selectedChannelsTableLayout.addWidget(self.selectedChannelsTableView)
        
        self.swapRadio = QCheckBox("Swap")
        self.autoRadio = QCheckBox("Auto")
        self.downsampleRadio = QCheckBox("Downsample")
        self.gridRadio = QCheckBox("Grid")
        self.alphaLabel = QLabel("Alpha:")
        self.alphaSlider = QSlider(Qt.Horizontal)
        self.alphaSlider.setValue(self.alpha)
        self.historyLabel = QLabel("History:")
        self.historySlider = QSlider(Qt.Horizontal)
        self.historySlider.setValue(self.history)

        self.autoXRadio = QCheckBox("Auto")
        self.manualXRadio = QCheckBox("Manual")
        self.setMinimumXLabel = QLabel("Minimum:")
        self.setMinimumXLineEdit = QLineEdit()
        self.setMaximumXLabel = QLabel("Maximum:")
        self.setMaximumXLineEdit = QLineEdit()

        self.invertXRadio = QCheckBox("Invert")
        self.logXRadio= QCheckBox("Log")
        self.autoPanXRadio = QCheckBox("Auto Pan")
        self.gridXRadio = QCheckBox("Grid")


        self.autoYRadio = QCheckBox("Auto")
        self.manualYRadio = QCheckBox("Manual")
        self.setMinimumYLabel = QLabel("Minimum:")
        self.setMinimumYLineEdit = QLineEdit()
        self.setMaximumYLabel = QLabel("Maximum:")
        self.setMaximumYLineEdit = QLineEdit()
        
        self.invertYRadio = QCheckBox("Invert")
        self.logYRadio= QCheckBox("Log")
        self.autoPanYRadio = QCheckBox("Auto Pan")
        self.gridYRadio = QCheckBox("Grid")

        self.controlsGroupBox = QGroupBox("Axis Controls")
        self.controlsGroupBox.setFixedHeight(250)
        self.controlsGroupBox.setFixedWidth(320)
        
        self.controlsLayout = QVBoxLayout()
        self.controlsLayout.addWidget(self.selectedChannelsTableGroupBox)
        self.controlsLayout.addWidget(self.commonChannelGroupBox)
        self.controlsLayout.addWidget(self.controlsGroupBox)

        self.globalControlsWidget = QWidget()
        self.globalControlsLayout = QGridLayout()
        self.globalControlsLayout.addWidget(self.autoRadio, 0, 0)
        self.globalControlsLayout.addWidget(self.gridRadio, 0, 1)
        self.globalControlsLayout.addWidget(self.swapRadio, 0, 2)
        self.globalControlsLayout.addWidget(self.alphaLabel, 1, 0)
        self.globalControlsLayout.addWidget(self.alphaSlider, 1, 1, 1, 2)
        self.globalControlsLayout.addWidget(self.historyLabel, 2, 0)
        self.globalControlsLayout.addWidget(self.historySlider, 2, 1, 1, 2)
        self.globalControlsWidget.setLayout(self.globalControlsLayout)

        self.xAxisControlsWidget = QWidget()
        self.xAxisControlsLayout = QGridLayout()
        self.xAxisControlsLayout.addWidget(self.autoXRadio, 0, 0)
        self.xAxisControlsLayout.addWidget(self.setMinimumXLabel, 0, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumXLabel, 0, 2)
        self.xAxisControlsLayout.addWidget(self.manualXRadio, 1, 0)
        self.xAxisControlsLayout.addWidget(self.setMinimumXLineEdit, 1, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumXLineEdit, 1, 2)
        self.xAxisControlsLayout.addWidget(self.invertXRadio,2 , 0)
        self.xAxisControlsLayout.addWidget(self.logXRadio, 2, 1)
        self.xAxisControlsLayout.addWidget(self.gridXRadio, 2, 2)
        self.xAxisControlsWidget.setLayout(self.xAxisControlsLayout)
        

        self.yAxisControlsWidget = QWidget()
        self.yAxisControlsLayout = QGridLayout()
        self.yAxisControlsLayout.addWidget(self.autoYRadio, 0, 0)
        self.yAxisControlsLayout.addWidget(self.setMinimumYLabel, 0, 1)
        self.yAxisControlsLayout.addWidget(self.setMaximumYLabel, 0, 2)
        self.yAxisControlsLayout.addWidget(self.manualYRadio, 1, 0)
        self.yAxisControlsLayout.addWidget(self.setMinimumYLineEdit, 1, 1)
        self.yAxisControlsLayout.addWidget(self.setMaximumYLineEdit, 1, 2)
        self.yAxisControlsLayout.addWidget(self.invertYRadio,2 , 0)
        self.yAxisControlsLayout.addWidget(self.logYRadio, 2, 1)
        self.yAxisControlsLayout.addWidget(self.gridYRadio, 2, 2)
        self.yAxisControlsWidget.setLayout(self.yAxisControlsLayout)

        self.controlsTabWidget = QTabWidget()
        self.controlsTabWidget.addTab(self.globalControlsWidget, "Global")
        self.controlsTabWidget.addTab(self.xAxisControlsWidget, "X")
        self.controlsTabWidget.addTab(self.yAxisControlsWidget, "Y")

        self.controlsTabsLayout = QVBoxLayout()
        self.controlsTabsLayout.addWidget(self.controlsTabWidget)
        self.controlsGroupBox.setLayout(self.controlsTabsLayout)

        self.selectedChannelsTableGroupBox.setLayout(self.selectedChannelsTableLayout) 
        self.selectedChannelsTableGroupBox.setFixedWidth(320)


        self.plotWindowLayout.addLayout(self.controlsLayout)
        self.setLayout(self.plotWindowLayout)

        self.setDarkMode() 
        self.fillCommonChannelComboBox()

        self.invertXRadio.stateChanged.connect(self.invertX)
        self.logXRadio.stateChanged.connect(self.logXAxis)
        self.invertYRadio.stateChanged.connect(self.invertY)
        self.logYRadio.stateChanged.connect(self.logYAxis)
        self.autoRadio.stateChanged.connect(self.autoRange)

        self.selectedChannelsTableView.clicked.connect(self.selectColour)
        self.colourPickerDialog.selectedColour.connect(self.setColour)

        self.commonChannelComboBox.currentIndexChanged.connect(self.setCommonChannel)
        # self.plot.getPlotItem().sigRangeChanged.connect()

    def fillCommonChannelComboBox(self):
        numChannels = len(self.channelsModel._data)
        for i in range(numChannels):
            channel = self.channelsModel._data[i]
            name = channel["name"]
            device = channel["device"]
            info = name + " " + device
            self.commonChannelComboBox.addItem(info)

    def createLines(self):
        self.lines = []
        numChannels = len(self.channelsModel._data)
        for i in range(numChannels):
            self.lines.append(self.plot.plot())

    def setCommonChannel(self, index):
        self.commonChannel = index

    @Slot(np.ndarray)
    def updateLines(self, plotData):
        styles = {'color':os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size':'16px'}
        numChannels = len(self.channelsModel._data)
        for i in range(numChannels):
            colour = self.channelsModel._data[i]["colour"]
            pen = pg.mkPen(colour)
            index = self.channelsModel.index(i,4)
            self.channelsModel.setData(index, "{:.2f}".format(plotData[-1,i]), role=Qt.EditRole)
            if self.channelsModel._data[i]["plot"] == False:
                self.lines[i].setData([],[])
            elif self.swapRadio.checkState() == False:
                self.lines[i].setData(plotData[:,self.commonChannel], plotData[:,i], pen=pen)
                self.plot.setLabel('left', 'Selected channels', **styles)
                self.plot.setLabel('bottom', 'Common channel', **styles)
            else:
                self.lines[i].setData(plotData[:,i], plotData[:,self.commonChannel], pen=pen)
                self.plot.setLabel('bottom', 'Selected channels', **styles)
                self.plot.setLabel('left', 'Common channel', **styles)
                

    # def manualRange(self):
    #     if self.manualRadio.checkState() == Qt.Checked:
    #         self.plot.disableAutoRange()
    #         self.autoRadio.setCheckState(Qt.Unchecked)

    def logXAxis(self):
        b = self.logXRadio.checkState()
        self.plot.setLogMode(x=b, y=None)

    def invertX(self):
        b = self.invertXRadio.checkState()
        self.plot.getPlotItem().invertX(b)

    def logYAxis(self):
        b = self.logYRadio.checkState()
        self.plot.setLogMode(x=None, y=b)

    def invertY(self):
        b = self.invertYRadio.checkState()
        self.plot.getPlotItem().invertY(b)

    def autoRange(self):
        if self.autoRadio.checkState() == Qt.Checked:
            self.plot.enableAutoRange()
            self.manualRadio.setCheckState(Qt.Unchecked)

    def setXRange(self):
        self.plot.getPlotItem().setXRange(1,4)

    def updateUI(self, newConfiguration):
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

    def setDarkMode(self):
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

        self.plot.setBackground(os.environ['QTMATERIAL_SECONDARYLIGHTCOLOR'])
        styles = {'color':os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size':'20px'}
        self.plot.setLabel('left', 'Selected channels', **styles)
        self.plot.setLabel('bottom', 'Common channel: Time (s)', **styles)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

    def selectColour(self, index):
        if index.column() == 1:
            model = index.model()
            item = model._data[index.row()]
            colour = item["colour"]
            self.colourPickerDialog.setTargetIndex(index)
            self.colourPickerDialog.show()

    def setColour(self, index, colour):
        self.channelsModel.setData(index, colour, Qt.EditRole)
            

    def closeEvent(self, event):
        self.plotWindowClosed.emit(self.plotNumber)