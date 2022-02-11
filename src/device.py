from PySide6.QtCore import QObject, Signal, Slot
import logging
import ruamel.yaml
from labjack import ljm
import numpy as np
import time
import sys
from time import sleep

log = logging.getLogger(__name__)

class Device(QObject):
    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)
    updatePositionSetPointC1 = Signal(float)
    updatePositionSetPointC2 = Signal(float)
    updatePositionProcessVariableC1 = Signal(float)
    updatePositionProcessVariableC2 = Signal(float)
    updateFeedbackProcessVariableC1 = Signal(float)
    updateFeedbackProcessVariableC2 = Signal(float)
    updateConnectionIndicatorC1 = Signal(bool)
    updateConnectionIndicatorC2 = Signal(bool)
    updateLimitIndicatorC1 = Signal(bool)
    updateLimitIndicatorC2 = Signal(bool)
    updateRunningIndicator = Signal(bool)

    def __init__(self, name, id, connection):
        super().__init__()
        self.name = name
        self.id = id 
        self.connection = connection
        self.handle = None

        # Variables
        self.data = np.zeros(2)
        self.enabledC1 = True
        self.enabledC2 = True
        self.feedbackC1 = True
        self.feedbackC2 = False
        self.running = False
        self.jogC1 = False
        self.jogC2 = False
        self.movingC1 = False
        self.movingC2 = False
        self.directionC1 = 1
        self.directionC2 = 1
        self.positionProcessVariableC1 = 0
        self.positionProcessVariableC2 = 0
        self.speedC1 = 0
        self.speedC2 = 0
        self.feedbackSetPointC1 = 0
        self.feedbackSetPointC2 = 0
        self.feedbackProcessVariableC1 = 0
        self.feedbackProcessVariableC2 = 0
        self.previousCountC1 = 0
        self.previousCountC2 = 0
        self.countsPerUnitC1 = 128000
        self.countsPerUnitC2 = 128000
        self.pulsesPerUnitC1 = 3200
        self.pulsesPerUnitC2 = 3200
        self.positionSetPointC1 = 0
        self.positionSetPointC2 = 0
        self.positionLeftLimitC1 = 0
        self.positionLeftLimitC2 = 0
        self.positionRightLimitC1 = 0
        self.positionRightLimitC2 = 0
        self.positionLeftLimitStatusC1 = False
        self.positionLeftLimitStatusC2 = False
        self.positionRightLimitStatusC1 = False
        self.positionRightLimitStatusC2 = False

        #  Initialise.
        self.openConnection()
        self.initialiseSettings()
        self.loadLuaScript()
        self.checkLimits()

        # Check Clock 0 is disabled.
        ljm.eWriteName(self.handle,'DIO_EF_CLOCK0_ENABLE',0)

    def checkLimits(self):
        # Refresh connection.
        self.handle = ljm.open(7, self.connection, self.id)
        
        # Check limits.
        self.minimumLimitC1 = bool(ljm.eReadName(self.handle, "CIO2"))
        self.maximumLimitC1 = bool(ljm.eReadName(self.handle, "CIO0"))
        self.minimumLimitC2 = bool(ljm.eReadName(self.handle, "CIO3"))
        self.maximumLimitC2 = bool(ljm.eReadName(self.handle, "CIO1"))

        # Turn on indicator if on limits.
        if self.minimumLimitC1 == True or self.maximumLimitC1 == True:
            self.updateLimitIndicatorC1.emit(True)
        else:
            self.updateLimitIndicatorC1.emit(False)
        
        #  Check if motor moving and stop if moving in the direction of the hard limit for C1.
        moving = ljm.eReadName(self.handle, "DIO4_EF_ENABLE")
        if moving == 1 and self.directionC1 == -1 and self.minimumLimitC1 == True:
            self.stopCommand("C1")
        elif moving == 1 and self.directionC1 == 1 and self.maximumLimitC1 == True:
            self.stopCommand("C1")

        #  Check if motor moving and stop if moving in the direction of the hard limit for C2.
        moving = ljm.eReadName(self.handle, "DIO5_EF_ENABLE")
        if moving == 1 and self.directionC2 == -1 and self.minimumLimitC2 == True:
            self.stopCommand("C2")
        elif moving == 1 and self.directionC2 == 1 and self.maximumLimitC2 == True:
            self.stopCommand("C2")

    @Slot(str, float)
    def setPosition(self, channel, value):
        if channel == "C1":
            self.positionProcessVariableC1 = value
            self.positionSetPointC1 = value
        elif channel == "C2":
            self.positionProcessVariableC2 = value
            self.positionSetPointC2 = value

    @Slot(bool)
    def setRunning(self, running):
        self.running = running
        self.updateRunningIndicator.emit(self.running)

    @Slot(str)
    def stopCommand(self, channel):
        if channel == "C1":
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
        elif channel == "C2":
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)

    @Slot(str)
    def zeroPosition(self, channel):
        if channel == "C1":
            self.positionProcessVariableC1 = 0
            self.positionSetPointC1 = 0
            self.previousCountC1 = 0
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1) 
            self.updatePositionProcessVariableC1.emit(self.positionProcessVariableC1)
            ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
        elif channel == "C2":
            self.positionProcessVariableC2 = 0
            self.positionSetPointC2 = 0
            self.previousCountC2 = 0
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2) 
            self.updatePositionProcessVariableC2.emit(self.positionProcessVariableC2)
            ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    def setClock(self, clock, freq):        
        # Define appropriate clock settings, selecting the minimum possible divisor 
        # that does not result in a roll value that exceeds the bit depth of the clock.
        if clock == 0:
            max_roll = 2**32
        else:
            max_roll = 2**16
        core_freq = 80000000
        divisors = np.asarray([1, 2, 4, 8, 16, 32, 64, 256])
        rolls = (core_freq/(freq*divisors)).astype(np.int64)
        ratios = rolls/max_roll
        if np.min(ratios) < 1:
            index = np.where(ratios == ratios[ratios < 1].max())[0]   
            divisor = divisors[index[0]]
            roll = int(rolls[index[0]])
        else:
            log.info('Warning: frequency not possible with this clock!. Defaulted to minimum viable frequency.')
            divisor = np.max(divisors)
            roll = max_roll
        if roll < 1:
            log.info('Warning: frequency not possible with this device. Defaulted to maximum frequency.')
            divisor = np.min(divisors)
            roll = 1
        freq = int(core_freq/(divisor*roll))
        
        # Set the clock.
        aNames = ['DIO_EF_CLOCK' + str(clock) + '_ENABLE',
                'DIO_EF_CLOCK' + str(clock) + '_DIVISOR',
                'DIO_EF_CLOCK' + str(clock) + '_ROLL_VALUE',
                'DIO_EF_CLOCK' + str(clock) + '_ENABLE']
        aValues = [0, divisor, roll, 1]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
        log.info("Clock {clock} set to {freq} Hz.".format(clock=clock, freq=freq))

        return freq, roll

    def checkConnection(self):
        self.handle = ljm.open(7, self.connection, self.id)
        
        connectedC1 = not bool(int(ljm.eReadName(self.handle, 'FIO0')))
        self.updateConnectionIndicatorC1.emit(connectedC1)

        connectedC2 = not bool(int(ljm.eReadName(self.handle, 'FIO2')))
        self.updateConnectionIndicatorC2.emit(connectedC2)
        
        return connectedC1, connectedC2

    @Slot(str, float)
    def updatePositionLeftLimit(self, channel, value):
        if channel == "C1":
            self.positionLeftLimitC1 = value
        elif channel == "C2":
            self.positionLeftLimitC2 = value
        
    @Slot(str, float)
    def updatePositionRightLimit(self, channel, value):
        if channel == "C1":
            self.positionRightLimitC1 = value
        elif channel == "C2":
            self.positionRightLimitC2 = value

    @Slot(str, bool)
    def updatePositionLeftLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionLeftLimitStatusC1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.positionLeftLimitStatusC2 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
    
    @Slot(str, bool)
    def updatePositionRightLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionRightLimitStatusC1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.positionRightLimitStatusC2 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)

    @Slot(str)
    def enableControl(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionSetPointC1 = self.positionProcessVariableC1
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
            ljm.eWriteName(self.handle, "EIO0", 1)
        elif channel == "C2":
            self.positionSetPointC2 = self.positionProcessVariableC2
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
            ljm.eWriteName(self.handle, "EIO2", 1)

    @Slot(str)
    def disableControl(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            name = "EIO0"
        elif channel == "C2":
            name = "EIO2"
        ljm.eWriteName(self.handle, name, 0)

    @Slot(str, float)
    def setSpeed(self, channel, speed):
        self.handle = ljm.open(7, self.connection, self.id)     
        if channel == "C1":
            self.speedC1 = speed
            targetFrequency = speed*self.countsPerUnitC1
            freq, roll = self.setClock(1, targetFrequency)
            aNames = ["DIO4_EF_ENABLE", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A"]
            aValues = [0, 0, 1, int(roll/2)]
            numFrames = len(aNames)
            results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            if self.movingC1 == True:
                self.moveToPosition(channel, self.positionSetPointC1)
        if channel == "C2":
            self.speedC2 = speed
            targetFrequency = speed*self.countsPerUnitC2 
            freq, roll = self.setClock(2, targetFrequency)
            aNames = ["DIO5_EF_ENABLE", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A"]
            aValues = [0, 0, 2, int(roll/2)]
            numFrames = len(aNames)
            results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            if self.movingC2 == True:
                self.moveToPosition(channel, self.positionSetPointC2)
        
    @Slot(str)
    def jogPositiveOn(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            if self.running == True and self.maximumLimitC1 == False:
                self.directionC1 = 1
                self.jogC1 = True
                self.setDirection("C1", self.directionC1)
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 1)
        elif channel == "C2":
            if self.running == True and self.maximumLimitC2 == False:
                self.directionC2 = 1
                self.jogC2 = True
                self.setDirection("C2", self.directionC2)
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 1)

    @Slot(str)
    def jogPositiveOff(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.jogC1 = False
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.jogC2 = False
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)  
    
    @Slot(str)
    def jogNegativeOn(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            if self.running == True and self.minimumLimitC1 == False:
                self.directionC1 = -1
                self.jogC1 = True
                self.setDirection("C1", self.directionC1)
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 1)
        elif channel == "C2":
            if self.running == True and self.minimumLimitC2 == False:
                self.directionC2 = -1
                self.jogC2 = True
                self.setDirection("C2", self.directionC2)
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 1)

    @Slot(str)
    def jogNegativeOff(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.jogC1 = False
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.jogC2 = False
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)

    @Slot()
    def updateControlPanelC1(self):
        if self.jogC1 == True: 
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
        self.updatePositionProcessVariableC1.emit(self.positionProcessVariableC1) 
        self.updateFeedbackProcessVariableC1.emit(self.data[0])
        
    @Slot()
    def updateControlPanelC2(self):   
        if self.jogC2 == True:
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
        self.updatePositionProcessVariableC2.emit(self.positionProcessVariableC2)
        self.updateFeedbackProcessVariableC2.emit(self.data[1])
        
    @Slot(str, float)
    def moveToPosition(self, channel, position):
        if self.running == True:
            if channel == "C1":
                currentPosition = self.positionProcessVariableC1
                increment = position - currentPosition
                if increment > 0:
                    self.directionC1 = 1
                elif increment < 0:   
                    self.directionC1 = -1
                self.setDirection(channel, self.directionC1)
                self.positionSetPointC1 = position
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 1)
                self.movingC1 = True
            elif channel == "C2":
                currentPosition = self.positionProcessVariableC2
                increment = position - currentPosition
                if increment > 0:
                    self.directionC2 = 1
                elif increment < 0:   
                    self.directionC2 = -1
                self.setDirection(channel, self.directionC2)
                self.positionSetPointC2 = position
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 1)
                self.movingC2 = True

    def setDirection(self, channel, direction):
        if channel == "C1":
            name = "EIO1"
        elif channel == "C2":
            name = "EIO3"
        if direction == 1:
            ljm.eWriteName(self.handle, name, 0)
        elif direction == -1:
            ljm.eWriteName(self.handle, name, 1)

    def getPositionC1(self):
        self.handle = ljm.open(7, self.connection, self.id)
        self.countC1 = ljm.eReadName(self.handle, "DIO1_EF_READ_A")
        increment = (self.countC1-self.previousCountC1)/self.pulsesPerUnitC1
        self.previousCountC1 = self.countC1
        if self.directionC1 == 1:
            self.positionProcessVariableC1 += increment
        elif self.directionC1 == -1:
            self.positionProcessVariableC1 -= increment
        # If moving under setpoint control, stop if target reached.
        if self.jogC1 == False:
            if self.directionC1 == 1 and self.positionProcessVariableC1 >= self.positionSetPointC1:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
                self.movingC1 = False
            elif self.directionC1 == -1 and self.positionProcessVariableC1 <= self.positionSetPointC1:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0) 
                self.movingC1 = False
        
    def getPositionC2(self):
        self.handle = ljm.open(7, self.connection, self.id)
        self.countC2 = ljm.eReadName(self.handle, "DIO3_EF_READ_A")
        increment = (self.countC2-self.previousCountC2)/self.pulsesPerUnitC2
        self.previousCountC2 = self.countC2
        if self.directionC2 == 1:
            self.positionProcessVariableC2 += increment
        elif self.directionC2 == -1:
            self.positionProcessVariableC2 -= increment
        # If moving under setpoint control, stop if target reached.
        if self.jogC2 == False:
            if self.directionC2 == 1 and self.positionProcessVariableC2 >= self.positionSetPointC2:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
                self.movingC2 = False
            elif self.directionC2 == -1 and self.positionProcessVariableC2 <= self.positionSetPointC2:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0) 
                self.movingC2 = False

    def configurePulseCounters(self):
        #  Refresh device connection.
        self.handle = ljm.open(7, self.connection, self.id)

        # Setup pulse counter for C1.
        aNames = ["DIO1_EF_ENABLE", "DIO1_EF_INDEX", "DIO1_EF_ENABLE"]
        aValues = [0, 8, 1]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

        # Setup pulse counter for C2.
        aNames = ["DIO3_EF_ENABLE", "DIO3_EF_INDEX", "DIO3_EF_ENABLE"]
        aValues = [0, 8, 1]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

        log.info("Pulse counters configured on device named " + self.name + ".")

    def configureADC(self):
        #  Refresh device connection.
        self.handle = ljm.open(7, self.connection, self.id)

        # Set the ADC settings.
        names = ["AIN_ALL_RANGE", "AIN_ALL_RESOLUTION_INDEX", "AIN_ALL_SETTLING_US"]
        aValues = [10, 2, 0] # No amplification; 16.5 effective bits; auto settling time.
        numFrames = len(names)
        ljm.eWriteNames(self.handle, numFrames, names, aValues) 

    def setAcquisition(self, channels, addresses, dataTypes, slopes, offsets, autozero, controlRate):
        self.channels = channels
        self.addresses = addresses
        self.dataTypes = dataTypes
        self.slopes = np.asarray(slopes)
        self.offsets = np.asarray(offsets)
        self.autozero = np.asarray(autozero)
        self.numFrames = len(self.addresses)
        self.controlRate = controlRate

    def openConnection(self):
        # Method to open a device connection
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.name = ljm.eReadNameString(self.handle, "DEVICE_NAME_DEFAULT")
            log.info("Connected to " + self.name + ".")
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def initialiseSettings(self):
        # Method to initialise the device.
        if self.handle != None:
            try:
                self.configureADC()
                self.configurePulseCounters()
            except ljm.LJMError:
                # Otherwise log the exception.
                ljme = sys.exc_info()[1]
                log.warning(ljme) 
            except Exception:
                e = sys.exc_info()[1]
                log.warning(e)

    def loadLuaScript(self):
        self.script = "src/failsafe.lua"
        self.loadLua()
        self.executeLua()
    
    def loadLua(self):
        try:
            # Read the Lua script.
            with open(self.script, "r") as f:
                lua = f.read()
            lua_length = len(lua)

            # Disable a running script by writing 0 to LUA_RUN twice. Wait for the Lua VM to shut down (and some T7 firmware versions need
            # a longer time to shut down than others) in between the repeated commands.
            ljm.eWriteName(self.handle, "LUA_RUN", 0)
            sleep(2)
            ljm.eWriteName(self.handle, "LUA_RUN", 0)

            # Write the size and the Lua Script to the device.
            ljm.eWriteName(self.handle, "LUA_SOURCE_SIZE", lua_length)
            ljm.eWriteNameByteArray(
                self.handle, "LUA_SOURCE_WRITE", lua_length, bytearray(lua, encoding="utf8")
            )

            # Start the script with debug output disabled.
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE", 1)
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE_DEFAULT", 1)
            log.info("Lua script loaded.")

            # Set the failsafe boolean to unity.
            ljm.eWriteName(self.handle, "USER_RAM0_U16", int(1))
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def executeLua(self):
        # Method to execute a Lua script.
        try:
            ljm.eWriteName(self.handle, "LUA_RUN", 1)
            log.info("Lua script executed.")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
    def readValues(self):
        # Method to read registers on device.
        try:
            # Read from the device and apply slope and offsets.
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "USER_RAM0_U16", 1) 
            self.checkLimits()
            self.raw = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.addresses, self.dataTypes))
            data = self.slopes*(self.raw - self.offsets)
            self.getPositionC1()
            self.getPositionC2()
            if self.feedbackC1 == False:
                dataC1 = np.hstack((self.positionSetPointC1, self.positionProcessVariableC1, int(self.directionC1), self.speedC1))
            elif self.feedbackC1 == True:
                dataC1 = np.hstack((self.positionSetPointC1, self.positionProcessVariableC1, int(self.directionC1), self.speedC1, self.feedbackSetPointC1, self.feedbackProcessVariableC1))
            if self.feedbackC2 == False:
                dataC2 = np.hstack((self.positionSetPointC2, self.positionProcessVariableC2, int(self.directionC2), self.speedC2))
            elif self.feedbackC2 == True:
                dataC2 = np.hstack((self.positionSetPointC2, self.positionProcessVariableC2, int(self.directionC2), self.speedC2, self.feedbackSetPointC2, self.feedbackProcessVariableC2))
            if self.enabledC1 == True:
                data = np.concatenate((data, dataC1))
            if self.enabledC2 == True:
                data = np.concatenate((data, dataC2))
            self.data = data
            self.emitData.emit(self.name, self.data)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot()
    def recalculateOffsets(self):
        # Method to autozero channels as required by the configuration.
        adjustOffsets = (self.raw-self.offsets)*self.autozero
        self.offsets = self.offsets + adjustOffsets

        # Update the device configuration.
        self.updateOffsets.emit(self.name, self.channels, self.offsets.tolist())
        log.info("Autozero applied to device.")

        
