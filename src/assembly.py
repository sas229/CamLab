from PySide6.QtCore import QObject, Signal, Slot, QDate, Qt
import logging
import numpy as np
from time import time
from scipy.ndimage import uniform_filter1d
from datetime import datetime
from PIL import Image
import cv2

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
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

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

        # Pop numTimesteps of data from each data object onto saveData and plotData if more than 0.
        if numTimesteps > 0:
            deviceData = []
            count = 0
            for device in self.enabledDevices:
                name = device["name"]
                deviceData = self.data[name][0:numTimesteps,:]
                self.data[name] = np.delete(self.data[name], range(numTimesteps), axis=0)
                
                # Perform averaging of data if appropriate.
                processedData = deviceData
                if device["type"] == "Hub":
                    if self.average > 1:
                        processedData = uniform_filter1d(processedData, size=self.average, axis=0, mode='nearest')

                if count == 0:
                    if device["type"] == "Camera":
                        saveData = processedData[:,0].copy()
                        plotData = processedData[:,1].copy()
                    else:
                        saveData = processedData.copy()
                        plotData = processedData.copy()
                else:
                    if device["type"] == "Camera":
                        saveData = np.column_stack((saveData, processedData[:,0]))
                        plotData = np.column_stack((plotData, processedData[:,1]))
                    else:
                        saveData = np.column_stack((saveData, processedData))
                        plotData = np.column_stack((plotData, processedData))
                count += 1

            # # If skip value greater than 0, skip values.
            # if self.skip > 1: 
            #     saveData = saveData[::self.skip,:].copy()

            # Add timestamp.
            n = np.shape(saveData)[0]
            timesteps = np.arange(0, n, 1)*self.DeltaT
            timesteps += self.time
            saveData = np.column_stack((timesteps, saveData))
            plotData = np.column_stack((timesteps, plotData))

            # Save data.
            np.savetxt(self.file, saveData, fmt='%8.3f', delimiter='\t', newline='\n')
            
            # Plot data.
            if np.shape(self.plotData)[0] > 0:
                self.plotData = np.vstack((self.plotData, plotData)) 
            else: 
                self.plotData = plotData
            self.time += n*self.DeltaT
            self.count += numTimesteps
            self.plotDataChanged.emit(self.plotData)
    
    @Slot(str, np.ndarray)
    def save_image(self, image_name, image_array):
        """Save image with given filename prepended with output file details."""
        filepath = self.path + "/" + self.filename + "_" + self.date + "_" + self.timestart + "_" + image_name
        # self.detect_aruco(image_array)
        img = Image.fromarray(image_array)
        img.save(filepath, "JPEG")
        
    def detect_aruco(self, image_array):
        corners, ids, rejected = cv2.aruco.detectMarkers(image_array, self.arucoDict,
            parameters=self.arucoParams)
        marker_image = cv2.aruco.drawDetectedMarkers(image_array, corners)
        print(len(corners))
        return marker_image

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