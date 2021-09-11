from PySide6.QtCore import QObject, Signal, Slot, QSettings, QTimer, QThread
from camlab.models import DeviceTableModel, AcquisitionTableModel
from camlab.device import Device
import copy
import logging
import ruamel.yaml
import os
import sys
from labjack import ljm
import numpy as np

log = logging.getLogger(__name__)

class Assembly(QObject):
    plotDataChanged = Signal(np.ndarray)
    samplesCount = Signal(int)

    def __init__(self):
        super().__init__()
        self.plotData = []
        self.time = 0.00
        self.count = 0
        self.offsets = np.asarray((0, 0, 0, 0, 0, 0, 0, 0))
        self.newData = []

    @Slot(np.ndarray)
    def updateNewData(self, data):
        if np.shape(self.newData)[0] > 0:
            self.newData = np.vstack((self.newData, data))
        else:
            self.newData = data

    def updatePlotData(self):
        if np.shape(self.newData)[0] > 0: 
            dt = 0.001
            newData = self.newData
            self.newData = []
            numTimesteps = np.shape(newData)[0]
            timesteps = np.linspace(0, (numTimesteps-1)*dt, numTimesteps)
            timesteps += self.time
            self.count += numTimesteps
            self.samplesCount.emit(self.count)
            newLines = np.column_stack((timesteps, newData-self.offsets))
            if np.shape(self.plotData)[0] > 0:
                self.plotData = np.vstack((self.plotData, newLines)) 
            else: 
                self.plotData = newLines
            self.plotDataChanged.emit(self.plotData)
            self.time += numTimesteps*dt 

    def clearPlotData(self):
        self.plotData = self.plotData[-1,:]

    def autozero(self):
        self.offsets = np.average(self.plotData[-10:,1:], axis=0)
        print(self.offsets)

class Manager(QObject):
    updateUI = Signal(dict)
    configurationChanged = Signal(dict)
    addAcquisitionTable = Signal(str)
    updateAcquisitionTabs = Signal()
    clearAcquisitionTabs = Signal()
    startTimers = Signal()
    endTimers = Signal()

    def __init__(self):
        super().__init__()
        self.configuration = {}
        self.acquisitionModels = {}
        self.acquisitionTables = {}

        self.defaultAcquisitionTable = [
            {"channel": "AIN0", "name": "Ch_1", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN1", "name": "Ch_2", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN2", "name": "Ch_3", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN3", "name": "Ch_4", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN4", "name": "Ch_5", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN5", "name": "Ch_6", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN6", "name": "Ch_7", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
            {"channel": "AIN7", "name": "Ch_8", "unit": "V", "slope": 1.0, "offset": 0.00, "connect": False, "autozero": True},
        ]

        # Instantiate the model for the device list.   
        self.deviceTableModel = DeviceTableModel()

        # Load last used configuration file.
        log.info("Finding previous YAML file location from QSettings.")
        self.settings = QSettings("CamLab", "Settings")
        self.settings.sync()
        self.findConfigurationPath()
        if self.configurationPath != None:
            self.loadConfiguration(self.configurationPath)
        else:
            self.initialiseDefaultConfiguration()

        # Create assembly thread.
        self.assembly = Assembly()
        log.info("Assembly thread instantiated.")
        self.assemblyThread = QThread()
        log.info("Assembly thread created.")
        self.assembly.moveToThread(self.assemblyThread)
        self.assemblyThread.start()
        log.info("Assembly thread started.")

        # Create device thread.
        aAddresses = [46000, 46002, 46004, 46006, 46008, 46010, 46012, 46014]
        dt = ljm.constants.FLOAT32
        aDataTypes = [dt, dt, dt, dt, dt, dt, dt, dt]
        self.device = Device(470019449, 1, aAddresses, aDataTypes)
        log.info("Device instance instantiated.")
        self.deviceThread = QThread()
        log.info("Device thread created.")
        self.device.moveToThread(self.deviceThread)
        self.deviceThread.start()
        log.info("Device thread started.")

        # Connections.
        self.device.emitData.connect(self.assembly.updateNewData)

    def loadDevicesFromConfiguration(self):
        # Find all devices listed in the configuration file.
        if "devices" in self.configuration:
            for device in self.configuration["devices"].keys():
                deviceInformation = {}
                deviceInformation["connect"] = True
                deviceInformation["name"] = device
                deviceInformation["id"] = self.configuration["devices"][device]["id"]
                deviceInformation["connection"] = self.configuration["devices"][device]["connection"]
                deviceInformation["address"] = self.configuration["devices"][device]["address"]
                deviceInformation["status"] = False
                # Try to connect to each device using the ID.
                try:
                    # If the connection is successful, set the device status to true.
                    handle = ljm.open(7, int(deviceInformation["connection"]), int(deviceInformation["id"]))
                    name = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                    ljm.close(handle)
                    deviceInformation["status"] = True
                except ljm.LJMError:
                    # Otherwise log the exception and set the device status to false.
                    ljme = sys.exc_info()[1]
                    log.warning(ljme) 
                except Exception:
                    e = sys.exc_info()[1]
                    log.warning(e)
                self.deviceTableModel.appendRow(deviceInformation)
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.addAcquisitionTable.emit(name)
            log.info("Configuration loaded.")
        self.updateAcquisitionTabs.emit()
        self.updateUI.emit(self.configuration)


    def findDevices(self):
        """Method to find all available devices and return an array of connection properties.
        USB connections are prioritised over Ethernet and WiFi connections to minimise jitter."""
        
        # Clear all tables and re-load the current configuration.
        self.deviceTableModel.clearData()
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.clearAcquisitionTabs.emit()
        self.loadDevicesFromConfiguration()

        # Get a list of already existing devices.
        existingDevices = self.deviceTableModel._data
        ID_Existing = []
        for device in existingDevices:
            ID_Existing.append(device["id"])

        # Check for USB connectons first and add to available device list if not already enabled.
        log.info("Scanning for additional USB devices.")
        info = ljm.listAll(7, 1)
        devicesUSB = info[0]
        connectionType = info[2]
        ID_USB = info[3]
        IP = info[4]
        for i in range(devicesUSB):
            if ID_USB[i] not in ID_Existing:
                deviceInformation = {}
                deviceInformation["connect"] = False
                handle = ljm.open(7, 1, ID_USB[i])
                deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                ljm.close(handle)
                deviceInformation["id"] = ID_USB[i]
                deviceInformation["connection"] = connectionType[i]
                deviceInformation["address"] = "N/A"
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)
                
                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 

                # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.addAcquisitionTable.emit(name)
                self.updateAcquisitionTabs.emit()
                self.updateUI.emit(self.configuration)
        log.info("Found " + str(devicesUSB) + " additional USB device(s).")

        # Check TCP and add to list if not already in available device list.
        log.info("Scanning for TCP devices.")
        info = ljm.listAll(7, 2)
        numDevicesTCP = 0
        devicesTCP = info[0]
        connectionType = info[2]
        ID_TCP = info[3]
        IP = info[4]
        for i in range(devicesTCP):
            if ID_TCP[i] not in ID_USB and ID_TCP[i] not in ID_Existing:
                numDevicesTCP += 1
                deviceInformation = {}
                deviceInformation["connect"] = False
                # Name string requires a brief connection.
                handle = ljm.open(7, 2, ID_TCP[i])
                deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                ljm.close(handle)
                deviceInformation["id"] = ID_TCP[i]
                deviceInformation["connection"] = connectionType[i]
                deviceInformation["address"] =  ljm.numberToIP(IP[i])
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)

                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 

                # Update acquisition table models and add TableView to TabWidget by emitting the appropriate Signal.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.addAcquisitionTable.emit(name)
                self.updateAcquisitionTabs.emit()
                self.updateUI.emit(self.configuration)
        log.info("Found " + str(numDevicesTCP) + " additional TCP device(s).")

    def configure(self):
        self.endTimers.emit()
        log.info("Configuring devices.")

    def run(self):
        self.startTimers.emit()
        log.info("Started acquisition and control.")

    def refreshDevices(self):
        log.info("Refreshing devices.")
        self.findDevices()

    def findConfigurationPath(self):
        if self.settings.value("configurationPath") == None:
            self.configurationPath = None
            log.info("No configuration file path found. Using defaults.")
        else:
            self.configurationPath = self.settings.value("configurationPath")
            log.info("Configuration file path found at " + str(self.configurationPath))
    
    def initialiseDefaultConfiguration(self):
        self.configuration = {}
        self.configuration["global"] = {
            "darkMode": True,
            "controlRate": 1000.00,
            "acquisitionRate": 100.00,
            "averageSamples": 10,
            "path": "/data",
            "filename": "junk"
            }
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def loadConfiguration(self, loadConfigurationPath):
        # Clear device table prior to loading devices from selected configuration.
        self.configuration = {}
        self.deviceTableModel.clearData()
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.clearAcquisitionTabs.emit()
        try:    
            log.info("Loading configuration from " + loadConfigurationPath + " and saving location to QSettings.")
            with open(loadConfigurationPath, "r") as file:
                self.configuration = ruamel.yaml.load(file, Loader=ruamel.yaml.Loader) 
                log.info("Configuration file parsed.")
                self.configurationPath = loadConfigurationPath
                self.configurationChanged.emit(self.configuration)    
                self.settings.setValue("configurationPath", loadConfigurationPath)
                self.loadDevicesFromConfiguration()
        except FileNotFoundError:
            log.warning("Previous configuration file not found.")  
            self.initialiseDefaultConfiguration()

    @Slot(str)
    def saveConfiguration(self, saveConfigurationPath):
        # Make deep copies of the configuration and filter out devices that are not enabled in the device table.
        configuration = copy.deepcopy(self.configuration)
        devices = copy.deepcopy(self.configuration["devices"])
        enabledDevices = self.deviceTableModel.enabledDevices()
        enabledDeviceList = []
        for device in enabledDevices:
            enabledDeviceList.append(device["name"])
        for device in configuration["devices"]:
            if device not in enabledDeviceList:
                devices.pop(device)
        configuration["devices"] = devices

        # Save the yaml file and its path to QSettings.
        with open(saveConfigurationPath, "w") as file:
            yaml = ruamel.yaml.YAML()
            yaml.dump(configuration, file)
        self.settings.setValue("configurationPath", saveConfigurationPath)
        log.info("Saved configuration saved at " + saveConfigurationPath)

    @Slot()
    def clearConfiguration(self):
        self.configuration = {}
        self.loadConfiguration("/NoneExistentFile.yaml")
        self.updateUI.emit(self.configuration)
        # self.findDevices()
        log.info("Cleared configuration by loading defaults.") 

    @Slot(str)
    def updateAcquisitionRate(self, newAcquisitionRate):
        self.configuration["global"]["acquisitionRate"] = float(newAcquisitionRate)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New acquisition rate = " + newAcquisitionRate + " Hz")
        
    @Slot(str)
    def updateControlRate(self, newControlRate):
        self.configuration["global"]["controlRate"] = float(newControlRate)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New control rate = " + newControlRate + " Hz")

    @Slot(str)
    def updateAverageSamples(self, newAverageSamples):
        self.configuration["global"]["averageSamples"] = int(newAverageSamples)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New average samples = " + newAverageSamples)
        
    @Slot(str)
    def updatePath(self, newPath):
        self.configuration["global"]["path"] = str(newPath)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New path = " + newPath)

    @Slot(str)
    def updateFilename(self, newFilename):
        self.configuration["global"]["filename"] = str(newFilename)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New filename = " + newFilename)

    @Slot(bool)
    def updateDarkMode(self, newDarkMode):
        self.configuration["global"]["darkMode"] = newDarkMode
        self.configurationChanged.emit(self.configuration) 
        # log.info("New darkMode = " + str(newDarkMode))


    

    