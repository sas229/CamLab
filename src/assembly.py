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
        """Assembly init."""
        super().__init__()
        self.plotData = []
        self.time = 0.00
        self.count = 0
        self.fileCount = 1
        self.data = {}
        self.offsets = []
        self.enabledDevices = []
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.arucoParams = cv2.aruco.DetectorParameters_create()
        self.index_start_thinout = []
        self.index_end_thinout = []
        self.points_threshold_thin_out = 5000

    def define_settings(self, rate, skip, average):
        """Method to define basic global settings."""
        self.skip = int(skip)
        self.average = int(average)
        self.DeltaT = (1/rate)*self.skip
        log.info("Assembly thread settings initialised.")

    def set_filename(self, path, filename, date, timestart, ext):
        """Method to set the output filename."""
        self.path = path
        self.filename = filename
        self.date = date
        self.timestart = timestart
        self.filepath = path + "/" + filename + "_" + date + "_" + timestart + "_1" + ext
        log.info("Filename set.")

    def write_header(self, header):
        """Method to write the header to the output file."""
        self.file = open(self.filepath, 'w+')
        self.file.write(header)
        self.file.close()
        self.file = open(self.filepath, 'ab')
        log.info("Header written.")

    @Slot(str, np.ndarray)
    def update_new_data(self, name, data):
        """Method to add data to numpy array for the sending device."""
        if np.shape(self.data[name])[0] > 0:
            self.data[name] = np.vstack((self.data[name], data))
        else:
            self.data[name] = data

    @Slot()
    def update_output_data(self):
        """Method to update the output data to save to file and to generate the plots."""
        # Compute the minumum number of rows in the data item within each device dict.
        numTimesteps = []
        if len(self.enabledDevices) > 0:
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

                # If skip value greater than 1, skip values.
                if self.skip > 1:
                    saveData = saveData[::self.skip,:].copy()
                    plotData = plotData[::self.skip, :].copy()
                
                # Add timestamp.
                n = np.shape(saveData)[0]
                timesteps = np.arange(0, n, 1)*self.DeltaT
                timesteps += self.time
                saveData = np.column_stack((timesteps, saveData))
                plotData = np.column_stack((timesteps, plotData))

                # New part for thinning out data
                if len(np.shape(self.plotData)) > 1:
                    tot_points = ((np.shape(self.plotData)[1]-1) * len(self.plotData))
                    if tot_points >= self.points_threshold_thin_out:
                        plotData = self.thinout_plotData()
                        plotData_copy = np.array(self.plotData.copy())
                        rows_to_delete = range(self.index_start_thinout[-1],len(plotData_copy))
                        plotData_copy = np.delete(plotData_copy, rows_to_delete, axis=0)
                        plotData_copy = plotData_copy.tolist()
                        plotData_copy.append(plotData)
                        plotData_copy = np.vstack(plotData_copy)
                        self.plotData = plotData_copy
                    else:
                        self.plotData = np.vstack((self.plotData, plotData))

                # Save data.
                np.savetxt(self.file, saveData, fmt='%8.3f', delimiter='\t', newline='\n')
                
                # Plot data.
                if np.shape(self.plotData)[0] == 0:
                    self.plotData = plotData
                self.time += n*self.DeltaT
                self.count += numTimesteps
                self.plotDataChanged.emit(self.plotData)
    
    def thinout_plotData(self):
        if self.index_start_thinout == []:
            self.index_start_thinout.append(0)
            data_to_thin_out = np.array(self.plotData).copy()
            proportion_data_retained = 0.01
            skip_rate = int(round(proportion_data_retained*self.points_threshold_thin_out))
            thinned_out_data = data_to_thin_out[::skip_rate, :]
            self.index_end_thinout.append(len(thinned_out_data))
            thinned_out_data = thinned_out_data.tolist()
            thinned_out_data = np.vstack(thinned_out_data)
        else:
            self.index_start_thinout.append(self.index_end_thinout[-1])
            data_to_thin_out = np.array(self.plotData[self.index_start_thinout[-1]:,:]).copy()
            proportion_data_retained = 0.01
            skip_rate = int(round(proportion_data_retained*self.points_threshold_thin_out))
            thinned_out_data = data_to_thin_out[::skip_rate, :]
            self.index_end_thinout.append(self.index_start_thinout[-1] + len(thinned_out_data))
            thinned_out_data = thinned_out_data.tolist()
            thinned_out_data = np.vstack(thinned_out_data)
        return thinned_out_data

    @Slot(str, np.ndarray)
    def save_image(self, image_name, image_array):
        """Method to save image with given filename prepended with output file details."""
        filepath = self.path + "/" + self.filename + "_" + self.date + "_" + self.timestart + "_" + image_name
        # self.detect_aruco(image_array)
        img = Image.fromarray(image_array)
        img.save(filepath, "JPEG")
        
    def detect_aruco(self, image_array):
        """Method to detect ArUco markers in image."""
        corners, ids, rejected = cv2.aruco.detectMarkers(image_array, self.arucoDict,
            parameters=self.arucoParams)
        marker_image = cv2.aruco.drawDetectedMarkers(image_array, corners)
        print(len(corners))
        return marker_image

    def clear_all_data(self):
        """Method to clear all data."""
        self.data = {}
        self.plotData = []
        self.time = 0.00
        self.count = 0

    def close_file(self):
        """Method to close file."""
        self.file.close()
    
    @Slot()
    def clear_plot_data(self):
        """Method to clear plot data."""
        self.plotData = self.plotData[-1,:]
        log.info("Plots cleared.")

    @Slot()
    def autozero(self):
        """Method to command devices to execute autozero function."""
        self.autozeroDevices.emit()
        log.info("Autozero signal sent by assembly.")

    @Slot()
    def new_file(self):
        """Method to start logging in a new file."""
        # Close current file.
        self.file.close()
        
        # Modify the filename and append fileCount.
        self.fileCount += 1
        filepath = self.filepath[:-6] + "_" + str(self.fileCount) + ".txt"
        
        # Open a new file.
        self.file = open(filepath,'ab')

    @Slot(list)
    def create_data_arrays(self, enabledDevices):
        """Method to create data arrays depending on enabled devices."""
        self.enabledDevices = enabledDevices
        self.data = {}
        for device in self.enabledDevices:
            if device["type"] == "Hub":
                name = device["name"]
                self.data[name] = np.array([])
        log.info("Output arrays created.")