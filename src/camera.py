from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import src.local_gxipy as gx

log = logging.getLogger(__name__)

class Camera(QObject):
    previewImage = Signal(np.ndarray)

    def __init__(self, name, id, connection):
        super().__init__()
        self.type = "Camera"
        self.name = name
        self.id = id 
        self.connection = connection
        self.manager = gx.DeviceManager()
        self.open_connection()
        self.fixed_settings()

    def open_connection(self):
        """Open connectiont to camera."""
        try:
            self.cam = self.manager.open_device_by_sn(self.id)
            self.name = self.cam.DeviceUserID.get()
            log.info("Connected to {name}.".format(name=self.name))
            self.cam.stream_on()
            log.info("Stream turned on for {name}.".format(name=self.name))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
    def close_connection(self):
        """Close connection to camera."""
        try:
            self.cam.stream_off()
            log.info("Stream turned off for {name}.".format(name=self.name))
            self.cam.close_device()
            log.info("Closed connection to {name}.".format(name=self.name))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def fixed_settings(self):
        """Define fixed settings for camera."""
        self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)    # Set white balance to continuous auto.

    def capture_image(self): 
        """Capture image."""    
        raw_image = self.cam.data_stream[0].get_image()
        rgb_image = raw_image.convert("RGB")
        numpy_image = rgb_image.get_numpy_array()
        self.previewImage.emit(numpy_image)

