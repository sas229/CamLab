import copy
import math
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QSlider
from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QIntValidator, QFont
from PySide6.QtCore import Signal, Slot, Qt, QModelIndex, QEvent
from qt_material import apply_stylesheet, QtStyleTools
from src.models import ChannelsTableModel, ColourPickerTableModel
from src.views import ChannelsTableView, ColourPickerTableView
from src.dialogs import ColourPickerDialog
import logging
import src.local_pyqtgraph.pyqtgraph as pg
import numpy as np
from qtrangeslider import QRangeSlider

log = logging.getLogger(__name__)

class PlotWindow(QWidget, QtStyleTools):
    plotWindowClosed = Signal(str)
    colourUpdated = Signal(QModelIndex, str)

    def __init__(self):
        super().__init__()
        self.defaultChannelsData = [{"plot": False, "name": "Time", "device": "ALL", "colour": "#35e3e3", "value": "0.00", "unit": "s"}]
        self.width = 1200
        self.height = 800
        #self.alpha = 50
        self.opacity = 50
        self.resize(self.width, self.height)
        self.commonChannel = 0
        self.colourPickerDialog = ColourPickerDialog(self)
        self.minCommonAxisLock = 0
        self.maxCommonAxisLock = 0
        self.minSelectedAxisLock = 0
        self.maxSelectedAxisLock = 0

        self.plot = pg.PlotWidget(self)

        styles = self.setStyle()
        self.plot.setLabel('left', 'Selected channels', **styles)
        self.plot.setLabel('bottom', 'Common channel', **styles)
        # self.plot.setMenuEnabled(enableMenu=False)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

        self.plotWindowLayout = QHBoxLayout()
        self.plotWindowLayout.addWidget(self.plot)   

        # Channels data model.
        self.selectedChannelsTableView = ChannelsTableView()
        self.setChannelsModel(self.defaultChannelsData)

        # self.createPens()
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

        self.autoCommonAxisCheckBox = QCheckBox("Auto")
        self.manualCommonAxisCheckBox = QCheckBox("Manual")
        self.setMinimumCommonAxisLabel = QLabel("Minimum:")
        self.setMinimumCommonAxisLineEdit = QLineEdit()
        self.setMinimumCommonAxisLineEdit.setEnabled(False)
        self.setMaximumCommonAxisLabel = QLabel("Maximum:")
        self.setMaximumCommonAxisLineEdit = QLineEdit()
        self.setMaximumCommonAxisLineEdit.setEnabled(False)

        self.lockCheckBox = QCheckBox("Lock")

        self.invertCommonAxisCheckBox = QCheckBox("Invert")

        self.logCommonAxisCheckBox= QCheckBox("Log")
        self.autoPanCommonAxisCheckBox = QCheckBox("Auto")
        self.lockCommonAxisCheckBox = QCheckBox("Lock")

        self.autoSelectedAxisCheckBox = QCheckBox("Auto")
        self.manualSelectedAxisCheckBox = QCheckBox("Manual")
        self.setMinimumSelectedAxisLabel = QLabel("Minimum:")
        self.setMinimumSelectedAxisLineEdit = QLineEdit()
        self.setMinimumSelectedAxisLineEdit.setEnabled(False)
        self.setMaximumSelectedAxisLabel = QLabel("Maximum:")
        self.setMaximumSelectedAxisLineEdit = QLineEdit()
        self.setMaximumSelectedAxisLineEdit.setEnabled(False)
        
        self.invertSelectedAxisCheckBox = QCheckBox("Invert")
        self.logSelectedAxisCheckBox= QCheckBox("Log")
        self.autoPanSelectedAxisCheckBox = QCheckBox("Auto")
        self.lockSelectedAxisCheckBox = QCheckBox("Lock")

        self.controlsGroupBox = QGroupBox("Axis Controls")
        self.controlsGroupBox.setFixedHeight(250)
        self.controlsGroupBox.setFixedWidth(340)
        
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
        self.xAxisControlsLayout.addWidget(self.setMinimumCommonAxisLineEdit, 1, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumCommonAxisLineEdit, 1, 2)
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
        self.yAxisControlsLayout.addWidget(self.setMinimumSelectedAxisLineEdit, 1, 1)
        self.yAxisControlsLayout.addWidget(self.setMaximumSelectedAxisLineEdit, 1, 2)
        self.yAxisControlsLayout.addWidget(self.lockSelectedAxisCheckBox, 2, 0)
        self.yAxisControlsLayout.addWidget(self.invertSelectedAxisCheckBox,2 , 1)
        self.yAxisControlsLayout.addWidget(self.logSelectedAxisCheckBox, 2, 2)
        self.yAxisControlsWidget.setLayout(self.yAxisControlsLayout)

        self.controlsTabWidget = QTabWidget()
        self.controlsTabWidget.addTab(self.globalControlsWidget, "   Global   ")
        self.controlsTabWidget.addTab(self.xAxisControlsWidget, "Common")
        self.controlsTabWidget.addTab(self.yAxisControlsWidget, "Selected")
        self.controlsTabWidget.setFixedWidth(285)

        self.controlsTabsLayout = QVBoxLayout()
        self.controlsTabsLayout.addWidget(self.controlsTabWidget)
        self.controlsGroupBox.setLayout(self.controlsTabsLayout)

        self.selectedChannelsTableGroupBox.setLayout(self.selectedChannelsTableLayout) 
        self.selectedChannelsTableGroupBox.setFixedWidth(340)


        self.plotWindowLayout.addLayout(self.controlsLayout)
        self.setLayout(self.plotWindowLayout)

        self.fillCommonChannelComboBox()

        rangeCommonAxis = self.plot.getViewBox().state
        self.setMinimumCommonAxisLineEdit.setText(str('%.2f' % rangeCommonAxis['viewRange'][0][0]))
        self.setMaximumCommonAxisLineEdit.setText(str('%.2f' % rangeCommonAxis['viewRange'][0][1]))
        rangeSelectedAxis = self.plot.getViewBox().state
        self.setMinimumSelectedAxisLineEdit.setText(str('%.2f' % rangeSelectedAxis['viewRange'][1][0]))
        self.setMaximumSelectedAxisLineEdit.setText(str('%.2f' % rangeSelectedAxis['viewRange'][1][1]))

        self.invertCommonAxisCheckBox.stateChanged.connect(self.invertCommonAxis)
        self.logCommonAxisCheckBox.stateChanged.connect(self.logCommonAxis)
        self.invertSelectedAxisCheckBox.stateChanged.connect(self.invertSelectedAxis)
        self.logSelectedAxisCheckBox.stateChanged.connect(self.logSelectedAxis)
        
        self.gridCheckBox.stateChanged.connect(self.setGrid)
        self.alphaSlider.valueChanged.connect(self.alphaSlider_value)
        self.opacitySlider.valueChanged.connect(self.opacitySlider_value)
        self.plot.scene().sigMousePanned.connect(self.switchToManual)
        self.plot.scene().sigMouseWheel.connect(self.switchToManual)
        
        self.plot.sigXRangeChanged.connect(self.updateCommonAxisRange)
        self.plot.sigYRangeChanged.connect(self.updateSelectedAxisRange)
        
        self.selectedChannelsTableView.clicked.connect(self.selectColour)
        self.colourPickerDialog.selectedColour.connect(self.setColour)
        self.colourPickerDialog.selectedColour.connect(self.emitColour)
        self.commonChannelComboBox.currentIndexChanged.connect(self.setCommonChannel)

        self.autoCheckBox.clicked.connect(self.autoMode)
        self.autoCommonAxisCheckBox.clicked.connect(self.setAutoCommonAxisMode)
        self.autoSelectedAxisCheckBox.clicked.connect(self.setAutoSelectedAxisMode)
        self.manualCommonAxisCheckBox.clicked.connect(self.setManualCommonAxisMode)
        self.manualSelectedAxisCheckBox.clicked.connect(self.setManualSelectedAxisMode)

        self.lockCheckBox.clicked.connect(self.setLock)
        self.lockCommonAxisCheckBox.stateChanged.connect(self.setLockX)
        self.lockSelectedAxisCheckBox.stateChanged.connect(self.setLockY)

        self.setMinimumCommonAxisLineEdit.returnPressed.connect(self.setNewCommonAxisRange)
        self.setMaximumCommonAxisLineEdit.returnPressed.connect(self.setNewCommonAxisRange)
        self.setMinimumSelectedAxisLineEdit.returnPressed.connect(self.setNewSelectedAxisRange)
        self.setMaximumSelectedAxisLineEdit.returnPressed.connect(self.setNewSelectedAxisRange)

    # @Slot 
    # def updateAxisRange(self):
    #     swap =

    @Slot()
    def setLock(self):
        lock = bool(self.lockCheckBox.checkState())
        if lock == True:
            self.lockCommonAxisCheckBox.setChecked(True)
            self.lockSelectedAxisCheckBox.setChecked(True)
        else:
            self.lockCommonAxisCheckBox.setChecked(False)
            self.lockSelectedAxisCheckBox.setChecked(False)

    @Slot()
    def setLockX(self):
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        if lockCommonAxis == True:
            self.minXLock = copy.deepcopy(self.configuration["plots"][self.plotNumber]["minXRange"])
            self.maxXLock = copy.deepcopy(self.configuration["plots"][self.plotNumber]["maxXRange"])
            self.setMinimumCommonAxisLineEdit.setEnabled(False)
            self.setMaximumCommonAxisLineEdit.setEnabled(False)
            if lockSelectedAxis == True:
                self.lockCheckBox.setChecked(True)
        else:
            self.lockCheckBox.setChecked(False)
            if manualCommonAxis == True:
                self.setMinimumCommonAxisLineEdit.setEnabled(True)
                self.setMaximumCommonAxisLineEdit.setEnabled(True)        

    @Slot()
    def setLockY(self):
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        if lockSelectedAxis == True:
            self.minYLock = copy.deepcopy(self.configuration["plots"][self.plotNumber]["minYRange"])
            self.maxYLock = copy.deepcopy(self.configuration["plots"][self.plotNumber]["maxYRange"])
            self.setMinimumSelectedAxisLineEdit.setEnabled(False)
            self.setMaximumSelectedAxisLineEdit.setEnabled(False)
            if lockCommonAxis == True:
                self.lockCheckBox.setChecked(True)
        else:
            self.lockCheckBox.setChecked(False)
            if manualSelectedAxis == True:
                self.setMinimumSelectedAxisLineEdit.setEnabled(True)
                self.setMaximumSelectedAxisLineEdit.setEnabled(True)

    @Slot()
    def autoMode(self):
        # When auto is True, enable the autoRange function on both axes, set autoCommonAxisCheckBox 
        # and autoSelectedAxisCheckBox to True and manualCommonAxisCheckBox and manualSelectedAxisCheckBox to False. 
        auto = bool(self.autoCheckBox.checkState())
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        if auto == True:
            self.plot.enableAutoRange()
            self.autoCommonAxisCheckBox.setChecked(True)
            self.autoSelectedAxisCheckBox.setChecked(True)
            self.manualCommonAxisCheckBox.setChecked(False)
            self.manualSelectedAxisCheckBox.setChecked(False)
            self.setMinimumCommonAxisLineEdit.setEnabled(False)
            self.setMaximumCommonAxisLineEdit.setEnabled(False)
            self.setMinimumSelectedAxisLineEdit.setEnabled(False)
            self.setMaximumSelectedAxisLineEdit.setEnabled(False)
        # Otherwise disable the autoRange function, set autoCommonAxisCheckBox 
        # and autoSelectedAxisCheckBox to False and manualCommonAxisCheckBox and manualSelectedAxisCheckBox to False.
        elif auto == False:
            self.plot.disableAutoRange()
            self.autoCommonAxisCheckBox.setChecked(False)
            self.autoSelectedAxisCheckBox.setChecked(False)
            self.manualCommonAxisCheckBox.setChecked(True)
            self.manualSelectedAxisCheckBox.setChecked(True)
            if lockCommonAxis == False:
                self.setMinimumCommonAxisLineEdit.setEnabled(True)
                self.setMaximumCommonAxisLineEdit.setEnabled(True)
            if lockSelectedAxis == False:
                self.setMinimumSelectedAxisLineEdit.setEnabled(True)
                self.setMaximumSelectedAxisLineEdit.setEnabled(True)
            self.setNewCommonAxisRange()
            self.setNewSelectedAxisRange()
        self.configuration["plots"][self.plotNumber]["auto"] = auto

    @Slot()
    def setAutoCommonAxisMode(self):
        autoCommonAxis = bool(self.autoCommonAxisCheckBox.checkState())
        if autoCommonAxis == True:
            self.manualCommonAxisCheckBox.setChecked(False)
            self.plot.enableAutoRange(axis='x')
            self.setMinimumCommonAxisLineEdit.setEnabled(False)
            self.setMaximumCommonAxisLineEdit.setEnabled(False)
        else:
            self.manualCommonAxisCheckBox.setChecked(True)
            self.setManualCommonAxisMode()
        self.configuration["plots"][self.plotNumber]["autoCommonAxis"] = autoCommonAxis

    @Slot()
    def setAutoSelectedAxisMode(self):
        autoSelectedAxis = bool(self.autoSelectedAxisCheckBox.checkState())
        if autoSelectedAxis == True:
            self.manualSelectedAxisCheckBox.setChecked(False)
            self.plot.enableAutoRange(axis='y')
            self.setMinimumSelectedAxisLineEdit.setEnabled(False)
            self.setMaximumSelectedAxisLineEdit.setEnabled(False)
        else:
            self.manualSelectedAxisCheckBox.setChecked(True)
            self.setmanualSelectedAxisMode()
        self.configuration["plots"][self.plotNumber]["autoSelectedAxis"] = autoSelectedAxis

    @Slot()
    def setManualCommonAxisMode(self):
        self.setNewCommonAxisRange()
        manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        if manualCommonAxis == True:
            self.plot.disableAutoRange(axis='x')
            self.autoCheckBox.setChecked(False)
            self.autoCommonAxisCheckBox.setChecked(False)
            if lockCommonAxis == False:
                self.setMinimumCommonAxisLineEdit.setEnabled(True)
                self.setMaximumCommonAxisLineEdit.setEnabled(True)
        else:
            self.autoCommonAxisCheckBox.setChecked(True)
            self.setautoCommonAxisMode()
        self.configuration["plots"][self.plotNumber]["manualCommonAxis"] = manualCommonAxis
            
    @Slot()
    def setManualSelectedAxisMode(self):
        self.setNewSelectedAxisRange()
        manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        if manualSelectedAxis == True:
            self.plot.disableAutoRange(axis='y')
            self.autoCheckBox.setChecked(False)
            self.autoSelectedAxisCheckBox.setChecked(False)
            if lockSelectedAxis == False:
                self.setMinimumSelectedAxisLineEdit.setEnabled(True)
                self.setMaximumSelectedAxisLineEdit.setEnabled(True)
        else:
            self.autoSelectedAxisCheckBox.setChecked(True)
            self.setautoSelectedAxisMode()      
        self.configuration["plots"][self.plotNumber]["manualSelectedAxis"] = manualSelectedAxis
    
    @Slot()
    def updateCommonAxisRange(self):
        # Store current minX and maxX when sigXRangeChanged signal received.
        rangeCommonAxis = self.plot.getViewBox().state
        self.minX = float('%.2f' % rangeCommonAxis['viewRange'][0][0])
        self.maxX = float('%.2f' % rangeCommonAxis['viewRange'][0][1])
        self.configuration["plots"][self.plotNumber]["minXRange"] = self.minX
        self.configuration["plots"][self.plotNumber]["maxXRange"] = self.maxX

        # If lock is False update the lineedit text.
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        if lockCommonAxis == True:
            self.setMinimumCommonAxisLineEdit.setText(str(self.minXLock))
            self.setMaximumCommonAxisLineEdit.setText(str(self.maxXLock))
        elif lockCommonAxis == False:
            self.setMinimumCommonAxisLineEdit.setText(str(self.minX))
            self.setMaximumCommonAxisLineEdit.setText(str(self.maxX))
    
    @Slot()
    def updateSelectedAxisRange(self):
        # Store current minY and maxY when sigXRangeChanged signal received.
        rangeSelectedAxis = self.plot.getViewBox().state
        self.minY = float('%.2f' % rangeSelectedAxis['viewRange'][1][0])
        self.maxY = float('%.2f' % rangeSelectedAxis['viewRange'][1][1])
        self.configuration["plots"][self.plotNumber]["minYRange"] = self.minY
        self.configuration["plots"][self.plotNumber]["maxYRange"] = self.maxY

        # If lock is False update the lineedit text.
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        if lockSelectedAxis == True:
            self.setMinimumSelectedAxisLineEdit.setText(str(self.minYLock))
            self.setMaximumSelectedAxisLineEdit.setText(str(self.maxYLock))
        elif lockSelectedAxis == False:
            self.setMinimumSelectedAxisLineEdit.setText(str(self.minY))
            self.setMaximumSelectedAxisLineEdit.setText(str(self.maxY))

    @Slot()
    def setNewCommonAxisRange(self):
        # Set the new range for the x axis.
        self.minX = float(self.setMinimumCommonAxisLineEdit.text())
        self.maxX = float(self.setMaximumCommonAxisLineEdit.text())
        self.plot.setXRange(self.minX, self.maxX, padding=0)
        
    @Slot()
    def setNewSelectedAxisRange(self):
        # Set the new range for the y axis.
        self.minY = float(self.setMinimumSelectedAxisLineEdit.text())
        self.maxY = float(self.setMaximumSelectedAxisLineEdit.text())
        self.plot.setYRange(self.minY, self.maxY, padding=0)
    
    @Slot()
    def setNewSwapCommonAxisRange(self):
        # Set the new range for the x axis (swapped).
        self.minY = float(self.setMinimumSelectedAxisLineEdit.text())
        self.maxY = float(self.setMaximumSelectedAxisLineEdit.text())
        self.plot.setXRange(self.minY, self.maxY, padding=0)
        
    @Slot()
    def setNewSwapSelectedAxisRange(self):
        # Set the new range for the y axis (swapped).
        self.minX = float(self.setMinimumCommonAxisLineEdit.text())
        self.maxX = float(self.setMaximumCommonAxisLineEdit.text())
        self.plot.setYRange(self.minX, self.maxX, padding=0)

    @Slot()
    def switchToManual(self):
        lockCommonAxis = bool(self.lockCommonAxisCheckBox.checkState())
        lockSelectedAxis = bool(self.lockSelectedAxisCheckBox.checkState())
        self.autoCheckBox.setChecked(False)
        self.autoCommonAxisCheckBox.setChecked(False)
        self.autoSelectedAxisCheckBox.setChecked(False)
        self.manualCommonAxisCheckBox.setChecked(True)
        if lockCommonAxis == False:
            self.setMinimumCommonAxisLineEdit.setEnabled(True)
            self.setMaximumCommonAxisLineEdit.setEnabled(True)
        self.manualSelectedAxisCheckBox.setChecked(True)
        if lockSelectedAxis == False:
            self.setMinimumSelectedAxisLineEdit.setEnabled(True)
            self.setMaximumSelectedAxisLineEdit.setEnabled(True)

    def formatColumns(self):
        self.selectedChannelsTableView.setColumnWidth(0, 30)
        self.selectedChannelsTableView.setColumnWidth(1, 30)
        self.selectedChannelsTableView.setColumnWidth(2, 70)
        self.selectedChannelsTableView.setColumnWidth(3, 50)
        self.selectedChannelsTableView.setColumnWidth(4, 60)
        self.selectedChannelsTableView.setColumnWidth(5, 30)

    def setPlotNumber(self, plotNumber):
        self.plotNumber = plotNumber

    def fillCommonChannelComboBox(self):
        numChannels = len(self.channelsModel._data)
        self.commonChannelComboBox.clear()
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
        alphaValue = self.alpha
        # manualCommonAxis = bool(self.manualCommonAxisCheckBox.checkState())
        # manualSelectedAxis = bool(self.manualSelectedAxisCheckBox.checkState())
        styles = self.setStyle()
        numChannels = len(self.channelsModel._data)
        #do this if statement for the first time the plot is run
        if bool(self.autoCheckBox.checkState()) == True:
            self.autoMode()

        for i in range(numChannels):
            colour = self.channelsModel._data[i]["colour"]
            pen = pg.mkPen(colour)
            index = self.channelsModel.index(i,4)
            self.channelsModel.setData(index, "{:.2f}".format(plotData[-1,i]), role=Qt.EditRole)
            if self.channelsModel._data[i]["plot"] == False:
                self.lines[i].setData([],[])
            elif self.swapCheckBox.checkState() == False:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(plotData[:,self.commonChannel], plotData[:,i], pen=pen)
                self.plot.setLabel('left', 'Selected channels', **styles)
                self.plot.setLabel('bottom', 'Common channel', **styles)
                # if manualCommonAxis == True:
                #     self.setNewCommonAxisRange()
                # if manualSelectedAxis == True:
                #     self.setNewSelectedAxisRange()
            else:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(plotData[:,i], plotData[:,self.commonChannel], pen=pen)
                self.plot.setLabel('bottom', 'Selected channels', **styles)
                self.plot.setLabel('left', 'Common channel', **styles)
                # if manualCommonAxis == True:
                #     self.setNewCommonAxisRange()
                # if manualSelectedAxis == True:
                #     self.setNewSelectedAxisRange()

    def setStyle(self):
        return {'color': os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size': '16px'}

    def logCommonAxis(self):
        swap = bool(self.swapCheckBox.checkState())
        logCommonAxis = bool(self.logCommonAxisCheckBox.checkState())
        if swap == True:
            self.plot.setLogMode(x=None, y=logCommonAxis)
        else:
            self.plot.setLogMode(x=logCommonAxis, y=None)
        self.configuration["plots"][self.plotNumber]["logCommonAxis"] = logCommonAxis

    def invertCommonAxis(self):
        swap = bool(self.swapCheckBox.checkState())
        invertCommonAxis = bool(self.invertCommonAxisCheckBox.checkState())
        if swap == True:
            self.plot.getPlotItem().invertY(invertCommonAxis)
        else:
            self.plot.getPlotItem().invertX(invertCommonAxis)
        self.configuration["plots"][self.plotNumber]["invertCommonAxis"] = invertCommonAxis

    def logSelectedAxis(self):
        swap = bool(self.swapCheckBox.checkState())
        logSelectedAxis = bool(self.logSelectedAxisCheckBox.checkState())
        if swap == True:
            self.plot.setLogMode(x=logSelectedAxis, y=None)
        else:
            self.plot.setLogMode(x=None, y=logSelectedAxis)
        self.configuration["plots"][self.plotNumber]["logSelectedAxis"] = logSelectedAxis

    def invertSelectedAxis(self):
        swap = bool(self.swapCheckBox.checkState())
        invertSelectedAxis = bool(self.invertSelectedAxisCheckBox.checkState())
        if swap == True:
            self.plot.getPlotItem().invertX(invertSelectedAxis)
        else:
            self.plot.getPlotItem().invertY(invertSelectedAxis)
        self.configuration["plots"][self.plotNumber]["invertSelectedAxis"] = invertSelectedAxis

    def setCommonRange(self):
        self.plot.getPlotItem().setXRange(1,4)

    def setGrid(self):
        b = self.gridCheckBox.checkState()
        self.plot.showGrid(x = b, y = b, alpha = self.opacity/100)
        self.configuration["plots"][self.plotNumber]["setGrid"] = (bool(b))

    def updateUI(self, newConfiguration):
        # Update the UI after any configuration change.
        self.configuration = newConfiguration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()
        log.info("Updated plot window settings in UI.")        

    def setDarkMode(self):
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        with open('CamLab.css') as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

        self.plot.setBackground(os.environ['QTMATERIAL_SECONDARYLIGHTCOLOR'])
        styles = self.setStyle()
        self.plot.setLabel('left', 'Selected channels', **styles)
        self.plot.setLabel('bottom', 'Common channel', **styles)
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

    def alphaSlider_value(self, i):
        self.alpha = i
        self.configuration["plots"][self.plotNumber]["alpha"] = (self.alpha)

    def opacitySlider_value(self, i):
        self.opacity = i
        if bool(self.gridCheckBox.checkState()) == True:
            self.setGrid()
        self.configuration["plots"][self.plotNumber]["opacity"] = (self.opacity)

    def setConfiguration(self, configuration):
        self.configuration = configuration
        
        self.logCommonAxisCheckBox.setChecked(self.configuration["plots"][self.plotNumber]["logCommonAxis"])
        self.logSelectedAxisCheckBox.setChecked(self.configuration["plots"][self.plotNumber]["logSelectedAxis"])
        self.invertCommonAxisCheckBox.setChecked(self.configuration["plots"][self.plotNumber]["invertCommonAxis"])
        self.invertSelectedAxisCheckBox.setChecked(self.configuration["plots"][self.plotNumber]["invertSelectedAxis"])
        self.gridCheckBox.setChecked(self.configuration["plots"][self.plotNumber]["setGrid"])
        self.alphaSlider.setValue(self.configuration["plots"][self.plotNumber]["alpha"])
        self.opacitySlider.setValue(self.configuration["plots"][self.plotNumber]["opacity"])

        minX = copy.deepcopy(self.configuration['plots'][self.plotNumber]["minCommonAxisRange"])
        maxX = copy.deepcopy(self.configuration['plots'][self.plotNumber]["maxCommonAxisRange"])
        minY = copy.deepcopy(self.configuration['plots'][self.plotNumber]["minSelectedAxisRange"])
        maxY = copy.deepcopy(self.configuration['plots'][self.plotNumber]["maxSelectedAxisRange"])
        self.manualCommonAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["manualCommonAxis"])
        self.manualSelectedAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["manualSelectedAxis"])
        self.plot.setXRange(minX, maxX, padding=0)
        self.plot.setYRange(minY, maxY, padding = 0)

        self.autoCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["auto"])
        self.autoCommonAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["autoCommonAxis"])
        self.autoSelectedAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["autoSelectedAxis"])

        self.swapCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["swap"])

        self.lockCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["lock"])
        self.lockCommonAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["lockCommonAxis"])
        self.lockSelectedAxisCheckBox.setChecked(self.configuration['plots'][self.plotNumber]["lockSelectedAxis"])

        self.setChannelsModel(self.configuration["plots"][self.plotNumber]["channels"])

        self.fillCommonChannelComboBox()
        self.createLines()

        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

