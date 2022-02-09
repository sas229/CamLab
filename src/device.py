from PySide6.QtCore import QObject, Signal, Slot
import logging
import ruamel.yaml
from labjack import ljm
import numpy as np
import time
import sys

log = logging.getLogger(__name__)

class Device(QObject):
    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)
    updatePositionSetPoint = Signal(float)
    updatePositionProcessVariable = Signal(float)
    updateFeedbackProcessVariable = Signal(float)

    def __init__(self, name, id, connection):
        super().__init__()
        self.name = name
        self.id = id 
        self.connection = connection
        self.handle = None
        self.openConnection()
        self.initialiseSettings()

        # Variables
        self.jog = False
        self.direction = 0
        self.position = 0
        self.countsPerUnit = 128000
        self.pulsesPerUnit = 3200
        self.previousCount = 0
        self.positionLeftLimitStatusC1 = False
        self.positionLeftLimitStatusC2 = False

    def setClock(self, clock, freq):
        # Check Clock 0 is disabled.
        ljm.eWriteName(self.handle,'DIO_EF_CLOCK0_ENABLE',0)
        
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
        freq = core_freq/(divisor*roll)
        
        # Set the clock.
        aNames = ['DIO_EF_CLOCK' + str(clock) + '_ENABLE',
                'DIO_EF_CLOCK' + str(clock) + '_DIVISOR',
                'DIO_EF_CLOCK' + str(clock) + '_ROLL_VALUE',
                'DIO_EF_CLOCK' + str(clock) + '_ENABLE']
        aValues = [0, divisor, roll, 1]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
        return freq, roll

    @Slot(str, bool)
    def updatePositionLeftLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionLeftLimitStatusC1 = status
            if status == True:
                ljm.eWriteAddress(self.handle, 44008, 1, 0)
        elif channel == "C2":
            self.positionLeftLimitStatusC2 = status
            if status == True:
                ljm.eWriteAddress(self.handle, 44010, 1, 0)
        # print("Left limit status: " + str(status))
    
    @Slot(str, bool)
    def updatePositionRightLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionRightLimitStatusC1 = status
            if status == True:
                ljm.eWriteAddress(self.handle, 44008, 1, 0)
        elif channel == "C2":
            self.positionRightLimitStatusC2 = status
            if status == True:
                ljm.eWriteAddress(self.handle, 44010, 1, 0)
        # print("Right limit status: " + str(status))

    @Slot(str)
    def enableControl(self, channel):
        # print(channel + " enabled.")
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            address = 2008
        elif channel == "C2":
            address = 2010
        ljm.eWriteAddress(self.handle, address, 0, 1)

    @Slot(str)
    def disableControl(self, channel):
        # print(channel + " disabled.")
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            address = 2008
        elif channel == "C2":
            address = 2010
        ljm.eWriteAddress(self.handle, address, 0, 0)

    @Slot(str, float)
    def setSpeed(self, channel, value):
        # print(channel + " speed: " + str(value))
        self.handle = ljm.open(7, self.connection, self.id)
        freq, roll = self.setClock(1, 128000)
        if channel == "C1":
            aNames = ["DIO4_EF_ENABLE", "DIO4_EF_INDEX", "DIO4_EF_CONFIG_A"]
            aValues = [0, 1, int(roll/2)]
        elif channel == "C2":
            aNames = ["DIO5_EF_ENABLE", "DIO5_EF_INDEX", "DIO5_EF_CONFIG_A"]
            aValues = [0, 2, int(roll/2)]
        numFrames = len(aNames)
        results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
    
    @Slot(str)
    def jogPositiveOn(self, channel):
        self.jog = True
        self.handle = ljm.open(7, self.connection, self.id)
        self.direction = 0
        if channel == "C1":
            ljm.eWriteAddress(self.handle, 2009, 0, self.direction)
            ljm.eWriteAddress(self.handle, 44008, 1, 1)
        elif channel == "C2":
            self.direction
            ljm.eWriteAddress(self.handle, 2011, 0, self.direction)
            ljm.eWriteAddress(self.handle, 44010, 1, 1)

    @Slot(str)
    def jogPositiveOff(self, channel):
        self.jog = False
        # print(channel + " jog positive off.")
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            ljm.eWriteAddress(self.handle, 44008, 1, 0)
        elif channel == "C2":
            ljm.eWriteAddress(self.handle, 44010, 1, 0)
          
    
    @Slot(str)
    def jogNegativeOn(self, channel):
        self.jog = True
        # print(channel + " jog negative on.")
        self.handle = ljm.open(7, self.connection, self.id)
        self.direction = 1
        if channel == "C1":
            ljm.eWriteAddress(self.handle, 2009, 0, self.direction)
            ljm.eWriteAddress(self.handle, 44008, 1, 1)
        elif channel == "C2":
            ljm.eWriteAddress(self.handle, 2011, 0, self.direction)
            ljm.eWriteAddress(self.handle, 44010, 1, 1)

    @Slot(str)
    def jogNegativeOff(self, channel):
        self.jog = False
        # print(channel + " jog negative off.")
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            ljm.eWriteAddress(self.handle, 44008, 1, 0)
        elif channel == "C2":
            ljm.eWriteAddress(self.handle, 44010, 1, 0)

    @Slot(str, float)
    def moveToPosition(self, channel, position):
        currentPosition = self.position
        increment = position - currentPosition
        direction = int(np.sign(increment))
        pulses = int(np.round(np.abs(increment)*self.pulsesPerUnit, 0))
        print(increment, direction, pulses)

    def getPosition(self):
        self.handle = ljm.open(7, self.connection, self.id)
        count = ljm.eReadName(self.handle, "DIO1_EF_READ_A")
        increment = (count - self.previousCount)/self.pulsesPerUnit
        if self.direction == 0:
            self.position += increment
        elif self.direction == 1:
            self.position -= increment
        self.updatePositionProcessVariable.emit(self.position)
        if self.jog == True:
            self.updatePositionSetPoint.emit(self.position)
        self.previousCount = count

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
        self.script = "src/acquire.lua"
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

            # Set the control loop interval at address 46180 in microseconds.
            ljm.eWriteAddress(self.handle, 46180, 0, int((1/self.controlRate)*1000000))
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
            self.raw = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.addresses, self.dataTypes))
            self.data = self.slopes*(self.raw - self.offsets)
            self.emitData.emit(self.name, self.data)
            self.getPosition()
            self.updateFeedbackProcessVariable.emit(self.data[0])
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

        
