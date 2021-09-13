import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QSlider
from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QIntValidator, QFont
from PySide6.QtCore import Signal, Slot, Qt
from qt_material import apply_stylesheet, QtStyleTools
from src.models import ChannelsTableModel, ColourPickerTableModel
from src.views import ChannelsTableView, ColourPickerTableView
from src.dialogs import ColourPickerDialog
import logging
import pyqtgraph as pg
import numpy as np
from qtrangeslider import QRangeSlider

log = logging.getLogger(__name__)

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
            # self.manualRadio.setCheckState(Qt.Unchecked)

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