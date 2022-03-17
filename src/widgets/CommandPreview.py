from PySide6.QtWidgets import QVBoxLayout, QGroupBox
from PySide6.QtCore import Slot
import numpy as np
import src.local_pyqtgraph.pyqtgraph as pg
from scipy import signal
import re
import os

class CommandPreview(QGroupBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.preview = pg.PlotWidget(self)
        styles = self.setStyle()
        self.preview.setMenuEnabled(enableMenu=False)
        self.updateColours()
        self.dT = 0.01
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.preview)
        self.setLayout(self.layout)
        self.preview.setLabel('left', 'Value', **styles)
        self.preview.setLabel('bottom', 'Time', units = 's', **styles)

    def updateColours(self):
        self.preview.setBackground(os.environ['QTMATERIAL_SECONDARYLIGHTCOLOR'])
        self.preview.getAxis('left').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])
        self.preview.getAxis('bottom').setTextPen(os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'])

    @Slot(np.ndarray, np.ndarray, str)
    def updatePreview(self, time, values, unit):
        self.preview.clear()
        self.preview.plot(time, values, pen ='r')
        styles = self.setStyle()
        self.preview.setLabel('left', 'Value', units = unit, **styles)

    @Slot()
    def clearPreview(self):
        self.preview.clear()
        styles = self.setStyle()
        self.preview.setLabel('left', 'Value', **styles)
        self.setStyle()

    def setStyle(self):
        return {'color': os.environ['QTMATERIAL_SECONDARYTEXTCOLOR'], 'font-size': '16px'}

    @Slot()
    def previewCommand(self, command):
        self.command = command
        if self.command["variable"] == "Position":
            unit = "mm"
        elif self.command["variable"] == "Feedback":
            unit = "N"
        elif self.command["variable"] == "Speed":
            unit = "mm/s"
        if self.command["command"] == "Ramp":
            amplitude = self.command["amplitude"]
            rate = self.command["rate"]
            elapsedTime = amplitude/rate
            time = np.arange(0, elapsedTime, self.dT)
            values = time*rate
            self.updatePreview(time, values, unit)
        elif self.command["command"] == "Demand":
            amplitude = self.command["amplitude"]
            time = np.asarray([-1, 0, 0, 1])
            values = np.asarray([0, 0, amplitude, amplitude])
            self.updatePreview(time, values, unit)
        elif self.command["command"] == "Triangle":
            amplitude = self.command["amplitude"]
            rate = self.command["rate"]
            offset = self.command["offset"]
            repeat = self.command["repeat"]
            elapsedTime = (abs(amplitude)/rate)*2*repeat
            time = np.arange(0, elapsedTime, self.dT)
            values = signal.sawtooth(t=np.pi*time*1/(abs(amplitude)/rate), width=0.5)*amplitude/2 + amplitude/2 - np.sign(amplitude)*offset
            if offset != 0.0:
                firstZeroIndex = np.where(values >= 0)[0][0]
                begin = values[firstZeroIndex:]
                end = values[:firstZeroIndex]
                values = np.hstack((begin, end))
            self.updatePreview(time, values, unit)
        elif self.command["command"] == "Sine":
            amplitude = self.command["amplitude"]
            rate = self.command["rate"]
            offset = self.command["offset"]
            repeat = self.command["repeat"]
            elapsedTime = (abs(amplitude)/rate)*2*repeat
            time = np.arange(0, elapsedTime, self.dT)
            values = np.sin(np.pi*time*1/(abs(amplitude)/rate))*amplitude/2 + offset
            if offset != 0.0:
                if offset < 0.0:
                    firstZeroIndex = np.where(values >= 0)[0][0]
                elif offset > 0.0:
                    firstZeroIndex = np.where(values <= 0)[0][0]
                begin = values[firstZeroIndex:]
                end = values[:firstZeroIndex]
                values = np.hstack((begin, end))
            self.updatePreview(time, values, unit)