from PySide6.QtCore import QObject, Signal, Slot
import logging
import ruamel.yaml
from labjack import ljm
import numpy as np
from time import sleep
import sys

log = logging.getLogger(__name__)

class Device(QObject):
    emitData = Signal(np.ndarray)

    def __init__(self, id, connection, addresses, dataTypes):
        super().__init__()
        self.aAddresses = addresses
        self.aDataTypes = dataTypes
        self.numFrames = len(self.aAddresses)
        self.id = id 
        self.connection = connection
        self.script = "camlab/acquire.lua"
        self.openConnection()
        self.initialiseSettings()
        self.loadLua()
        self.executeLua()

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
        # Method to initialise teh device.
        try:
            # Set the control loop interval at address 46180 in microseconds.
            ljm.eWriteAddress(self.handle, 46180, 0, 1000)
            # Set the ADC settings.
            names = ["AIN_ALL_RANGE", "AIN0_RESOLUTION_INDEX", "AIN_ALL_SETTLING_US"]
            aValues = [10, 2, 0] # No amplification; 16.5 effective bits; auto settling time.
            numFrames = len(names)
            ljm.eWriteNames(self.handle, numFrames, names, aValues) 
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

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

    def readAIN(self):
        # Method to read AIN registers on device.
        try:
            # Read from the device.
            self.handle = ljm.open(7, self.connection, self.id)
            data = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.aAddresses, self.aDataTypes))
            self.emitData.emit(data)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
