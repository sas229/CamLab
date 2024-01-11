from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import time
import sys
from time import sleep
import requests

log = logging.getLogger(__name__)

class PicoW_FHA(QObject):

    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)

    def __init__(self, name, id, connection, ip):
        super().__init__()
        self.type = "RPi-PicoW-FHA"
        self.name = name
        self.id = id 
        self.ip = ip
        self.connection = connection

        self.slopes = 1
        self.offsets = 0


    def get_request_to_take_readings(self):

        url = "http://" + self.ip + "/GetReadings" 
        response = requests.get(url)

        if response.status_code == 200:
            
            output_text = response.text
            
            output_list = []
            output = ""
            for txt in output_text:
                if txt != " ":
                    output = output + txt
                else:
                    output_list.append(float(output))
                    output = ""
            
            output_array = np.asanyarray(output_list)
            return output_array


    def send_data(self):

        """Send output data."""
        self.data = self.current_data
        # Emit data signal.
        self.emitData.emit(self.name, np.atleast_2d(self.data))    

    def process(self):
        """Method to process timed commands."""
        try:
            # Read from the device and apply slope and offsets.

            
            self.raw = self.get_request_to_take_readings()
            print(self.raw)
            self.current_data = self.slopes*(self.raw - self.offsets)

            # Concatenate output data.
            self.send_data()
  
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot()
    def recalculate_offsets(self):
        """Method to autozero channels as required by the configuration."""
        # Autozero as required.
        adjustOffsets = (self.raw-self.offsets)*self.autozero
        self.offsets = self.offsets + adjustOffsets

        # Update the device configuration.
        self.updateOffsets.emit(self.name, self.channels, self.offsets.tolist())
        log.info("Autozero applied to device.")
