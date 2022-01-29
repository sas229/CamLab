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
    channelsModelUpdated = Signal(str)

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
        # self.colourPickerDialog = ColourPickerDialog()
        self.lock_xMin = 0
        self.lock_xMax = 0
        self.lock_yMin = 0
        self.lock_yMax = 0

        self.plot = pg.PlotWidget(self)

        styles = self.setStyle()
        self.plot.setLabel('left', 'Selected channels', **styles)
        self.plot.setLabel('bottom', 'Common channel', **styles)
        # self.plot.setMenuEnabled(enableMenu=False)
        self.plot.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.plot.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

        self.plotWindowLayout = QHBoxLayout()
        self.plotWindowLayout.addWidget(self.plot)   

        # Channels data model and table.
        self.selectedChannelsTableView = ChannelsTableView()
        self.setChannelsModel(self.defaultChannelsData)
        self.selectedChannelsTableView.setModel(self.channelsModel)

        # self.createPens()
        self.createLines()

        self.selectedChannelsLabel = QLabel("Selected channels:")
        
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
        
        self.swapRadio = QCheckBox("Swap")
        self.autoRadio = QCheckBox("Auto")
        self.downsampleRadio = QCheckBox("Downsample")
        self.gridRadio = QCheckBox("Grid")
        self.alphaLabel = QLabel("Alpha:")
        self.alphaSlider = QSlider(Qt.Horizontal)
        #self.alphaSlider.setValue(self.alpha)
        self.opacityLabel = QLabel("Opacity:")
        self.opacitySlider = QSlider(Qt.Horizontal)
        #self.opacitySlider.setValue(self.opacity)

        self.autoXRadio = QCheckBox("Auto")
        self.manualXRadio = QCheckBox("Manual")
        self.setMinimumXLabel = QLabel("Minimum:")
        self.setMinimumXLineEdit = QLineEdit()
        self.setMinimumXLineEdit.setEnabled(False)
        self.setMaximumXLabel = QLabel("Maximum:")
        self.setMaximumXLineEdit = QLineEdit()
        self.setMaximumXLineEdit.setEnabled(False)

        self.lockRadio = QCheckBox("Lock")

        self.invertXRadio = QCheckBox("Invert")

        self.logXRadio= QCheckBox("Log")
        self.autoPanXRadio = QCheckBox("Auto Pan")
        self.gridXRadio = QCheckBox("Grid")


        self.autoYRadio = QCheckBox("Auto")
        self.manualYRadio = QCheckBox("Manual")
        self.setMinimumYLabel = QLabel("Minimum:")
        self.setMinimumYLineEdit = QLineEdit()
        self.setMinimumYLineEdit.setEnabled(False)
        self.setMaximumYLabel = QLabel("Maximum:")
        self.setMaximumYLineEdit = QLineEdit()
        self.setMaximumYLineEdit.setEnabled(False)
        
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
        self.globalControlsLayout.addWidget(self.lockRadio, 0, 3)
        self.globalControlsLayout.addWidget(self.alphaLabel, 1, 0)
        self.globalControlsLayout.addWidget(self.alphaSlider, 1, 1, 1, 3)
        self.globalControlsLayout.addWidget(self.opacityLabel, 2, 0)
        self.globalControlsLayout.addWidget(self.opacitySlider, 2, 1, 1, 3)
        self.globalControlsWidget.setLayout(self.globalControlsLayout)

        self.xAxisControlsWidget = QWidget()
        self.xAxisControlsLayout = QGridLayout()
        self.xAxisControlsLayout.addWidget(self.autoXRadio, 0, 0)
        self.xAxisControlsLayout.addWidget(self.setMinimumXLabel, 0, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumXLabel, 0, 2)
        self.xAxisControlsLayout.addWidget(self.manualXRadio, 1, 0)
        self.xAxisControlsLayout.addWidget(self.setMinimumXLineEdit, 1, 1)
        self.xAxisControlsLayout.addWidget(self.setMaximumXLineEdit, 1, 2)
        self.xAxisControlsLayout.addWidget(self.invertXRadio, 2, 0)
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

        self.fillCommonChannelComboBox()

        rangeX = self.plot.getViewBox().state
        self.setMinimumXLineEdit.setText(str('%.2f' % rangeX['viewRange'][0][0]))
        self.setMaximumXLineEdit.setText(str('%.2f' % rangeX['viewRange'][0][1]))
        rangeY = self.plot.getViewBox().state
        self.setMinimumYLineEdit.setText(str('%.2f' % rangeY['viewRange'][1][0]))
        self.setMaximumYLineEdit.setText(str('%.2f' % rangeY['viewRange'][1][1]))

        self.invertXRadio.stateChanged.connect(self.invertX)
        self.logXRadio.stateChanged.connect(self.logXAxis)
        self.invertYRadio.stateChanged.connect(self.invertY)
        self.logYRadio.stateChanged.connect(self.logYAxis)
        self.autoRadio.stateChanged.connect(self.autoRange)
        self.autoXRadio.stateChanged.connect(self.autoXRange)
        self.autoYRadio.stateChanged.connect(self.autoYRange)
        self.gridRadio.stateChanged.connect(self.setGridXY)
        self.gridXRadio.stateChanged.connect(self.setGridX)
        self.gridYRadio.stateChanged.connect(self.setGridY)
        self.alphaSlider.valueChanged.connect(self.alphaSlider_value)
        self.opacitySlider.valueChanged.connect(self.opacitySlider_value)
        self.plot.scene().sigMousePanned.connect(self.switchToManualXY)
        self.plot.scene().sigMouseWheel.connect(self.switchToManualXY)
        self.manualXRadio.stateChanged.connect(self.manualXRange)
        self.manualYRadio.stateChanged.connect(self.manualYRange)
        self.plot.sigXRangeChanged.connect(self.manualXRange)
        self.plot.sigYRangeChanged.connect(self.manualYRange)
        self.lockRadio.stateChanged.connect(self.lockCheckBox)
        self.selectedChannelsTableView.clicked.connect(self.selectColour)
        self.colourPickerDialog.selectedColour.connect(self.setColour)
        self.colourPickerDialog.selectedColour.connect(self.emitColour)
        self.commonChannelComboBox.currentIndexChanged.connect(self.setCommonChannel)


    def formatColumns(self):
        self.selectedChannelsTableView.setColumnWidth(0, 30)
        self.selectedChannelsTableView.setColumnWidth(1, 25)
        self.selectedChannelsTableView.setColumnWidth(2, 60)
        self.selectedChannelsTableView.setColumnWidth(3, 55)
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
        styles = self.setStyle()
        numChannels = len(self.channelsModel._data)
        #do this if statement for the first time the plot is run
        if bool(self.autoRadio.checkState()) == True:
            self.autoRange()

        for i in range(numChannels):
            colour = self.channelsModel._data[i]["colour"]
            pen = pg.mkPen(colour)
            index = self.channelsModel.index(i,4)
            self.channelsModel.setData(index, "{:.2f}".format(plotData[-1,i]), role=Qt.EditRole)
            if self.channelsModel._data[i]["plot"] == False:
                self.lines[i].setData([],[])
            elif self.swapRadio.checkState() == False:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(plotData[:,self.commonChannel], plotData[:,i], pen=pen)
                self.plot.setLabel('left', 'Selected channels', **styles)
                self.plot.setLabel('bottom', 'Common channel', **styles)
            else:
                self.lines[i].setAlpha(alphaValue/100, False)
                self.lines[i].setData(plotData[:,i], plotData[:,self.commonChannel], pen=pen)
                self.plot.setLabel('bottom', 'Selected channels', **styles)
                self.plot.setLabel('left', 'Common channel', **styles)

    def setStyle(self):
        return {'color': os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size': '16px'}

    def logXAxis(self):
        b = self.logXRadio.checkState()
        self.plot.setLogMode(x=b, y=None)
        self.configuration["plots"][self.plotNumber]["logXAxis"] = (bool(b))

    def invertX(self):
        b = self.invertXRadio.checkState()
        self.plot.getPlotItem().invertX(b)
        self.configuration["plots"][self.plotNumber]["invertX"] = (bool(b))

    def logYAxis(self):
        b = self.logYRadio.checkState()
        self.plot.setLogMode(x=None, y=b)
        self.configuration["plots"][self.plotNumber]["logYAxis"] = (bool(b))

    def invertY(self):
        b = self.invertYRadio.checkState()
        self.plot.getPlotItem().invertY(b)
        self.configuration["plots"][self.plotNumber]["invertY"] = (bool(b))

    def setXRange(self):
        self.plot.getPlotItem().setXRange(1,4)

    def setGridXY(self):
        b = self.gridRadio.checkState()
        self.plot.showGrid(x = b, y = b, alpha = self.opacity/100)
        self.gridXRadio.setChecked(bool(b))
        self.gridYRadio.setChecked(bool(b))

        self.configuration["plots"][self.plotNumber]["setGrid"] = (bool(b))

    def setGridX(self):
        b = self.gridXRadio.checkState()
        self.plot.showGrid(x = b, y = None, alpha = self.opacity/100)
        if bool(self.gridXRadio.checkState()) == False and bool(self.gridYRadio.checkState()) == True:
            self.gridRadio.setChecked(False)
            self.gridYRadio.setChecked(True)
        elif bool(self.gridXRadio.checkState()) == False and bool(self.gridYRadio.checkState()) == False:
            self.gridRadio.setChecked(False)
            self.gridYRadio.setChecked(False)
        elif bool(self.gridXRadio.checkState()) == True and bool(self.gridYRadio.checkState()) == True and bool(self.gridRadio.checkState()) == False:
            self.gridRadio.setChecked(True)

        self.configuration["plots"][self.plotNumber]["setGridX"] = (bool(b))

    def setGridY(self):
        b = self.gridYRadio.checkState()
        self.plot.showGrid(x=None, y=b, alpha = self.opacity/100)
        if bool(self.gridYRadio.checkState()) == False and bool(self.gridXRadio.checkState()) == True:
            self.gridRadio.setChecked(False)
            self.gridXRadio.setChecked(True)
        elif bool(self.gridYRadio.checkState()) == False and bool(self.gridXRadio.checkState()) == False:
            self.gridRadio.setChecked(False)
            self.gridXRadio.setChecked(False)
        elif bool(self.gridYRadio.checkState()) == True and bool(self.gridXRadio.checkState()) == True and bool(self.gridRadio.checkState()) == False:
            self.gridRadio.setChecked(True)

        self.configuration["plots"][self.plotNumber]["setGridY"] = (bool(b))

    # def updateUI(self, newConfiguration):
    #     # Update the UI after any configuration change.
    #     self.configuration = newConfiguration
    #     self.darkMode = self.configuration["global"]["darkMode"]
    #     self.setDarkMode()
    #     log.info("Updated plot window settings in UI.")        

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
        if bool(self.gridRadio.checkState()) == True:
            self.setGridXY()
        elif bool(self.gridRadio.checkState()) == False:
            self.setGridY()
            self.setGridX()
        self.configuration["plots"][self.plotNumber]["opacity"] = (self.opacity)

    def autoRange(self):
        b = self.autoRadio.checkState()
        if bool(b) == True:
            self.plot.enableAutoRange()
            self.autoXRadio.setChecked(True)
            self.autoYRadio.setChecked(True)
            self.manualXRadio.setChecked(False)
            self.manualYRadio.setChecked(False)

        elif bool(b) == False:
            self.plot.disableAutoRange()
            self.autoXRadio.setChecked(False)
            self.autoYRadio.setChecked(False)

    def autoXRange(self):
        b = self.autoXRadio.checkState()
        if bool(b) == False and bool(self.autoYRadio.checkState()) == True:
            self.plot.disableAutoRange(axis='x')
            self.manualXRadio.setChecked(True)
            self.autoRadio.setChecked(False)
            self.autoYRadio.setChecked(True)

        elif bool(b) == False and bool(self.autoYRadio.checkState()) == False:
            self.plot.disableAutoRange(axis='x')
            self.manualXRadio.setChecked(True)
            self.autoRadio.setChecked(False)
            self.autoYRadio.setChecked(False)

        elif bool(b) == True and bool(self.autoYRadio.checkState()) == False:
            self.plot.enableAutoRange(axis='x')
            self.manualXRadio.setChecked(False)

        elif bool(b) == True and bool(self.autoYRadio.checkState()) == True and bool(
                self.autoRadio.checkState()) == False:
            self.manualXRadio.setChecked(False)
            self.autoRadio.setChecked(True)

    def autoYRange(self):
        b = self.autoYRadio.checkState()
        if bool(b) == False and bool(self.autoXRadio.checkState()) == True:
            self.plot.disableAutoRange(axis='y')
            self.manualYRadio.setChecked(True)
            self.autoRadio.setChecked(False)
            self.autoXRadio.setChecked(True)

        elif bool(b) == False and bool(self.autoXRadio.checkState()) == False:
            self.plot.disableAutoRange(axis='y')
            self.manualYRadio.setChecked(True)
            self.autoRadio.setChecked(False)
            self.autoXRadio.setChecked(False)

        elif bool(b) == True and bool(self.autoXRadio.checkState()) == False:
            self.plot.enableAutoRange(axis='y')
            self.manualYRadio.setChecked(False)

        elif bool(b) == True and bool(self.autoXRadio.checkState()) == True and bool(
                self.autoRadio.checkState()) == False:
            self.manualYRadio.setChecked(False)
            self.autoRadio.setChecked(True)

    def switchToManualXY(self):
        self.autoRadio.setChecked(False)
        if bool(self.autoRadio.checkState()) == False:
            self.autoXRadio.setChecked(False)
            self.autoYRadio.setChecked(False)

    def manualXRange(self):
        rangeX = self.plot.getViewBox().state
        xMin = float('%.2f' % rangeX['viewRange'][0][0])
        xMax = float('%.2f' % rangeX['viewRange'][0][1])
        self.setMinimumXLineEdit.setText(str(xMin))
        self.setMaximumXLineEdit.setText(str(xMax))


        b = self.manualXRadio.checkState()

        if bool(b) == True:
            self.setMinimumXLineEdit.setEnabled(True)
            self.setMaximumXLineEdit.setEnabled(True)

            self.setMinimumXLineEdit.returnPressed.connect(self.setNewXRange)
            self.setMaximumXLineEdit.returnPressed.connect(self.setNewXRange)

            self.autoXRadio.setChecked(False)


        elif bool(b) == False:
            self.setMinimumXLineEdit.setEnabled(False)
            self.setMaximumXLineEdit.setEnabled(False)

            self.autoXRadio.setChecked(True)

        if bool(self.lockRadio.checkState()) == True:
            self.setMinimumXLineEdit.setEnabled(False)
            self.setMaximumXLineEdit.setEnabled(False)
            xMin = self.lock_xMin
            xMax = self.lock_xMax
            self.setMinimumXLineEdit.setText(str(xMin))
            self.setMaximumXLineEdit.setText(str(xMax))

        self.configuration["plots"][self.plotNumber]["minXRange"] = xMin
        self.configuration["plots"][self.plotNumber]["maxXRange"] = xMax
        self.configuration["plots"][self.plotNumber]["manualX"] = (bool(b))

    def manualYRange(self):
        rangeY = self.plot.getViewBox().state
        yMin = float('%.2f' % rangeY['viewRange'][1][0])
        yMax = float('%.2f' % rangeY['viewRange'][1][1])
        self.setMinimumYLineEdit.setText(str(yMin))
        self.setMaximumYLineEdit.setText(str(yMax))

        b = self.manualYRadio.checkState()
        if bool(b) == True:
            self.setMinimumYLineEdit.setEnabled(True)
            self.setMaximumYLineEdit.setEnabled(True)

            self.setMinimumYLineEdit.returnPressed.connect(self.setNewYRange)
            self.setMaximumYLineEdit.returnPressed.connect(self.setNewYRange)

            self.autoYRadio.setChecked(False)

        elif bool(b) == False:
            self.setMinimumYLineEdit.setEnabled(False)
            self.setMaximumYLineEdit.setEnabled(False)
            self.autoYRadio.setChecked(True)

        if bool(self.lockRadio.checkState()) == True:
            self.setMinimumYLineEdit.setEnabled(False)
            self.setMaximumYLineEdit.setEnabled(False)
            yMin = self.lock_yMin
            yMax = self.lock_yMax
            self.setMinimumYLineEdit.setText(str(yMin))
            self.setMaximumYLineEdit.setText(str(yMax))


        self.configuration["plots"][self.plotNumber]["minYRange"] = yMin
        self.configuration["plots"][self.plotNumber]["maxYRange"] = yMax
        self.configuration["plots"][self.plotNumber]["manualY"] = (bool(b))

    def setNewXRange(self):
        xMin = float(self.setMinimumXLineEdit.text())
        xMax = float(self.setMaximumXLineEdit.text())
        self.plot.setXRange(xMin, xMax, padding=0)
        self.configuration["plots"][self.plotNumber]["minXRange"] = xMin
        self.configuration["plots"][self.plotNumber]["maxXRange"] = xMax

    def setNewYRange(self):
        yMin = float(self.setMinimumYLineEdit.text())
        yMax = float(self.setMaximumYLineEdit.text())
        self.plot.setYRange(yMin, yMax, padding=0)
        self.configuration["plots"][self.plotNumber]["minYRange"] = yMin
        self.configuration["plots"][self.plotNumber]["maxYRange"] = yMax

    def lockCheckBox(self):

        b = self.lockRadio.checkState()
        if bool(b) == True:
            #self.autoRadio.setChecked(False)
            self.lock_xMin = copy.deepcopy(self.configuration["plots"][self.plotNumber]["minXRange"])
            self.lock_xMax = copy.deepcopy(self.configuration["plots"][self.plotNumber]["maxXRange"])
            self.lock_yMin = copy.deepcopy(self.configuration["plots"][self.plotNumber]["minYRange"])
            self.lock_yMax = copy.deepcopy(self.configuration["plots"][self.plotNumber]["maxYRange"])

            self.plot.sigXRangeChanged.disconnect(self.manualXRange)
            self.plot.sigYRangeChanged.disconnect(self.manualYRange)
            self.setMinimumXLineEdit.setEnabled(False)
            self.setMaximumXLineEdit.setEnabled(False)
            self.setMinimumYLineEdit.setEnabled(False)
            self.setMaximumYLineEdit.setEnabled(False)

        elif bool(b) == False:
            self.plot.sigXRangeChanged.connect(self.manualXRange)
            self.plot.sigYRangeChanged.connect(self.manualYRange)
            if bool(self.manualXRadio.checkState()) == True:
                self.setMinimumXLineEdit.setEnabled(True)
                self.setMaximumXLineEdit.setEnabled(True)
            if bool(self.manualYRadio.checkState()) == True:
                self.setMinimumYLineEdit.setEnabled(True)
                self.setMaximumYLineEdit.setEnabled(True)


        self.configuration["plots"][self.plotNumber]["lock"] = bool(b)

    def setConfiguration(self, configuration):
        self.configuration = configuration
        
        self.logXRadio.setChecked(self.configuration["plots"][self.plotNumber]["logXAxis"])
        self.logYRadio.setChecked(self.configuration["plots"][self.plotNumber]["logYAxis"])
        self.invertXRadio.setChecked(self.configuration["plots"][self.plotNumber]["invertX"])
        self.invertYRadio.setChecked(self.configuration["plots"][self.plotNumber]["invertY"])
        self.gridRadio.setChecked(self.configuration["plots"][self.plotNumber]["setGrid"])
        self.gridXRadio.setChecked(self.configuration["plots"][self.plotNumber]["setGridX"])
        self.gridYRadio.setChecked(self.configuration["plots"][self.plotNumber]["setGridY"])
        self.alphaSlider.setValue(self.configuration["plots"][self.plotNumber]["alpha"])
        self.opacitySlider.setValue(self.configuration["plots"][self.plotNumber]["opacity"])

        xMin = copy.deepcopy(self.configuration['plots'][self.plotNumber]["minXRange"])
        xMax = copy.deepcopy(self.configuration['plots'][self.plotNumber]["maxXRange"])
        yMin = copy.deepcopy(self.configuration['plots'][self.plotNumber]["minYRange"])
        yMax = copy.deepcopy(self.configuration['plots'][self.plotNumber]["maxYRange"])
        self.manualXRadio.setChecked(self.configuration['plots'][self.plotNumber]["manualX"])
        self.manualYRadio.setChecked(self.configuration['plots'][self.plotNumber]["manualY"])
        self.plot.setXRange(xMin, xMax, padding=0)
        self.plot.setYRange(yMin, yMax, padding = 0)

        self.autoRadio.setChecked(self.configuration['plots'][self.plotNumber]["auto"])
        self.autoXRadio.setChecked(self.configuration['plots'][self.plotNumber]["autoX"])
        self.autoYRadio.setChecked(self.configuration['plots'][self.plotNumber]["autoY"])


        self.lockRadio.setChecked(self.configuration['plots'][self.plotNumber]["lock"])

        self.setChannelsModel(self.configuration["plots"][self.plotNumber]["channels"])

        self.fillCommonChannelComboBox()
        self.createLines()

        self.darkMode = self.configuration["global"]["darkMode"]
        self.setDarkMode()

