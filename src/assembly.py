from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
from time import time

log = logging.getLogger(__name__)

class Assembly(QObject):
    plotDataChanged = Signal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.plotData = []
        self.time = 0.00
        self.count = 0
        self.offsets = np.asarray((0, 0, 0, 0, 0, 0, 0, 0))
        self.dt = 0.01

        self.data = {}

    @Slot(str, np.ndarray)
    def updateNewData(self, name, data):
        # Add data to numpy array for the sending device.
        if np.shape(self.data[name])[0] > 0:
            self.data[name] = np.vstack((self.data[name], data))
        else:
            self.data[name] = data
        # print(name + str(np.shape(self.data[name])))

    @Slot()
    def updatePlotData(self):
        # Compute the minumum number of rows in the data item within each device dict.
        numTimesteps = []
        for device in self.enabledDevices:
            name = device["name"]
            numTimesteps.append(np.shape(self.data[name])[0])
        # print(numTimesteps)
        numTimesteps = min(numTimesteps)
        
        # Pop numTimesteps of data from each data object onto assembledData if more than 0.
        if numTimesteps > 0:
            timesteps = np.linspace(0, (numTimesteps-1)*self.dt, numTimesteps)
            timesteps += self.time
            deviceData = []
            count = 0
            for device in self.enabledDevices:
                name = device["name"]
                # print(name)
                deviceData = self.data[name][0:numTimesteps,:]
                # print(np.shape(deviceData))
                self.data[name] = np.delete(self.data[name], range(numTimesteps), axis=0)
                # print(np.shape(self.data[name])[0])
                if count == 0:
                    assembledData = np.column_stack((timesteps, deviceData))
                else:
                    assembledData = np.column_stack((assembledData, deviceData))
                count += 1
            # Add save data functionality in here.
            if np.shape(self.plotData)[0] > 0:
                self.plotData = np.vstack((self.plotData, assembledData)) 
            else: 
                self.plotData = assembledData
            # print(np.shape(self.plotData))
            self.time += numTimesteps*self.dt 
            self.count += numTimesteps
            self.plotDataChanged.emit(self.plotData)
            # print("Signal emitted...")

    def clearAllData(self):
        self.data = {}
        self.plotData = []
        self.time = 0.00
        self.count = 0

    @Slot()
    def clearPlotData(self):
        self.plotData = self.plotData[-1,:]

    @Slot()
    def autozero(self):
        self.offsets = np.average(self.plotData[-10:,1:], axis=0)

    @Slot(list)
    def createDataArrays(self, enabledDevices):
        self.enabledDevices = enabledDevices
        self.data = {}
        for device in self.enabledDevices:
            name = device["name"]
            self.data[name] = np.array([])
        log.info("Output arrays created.")
