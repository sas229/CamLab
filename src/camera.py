from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import src.local_gxipy as gx

log = logging.getLogger(__name__)

class Camera(QObject):
    previewImage = Signal(np.ndarray)
    saveImage = Signal(str, np.ndarray)
    setImageMode = Signal(str)
    setExposureTime = Signal(int)
    setGain = Signal(float)
    setAcquisitionRate = Signal(float)
    emitData = Signal(str, np.ndarray)
    
    def __init__(self, name, id, connection):
        super().__init__()
        self.type = "Camera"
        self.name = name
        self.id = id 
        self.connection = connection
        self.manager = gx.DeviceManager()
        self.open_connection()
        self.running = True
        self.save_count = 0
        self.binning = 1
        self.stop_stream = False
        self.rate = 10.0
        self.preview_count = 0
        self.previous_preview_count = 0

    def initialise(self):
        try:
            if self.cam.PixelColorFilter.is_implemented() is False:
                self.mode = "Mono"
            else:
                self.mode = "RGB"
            self.setImageMode.emit(self.mode)
            self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def open_connection(self):
        """Open connection to camera."""
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

    @Slot()
    def capture_image(self): 
        """Capture image."""
        try: 
            if self.stop_stream == False:
                self.raw_image = self.cam.data_stream[0].get_image()
                self.rgb_image = self.raw_image.convert("RGB")
                # Convert to monochrome if required.
                if self.mode == "Mono":
                    self.rgb_image.saturation(0)
                self.numpy_image = self.rgb_image.get_numpy_array()
                self.previewImage.emit(self.numpy_image)
                self.preview_count += 1
                # If in auto exposure mode, update the exposure time.
                value, enum = self.cam.ExposureAuto.get()
                if enum != "Off":
                    value = self.cam.ExposureTime.get()
                    self.setExposureTime.emit(value)
                # If in auto gain mode, update the gain.
                value, enum = self.cam.GainAuto.get()
                if enum != "Off":
                    value = self.cam.Gain.get()
                    self.setGain.emit(value)
                # If in maximum acquisition rate mode, update the acquisition rate.
                value, enum = self.cam.AcquisitionFrameRateMode.get()
                if enum == "Off":
                    rate = self.cam.CurrentAcquisitionFrameRate.get()
                    self.setAcquisitionRate.emit(rate)
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)        

    @Slot()
    def save_image(self):
        try:
            if self.preview_count > self.previous_preview_count:
                self.image_name = self.name + "_" + str(self.save_count) + ".jpg"
                self.saveImage.emit(self.image_name, self.numpy_image)
                self.emitData.emit(self.name, np.atleast_2d(self.save_count))
                self.save_count += 1
                self.previous_preview_count = 0
                self.preview_count = 0
            else:
                self.emitData.emit(self.name, np.atleast_2d(np.nan))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def set_image_mode(self, mode):
        """Set image mode."""
        if self.cam.PixelColorFilter.is_implemented() is False and mode == "RGB":
            self.mode = "Mono"
        else:
            self.mode = mode

    @Slot(str)
    def set_auto_white_balance_mode(self, mode):
        try:
            if mode == "Continuous":
                self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.CONTINUOUS)
            elif mode == "Once":
                self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.ONCE)
            elif mode == "Off":
                self.cam.BalanceWhiteAuto.set(gx.GxAutoEntry.OFF)
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def set_auto_exposure_mode(self, mode):
        try:
            if mode == "Continuous":
                self.cam.ExposureAuto.set(gx.GxAutoEntry.CONTINUOUS)
                log.info("Auto exposure mode set to continuous.")
            elif mode == "Once":
                self.cam.ExposureAuto.set(gx.GxAutoEntry.ONCE)
                log.info("Auto exposure mode set to once.")
            elif mode == "Off":
                self.cam.ExposureAuto.set(gx.GxAutoEntry.OFF)
                log.info("Auto exposure mode set to off.")
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(int)
    def set_exposure_time(self, value):
        try:
            self.cam.ExposureTime.set(value)
            log.info("Exposure time set to {value}.".format(value=value))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def set_auto_gain(self, mode):
        try:
            if mode == "On":
                self.cam.GainAuto.set(gx.GxAutoEntry.CONTINUOUS)
                log.info("Auto gain on.")
            elif mode == "Off":
                self.cam.GainAuto.set(gx.GxAutoEntry.OFF)
                log.info("Auto gain off.")
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(float)
    def set_gain(self, value):
        try:
            self.cam.Gain.set(value)
            log.info("Gain set to {value}.".format(value=value))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def set_binning_mode(self, mode):
        try:
            self.stop_stream = True
            self.cam.stream_off()
            if mode == "Off":
                self.binning = 1
                self.cam.BinningHorizontal.set(self.binning)
                self.cam.BinningVertical.set(self.binning)
                log.info("Binning turned off.")
            elif mode == "Average":
                self.cam.BinningHorizontalMode.set(gx.GxBinningHorizontalModeEntry.AVERAGE)
                self.cam.BinningVerticalMode.set(gx.GxBinningHorizontalModeEntry.AVERAGE)
                log.info("Binning set to sum mode.")
            elif mode == "Sum":
                self.cam.BinningHorizontalMode.set(gx.GxBinningHorizontalModeEntry.SUM)
                self.cam.BinningVerticalMode.set(gx.GxBinningHorizontalModeEntry.SUM)
                log.info("Binning set to sum mode.")
            self.cam.stream_on()
            self.stop_stream = False
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(float)
    def set_binning(self, value):
        try:
            self.stop_stream = True
            self.cam.stream_off()
            self.binning = value
            self.cam.BinningHorizontal.set(self.binning)
            self.cam.BinningVertical.set(self.binning)
            self.cam.stream_on()
            self.stop_stream = False
            log.info("Binning set to {value}.".format(value=value))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def set_acquisition_mode(self, mode):
        try:
            if mode == "Max":
                self.cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.OFF)
                log.info("Acquisition mode set to max.")
            elif mode == "Defined":
                self.cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)
                self.cam.AcquisitionFrameRate.set(self.rate)
                log.info("Acquisition mode set to {value} Hz.".format(value=self.rate))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(float)
    def set_acquisition_rate(self, value):
        try:
            self.rate = value
            self.cam.AcquisitionFrameRate.set(self.rate)
            log.info("Acquisition rate set to {value} Hz.".format(value=value))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


