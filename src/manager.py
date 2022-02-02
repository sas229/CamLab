from PySide6.QtCore import QObject, Signal, Slot, QSettings, QThread
from src.models import DeviceTableModel, AcquisitionTableModel, ChannelsTableModel, ControlTableModel
from src.device import Device
from src.assembly import Assembly
from src.timing import Timing
import copy
import logging
import ruamel.yaml
import os
import sys
from labjack import ljm
import numpy as np
import time
import re

log = logging.getLogger(__name__)

class Manager(QObject):
    updateUI = Signal(dict)
    configurationChanged = Signal(dict)
    deviceConfigurationAdded = Signal(str, list)
    clearDeviceConfigurationTabs = Signal()
    closePlots = Signal()
    addControlTable = Signal(str, list)
    updateDeviceConfigurationTab = Signal()
    removeWidget = Signal(str)
    plotWindowChannelsUpdated = Signal()
    existingPlotsFound = Signal()

    def __init__(self):
        super().__init__()
        self.configuration = {}
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.controlModels = {}
        self.devices = {}
        self.deviceThreads = {}
        self.refreshing = False
        self.deviceList = []
        self.j, self.k = 0, 4
        

        # Defaults.
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
        self.defaultControlTable = [
            {"channel": "C1", "enable": False, "type": 0, "control": 0, "feedback": 0},
            {"channel": "C2", "enable": False, "type": 0, "control": 0, "feedback": 0}
        ]
        self.controlModeList = ['Analogue', 'Digital']
        self.controlActuatorList = ['Linear Actuator', 'Rotary Actuator', 'Pressure Pump']
        self.defaultFeedbackChannel = ['N/A']

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
        log.info("Assembly instance created.")
        self.assemblyThread = QThread(parent=self)
        log.info("Assembly thread created.")
        self.assembly.moveToThread(self.assemblyThread)
        self.assemblyThread.start()
        log.info("Assembly thread started.")

        # Create timing thread.
        self.timing = Timing()
        log.info("Timing instance created.")
        self.timingThread = QThread(parent=self)
        log.info("Timing thread created.")
        self.timing.moveToThread(self.timingThread)
        self.timingThread.start()
        log.info("Timing thread started.")

    def createDeviceThreads(self):
        log.info("Creating device threads.")
        self.devices = {}
        self.deviceThreads = {}
        enabledDevices = self.deviceTableModel.enabledDevices()

        # Create output arrays in assembly thread.
        self.assembly.createDataArrays(enabledDevices)

        # For each device set the acuisition array and execute in a separate thread.
        for device in enabledDevices:
            name = device["name"]
            id = device["id"]
            connection = device["connection"]
            
            # Generate addresses for acqusition.
            enabledChannels, enabledNames, enabledUnits = self.acquisitionModels[name].enabledChannels()
            aAddresses = []
            aDataTypes = []
            dt = ljm.constants.FLOAT32
            for channel in enabledChannels:
                address = int(re.findall(r'\d+', channel)[0])*2 # Multiply by two to get correct LJ address for AIN.
                aAddresses.append(address)
                aDataTypes.append(dt)
            controlRate = self.configuration["global"]["controlRate"]

            # Create device instance and move to thread.
            self.devices[name] = Device(name, id, connection, aAddresses, aDataTypes, controlRate)
            log.info("Device instance created for device named " + name + ".")
            self.deviceThreads[name] = QThread(parent=self)
            log.info("Device thread created for device named " + name + ".")
            self.devices[name].moveToThread(self.deviceThreads[name])
            self.deviceThreads[name].start()
            log.info("Device thread started for device named " + name + ".")

            # Emit signal to connect sample timer to slot for the current device object.
            self.timing.controlDevices.connect(self.devices[name].readValues)

            # Connections.
            self.devices[name].emitData.connect(self.assembly.updateNewData)
            log.info(name + " attached to assembly thread updateNewData method.")
        log.info("Device threads created.")

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
                # Update acquisition and control table models and add to TabWidget by emitting the appropriate Signal.
                self.deviceTableModel.appendRow(deviceInformation)
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.controlModels[name] = ControlTableModel(self.configuration["devices"][name]["control"])
                self.deviceConfigurationAdded.emit(name, self.defaultFeedbackChannel)
                self.setListFeedbackCombobox()
            log.info("Configuration loaded.")
        self.updateDeviceConfigurationTab.emit()
        self.updateUI.emit(self.configuration)

    def findDevices(self):
        """Method to find all available devices and return an array of connection properties.
        USB connections are prioritised over Ethernet and WiFi connections to minimise jitter."""

        # Boolean to indicate that the device list is refreshing.
        self.refreshing = True

        # Clear all tables and re-load the current configuration.
        self.deviceTableModel.clearData()
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.controlModels = {}
        self.clearDeviceConfigurationTabs.emit()
        self.loadDevicesFromConfiguration()

        # Add LabJack USB devices, then TCP devices (USB preferred due to reduced latency).
        self.addLJDevices("USB")
        self.addLJDevices("TCP")

        # Boolean to indicate that the device list has finished refreshing.
        self.refreshing = False

    def addLJDevices(self, mode):
        # Get a list of already existing devices.
        existingDevices = self.deviceTableModel._data
        ID_Existing = []
        for device in existingDevices:
            ID_Existing.append(device["id"])
        
        # Scan for devices.
        if mode == "USB":
            log.info("Scanning for additional USB devices.")
            info = ljm.listAll(7, 1)
        elif mode == "TCP": 
            log.info("Scanning for additional TCP devices.")
            info = ljm.listAll(7, 2)
        numDevices = info[0]
        connectionType = info[2]
        ID = info[3]
        IP = info[4]

        # Add devices if not already in device list.
        for i in range(numDevices):
            if ID[i] not in ID_Existing:
                deviceInformation = {}
                deviceInformation["connect"] = False
                if mode == "USB":
                    handle = ljm.open(7, 1, ID[i])
                elif mode == "TCP":
                    handle = ljm.open(7, 2, ID[i])
                deviceInformation["name"] = ljm.eReadNameString(handle, "DEVICE_NAME_DEFAULT")
                ljm.close(handle)
                deviceInformation["id"] = ID[i]
                deviceInformation["connection"] = connectionType[i]
                if mode == "USB":
                    deviceInformation["address"] = "N/A"
                elif mode == "TCP":
                    deviceInformation["address"] = ljm.numberToIP(IP[i])
                deviceInformation["status"] = True
                self.deviceTableModel.appendRow(deviceInformation)
                self.updateUI.emit(self.configuration)
                
                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                controlTable = copy.deepcopy(self.defaultControlTable)
                newDevice = {
                    "id": deviceInformation["id"],
                    "connection": deviceInformation["connection"],
                    "address": deviceInformation["address"],
                    "acquisition": acquisitionTable,
                    "control" : controlTable
                }

                # If no previous devices are configured, add the "devices" key to the configuration.
                name = deviceInformation["name"]
                if "devices" not in self.configuration:
                    self.configuration["devices"] = {name: newDevice} 
                else:
                    self.configuration["devices"][name] = newDevice 

                # Update acquisition and control table models and add to TabWidget by emitting the appropriate Signal.
                self.acquisitionModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.controlModels[name] = ControlTableModel(self.configuration["devices"][name]["control"])
                self.deviceConfigurationAdded.emit(name, self.defaultFeedbackChannel)
                self.updateDeviceConfigurationTab.emit()
                self.updateUI.emit(self.configuration)
        if mode == "USB":
            log.info("Found " + str(numDevices) + " USB device(s).")
        elif mode == "TCP":
            log.info("Found " + str(numDevices) + " TCP device(s).")

    @Slot()
    def configure(self):
        # Stop acquisition.
        self.timing.stop()

        # Clear all previous data.
        self.assembly.clearAllData()
        
        # Close device threads.
        for name in self.deviceThreads:
            self.deviceThreads[name].quit()
            log.info("Thread for " + name + " stopped.")

        log.info("Configuring devices.")
    
    @Slot()
    def run(self):
        # Create device threads.
        self.createDeviceThreads()

        # Start acquisition.
        self.timing.start(self.configuration["global"]["controlRate"])
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
            "x": 0,
            "y": 0,
            "darkMode": True,
            "controlRate": 1000.00,
            "skipSamples": 10,
            "averageSamples": 10,
            "path": "/data",
            "filename": "junk"
            }
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def loadConfiguration(self, loadConfigurationPath):
        # Clear the configuration.
        self.clearConfiguration()
        time.sleep(1)

        # Next clear the device list and configuration tabs.
        self.deviceTableModel.clearData()
        self.clearDeviceConfigurationTabs.emit()
        
        # # Clear all underlying models and tables.
        self.configuration = {}
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.controlModels = {}
        self.controlTables = {}

        # Load configuration.
        if not loadConfigurationPath is None:
            try:
                log.info("Loading configuration from " + loadConfigurationPath + " and saving location to QSettings.")
                with open(loadConfigurationPath, "r") as file:
                    self.configuration = ruamel.yaml.load(file, Loader=ruamel.yaml.Loader)
                    log.info("Configuration file parsed.")
                    self.configurationPath = loadConfigurationPath
                    # self.configurationChanged.emit(self.configuration)
                    self.settings.setValue("configurationPath", loadConfigurationPath)
                    self.loadDevicesFromConfiguration()
                    self.setListFeedbackCombobox()
                    if "plots" in self.configuration:
                        self.existingPlotsFound.emit()
            except FileNotFoundError:
                log.warning("Previous configuration file not found.")
                self.initialiseDefaultConfiguration()

    @Slot(str)
    def saveConfiguration(self, saveConfigurationPath):
        # Make deep copies of the configuration and filter out devices that are not enabled in the device table.
        configuration = copy.deepcopy(self.configuration)
        if "devices" in configuration:
            devices = copy.deepcopy(self.configuration["devices"])
            enabledDevices = self.deviceTableModel.enabledDevices()
            enabledDeviceList = []
            for device in enabledDevices:
                enabledDeviceList.append(device["name"])
            for device in configuration["devices"]:
                if device not in enabledDeviceList:
                    devices.pop(device)
            configuration["devices"] = devices

        if "plots" in configuration:
           for plotNumber in configuration["plots"]:
               for channel in configuration["plots"][plotNumber]["channels"]:
                   channel['value'] = 0.00

        # Save the yaml file and its path to QSettings.
        with open(saveConfigurationPath, "w") as file:
            yaml = ruamel.yaml.YAML()
            yaml.dump(configuration, file)
        self.settings.setValue("configurationPath", saveConfigurationPath)
        log.info("Saved configuration saved at " + saveConfigurationPath)

    @Slot()
    def clearConfiguration(self):
        # Delete all plots first.
        self.closePlots.emit()

        # Next clear the device list and configuration tabs.
        self.deviceTableModel.clearData()
        self.clearDeviceConfigurationTabs.emit()
        
        # Clear all underlying models and tables.
        self.acquisitionModels = {}
        self.acquisitionTables = {}
        self.controlModels = {}

        # Initialise the basic default configuration.
        self.initialiseDefaultConfiguration()
        self.updateUI.emit(self.configuration)
        log.info("Cleared configuration by loading defaults.") 

    @Slot(str)
    def updateControlRate(self, newControlRate):
        self.configuration["global"]["controlRate"] = float(newControlRate)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New control rate = " + newControlRate + " Hz")

    @Slot(str)
    def updateSkipSamples(self, newSkipSamples):
        self.configuration["global"]["skipSamples"] = int(newSkipSamples)
        self.configurationChanged.emit(self.configuration) 
        # log.info("New acquisition rate = " + newSkipSamples + " Hz")

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
        log.info("New darkMode = " + str(newDarkMode))

    def resetColourSelector(self):
        self.j = 0
        self.k = 4

    def getGenericChannelsData(self):
        deviceList = self.deviceTableModel.enabledDevices()
        self.resetColourSelector()
        genericChannelsData = []
        genericChannelsData.append(
            {"plot": False, "name": "Time", "device": "ALL", "colour": "#35e3e3", "value": "0.00", "unit": "s"})
        for device in deviceList:
            # Get lists of the enabled channel names and units.
            enabledChannels, enabledNames, enabledUnits = self.acquisitionModels[device["name"]].enabledChannels()

            # Create a generic channelsData list.
            for i in range(len(enabledChannels)):
                genericChannelsData.append(
                    {"plot": False, "name": enabledNames[i], "device": device["name"], "colour": self.setColourDefault(),
                     "value": "0.00", "unit": enabledUnits[i]})

        return genericChannelsData

    def updatePlotWindowChannelsData(self):
        # Create a generic channelsData list for the enabled devices.
        genericChannelsData = self.getGenericChannelsData()

        # For each PlotWindow object compare the above with the current channelsData object.
        for plotNumber in self.configuration["plots"]:
            channelsData = self.configuration["plots"][plotNumber]["channels"]

            # Iterate through the genericChannelsData and compare with channelsData, inheriting the colour if it exists.
            for genericChannel in genericChannelsData:
                name = genericChannel["name"]
                device = genericChannel["device"]
                for channel in channelsData:
                    if channel["name"] == name and channel["device"] == device:
                        genericChannel["plot"] = copy.deepcopy(channel["plot"])
                        genericChannel["colour"] = copy.deepcopy(channel["colour"])
            self.configuration["plots"][plotNumber]["channels"] = copy.deepcopy(genericChannelsData)
            self.plotWindowChannelsUpdated.emit()

    def setColourDefault(self):
        colour = [
            ["#ffcdd2", "#ef9a9a", "#e57373", "#ef5350", "#f44336", "#e53935", "#d32f2f", "#c62828", "#b71c1c"],
            ["#f8bbd0", "#f48fb1", "#f06292", "#ec407a", "#e91e63", "#d81b60", "#c2185b", "#ad1457", "#880e4f"],
            ["#e1bee7", "#ce93d8", "#ba68c8", "#ab47bc", "#9c27b0", "#8e24aa", "#7b1fa2", "#6a1b9a", "#4a148c"],
            ["#d1c4e9", "#b39ddb", "#9575cd", "#7e57c2", "#673ab7", "#5e35b1", "#512da8", "#4527a0", "#311b92"],
            ["#c5cae9", "#9fa8da", "#7986cb", "#5c6bc0", "#3f51b5", "#3949ab", "#303f9f", "#283593", "#1a237e"],
            ["#bbdefb", "#90caf9", "#64b5f6", "#42a5f5", "#2196f3", "#1e88e5", "#1976d2", "#1565c0", "#0d47a1"],
            ["#b3e5fc", "#81d4fa", "#4fc3f7", "#29b6f6", "#03a9f4", "#039be5", "#0288d1", "#0277bd", "#01579b"],
            ["#b2ebf2", "#80deea", "#4dd0e1", "#26c6da", "#00bcd4", "#00acc1", "#0097a7", "#00838f", "#006064"],
            ["#b2dfdb", "#80cbc4", "#4db6ac", "#26a69a", "#009688", "#00897b", "#00796b", "#00695c", "#004d40"],
            ["#c8e6c9", "#a5d6a7", "#81c784", "#66bb6a", "#4caf50", "#43a047", "#388e3c", "#2e7d32", "#1b5e20"],
            ["#dcedc8", "#c5e1a5", "#aed581", "#9ccc65", "#8bc34a", "#7cb342", "#689f38", "#558b2f", "#33691e"],
            ["#f0f4c3", "#e6ee9c", "#dce775", "#d4e157", "#cddc39", "#c0ca33", "#afb42b", "#9e9d24", "#827717"],
            ["#fff9c4", "#fff59d", "#fff176", "#ffee58", "#ffeb3b", "#fdd835", "#fbc02d", "#f9a825", "#f57f17"],
            ["#ffecb3", "#ffe082", "#ffd54f", "#ffca28", "#ffc107", "#ffb300", "#ffa000", "#ff8f00", "#ff6f00"],
            ["#ffe0b2", "#ffcc80", "#ffb74d", "#ffa726", "#ff9800", "#fb8c00", "#f57c00", "#ef6c00", "#e65100"],
            ["#ffccbc", "#ffab91", "#ff8a65", "#ff7043", "#ff5722", "#f4511e", "#e64a19", "#d84315", "#bf360c"],
            ["#d7ccc8", "#bcaaa4", "#a1887f", "#8d6e63", "#795548", "#6d4c41", "#5d4037", "#4e342e", "#3e2723"],
            ["#f5f5f5", "#eeeeee", "#e0e0e0", "#bdbdbd", "#9e9e9e", "#757575", "#616161", "#424242", "#212121"],
            ["#cfd8dc", "#b0bec5", "#90a4ae", "#78909c", "#607d8b", "#546e7a", "#455a64", "#37474f", "#263238"]
        ]
        if self.j > len(colour)-1:
            self.k = self.k-1
            self.j = 0
            if self.k < 0:
                self.k = len(colour[1])-1
        c =  colour[self.j][self.k]
        self.j = self.j + 1

        return c

    def setColourNewPlot(self, newPlotNumber):
        # Set the colour of the new plot based on the colours of the first plot in the configuration.
        channelColours = []
        for plotNumber in self.configuration["plots"]:
            for channel in self.configuration["plots"][plotNumber]["channels"]:
                channelColours.append(channel["colour"])
            break
        i = 0
        for channel in self.configuration["plots"][newPlotNumber]["channels"]:
            channel["colour"] = channelColours[i]
            i = i+1

    def setListFeedbackCombobox(self):
        # Get enabled device list.
        enabledDevices = self.deviceTableModel.enabledDevices()

        # Create lists of dicts of enabled channels with default feedback channel as N/A.
        deviceChannelList = []
        for device in enabledDevices:
            name = device['name']
            enabledChannels = self.acquisitionModels[device["name"]].enabledChannels()
            enabledChannels[0].insert(0, 'N/A')
            deviceChannelList.append({name : enabledChannels[0]})

        # For all devices, pass the appropriate feedbackChannelList object.
        for device in deviceChannelList:
            for key, value in device.items():
                # If value is not empty, pass the feedbackChannelList object, otherwise pass the defaults.
                if value != []:
                    feedbackChannelList = copy.deepcopy(value)
                    self.removeWidget.emit(key)
                    self.addControlTable.emit(key, feedbackChannelList)
                elif value == []:
                    self.removeWidget.emit(key)
                    self.addControlTable.emit(key, self.defaultFeedbackChannel)

    def resetIndexFeedbackComboBox(self, row, name):
        # Make a copy of the controls configuration for the current device.
        controls = copy.deepcopy(self.configuration["devices"][name]["control"])

        # Create a list of boolean indicators for the channels in order to 
        # calculate the total number of indices required in the combobox.
        connections = []
        for channel in self.configuration["devices"][name]["acquisition"]:
            connections.append(channel['connect'])
        indexCombo = sum(connections)

        # Loop through the combobox options and redefine values.
        for i in range(len(controls)):
            # If the removed channel was the feedback channel, set to N/A.
            if connections[row] == False and controls[i]["feedback"] == indexCombo:
                self.configuration["devices"][name]["control"][i]["feedback"] = 0
            # If the removed channel was not the feedback channel, redefine values.
            elif connections[row] == False and controls[i]["feedback"] != indexCombo:
                if controls[i]["feedback"] != 0 and indexCombo < controls[i]["feedback"]+1:
                    self.configuration["devices"][name]["control"][i]["feedback"] = copy.deepcopy(controls[i]["feedback"] - 1)
            elif connections[row] == True:
                if indexCombo < controls[i]["feedback"]+1:
                    self.configuration["devices"][name]["control"][i]["feedback"] = copy.deepcopy(controls[i]["feedback"] + 1)

