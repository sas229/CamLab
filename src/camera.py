from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import src.local_gxipy as gx

log = logging.getLogger(__name__)

class Camera(QObject):

    def __init__(self, name, id, connection):
        super().__init__()
        self.name = name
        self.id = id 
        self.connection = connection
        self.manager = gx.DeviceManager()

    def open_connection(self):
        try:
            self.cam = self.manager.open_device_by_sn(self.id)
            self.name = self.cam.DeviceUserID.get()
            log.info("Connected to {name}.".format(name=self.name))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        

    def close_connection(self):
        self.cam.close_device()
