from PySide6.QtCore import QObject, Signal, Slot
import logging
import numpy as np
import local_gxipy as gx
import sys
import cv2
from PIL import Image, ImageDraw, ImageColor
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import os

log = logging.getLogger(__name__)

class Camera(QObject):
    previewImage = Signal(np.ndarray)
    saveImage = Signal(str, np.ndarray)
    updateExposureTime = Signal(int)
    updateGain = Signal(float)
    updateAcquisitionRate = Signal(float)
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
        self.stop_stream = False
        self.preview_count = 0
        self.previous_preview_count = 0
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.arucoParams = cv2.aruco.DetectorParameters_create()
        self.board = cv2.aruco.CharucoBoard_create(11, 8, 15/1000, 12/1000, self.arucoDict)
        self.calibrating = False

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
    def calibrate(self):
        log.info("Calibrating camera...")
        self.calibrating = True
        self.calibrate_count = 0 
        self.corners = []
        self.ids = [] 
        self.n = 0
        self.shape = self.numpy_image[:,:,0].shape
        self.width = self.numpy_image[:,:,0].shape[1]
        self.height = self.numpy_image[:,:,0].shape[0]
        self.coverage = np.zeros((self.height, self.width, 3))

    @Slot()
    def capture_image(self): 
        """Capture image."""
        try: 
            if self.stop_stream == False:
                self.raw_image = self.cam.data_stream[0].get_image()
                # If NoneType, log warning, else update preview image.
                if type(self.raw_image) == type(None):
                    log.warning("Incomplete frame on {device}.".format(device=self.name))
                else:
                    # If colour camera, convert to RGB image, otherwise convert directly to numpy array.
                    if self.cam.PixelColorFilter.is_implemented() == True:
                        self.rgb_image = self.raw_image.convert("RGB")
                        # Convert to monochrome if required.
                        if self.mode == "Mono":
                            self.rgb_image.saturation(0)
                        self.numpy_image = self.rgb_image.get_numpy_array()
                    else:
                        self.numpy_image = self.raw_image.get_numpy_array()
                    self.preview_count += 1
                    if self.calibrating == True:

                        self.charuco_calibrate()
                self.previewImage.emit(self.numpy_image)
                self.updateUI()
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)      

    def update_coverage(self, corners):
        # Create blank image space.
        # background = ImageColor.getcolor(os.environ['QTMATERIAL_SECONDARYLIGHTCOLOR'], "RGB")
        img = Image.new("RGB", (self.width, self.height), 0)
        # Define polygon.
        hull = ConvexHull(corners)
        x = corners[hull.vertices,0]
        y = corners[hull.vertices,1]
        polygon = np.vstack((x,y))
        polygon = np.rot90(polygon)
        coord = np.atleast_2d(polygon[0,:])
        polygon = np.append(polygon, coord, axis=0)
        polygon = polygon.astype(int)
        polygon = polygon.flatten()
        polygon = polygon.tolist()
        ImageDraw.Draw(img).polygon(polygon, outline=60, fill=(25, 0, 0))
        # Make numpy array.
        img_array = np.array(img)
        # Add to current coverage array.
        self.coverage = self.coverage + img_array
        # Clip to 8 bit image range.
        self.coverage = np.clip(self.coverage, 0, 255)
    
    def charuco_calibrate(self):
        corners, ids, rejected = cv2.aruco.detectMarkers(self.numpy_image, self.arucoDict,
            parameters=self.arucoParams)
        marker_image = self.numpy_image
        if (ids is not None):
            # Read chessboard corners between markers
            _, c_corners, c_ids = cv2.aruco.interpolateCornersCharuco(corners,
                                                                        ids,
                                                                        self.numpy_image,
                                                                        self.board)
            marker_image = cv2.aruco.drawDetectedMarkers(self.numpy_image, corners)
            # print(c_corners)
            id_color = (255, 255, 0)
            marker_image = cv2.aruco.drawDetectedCornersCharuco(self.numpy_image, c_corners, c_ids, id_color)
            if c_ids is not None:
                if len(c_corners) > 40:
                    self.corners.append(c_corners)
                    self.n = self.n + len(c_corners)
                    self.ids.append(c_ids)
                    self.calibrate_count += 1
                    self.numpy_image = marker_image
                    self.update_coverage(c_corners[:,0,:])
                    log.info("Captured {images} calibration images and {n} corners.".format(images=self.calibrate_count, n=self.n))
            if self.calibrate_count == 30:
                log.info("Captured sufficient calibration data!")
                self.calibrating = False
                self.imsize = self.numpy_image[:,:,0].shape
                ret, camera_matrix, dist_coeff, rvecs, tvecs, stdIntrinsic, stdExtrinsic, errors = cv2.aruco.calibrateCameraCharucoExtended(self.corners, self.ids, self.board, self.imsize, None, None)
                print(ret)
                print(camera_matrix)
                print(dist_coeff)
                print(self.coverage.shape)
                print(stdIntrinsic)
                print(stdExtrinsic)
                print(errors)
                for index, rvec in enumerate(rvecs):
                    tvec = tvecs[index]
                    corners = self.corners[index]
                    ids = self.ids[index]
                    objPoints, imgPoints = cv2.aruco.getBoardObjectAndImagePoints(self.board, corners, ids)
                    # _, rvec, tvec = cv2.solvePnP(objPoints, imgPoints, camera_matrix, dist_coeff)
                    projectedPoints, _ = cv2.projectPoints(objPoints, rvec, tvec, camera_matrix, dist_coeff)
                    error = imgPoints - projectedPoints
                    for j in range(len(error)):
                        pt_error = error[j]
                        plt.scatter(pt_error[0,0], pt_error[0,1])
                        # plt.scatter(projectedPoints[:,0,1], imgPoints[:,0,1])
                    # print(projectedPoints.shape)
                    # print(imgPoints.shape)    
                plt.show()
                # coverage = Image.fromarray(self.coverage.astype(np.uint8))
                # coverage.show()
        return

    def updateUI(self):
        """Update UI for automatically adjusted settings."""
        # If in auto exposure mode, update the exposure time.
        _, enum = self.cam.ExposureAuto.get()
        if enum != "Off":
            value = self.cam.ExposureTime.get()
            self.updateExposureTime.emit(value)
        # If in auto gain mode, update the gain.
        _, enum = self.cam.GainAuto.get()
        if enum != "Off":
            value = self.cam.Gain.get()
            self.updateGain.emit(value)
        # If in maximum acquisition rate mode, update the acquisition rate.
        _, enum = self.cam.AcquisitionFrameRateMode.get()
        if enum == "Off":
            rate = self.cam.CurrentAcquisitionFrameRate.get()
            self.updateAcquisitionRate.emit(rate)
        
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
        try:
            if self.cam.PixelColorFilter.is_implemented() is False and mode == "RGB":
                self.mode = "Mono"
            else:
                self.mode = mode
            log.info("Image mode on {device} set to {mode}.".format(device=self.name, mode=mode))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

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
            _, enum = self.cam.ExposureAuto.get()
            if enum == "Off":
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
            _, enum = self.cam.GainAuto.get()
            if enum == "Off":
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
                log.info("Binning turned Off.")
            elif mode == "Average":
                self.cam.BinningHorizontalMode.set(gx.GxBinningHorizontalModeEntry.AVERAGE)
                self.cam.BinningVerticalMode.set(gx.GxBinningHorizontalModeEntry.AVERAGE)
                log.info("Binning set to Average mode.")
            elif mode == "Sum":
                self.cam.BinningHorizontalMode.set(gx.GxBinningHorizontalModeEntry.SUM)
                self.cam.BinningVerticalMode.set(gx.GxBinningHorizontalModeEntry.SUM)
                log.info("Binning set to Sum mode.")
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
            if mode == "Maximum":
                self.cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.OFF)
                log.info("Acquisition mode set to Maximum.")
            elif mode == "Defined":
                self.cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.ON)
                log.info("Acquisition rate set to Defined.")
            elif mode == "Triggered":
                self.cam.AcquisitionFrameRateMode.set(gx.GxSwitchEntry.OFF)
                log.info("Acquisition mode set to Triggered.")
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(float)
    def set_acquisition_rate(self, value):
        try:
            _, enum = self.cam.AcquisitionFrameRateMode.get()
            if enum == "Off":
                self.cam.AcquisitionFrameRate.set(value)
                log.info("Acquisition rate set to {value} Hz.".format(value=value))
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


