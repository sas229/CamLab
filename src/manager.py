from PySide6.QtCore import QObject, Signal, Slot, QSettings, QThread, QModelIndex, QDate, Qt
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
from datetime import datetime

log = logging.getLogger(__name__)

class Manager(QObject):
    # updateUI = Signal(dict)
    configurationChanged = Signal(dict)
    deviceAdded = Signal(str)
    clearDeviceConfigurationTabs = Signal()
    closePlots = Signal()
    clearControlTabs = Signal()
    addControlTable = Signal(str, list)
    deviceToggled = Signal(str, bool)
    removeControlTable = Signal(str)
    plotWindowChannelsUpdated = Signal()
    existingPlotsFound = Signal()
    outputText = Signal(str)
    # updateFeedbackChannelList = Signal(str, list)

    def __init__(self):
        super().__init__()
        self.configuration = {}
        self.acquisitionTableModels = {}
        self.acquisitionTables = {}
        self.controlTableModels = {}
        self.feedbackChannelLists = {}
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
        defaultControlSettings = {
            "mode": "tab",
            "x": 0,
            "y": 0,
            "width": 1200,
            "height": 560,
            "primaryMinimum": -100.00,
            "primaryMaximum": 100.00,
            "primaryLeftLimit": -80.00,
            "primaryRightLimit": 80.00,
            "primarySetPoint": 0.00,
            "primaryProcessVariable": 0.00,
            "primaryUnit": "(mm)",
            "secondarySetPoint": 3.000,
            "secondaryUnit": "(mm/s)",
            "feedbackMinimum": -20.00,
            "feedbackMaximum": 100.00,
            "feedbackLeftLimit": -10.00,
            "feedbackRightLimit": 90.00,
            "feedbackSetPoint": 0.00,
            "feedbackProcessVariable": 0.00,
            "feedbackUnit": "(N)",
            "feedbackIndex": 0,
            "KP": 0.00,
            "KI": 0.00,
            "KD": 0.00,
            "proportionalOnMeasurement": False
        }
        self.defaultControlTable = [
            {"channel": "C1", "name": "C1", "enable": False, "type": "N/A", "control": "N/A", "feedback": "N/A", "settings": defaultControlSettings},
            {"channel": "C2", "name": "C2", "enable": False, "type": "N/A", "control": "N/A", "feedback": "N/A", "settings": defaultControlSettings}
        ]
        self.controlModeList = ["N/A", "Digital"]
        self.controlActuatorList = ["N/A", "Linear"]
        self.defaultFeedbackChannelList = ["N/A"]
        
        # Instantiate the model for the device list and connect to device thread manager.   
        self.deviceTableModel = DeviceTableModel()
        self.deviceTableModel.deviceConnectStatusUpdated.connect(self.manageDeviceThreads)

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

        # Load last used configuration file.
        log.info("Finding previous YAML file location from QSettings.")
        self.settings = QSettings("CamLab", "Settings")
        self.settings.sync()
        self.findConfigurationPath()
        if self.configurationPath != None:
            self.loadConfiguration(self.configurationPath)
        else:
            self.initialiseDefaultConfiguration()

    @Slot(str, list, list)
    def updateDeviceOffsets(self, name, channels, newOffsets):
        count = 0
        for channel in channels:
            index = int(re.findall(r'\d+', channel)[0])
            offset = round(newOffsets[count], 3)
            self.configuration["devices"][name]["acquisition"][index]["offset"] = offset
            self.configurationChanged.emit(self.configuration)
            count += 1
        log.info("Updated offsets in configuration.")

    def generateFilename(self):
        initialTime = datetime.now()
        initialDate = QDate.currentDate()
        path = str(self.configuration["global"]["path"])
        filename = str(self.configuration["global"]["filename"])
        date = str(initialDate.toString(Qt.ISODate))
        time = str("{hours:02}:{minutes:02}:{seconds:02}".format(hours=initialTime.hour, minutes=initialTime.minute, seconds=initialTime.second))
        ext = ".txt"
        output = path + "/" + filename + "_" + date + "_" + time + "_1" + ext
        self.outputText.emit(output)
        return  path, filename, date, time, ext

    def createHeader(self):
        path, filename, date, timestart, ext = self.generateFilename()
        byeline = "CamLab data acquisition and device control system: https://github.com/sas229/CamLab\n"
        testline = "Test name: " + filename + "\nDate: " + date + "\nTime: " + timestart + "\n\n"
        slopeline = "Slopes:"
        offsetline = "Offsets:"
        channelline = "Channel:"
        nameline = "Time (s)"
        #  For each enabled device, add the enabled channels for acquisition and control.
        enabledDevices = self.deviceTableModel.enabledDevices()
        for device in enabledDevices:
            deviceName = device["name"]
            # Acquisition channels.
            channels, names, units, slopes, offsets, autozero = self.acquisitionTableModels[deviceName].acquisitionSettings()
            for slope in slopes:
                slopeline += "\t"
                slopeline += str(slope)
            for offset in offsets:
                offsetline += "\t"
                offsetline += str(offset)
            for channel in channels:
                channelline += "\t"
                channelline += str(channel) + " [" + str(deviceName) + "]"
            for i in range(len(names)):
                nameline += "\t"
                nameline += str(names[i]) + " (" + str(units[i]) + ")"
            # Control channels.
            controls = self.controlTableModels[deviceName].enabledControls()
            for control in controls:
                # Get name of control and units.
                controlName = deviceName + " " + control["channel"]
                if control["channel"] == "C1":
                    channel = 0
                elif control["channel"] == "C2":
                    channel = 1
                primaryUnit = self.configuration["devices"][deviceName]["control"][channel]["settings"]["primaryUnit"]
                secondaryUnit = self.configuration["devices"][deviceName]["control"][channel]["settings"]["secondaryUnit"]
                feedbackUnit = self.configuration["devices"][deviceName]["control"][channel]["settings"]["feedbackUnit"]
                feedbackIndex = self.configuration["devices"][deviceName]["control"][channel]["settings"]["feedbackIndex"]
                feedbackChannel = self.configuration["devices"][deviceName]["control"][channel]["feedback"]
                
                # For each enabled control add the required header components depending on the actuator type.
                if control["control"] == "Linear":
                    if feedbackIndex == 0:
                        slopeline += "\t 1 \t 1 \t 1 \t 1" 
                        offsetline += "\t 0 \t 0 \t 0 \t 0"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]" 
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]" 
                        nameline += "\t Position SP " + str(primaryUnit)
                        nameline += "\t Position PV " + str(primaryUnit)
                        nameline += "\t Direction (-)"
                        nameline += "\t Speed " + str(secondaryUnit)
                    else:
                        slopeline += "\t 1 \t 1 \t 1 \t 1 \t 1 \t 1" 
                        offsetline += "\t 0 \t 0 \t 0 \t 0 \t 0 \t 0"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]" 
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]" 
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]"
                        channelline += "\t" + str(control["channel"]) + " [" + str(deviceName) + "]" 
                        nameline += "\t Position SP " + str(primaryUnit)
                        nameline += "\t Position PV " + str(primaryUnit)
                        nameline += "\t Direction (-)"
                        nameline += "\t Speed " + str(secondaryUnit)
                        nameline += "\t Feedback SP " + str(feedbackUnit)
                        nameline += "\t Feedback PV " + str(feedbackUnit)
        slopeline += "\n"
        offsetline += "\n\n"
        channelline += "\n\n"
        nameline += "\n"
        header = byeline + testline + slopeline + offsetline + channelline + nameline
        return header

    def setAcquisitionSettings(self):
        log.info("Setting acquisition for all devices.")
        # Get a list of enabled devices.
        enabledDevices = self.deviceTableModel.enabledDevices()

        # Create output arrays in assembly thread.
        self.assembly.createDataArrays(enabledDevices)
        
        # Initialise assembly thread.
        controlRate = self.configuration["global"]["controlRate"]
        skipSamples = self.configuration["global"]["skipSamples"]
        averageSamples = self.configuration["global"]["averageSamples"]
        self.assembly.settings(controlRate, skipSamples, averageSamples)

        # Set filename.
        path, filename, date, time, ext = self.generateFilename()
        self.assembly.setFilename(path, filename, date, time, ext)

        # Generate the header for the output file.
        header = self.createHeader()
        self.assembly.writeHeader(header)
        
        # For each device set the acquisition array and execute in a separate thread.
        for device in enabledDevices:
            name = device["name"]
            
            # Generate addresses for acqusition and set acquisition in device.
            channels, names, units, slopes, offsets, autozero = self.acquisitionTableModels[name].acquisitionSettings()
            addresses = []
            dataTypes = []
            dt = ljm.constants.FLOAT32
            for channel in channels:
                address = int(re.findall(r'\d+', channel)[0])*2 # Multiply by two to get correct LJ address for AIN.
                addresses.append(address)
                dataTypes.append(dt)
            controlRate = self.configuration["global"]["controlRate"]
            self.devices[name].setAcquisition(channels, addresses, dataTypes, slopes, offsets, autozero, controlRate)
            log.info("Acquisition settings set for device named " + name + ".")

    def setDeviceFeedbackChannels(self):
        log.info("Setting feedback channels for all devices.")
        # Get a list of enabled devices.
        enabledDevices = self.deviceTableModel.enabledDevices()

        # For each device set the acquisition array and execute in a separate thread.
        for device in enabledDevices:
            deviceName = device["name"]

            # Control channels.
            enabledControls = self.controlTableModels[deviceName].enabledControls()
            for control in enabledControls:
                channel = int(control["channel"][-1])-1
                feedbackIndex = self.configuration["devices"][deviceName]["control"][channel]["settings"]["feedbackIndex"]
                self.devices[deviceName].setFeedbackChannels(control["channel"], feedbackIndex)
                log.info("Feedback channel set to " + str(control["feedback"]) + " for control channel " + control["channel"] + " on " + deviceName + ".")

    @Slot(str, int, int, bool)
    def manageDeviceThreads(self, name, id, connection, connect):
        # Create device instance and move to thread if it doesn't already exist.
        if connect == True and name not in self.devices:
            print("Adding device...")
            self.devices[name] = Device(name, id, connection)
            log.info("Device instance created for device named " + name + ".")
            self.deviceThreads[name] = QThread()
            log.info("Device thread created for device named " + name + ".")
            self.devices[name].moveToThread(self.deviceThreads[name])
            self.deviceThreads[name].start()
            log.info("Device thread started for device named " + name + ".")

            # Connections.
            self.timing.controlDevices.connect(self.devices[name].readValues)
            self.assembly.autozeroDevices.connect(self.devices[name].recalculateOffsets)
            self.devices[name].emitData.connect(self.assembly.updateNewData)
            self.devices[name].updateOffsets.connect(self.updateDeviceOffsets)
            log.info(name + " attached to basic acquisition connections.")

            # Emit signal.
            self.deviceAdded.emit(name)
            # self.deviceToggled.emit(name, connect)

        elif connect == False:  
            # Emit signal to remove device configuration tab.
            self.deviceToggled.emit(name, connect)

            # Remove device.
            # del self.devices[name]
            self.devices.pop(name)
            log.info("Device instance deleted for device named " + name + ".")
            self.deviceThreads[name].quit()
            # sleep(1.0)
            self.deviceThreads.pop(name)
            log.info("Device thread deleted for device named " + name + ".")

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
                self.manageDeviceThreads(name=device, id=deviceInformation["id"], connection=deviceInformation["connection"], connect=True)
                self.acquisitionTableModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.controlTableModels[name] = ControlTableModel(name, self.configuration["devices"][name]["control"])
                self.feedbackChannelLists[name] = self.setFeedbackChannelList(name)
                # self.addControlSettings(name)
                # self.deviceAdded.emit(name)
            log.info("Configuration loaded.")
        # self.deviceToggled.emit(name, connect)
        self.configurationChanged.emit(self.configuration)

    def findDevices(self):
        """Method to find all available devices and return an array of connection properties.
        USB connections are prioritised over Ethernet and WiFi connections to minimise jitter."""

        # Boolean to indicate that the device list is refreshing.
        self.refreshing = True

        # Clear all tables and re-load the current configuration.
        self.deviceTableModel.clearData()
        self.acquisitionTableModels = {}
        self.acquisitionTables = {}
        self.controlTableModels = {}
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
                self.configurationChanged.emit(self.configuration)
                
                # Make a deep copy to avoid pointers in the YAML output.
                acquisitionTable = copy.deepcopy(self.defaultAcquisitionTable)
                controlTable = copy.deepcopy(self.defaultControlTable)
                controlTable[0]["name"] = deviceInformation["name"] + " C1"
                controlTable[1]["name"] = deviceInformation["name"] + " C2"
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
                log.info("Instantiating data models for device.")
                self.acquisitionTableModels[name] = AcquisitionTableModel(self.configuration["devices"][name]["acquisition"])
                self.controlTableModels[name] = ControlTableModel(name, self.configuration["devices"][name]["control"])
                self.feedbackChannelLists[name] = self.setFeedbackChannelList(name)
                log.info("Data models instantiated for device.")
            
                # Addd device to UI.
                log.info("Adding device to UI.")
                # self.addControlSettings(name)
                # self.deviceAdded.emit(name)
                self.configurationChanged.emit(self.configuration)
        if mode == "USB":
            log.info("Found " + str(numDevices) + " USB device(s).")
        elif mode == "TCP":
            log.info("Found " + str(numDevices) + " TCP device(s).")

    def addControlSettings(self, name):
        #  Configure control settings.
        log.info("Adding control settings for device.")
        for channel in range(self.controlTableModels[name].rowCount()):
            if "settings" not in self.configuration["devices"][name]["control"][channel]:
                self.configuration["devices"][name]["control"][channel]["settings"] = copy.deepcopy(self.defaultControlSettings)

    @Slot()
    def configure(self):
        # Close current file.
        self.assembly.closeFile()

        # Stop acquisition.
        self.timing.stop()
        
        # Clear all previous data.
        self.assembly.clearAllData()
        log.info("Configuring devices.")
    
    @Slot()
    def run(self):
        # Set acquisition settings.
        self.setAcquisitionSettings()

        # Set feedback channels.
        self.setDeviceFeedbackChannels()
        
        # Start acquisition.
        self.timing.start(self.configuration["global"]["controlRate"])
        log.info("Started acquisition and control.")

    @Slot()
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
            "controlRate": 100.00,
            "skipSamples": 1,
            "averageSamples": 1,
            "path": "/home/sam/Documents",
            "filename": "junk"
            }
        self.configuration["configurationWindow"] = {
            "x": 0,
            "y": 0
        }
        self.configuration["controlWindow"] = {
            "x": 0,
            "y": 0,
            "width": 1200,
            "height": 600,
            "visible": False
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
        self.acquisitionTableModels = {}
        self.acquisitionTables = {}
        self.controlTableModels = {}
        self.controlTables = {}

        # Load configuration.
        if not loadConfigurationPath is None:
            try:
                log.info("Loading configuration from " + loadConfigurationPath + " and saving location to QSettings.")
                with open(loadConfigurationPath, "r") as file:
                    self.configuration = ruamel.yaml.load(file, Loader=ruamel.yaml.Loader)
                    log.info("Configuration file parsed.")
                    self.configurationPath = loadConfigurationPath
                    self.configurationChanged.emit(self.configuration)
                    self.settings.setValue("configurationPath", loadConfigurationPath)
                    self.loadDevicesFromConfiguration()
                    # self.setListFeedbackCombobox()
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
        self.clearControlTabs.emit()

        # Next clear the device list and configuration tabs.
        self.deviceTableModel.clearData()
        self.clearDeviceConfigurationTabs.emit()
        
        # Clear all underlying models and tables. 
        self.acquisitionTableModels = {}
        self.acquisitionTables = {}
        self.controlTableModels = {}

        # Initialise the basic default configuration.
        self.initialiseDefaultConfiguration()
        self.configurationChanged.emit(self.configuration)
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
            name = device["name"]
            channels, names, units, slopes, offsets, autozero = self.acquisitionTableModels[name].acquisitionSettings()

            # Create a generic channelsData list.
            for i in range(len(channels)):
                genericChannelsData.append(
                    {"plot": False, "name": names[i], "device": device["name"], "colour": self.setColourDefault(),
                     "value": "0.00", "unit": units[i]})
            # Control channels.
            controls = self.controlTableModels[name].enabledControls()
            device = device["name"]
            for control in controls:
                controlName = name + " " + control["channel"]
                if control["channel"] == "C1":
                    channel = 0
                elif control["channel"] == "C2":
                    channel = 1
                # Slice in lines that follows removes the brackets.
                primaryUnit = self.configuration["devices"][name]["control"][channel]["settings"]["primaryUnit"][1:-1]
                secondaryUnit = self.configuration["devices"][name]["control"][channel]["settings"]["secondaryUnit"][1:-1]
                feedbackUnit = self.configuration["devices"][name]["control"][channel]["settings"]["feedbackUnit"][1:-1]
                channel = control["channel"]
                if control["feedback"] == "N/A":
                    if control["control"] == "Linear":
                        genericChannelsData.append(
                        {"plot": False, "name": "Postion SP" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": primaryUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Postion PV" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": primaryUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Direction" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": "-"})
                        genericChannelsData.append(
                        {"plot": False, "name": "Speed" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": secondaryUnit})
                else:
                    if control["control"] == "Linear":
                        genericChannelsData.append(
                        {"plot": False, "name": "Postion SP" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": primaryUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Postion PV" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": primaryUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Direction" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": "-"})
                        genericChannelsData.append(
                        {"plot": False, "name": "Speed" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": secondaryUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Feedback SP" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": feedbackUnit})
                        genericChannelsData.append(
                        {"plot": False, "name": "Feedback PV" , "device": control["name"], "colour": self.setColourDefault(),
                        "value": "0.00", "unit": feedbackUnit})
        return genericChannelsData

    @Slot()
    def updatePlotWindowChannelsData(self):
        if "plots" in self.configuration:
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

    def setFeedbackChannelList(self, name):
        # Create lists of enabled channels with default feedback channel as N/A.
        feedbackChannelList = []
        feedbackChannelList.append("N/A")
        enabledChannels = self.acquisitionTableModels[name].enabledChannels()
        for channel in enabledChannels:
            feedbackChannelList.append(channel)
        
        # Store feedback channel list.
        if name not in self.feedbackChannelLists:
            self.feedbackChannelLists = {name: copy.deepcopy(feedbackChannelList)}
        else:
            self.feedbackChannelLists[name] = copy.deepcopy(feedbackChannelList)
        log.info("Feedback channel list created.")
        print(feedbackChannelList)
        return feedbackChannelList

    def updateFeedbackComboBox(self, deviceName, row):
        # Make a deep copy of the current feedback channel list.
        feedbackChannelList = copy.deepcopy(self.feedbackChannelLists[deviceName])

        # Get the updated feedback channel list.
        updatedFeedbackChannelList = self.setFeedbackChannelList(deviceName)