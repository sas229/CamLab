import copy
import math
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QSlider
from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QFont
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QEvent, QLocale
from src.local_qt_material import apply_stylesheet, QtStyleTools
from src.models import ChannelsTableModel, ColourPickerTableModel
from src.views import ChannelsTableView, ColourPickerTableView
from src.dialogs import ColourPickerDialog
import logging
import src.local_pyqtgraph.pyqtgraph as pg
import numpy as np

log = logging.getLogger(__name__)

class PlotWindow(QWidget, QtStyleTools):
    plotWindowClosed = Signal(str)
    colourUpdated = Signal(QModelIndex, str)

    def __init__(self):
        super().__init__()
        self.defaultChannelsData = [{"plot": False, "name": "Time", "device": "ALL", "colour": "#35e3e3", "value": "0.00", "unit": "s"}]
        self.initWidth = 1200
        self.initHeight = 800
        self.resize(self.initWidth, self.initHeight)
        self.setMinimumSize(850, 550)
        self.alpha = 50
        self.opacity = 50
        self.commonChannel = 0
        self.colourPickerDialog = ColourPickerDialog(self)
        self.minCommonAxisLock = 0
        self.maxCommonAxisLock = 0
        self.minSelectedAxisLock = 0
        self.maxSelectedAxisLock = 0
    
        self.plot = pg.PlotWidget(self)

        styles = self.setStyle()
        # self.plot.setLabel('left', 'Selected channels', **styles)
        # self.plot.setLabel('bottom', 'Common channel', **styles)
        self.plot.setMenuEnabled(enableMenu=False)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

        self.plotWindowLayout = QHBoxLayout()
        self.plotWindowLayout.addWidget(self.plot)   

        # Channels data model.
        self.selectedChannelsTableView = ChannelsTableView()
        self.setChannelsModel(self.defaultChannelsData)

        self.createLines()

        self.selectedChannelsLabel = QLabel("Selected channels:")
        self.selectedChannelsTableView.setModel(self.channelsModel)
        self.formatColumns()

        self.commonChannelLabel = QLabel("Common channel:")
        self.commonChannelComboBox = QComboBox()
        
        self.commonChannelGroupBox = QGroupBox("Common Channel")
        self.commonChannelLayout = QVBoxLayout()
        self.commonChannelLayout.addWidget(self.commonChannelComboBox)
        self.commonChannelGroupBox.setLayout(self.commonChannelLayout)

        self.selectedChannelsTableGroupBox = QGroupBox("Selected Channels")
        self.selectedChannelsTableLayout = QVBoxLayout()
        self.selectedChannelsTableLayout.addWidget(self.selectedChannelsTableView)
        
        self.swapCheckBox = QCheckBox("Swap")
        self.autoCheckBox = QCheckBox("Auto")
        self.downsampleCheckBox = QCheckBox("Downsample")
        self.gridCheckBox = QCheckBox("Grid")
        self.alphaLabel = QLabel("Alpha:")
        self.alphaSlider = QSlider(Qt.Horizontal)
        self.opacityLabel = QLabel("Opacity:")
        self.opacitySlider = QSlider(Qt.Horizontal)

        validator = QDoubleValidator(self, decimals=3)
        validator.setNotation(QDoubleValidator.StandardNotation)
        locale = QLocale("en")
        locale.setNumberOptions(QLocale.IncludeTrailingZeroesAfterDot)
        validator.setLocale(locale)

        self.autoCommonAxisCheckBox = QCheckBox("Auto")
        self.manualCommonAxisCheckBox = QCheckBox("Manual")
        self.setMinimumCommonAxisLabel = QLabel("Minimum:")
        self.minimumCommonAxisLineEdit = QLineEdit()
        self.minimumCommonAxisLineEdit.setEnabled(False)
        self.minimumCommonAxisLineEdit.setValidator(validator)
        self.minimumCommonAxisLineEdit.setFixedWidth(80)
        self.setMaximumCommonAxisLabel = QLabel("Maximum:")
        self.maximumCommonAxisLineEdit = QLineEdit()
        self.maximumCommonAxisLineEdit.setEnabled(False)
        self.maximumCommonAxisLineEdit.setValidator(validator)
        self.maximumCommonAxisLineEdit.setFixedWidth(80)

        self.lockCheckBox = QCheckBox("Lock")

        self.invertCommonAxisCheckBox = QCheckBox("Invert")

        self.logCommonAxisCheckBox= QCheckBox("Log")
        self.autoPanCommonAxisCheckBox = QCheckBox("Auto")
        self.lockCommonAxisCheckBox = QCheckBox("Lock")

        self.autoSelectedAxisCheckBox = QCheckBox("Auto")
        self.manualSelectedAxisCheckBox = QCheckBox("Manual")
        self.setMinimumSelectedAxisLabel = QLabel("Minimum:")
        self.minimumSelectedAxisLineEdit = QLineEdit()
        self.minimumSelectedAxisLineEdit.setEnabled(False)
        self.minimumSelectedAxisLineEdit.setValidator(validator)
        self.minimumSelectedAxisLineEdit.setFixedWidth(80)
        self.setMaximumSelectedAxisLabel = QLabel("Maximum:")
        self.maximumSelectedAxisLineEdit = QLineEdit()
        self.maximumSelectedAxisLineEdit.setEnabled(False)
        self.maximumSelectedAxisLineEdit.setValidator(validator)
        self.maximumSelectedAxisLineEdit.setFixedWidth(80)
        
        self.invertSelectedAxisCheckBox = QCheckBox("Invert")
        self.logSelectedAxisCheckBox= QCheckBox("Log")
        self.autoPanSelectedAxisCheckBox = QCheckBox("Auto")
        self.lockSelectedAxisCheckBox = QCheckBox("Lock")

        self.controlsGroupBox = QGroupBox("Axis Controls")
        self.controlsGroupBox.setFixedHeight(250)
        self.controlsGroupBox.setFixedWidth(400)
        
        self.controlsLayout = QVBoxLayout()
        self.controlsLayout.addWidget(self.selectedChannelsTableGroupBox)
        self.controlsLayout.addWidget(self.commonChannelGroupBox)
        self.controlsLayout.addWidget(self.controlsGroupBox)

        self.globalControlsWidget = QWidget()
        self.globalControlsLayout = QGridLayout()
        self.globalControlsLayout.addWidget(self.autoCheckBox, 0, 0)
        self.globalControlsLayout.addWidget(self.gridCheckBox, 0, 1)
        self.globalControlsLayout.addWidget(self.swapCheckBox, 0, 2)
        self.globalControlsLayout.addWidget(self.lockCheckBox, 0, 3)
        self.globalControlsLayout.addWidget(self.alphaLabel, 1, 0)
        self.globalControlsLayout.addWidget(self.alphaSlider, 1, 1, 1, 3)
        self.globalControlsLayout.addWidget(self.opacityLabel, 2, 0)
        self.globalControlsLayout.addWidget(self.opacitySlider, 2, 1, 1, 3)
        self.globalControlsWidget.setLayout(self.globalControlsLayout)

        self.xAxisControlsWidget = QWidget()
        self.xAxisControlsLayout = QGridLayout()
        self.xAxisControlsLayout.addWidget(self.autoCommonAxisCheckBox, 0, 0)
        self.xAxisControlsLayout.addWidget(self.setMinimumCommonAxisLabel, 0, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumCommonAxisLabel, 0, 2)
        self.xAxisControlsLayout.addWidget(self.manualCommonAxisCheckBox, 1, 0)
        self.xAxisControlsLayout.addWidget(self.minimumCommonAxisLineEdit, 1, 1)
        self.xAxisControlsLayout.addWidget(self.maximumCommonAxisLineEdit, 1, 2)
        self.xAxisControlsLayout.addWidget(self.lockCommonAxisCheckBox, 2, 0)
        self.xAxisControlsLayout.addWidget(self.invertCommonAxisCheckBox, 2, 1)
        self.xAxisControlsLayout.addWidget(self.logCommonAxisCheckBox, 2, 2)
        self.xAxisControlsWidget.setLayout(self.xAxisControlsLayout)

        self.yAxisControlsWidget = QWidget()
        self.yAxisControlsLayout = QGridLayout()
        self.yAxisControlsLayout.addWidget(self.autoSelectedAxisCheckBox, 0, 0)
        self.yAxisControlsLayout.addWidget(self.setMinimumSelectedAxisLabel, 0, 1)
        self.yAxisControlsLayout.addWidget(self.setMaximumSelectedAxisLabel, 0, 2)
        self.yAxisControlsLayout.addWidget(self.manualSelectedAxisCheckBox, 1, 0)
        self.yAxisControlsLayout.addWidget(self.minimumSelectedAxisLineEdit, 1, 1)
        self.yAxisControlsLayout.addWidget(self.maximumSelectedAxisLineEdit, 1, 2)
        self.yAxisControlsLayout.addWidget(self.lockSelectedAxisCheckBox, 2, 0)
        self.yAxisControlsLayout.addWidget(self.invertSelectedAxisCheckBox,2 , 1)
        self.yAxisControlsLayout.addWidget(self.logSelectedAxisCheckBox, 2, 2)
        self.yAxisControlsWidget.setLayout(self.yAxisControlsLayout)

        self.controlsTabWidget = QTabWidget()
        self.controlsTabWidget.addTab(self.globalControlsWidget, "   Global   ")
        self.controlsTabWidget.addTab(self.xAxisControlsWidget, "Common")
        self.controlsTabWidget.addTab(self.yAxisControlsWidget, "Selected")
        # self.controlsTabWidget.setFixedWidth(285)

        self.controlsTabsLayout = QVBoxLayout()
        self.controlsTabsLayout.addWidget(self.controlsTabWidget)
        self.controlsGroupBox.setLayout(self.controlsTabsLayout)

        self.selectedChannelsTableGroupBox.setLayout(self.selectedChannelsTableLayout) 
        self.selectedChannelsTableGroupBox.setFixedWidth(400)


        self.plotWindowLayout.addLayout(self.controlsLayout)
        self.setLayout(self.plotWindowLayout)

        self.fillCommonChannelComboBox()

        rangeCommonAxis = self.plot.getViewBox().state
        self.minimumCommonAxisLineEdit.setText(str('%.2f' % rangeCommonAxis['viewRange'][0][0]))
        self.maximumCommonAxisLineEdit.setText(str('%.2f' % rangeCommonAxis['viewRange'][0][1]))
        rangeSelectedAxis = self.plot.getViewBox().state
        self.minimumSelectedAxisLineEdit.setText(str('%.2f' % rangeSelectedAxis['viewRange'][1][0]))
        self.maximumSelectedAxisLineEdit.setText(str('%.2f' % rangeSelectedAxis['viewRange'][1][1]))

        self.invertCommonAxisCheckBox.clicked.connect(self.setInvertCommonAxis)
        self.logCommonAxisCheckBox.clicked.connect(self.setLogCommonAxis)
        self.invertSelectedAxisCheckBox.clicked.connect(self.setInvertSelectedAxis)
        self.logSelectedAxisCheckBox.clicked.connect(self.setLogSelectedAxis)
        
        self.gridCheckBox.clicked.connect(self.setGrid)
        self.alphaSlider.sliderReleased.connect(self.setAlpha)
        self.opacitySlider.sliderReleased.connect(self.setOpacity)
        self.plot.scene().sigMousePanned.connect(self.switchOffAuto)
        self.plot.scene().sigMouseWheel.connect(self.switchOffAuto)
        
        self.plot.sigXRangeChanged.connect(self.updateCommonAxisRange)
        self.plot.sigYRangeChanged.connect(self.updateSelectedAxisRange)
        
        self.selectedChannelsTableView.clicked.connect(self.selectColour)
        self.colourPickerDialog.selectedColour.connect(self.setColour)
        self.colourPickerDialog.selectedColour.connect(self.emitColour)
        self.commonChannelComboBox.currentIndexChanged.connect(self.setCommonChannel)

        # All Signals for axis mode controls must be clicked.
        self.autoCheckBox.clicked.connect(self.setAutoMode)
        self.autoCommonAxisCheckBox.clicked.connect(self.setAutoCommonAxisMode)
        self.autoSelectedAxisCheckBox.clicked.connect(self.setAutoSelectedAxisMode)
        self.manualCommonAxisCheckBox.clicked.connect(self.setManualCommonAxisMode)
        self.manualSelectedAxisCheckBox.clicked.connect(self.setManualSelectedAxisMode)

        # Global lock control Signal must be clicked. Common and Selected Signals can 
        self.lockCheckBox.clicked.connect(self.setLock)
        self.lockCommonAxisCheckBox.clicked.connect(self.setLockCommonAxis)
        self.lockSelectedAxisCheckBox.clicked.connect(self.setLockSelectedAxis)

        self.swapCheckBox.clicked.connect(self.setSwap)

        self.minimumCommonAxisLineEdit.returnPressed.connect(self.setNewCommonAxisRange)
        self.maximumCommonAxisLineEdit.returnPressed.connect(self.setNewCommonAxisRange)
        self.minimumSelectedAxisLineEdit.returnPressed.connect(self.setNewSelectedAxisRange)
        self.maximumSelectedAxisLineEdit.returnPressed.connect(self.setNewSelectedAxisRange)

    def resizeEvent(self, event):
        # Save updated size in configuration.
        self.configuration["plots"][self.plotNumber]["width"] = int(self.width())
        self.configuration["plots"][self.plotNumber]["height"] = int(self.height())

    def moveEvent(self, event):
        # Save updated position in configuration.
        position = self.geometry()
        self.configuration["plots"][self.plotNumber]["x"] = int(position.x())
        self.configuration["plots"][self.plotNumber]["y"] = int(position.y())

    def setConfiguration(self, configuration):
        # Set the configuration.
        self.configuration = configuration
        if "plots" in self.configuration:
            x = int(self.configuration["plots"][self.plotNumber]["x"])
            y = int(self.configuration["plots"][self.plotNumber]["y"])
            w = int(self.configuration["plots"][self.plotNumber]["width"])
            h = int(self.configuration["plots"][self.plotNumber]["height"])
            self.setGeometry(x, y, w, h)
            self.alphaSlider.setValue(int(self.configuration["plots"][self.plotNumber]["alpha"]))
            self.autoCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["auto"]))
            self.autoCommonAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["autoCommonAxis"]))
            self.autoSelectedAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["autoSelectedAxis"]))
            self.invertCommonAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["invertCommonAxis"]))
            self.invertSelectedAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["invertSelectedAxis"]))
            self.lockCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["lock"]))
            self.lockCommonAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["lockCommonAxis"]))
            self.lockSelectedAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["lockSelectedAxis"]))
            self.logCommonAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["logCommonAxis"]))
            self.logSelectedAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["logSelectedAxis"]))
            self.manualCommonAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["manualCommonAxis"]))
            self.manualSelectedAxisCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["manualSelectedAxis"]))
            self.minCommonAxis = self.configuration["plots"][self.plotNumber]["minCommonAxisRange"]
            self.maxCommonAxis = self.configuration["plots"][self.plotNumber]["maxCommonAxisRange"]
            self.minSelectedAxis = self.configuration["plots"][self.plotNumber]["minSelectedAxisRange"]
            self.maxSelectedAxis = self.configuration["plots"][self.plotNumber]["maxSelectedAxisRange"]
            self.minCommonAxisLock = self.configuration["plots"][self.plotNumber]["minCommonAxisRangeLock"]
            self.maxCommonAxisLock = self.configuration["plots"][self.plotNumber]["maxCommonAxisRangeLock"]
            self.minSelectedAxisLock = self.configuration["plots"][self.plotNumber]["minSelectedAxisRangeLock"]
            self.maxSelectedAxisLock = self.configuration["plots"][self.plotNumber]["maxSelectedAxisRangeLock"]
            if bool(self.lockCommonAxisCheckBox.checkState()) == False and bool(self.lockSelectedAxisCheckBox.checkState()) == False:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxCommonAxisRange"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxSelectedAxisRange"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minCommonAxisRange"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minSelectedAxisRange"]))
            elif bool(self.lockCommonAxisCheckBox.checkState()) == True and bool(self.lockSelectedAxisCheckBox.checkState()) == False:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxCommonAxisRangeLock"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxSelectedAxisRangeLock"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minCommonAxisRange"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minSelectedAxisRange"]))
            elif bool(self.lockCommonAxisCheckBox.checkState()) == False and bool(self.lockSelectedAxisCheckBox.checkState()) == True:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxCommonAxisRange"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["maxSelectedAxisRange"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minCommonAxisRangeLock"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["plots"][self.plotNumber]["minSelectedAxisRangeLock"]))
            self.opacitySlider.setValue(int(self.configuration["plots"][self.plotNumber]["opacity"]))
            self.gridCheckBox.setChecked(int(self.configuration["plots"][self.plotNumber]["setGrid"]))
            self.swapCheckBox.setChecked(bool(self.configuration["plots"][self.plotNumber]["swap"]))
            self.setChannelsModel(self.configuration["plots"][self.plotNumber]["channels"])
            self.numChannels = len(self.channelsModel._data)
            self.plotData = np.zeros((1, self.numChannels))        
            self.setLock()
            self.setAutoMode()
            self.setManualCommonAxisMode()
            self.setManualSelectedAxisMode()
            self.setNewCommonAxisRange()
            self.setNewSelectedAxisRange()
            self.setGrid()
            self.setLogCommonAxis()
            self.setLogSelectedAxis()
            self.setInvertCommonAxis()
            self.setInvertSelectedAxis()
            self.fillCommonChannelComboBox()
            self.setSwap()
            self.setAxesLabels()
            self.updatePlot()
            self.darkMode = self.configuration["global"]["darkMode"]
            self.setDarkMode()
            # log.info("Configuration set.")

    def updateConfiguration(self):
        # Update the configuration based on current GUI settings.
        self.configuration["plots"][self.plotNumber]["alpha"] = int(self.alphaSlider.value())
        self.configuration["plots"][self.plotNumber]["auto"] = bool(self.autoCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["autoCommonAxis"] = bool(self.autoCommonAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["autoSelectedAxis"] = bool(self.autoSelectedAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["invertCommonAxis"] = bool(self.invertCommonAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["invertSelectedAxis"] = bool(self.invertSelectedAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["lock"] = bool(self.lockCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["lockCommonAxis"] = bool(self.lockCommonAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["lockSelectedAxis"] = bool(self.lockSelectedAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["logCommonAxis"] = bool(self.logCommonAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["logSelectedAxis"] = bool(self.logSelectedAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["manualCommonAxis"] = bool(self.manualCommonAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["manualSelectedAxis"] = bool(self.manualSelectedAxisCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["maxCommonAxisRange"] = float(self.maximumCommonAxisLineEdit.text())
        self.configuration["plots"][self.plotNumber]["maxSelectedAxisRange"] = float(self.maximumSelectedAxisLineEdit.text())
        self.configuration["plots"][self.plotNumber]["minCommonAxisRange"] = float(self.minimumCommonAxisLineEdit.text())
        self.configuration["plots"][self.plotNumber]["minSelectedAxisRange"] = float(self.minimumSelectedAxisLineEdit.text())
        self.configuration["plots"][self.plotNumber]["maxCommonAxisRangeLock"] = float(self.maxCommonAxisLock)
        self.configuration["plots"][self.plotNumber]["maxSelectedAxisRangeLock"] = float(self.maxSelectedAxisLock)
        self.configuration["plots"][self.plotNumber]["minCommonAxisRangeLock"] = float(self.minCommonAxisLock)
        self.configuration["plots"][self.plotNumber]["minSelectedAxisRangeLock"] = float(self.minSelectedAxisLock)
        self.configuration["plots"][self.plotNumber]["opacity"] = int(self.opacitySlider.value())
        self.configuration["plots"][self.plotNumber]["setGrid"] = bool(self.gridCheckBox.checkState())
        self.configuration["plots"][self.plotNumber]["swap"] = bool(self.swapCheckBox.checkState())
        # log.info("Configuration updated.")

    @Slot()
    def setSwap(self):
        self.updateConfiguration()
        self.updatePlot()

    def setAxesLabels(self):
        swap = bool(self.swapCheckBox.checkState())
        styles = self.setStyle()
        if swap == True:
            self.plot.setLabel('bottom', 'Selected channels', **styles)
            self.plot.setLabel('left', 'Common channel', **styles)
        elif swap == False:
            self.plot.setLabel('left', 'Selected channels', **styles)
            self.plot.setLabel('bottom', 'Common channel', **styles)

    @Slot()
    def setLock(self):
        # Set lock boolean in GUI and configuration.
        lock = bool(self.lockCheckBox.checkState())
        if lock == True:
            self.lockCommonAxisCheckBox.setChecked(True)
            self.lockSelectedAxisCheckBox.setChecked(True)
        else:
            self.lockCommonAxisCheckBox.setChecked(False)
            self.lockSelectedAxisCheckBox.setChecked(False)
        self.setLockCommonAxis()
        self.setLockSelectedAxis()
        self.updateConfiguration()

    @Slot()
    def setLockCommonAxis(self):
        # Set common axis lock boolean in GUI and configuration.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        if lockCommonAxis == True:
            self.minCommonAxisLock = float(self.minimumCommonAxisLineEdit.text())
            self.maxCommonAxisLock = float(self.maximumCommonAxisLineEdit.text())
            self.minimumCommonAxisLineEdit.setEnabled(False)
            self.maximumCommonAxisLineEdit.setEnabled(False)
            if lockSelectedAxis == True:
                self.lockCheckBox.setChecked(True)
        else:
            self.lockCheckBox.setChecked(False)
            if manualCommonAxis == True:
                self.minimumCommonAxisLineEdit.setEnabled(True)
                self.maximumCommonAxisLineEdit.setEnabled(True)   
        self.updateCommonAxisRange()
        self.updateConfiguration()

    @Slot()
    def setLockSelectedAxis(self):
        # Set selected axis lock boolean in GUI and configuration.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        if lockSelectedAxis == True:
            self.minSelectedAxisLock = float(self.minimumSelectedAxisLineEdit.text())
            self.maxSelectedAxisLock = float(self.maximumSelectedAxisLineEdit.text())
            self.minimumSelectedAxisLineEdit.setEnabled(False)
            self.maximumSelectedAxisLineEdit.setEnabled(False)
            if lockCommonAxis == True:
                self.lockCheckBox.setChecked(True)
        else:
            self.lockCheckBox.setChecked(False)
            if manualSelectedAxis == True:
                self.minimumSelectedAxisLineEdit.setEnabled(True)
                self.maximumSelectedAxisLineEdit.setEnabled(True)
        self.updateSelectedAxisRange()
        self.updateConfiguration()

    @Slot()
    def setAutoMode(self):
        # When auto is True, enable the autoRange function on both axes, set 
        # autoCommonAxisCheckBox and autoSelectedAxisCheckBox to True and 
        # manualCommonAxisCheckBox and manualSelectedAxisCheckBox to False. 
        auto = bool(self.autoCheckBox.checkState())
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        if auto == True:
            self.plot.enableAutoRange()
            self.autoCommonAxisCheckBox.setChecked(True)
            self.autoSelectedAxisCheckBox.setChecked(True)
            self.manualCommonAxisCheckBox.setChecked(False)
            self.manualSelectedAxisCheckBox.setChecked(False)
            self.minimumCommonAxisLineEdit.setEnabled(False)
            self.maximumCommonAxisLineEdit.setEnabled(False)
            self.minimumSelectedAxisLineEdit.setEnabled(False)
            self.maximumSelectedAxisLineEdit.setEnabled(False)
        # Otherwise disable the autoRange function, set autoCommonAxisCheckBox 
        # and autoSelectedAxisCheckBox to False and manualCommonAxisCheckBox and 
        # manualSelectedAxisCheckBox to False.
        elif auto == False:
            self.plot.disableAutoRange()
            self.autoCommonAxisCheckBox.setChecked(False)
            self.autoSelectedAxisCheckBox.setChecked(False)
            if lockCommonAxis == False:
                self.minimumCommonAxisLineEdit.setEnabled(True)
                self.maximumCommonAxisLineEdit.setEnabled(True)
            if lockSelectedAxis == False:
                self.minimumSelectedAxisLineEdit.setEnabled(True)
                self.maximumSelectedAxisLineEdit.setEnabled(True)
            self.setNewCommonAxisRange()
            self.setNewSelectedAxisRange()
        self.updateConfiguration()

    @Slot()
    def setAutoCommonAxisMode(self):
        # Check the boolean and if True set auto mode on common axis, 
        # otherwise if False set manual mode on common axis.
        autoCommonAxis = bool(self.autoCommonAxisCheckBox.checkState())
        autoSelectedAxis = bool(self.autoSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        if autoCommonAxis == True:
            self.manualCommonAxisCheckBox.setChecked(False)
            if swap == True:
                self.plot.enableAutoRange(axis='y')
            elif swap == False:
                self.plot.enableAutoRange(axis='x')
            self.minimumCommonAxisLineEdit.setEnabled(False)
            self.maximumCommonAxisLineEdit.setEnabled(False)
            if autoSelectedAxis == True:
                self.autoCheckBox.setChecked(True)
        else:
            if swap == True:
                self.plot.disableAutoRange(axis='y')
            elif swap == False:
                self.plot.disableAutoRange(axis='x')
        self.updateConfiguration()

    @Slot()
    def setAutoSelectedAxisMode(self):
        # Check the boolean and if True set auto mode on selected axis, 
        # otherwise if False set manual mode on common axis.
        autoCommonAxis = bool(self.autoCommonAxisCheckBox.checkState())
        autoSelectedAxis = bool(self.autoSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        if autoSelectedAxis == True:
            self.manualSelectedAxisCheckBox.setChecked(False)
            if swap == True:
                self.plot.enableAutoRange(axis='x')
            elif swap == False:
                self.plot.enableAutoRange(axis='y')
            self.minimumSelectedAxisLineEdit.setEnabled(False)
            self.maximumSelectedAxisLineEdit.setEnabled(False)
            if autoCommonAxis == True:
                self.autoCheckBox.setChecked(True)
        else:
            if swap == True:
                self.plot.disableAutoRange(axis='x')
            elif swap == False:
                self.plot.disableAutoRange(axis='y')
        self.updateConfiguration()

    @Slot()
    def setManualCommonAxisMode(self):
        # Check the boolean and if True set manual mode on common axis, 
        # otherwise if False set auto mode on common axis.
        manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        if manualCommonAxis == True:
            if swap == True:        
                self.plot.disableAutoRange(axis='y')
            elif swap == False:
                self.plot.disableAutoRange(axis='x')
            self.autoCheckBox.setChecked(False)
            self.autoCommonAxisCheckBox.setChecked(False)
            if lockCommonAxis == False:
                self.minimumCommonAxisLineEdit.setEnabled(True)
                self.maximumCommonAxisLineEdit.setEnabled(True)
        else:
            self.minimumCommonAxisLineEdit.setEnabled(False)
            self.maximumCommonAxisLineEdit.setEnabled(False)
        self.setNewCommonAxisRange()
        self.updateConfiguration()
            
    @Slot()
    def setManualSelectedAxisMode(self):
        # Check the boolean and if True set auto mode on selected axis, 
        # otherwise if False set auto mode on commoself.minCommonAxisLockn axis.
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        if manualSelectedAxis == True:
            if swap == True:
                self.plot.disableAutoRange(axis='x')
            elif swap == False:
                self.plot.disableAutoRange(axis='y')
            self.autoCheckBox.setChecked(False)
            self.autoSelectedAxisCheckBox.setChecked(False)
            if lockSelectedAxis == False:
                self.minimumSelectedAxisLineEdit.setEnabled(True)
                self.maximumSelectedAxisLineEdit.setEnabled(True)
        else:
            self.minimumSelectedAxisLineEdit.setEnabled(False)
            self.maximumSelectedAxisLineEdit.setEnabled(False)
        self.setNewSelectedAxisRange()
        self.updateConfiguration()
    
    @Slot()
    def updateCommonAxisRange(self):
        # Store current minCommon and maxCommon values.
        rangeCommonAxis = self.plot.getViewBox().state
        swap = bool(self.swapCheckBox.checkState())
        if swap == True:
            self.minCommonAxis = float('%.2f' % rangeCommonAxis['viewRange'][1][0])
            self.maxCommonAxis = float('%.2f' % rangeCommonAxis['viewRange'][1][1])
        elif swap == False:
            self.minCommonAxis = float('%.2f' % rangeCommonAxis['viewRange'][0][0])
            self.maxCommonAxis = float('%.2f' % rangeCommonAxis['viewRange'][0][1])

        # If lock is False update the lineedit text.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        if lockCommonAxis == True:
            self.minimumCommonAxisLineEdit.setText(str(self.minCommonAxisLock))
            self.maximumCommonAxisLineEdit.setText(str(self.maxCommonAxisLock))
        elif lockCommonAxis == False:
            self.minimumCommonAxisLineEdit.setText(str(self.minCommonAxis))
            self.maximumCommonAxisLineEdit.setText(str(self.maxCommonAxis))
        self.updateConfiguration()
        
    @Slot()
    def updateSelectedAxisRange(self):
        # Store current minSelected and maxSelected values.
        rangeSelectedAxis = self.plot.getViewBox().state
        swap = bool(self.swapCheckBox.checkState())
        if swap == True:
            self.minSelectedAxis = float('%.2f' % rangeSelectedAxis['viewRange'][0][0])
            self.maxSelectedAxis = float('%.2f' % rangeSelectedAxis['viewRange'][0][1])
        elif swap == False:
            self.minSelectedAxis = float('%.2f' % rangeSelectedAxis['viewRange'][1][0])
            self.maxSelectedAxis = float('%.2f' % rangeSelectedAxis['viewRange'][1][1])

        # If lock is False update the lineedit text.
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        if lockSelectedAxis == True:
            self.minimumSelectedAxisLineEdit.setText(str(self.minSelectedAxisLock))
            self.maximumSelectedAxisLineEdit.setText(str(self.maxSelectedAxisLock))
        elif lockSelectedAxis == False:
            self.minimumSelectedAxisLineEdit.setText(str(self.minSelectedAxis))
            self.maximumSelectedAxisLineEdit.setText(str(self.maxSelectedAxis))
        self.updateConfiguration()
    
    @Slot()
    def setNewCommonAxisRange(self):
        # Set the new range for the common axis.
        swap = bool(self.swapCheckBox.checkState())
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        self.minCommonAxis = float(self.minimumCommonAxisLineEdit.text())
        self.maxCommonAxis = float(self.maximumCommonAxisLineEdit.text())
        if swap == True and lockCommonAxis == True:
            self.plot.setYRange(self.minCommonAxisLock, self.maxCommonAxisLock, padding=0)
        elif swap == True and lockCommonAxis == False:
            self.plot.setYRange(self.minCommonAxis, self.maxCommonAxis, padding=0)
        elif swap == False and lockCommonAxis == True:
            self.plot.setXRange(self.minCommonAxisLock, self.maxCommonAxisLock, padding=0)
        elif swap == False and lockCommonAxis == False:
            self.plot.setXRange(self.minCommonAxis, self.maxCommonAxis, padding=0)
        
    @Slot()
    def setNewSelectedAxisRange(self):
        # Set the new range for the selected axis.
        swap = bool(self.swapCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        self.minSelectedAxis = float(self.minimumSelectedAxisLineEdit.text())
        self.maxSelectedAxis = float(self.maximumSelectedAxisLineEdit.text())
        if swap == True and lockSelectedAxis == True:
            self.plot.setXRange(self.minSelectedAxisLock, self.maxSelectedAxisLock, padding=0)
        elif swap == True and lockSelectedAxis == False:
            self.plot.setXRange(self.minSelectedAxis, self.maxSelectedAxis, padding=0)
        elif swap == False and lockSelectedAxis == True:
            self.plot.setYRange(self.minSelectedAxisLock, self.maxSelectedAxisLock, padding=0)
        elif swap == False and lockSelectedAxis == False:
            self.plot.setYRange(self.minSelectedAxis, self.maxSelectedAxis, padding=0)

    @Slot()
    def switchOffAuto(self):
        # Switch off auto mode on scroll wheel event.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        self.autoCheckBox.setChecked(False)
        self.autoCommonAxisCheckBox.setChecked(False)
        self.autoSelectedAxisCheckBox.setChecked(False)
        self.manualCommonAxisCheckBox.setChecked(False)
        self.manualSelectedAxisCheckBox.setChecked(False)
        self.minimumCommonAxisLineEdit.setEnabled(False)
        self.maximumCommonAxisLineEdit.setEnabled(False)
        self.minimumSelectedAxisLineEdit.setEnabled(False)
        self.maximumSelectedAxisLineEdit.setEnabled(False)
        self.updateConfiguration()

    def formatColumns(self):
        # Format channels table columns.
        self.selectedChannelsTableView.setColumnWidth(0, 30)
        self.selectedChannelsTableView.setColumnWidth(1, 30)
        self.selectedChannelsTableView.setColumnWidth(2, 95)
        self.selectedChannelsTableView.setColumnWidth(3, 75)
        self.selectedChannelsTableView.setColumnWidth(4, 55)
        self.selectedChannelsTableView.setColumnWidth(5, 40)

    def setPlotNumber(self, plotNumber):
        # Set the plot number.
        self.plotNumber = plotNumber

    def fillCommonChannelComboBox(self):
        # Fill the common channel combobox.
        self.numChannels = len(self.channelsModel._data)
        self.commonChannelComboBox.clear()
        for i in range(self.numChannels):
            channel = self.channelsModel._data[i]
            name = channel["name"]
            device = channel["device"]
            info = name + " " + device
            self.commonChannelComboBox.addItem(info)

    def createLines(self):
        # Create lines.
        self.lines = []
        self.numChannels = len(self.channelsModel._data)
        for i in range(self.numChannels):
            self.lines.append(self.plot.plot())

    @Slot(np.ndarray)
    def updatePlotData(self, plotData):
        # Update plotData and save as attribute.
        self.plotData = plotData
        self.updatePlot()

    def setCommonChannel(self, index):
        # Set common channel.
        self.commonChannel = index

    @Slot(np.ndarray)
    def updatePlot(self):
        # Update plot.
        alphaValue = int(self.alphaSlider.value())
        manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        lockCommon = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelected = bool(self.lockSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        logCommonAxis = bool(self.logCommonAxisCheckBox.checkState())
        logSelectedAxis = bool(self.logSelectedAxisCheckBox.checkState())
        
        # Do this if statement for the first time the plot is run.
        if bool(self.autoCheckBox.checkState()) == True:
            self.setAutoMode()
        self.plot.clear()
        self.createLines()
        styles = self.setStyle()
        for i in range(self.numChannels):
            colour = self.channelsModel._data[i]["colour"]
            pen = pg.mkPen(colour, width=1)
            index = self.channelsModel.index(i,4)
            self.channelsModel.setData(index, "{:.2f}".format(self.plotData[-1,i]), role=Qt.EditRole)
            if self.channelsModel._data[i]["plot"] == False:
                self.lines[i].setData([],[])
            elif swap == False:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(self.plotData[:,self.commonChannel], self.plotData[:,i], pen=pen)
                if logCommonAxis == True:
                    self.plot.setLogMode(x=True)
                elif logCommonAxis == False:
                    self.plot.setLogMode(x=False)
                if logSelectedAxis == True:
                    self.plot.setLogMode(y=True)
                elif logSelectedAxis == False:
                    self.plot.setLogMode(y=False)
            elif swap == True:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(self.plotData[:,i], self.plotData[:,self.commonChannel], pen=pen)
                if logCommonAxis == True:
                    self.plot.setLogMode(y=True)
                elif logCommonAxis == False:
                    self.plot.setLogMode(y=False)
                if logSelectedAxis == True:
                    self.plot.setLogMode(x=True)
                elif logSelectedAxis == False:
                    self.plot.setLogMode(x=False)

            if manualCommonAxis == True and lockCommon == True:
                self.setNewCommonAxisRange()
                self.setNewSelectedAxisRange()
            if manualSelectedAxis == True and lockSelected == True:
                self.setNewCommonAxisRange()
                self.setNewSelectedAxisRange()

            self.setAxesLabels()
                
    def setStyle(self):
        return {'color': os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size': '16px'}

    def setLogCommonAxis(self):
        # Set log scale on common axis.
        swap = bool(self.swapCheckBox.checkState())
        logCommonAxis = bool(self.logCommonAxisCheckBox.checkState())
        if swap == True:
            self.plot.setLogMode(x=None, y=logCommonAxis)
        else:
            self.plot.setLogMode(x=logCommonAxis, y=None)
        self.updateConfiguration()

    def setLogSelectedAxis(self):
        # Set log scale on selected axis.
        swap = bool(self.swapCheckBox.checkState())
        logSelectedAxis = bool(self.logSelectedAxisCheckBox.checkState())
        if swap == True:
            self.plot.setLogMode(x=logSelectedAxis, y=None)
        else:
            self.plot.setLogMode(x=None, y=logSelectedAxis)
        self.updateConfiguration()

    def setInvertCommonAxis(self):
        # Set invert on common axis.
        swap = bool(self.swapCheckBox.checkState())
        invertCommonAxis = bool(self.invertCommonAxisCheckBox.checkState())
        if swap == True:
            self.plot.getPlotItem().invertY(invertCommonAxis)
        else:
            self.plot.getPlotItem().invertX(invertCommonAxis)
        self.updateConfiguration()


    def setInvertSelectedAxis(self):
        # Set invert on selected axis.
        swap = bool(self.swapCheckBox.checkState())
        invertSelectedAxis = bool(self.invertSelectedAxisCheckBox.checkState())
        if swap == True:
            self.plot.getPlotItem().invertX(invertSelectedAxis)
        else:
            self.plot.getPlotItem().invertY(invertSelectedAxis)
        self.updateConfiguration()

    def setGrid(self):
        # Set grid.
        grid = self.gridCheckBox.checkState()
        self.plot.showGrid(x = grid, y = grid, alpha = self.opacity/100)
        self.updateConfiguration()

    def updateUI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()
        log.info("Updated plot window settings in UI.")        

    def setDarkMode(self):
        # Set dark mode.
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

        self.plot.setBackground(os.environ['QTMATERIAL_SECONDARYLIGHTCOLOR'])
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

    def emitColour(self, index, colour):
        self.colourUpdated.emit(index, colour)

    def closeEvent(self, event):
        self.plotWindowClosed.emit(self.plotNumber)

    def setChannelsModel(self, channelsData):
        self.channelsModel = ChannelsTableModel(channelsData)
        self.selectedChannelsTableView.setModel(self.channelsModel)

    def setAlpha(self):
        self.alpha = int(self.alphaSlider.value())
        self.updateConfiguration()
        self.updatePlot()

    def setOpacity(self):
        self.opacity = int(self.opacitySlider.value())
        if bool(self.gridCheckBox.checkState()) == True:
            self.setGrid()
        self.updateConfiguration()

