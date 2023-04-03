import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QSlider
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QLocale
from local_qt_material import QtStyleTools
from models import ChannelsTableModel
from views import ChannelsTableView
from dialogs import ColourPickerDialog
import logging
import local_pyqtgraph.pyqtgraph as pg
import numpy as np
from pathlib import Path

log = logging.getLogger(__name__)

class PlotWidget(QWidget, QtStyleTools):
    plotWidgetClosed = Signal(QWidget)
    colourUpdated = Signal(QModelIndex, str)

    def __init__(self):
        super().__init__()
        log.info("Plot instantiated.")
        self.setWhatsThis("plot")
        self.defaultChannelsData = [{"plot": False, "name": "Time", "device": "ALL", "colour": "#35e3e3", "value": "0.00", "unit": "s"}]
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

        self.setStyle()
        self.plot.setMenuEnabled(enableMenu=False)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

        self.plotWidgetLayout = QHBoxLayout()
        self.plotWidgetLayout.addWidget(self.plot)   

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


        self.plotWidgetLayout.addLayout(self.controlsLayout)
        self.setLayout(self.plotWidgetLayout)

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

    # def set_window(self):
    #     x = int(self.configuration["shearbox"]["plot"]["x"])
    #     y = int(self.configuration["shearbox"]["plot"]["y"])
    #     w = int(self.configuration["shearbox"]["plot"]["width"])
    #     h = int(self.configuration["shearbox"]["plot"]["height"])
    #     self.setGeometry(x, y, w, h)
        # self.configuration["shearbox"]["plot"]["mode"] = "window"

    # def set_tab(self):
        # self.configuration["shearbox"]["plot"]["mode"] = "tab"
        
    def resizeEvent(self, event):
        # Save updated size in configuration.
        self.configuration["shearbox"]["plot"]["width"] = int(self.width())
        self.configuration["shearbox"]["plot"]["height"] = int(self.height())

    def moveEvent(self, event):
        # Save updated position in configuration.
        position = self.geometry()
        self.configuration["shearbox"]["plot"]["x"] = int(position.x())
        self.configuration["shearbox"]["plot"]["y"] = int(position.y())

    def set_configuration(self):
        # Set the configuration.
        if "plot" in self.configuration["shearbox"]:
            self.alphaSlider.setValue(int(self.configuration["shearbox"]["plot"]["alpha"]))
            self.autoCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["auto"]))
            self.autoCommonAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["autoCommonAxis"]))
            self.autoSelectedAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["autoSelectedAxis"]))
            self.invertCommonAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["invertCommonAxis"]))
            self.invertSelectedAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["invertSelectedAxis"]))
            self.lockCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["lock"]))
            self.lockCommonAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["lockCommonAxis"]))
            self.lockSelectedAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["lockSelectedAxis"]))
            self.logCommonAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["logCommonAxis"]))
            self.logSelectedAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["logSelectedAxis"]))
            self.manualCommonAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["manualCommonAxis"]))
            self.manualSelectedAxisCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["manualSelectedAxis"]))
            self.minCommonAxis = self.configuration["shearbox"]["plot"]["minCommonAxisRange"]
            self.maxCommonAxis = self.configuration["shearbox"]["plot"]["maxCommonAxisRange"]
            self.minSelectedAxis = self.configuration["shearbox"]["plot"]["minSelectedAxisRange"]
            self.maxSelectedAxis = self.configuration["shearbox"]["plot"]["maxSelectedAxisRange"]
            self.minCommonAxisLock = self.configuration["shearbox"]["plot"]["minCommonAxisRangeLock"]
            self.maxCommonAxisLock = self.configuration["shearbox"]["plot"]["maxCommonAxisRangeLock"]
            self.minSelectedAxisLock = self.configuration["shearbox"]["plot"]["minSelectedAxisRangeLock"]
            self.maxSelectedAxisLock = self.configuration["shearbox"]["plot"]["maxSelectedAxisRangeLock"]
            if bool(self.lockCommonAxisCheckBox.checkState()) == False and bool(self.lockSelectedAxisCheckBox.checkState()) == False:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxCommonAxisRange"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxSelectedAxisRange"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minCommonAxisRange"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minSelectedAxisRange"]))
            elif bool(self.lockCommonAxisCheckBox.checkState()) == True and bool(self.lockSelectedAxisCheckBox.checkState()) == False:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxCommonAxisRangeLock"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxSelectedAxisRangeLock"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minCommonAxisRange"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minSelectedAxisRange"]))
            elif bool(self.lockCommonAxisCheckBox.checkState()) == False and bool(self.lockSelectedAxisCheckBox.checkState()) == True:
                self.maximumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxCommonAxisRange"]))
                self.maximumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["maxSelectedAxisRange"]))
                self.minimumCommonAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minCommonAxisRangeLock"]))
                self.minimumSelectedAxisLineEdit.setText(str(self.configuration["shearbox"]["plot"]["minSelectedAxisRangeLock"]))
            self.opacitySlider.setValue(int(self.configuration["shearbox"]["plot"]["opacity"]))
            self.gridCheckBox.setChecked(int(self.configuration["shearbox"]["plot"]["setGrid"]))
            self.swapCheckBox.setChecked(bool(self.configuration["shearbox"]["plot"]["swap"]))
            self.setChannelsModel(self.configuration["shearbox"]["plot"]["channels"])
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
            self.setDarkMode()
            # log.info("Configuration set.")

    def updateConfiguration(self):
        # Update the configuration based on current GUI settings.
        self.configuration["shearbox"]["plot"]["alpha"] = int(self.alphaSlider.value())
        self.configuration["shearbox"]["plot"]["auto"] = bool(self.autoCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["autoCommonAxis"] = bool(self.autoCommonAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["autoSelectedAxis"] = bool(self.autoSelectedAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["invertCommonAxis"] = bool(self.invertCommonAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["invertSelectedAxis"] = bool(self.invertSelectedAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["lock"] = bool(self.lockCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["lockCommonAxis"] = bool(self.lockCommonAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["lockSelectedAxis"] = bool(self.lockSelectedAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["logCommonAxis"] = bool(self.logCommonAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["logSelectedAxis"] = bool(self.logSelectedAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["manualCommonAxis"] = bool(self.manualCommonAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["manualSelectedAxis"] = bool(self.manualSelectedAxisCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["maxCommonAxisRange"] = float(self.maximumCommonAxisLineEdit.text())
        self.configuration["shearbox"]["plot"]["maxSelectedAxisRange"] = float(self.maximumSelectedAxisLineEdit.text())
        self.configuration["shearbox"]["plot"]["minCommonAxisRange"] = float(self.minimumCommonAxisLineEdit.text())
        self.configuration["shearbox"]["plot"]["minSelectedAxisRange"] = float(self.minimumSelectedAxisLineEdit.text())
        self.configuration["shearbox"]["plot"]["maxCommonAxisRangeLock"] = float(self.maxCommonAxisLock)
        self.configuration["shearbox"]["plot"]["maxSelectedAxisRangeLock"] = float(self.maxSelectedAxisLock)
        self.configuration["shearbox"]["plot"]["minCommonAxisRangeLock"] = float(self.minCommonAxisLock)
        self.configuration["shearbox"]["plot"]["minSelectedAxisRangeLock"] = float(self.minSelectedAxisLock)
        self.configuration["shearbox"]["plot"]["opacity"] = int(self.opacitySlider.value())
        self.configuration["shearbox"]["plot"]["setGrid"] = bool(self.gridCheckBox.checkState())
        self.configuration["shearbox"]["plot"]["swap"] = bool(self.swapCheckBox.checkState())
        # log.info("Configuration updated.")

    @Slot()
    def setSwap(self):
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
        if swap:
            self.plot.setMouseEnabled(not lockSelectedAxis, not lockCommonAxis)
        else:
            self.plot.setMouseEnabled(not lockCommonAxis, not lockSelectedAxis)
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
        swap = bool(self.swapCheckBox.checkState())
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
        if swap:
            self.plot.setMouseEnabled(not lockSelectedAxis, not lockCommonAxis)
        else:
            self.plot.setMouseEnabled(not lockCommonAxis, not lockSelectedAxis)
        self.updateCommonAxisRange()
        self.updateConfiguration()

    @Slot()
    def setLockSelectedAxis(self):
        # Set selected axis lock boolean in GUI and configuration.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        swap = bool(self.swapCheckBox.checkState())
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
        if swap:
            self.plot.setMouseEnabled(not lockSelectedAxis, not lockCommonAxis)
        else:
            self.plot.setMouseEnabled(not lockCommonAxis, not lockSelectedAxis)
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
    def update_output_data(self, plotData):
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
            pen = pg.mkPen(colour, width=2)
            index = self.channelsModel.index(i,4)
            self.channelsModel.setData(index, "{:.2f}".format(self.plotData[-1,i]), role=Qt.EditRole)
            if self.channelsModel._data[i]["plot"] == False:
                self.lines[i].setData([],[])
            elif swap == False:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(self.plotData[:,self.commonChannel], self.plotData[:,i], pen=pen, connect="finite")
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
                self.lines[i].setData(self.plotData[:,i], self.plotData[:,self.commonChannel], pen=pen, connect="finite")
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

    def update_UI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()
        log.info("Updated plot window settings in UI.")        

    def setDarkMode(self):
        # Set dark mode.
        self.darkMode = self.configuration["global"]["darkMode"]
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
        self.plotWidgetClosed.emit(self)

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
