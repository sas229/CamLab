from PySide6.QtCore import QObject, Signal, Slot, QDate, Qt
import logging
import numpy as np
from time import time
from scipy.ndimage import uniform_filter1d
from datetime import datetime

log = logging.getLogger(__name__)

class Assembly(QObject):
    plotDataChanged = Signal(np.ndarray)
    autozeroDevices = Signal()
    
    def __init__(self):
        super().__init__()
        self.plotData = []
        self.time = 0.00
        self.count = 0
        self.fileCount = 1
        self.data = {}
        self.offsets = []

    def settings(self, rate, skip, average):
        self.skip = int(skip)
        self.average = int(average)
        self.DeltaT = (1/rate)*self.skip
        log.info("Assembly thread settings initialised.")

    def setFilename(self, path, filename, date, timestart, ext):
        self.path = path
        self.filename = filename
        self.date = date
        self.timestart = timestart
        self.filepath = path + "/" + filename + "_" + date + "_" + timestart + "_1" + ext
        log.info("Filename set.")

    def writeHeader(self, header):
        self.file = open(self.filepath, 'w+')
        self.file.write(header)
        self.file.close()
        self.file = open(self.filepath, 'ab')
        log.info("Header written.")

    @Slot(str, np.ndarray)
    def updateNewData(self, name, data):
        # Add data to numpy array for the sending device.
        if np.shape(self.data[name])[0] > 0:
            self.data[name] = np.vstack((self.data[name], data))
        else:
            self.data[name] = data

    @Slot()
    def updatePlotData(self):
        # Compute the minumum number of rows in the data item within each device dict.
        numTimesteps = []
        for device in self.enabledDevices:
            name = device["name"]
            numTimesteps.append(np.shape(self.data[name])[0])
        numTimesteps = min(numTimesteps)
        numTimesteps = numTimesteps - (numTimesteps % self.skip)

        # Pop numTimesteps of data from each data object onto assembledData if more than 0.
        if numTimesteps > 0:
            deviceData = []
            count = 0
            for device in self.enabledDevices:
                name = device["name"]
                deviceData = self.data[name][0:numTimesteps,:]
                self.data[name] = np.delete(self.data[name], range(numTimesteps), axis=0)
                if count == 0:
                    # assembledData = np.column_stack((timesteps, deviceData))
                    assembledData = deviceData.copy()
                else:
                    assembledData = np.column_stack((assembledData, deviceData))
                count += 1

            # Perform averaging.
            processedData = assembledData
            if self.average > 1:
                processedData = uniform_filter1d(processedData, size=self.average, axis=0, mode='nearest')
            if self.skip > 1: 
                processedData = processedData[::self.skip,:].copy()

            # Add timestamp.
            n = np.shape(processedData)[0]
            timesteps = np.arange(0, n, 1)*self.DeltaT
            timesteps += self.time
            processedData = np.column_stack((timesteps, processedData))

            # Add save data functionality in here.
            np.savetxt(self.file, processedData, fmt='%8.3f', delimiter='\t', newline='\n')

            if np.shape(self.plotData)[0] > 0:
                self.plotData = np.vstack((self.plotData, processedData)) 
            else: 
                self.plotData = processedData
            self.time += n*self.DeltaT
            self.count += numTimesteps
            self.plotDataChanged.emit(self.plotData)

    def clearAllData(self):
        self.data = {}
        self.plotData = []
        self.time = 0.00
        self.count = 0

    def closeFile(self):
        self.file.close()
    
    @Slot()
    def clearPlotData(self):
        self.plotData = self.plotData[-1,:]
        log.info("Plots cleared.")

    @Slot()
    def autozero(self):
        self.autozeroDevices.emit()
        log.info("Autozero signal sent by assembly.")

    @Slot()
    def newFile(self):
        # Close current file.
        self.file.close()
        
        # Modify the filename and append fileCount.
        self.fileCount += 1
        filepath = self.filepath[:-6] + "_" + str(self.fileCount) + ".txt"
        
        # Open a new file.
        self.file = open(filepath,'ab')

    @Slot(list)
    def createDataArrays(self, enabledDevices):
        self.enabledDevices = enabledDevices
        self.data = {}
        for device in self.enabledDevices:
            name = device["name"]
            self.data[name] = np.array([])
        log.info("Output arrays created.")