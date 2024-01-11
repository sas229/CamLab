from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import time
import sys
from time import sleep

log = logging.getLogger(__name__)

class PicoW_FHA(QObject):

    def __init__(self, name, id, connection):
        super().__init__()
        self.type = "Hub"
        self.name = name
        self.id = id 
        self.connection = connection
