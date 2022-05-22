from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
import logging

log = logging.getLogger(__name__)

class CameraSettings(QWidget):
    setImageMode = Signal(str)
    setAutoWhiteBalanceMode = Signal(str) 
    setAutoExposureMode = Signal(str) 
    setExposureTime = Signal(int) 
    setGain = Signal(float) 
    setAutoGain = Signal(str) 
    setBinningMode = Signal(str)
    setBinning = Signal(int)
    setAcquisitionMode = Signal(str)
    setAcquisitionRate = Signal(float)
    
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        self.settingsGroupBox = QGroupBox("Image Capture Settings")
        self.calibrationGroupBox = QGroupBox("Calibration and Tracking")

        # Image capture settings widgets.
        self.imageModeLabel = QLabel("Image Mode")

        self.imageModeComboBox = QComboBox()
        self.imageModeComboBox.addItems(["RGB", "Mono"])
        self.imageModeComboBox.setFixedWidth(130)
        self.imageModeComboBox.setCurrentIndex(1)

        self.autoExposureLabel = QLabel("Auto Exposure")
        
        self.autoExposureComboBox = QComboBox()
        self.autoExposureComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoExposureComboBox.setFixedWidth(130)
        self.autoExposureComboBox.setCurrentIndex(0)

        self.exposureTimeLabel = QLabel("Exposure Time (us)")
        
        self.exposureTimeLineEdit = QLineEdit()
        self.exposureTimeLineEdit.setEnabled(False)
        self.exposureTimeLineEdit.setFixedWidth(130)
        self.exposureTimeValidator = QIntValidator(bottom=24, top=1000000)
        self.exposureTimeLineEdit.setValidator(self.exposureTimeValidator)
        self.exposureTimeLineEdit.setText("10000")

        self.autoGainLabel = QLabel("Auto Gain")

        self.autoGainComboBox = QComboBox()
        self.autoGainComboBox.addItems(["On", "Off"])
        self.autoGainComboBox.setFixedWidth(130)
        self.autoGainComboBox.setCurrentIndex(0)

        self.gainLabel = QLabel("Gain (dB)")

        self.gainLineEdit = QLineEdit()
        self.gainLineEdit.setEnabled(False)
        self.gainLineEdit.setFixedWidth(130)
        self.gainValidator = QDoubleValidator(bottom=0.00, top=24.00, decimals=2)
        self.gainLineEdit.setValidator(self.gainValidator)

        self.binningModeLabel = QLabel("Binning")

        self.binningModeComboBox = QComboBox()
        self.binningModeComboBox.addItems(["Off", "Average", "Sum"])
        self.binningModeComboBox.setFixedWidth(130)
        self.binningModeComboBox.setCurrentIndex(0)

        self.binningValueLabel = QLabel("Value (-)")
        
        self.binningValueComboBox = QComboBox()
        self.binningValueComboBox.addItems(["1", "2", "4"])
        self.binningValueComboBox.setCurrentIndex(0)
        self.binningValueComboBox.setFixedWidth(130)
        self.binningValueComboBox.setEnabled(False)

        self.autoWhiteBalanceLabel = QLabel("Auto White Balance")

        self.autoWhiteBalanceComboBox = QComboBox()
        self.autoWhiteBalanceComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoWhiteBalanceComboBox.setFixedWidth(130)
        self.autoWhiteBalanceComboBox.setCurrentIndex(0)

        # Calibration and tracking widgets. 
        self.calibrateButton = QPushButton("Calibrate")
        # self.calibrateButton.setCheckable(True)
        self.calibrateButton.setFixedWidth(130)

        self.trackingButton = QPushButton("Tracking")
        self.trackingButton.setCheckable(True)
        self.trackingButton.setFixedWidth(130)
        # self.trackingButton.setEnabled(False)

        self.trackingLabel = QLabel("Tracking")

        self.trackingComboBox = QComboBox()
        self.trackingComboBox.addItems(["Off", "On"])
        self.trackingComboBox.setFixedWidth(130)
        self.trackingComboBox.setCurrentIndex(0)

        self.dictionaryLabel = QLabel("Dictionary")

        self.dictionaryComboBox = QComboBox()
        self.dictionaryComboBox.addItems(["N/A", "DICT_4X4_50", "DICT_4X4_100", "DICT_4X4_250", "DICT_4X4_1000"])
        self.dictionaryComboBox.setFixedWidth(130)
        self.dictionaryComboBox.setCurrentIndex(0)
        self.dictionaryComboBox.setEnabled(False)

        self.calibrationLabel = QLabel("Calibration")

        self.calibrationModelComboBox = QComboBox()
        self.calibrationModelComboBox.addItems(["N/A", "4", "5", "8", "12", "14"])
        self.calibrationModelComboBox.setFixedWidth(130)
        self.calibrationModelComboBox.setCurrentIndex(0)
        self.calibrationModelComboBox.setEnabled(False)

        self.acquisitionModeLabel = QLabel("Acquisition Rate")

        self.acquisitionModeComboBox = QComboBox()
        self.acquisitionModeComboBox.addItems(["Maximum", "Defined", "Triggered"])
        self.acquisitionModeComboBox.setFixedWidth(130)
        self.acquisitionModeComboBox.setCurrentIndex(0)

        self.acquisitionRateLabel = QLabel("Frequency (Hz)")

        self.acquisitionRateLineEdit = QLineEdit()
        self.acquisitionRateLineEdit.setEnabled(False)
        self.acquisitionRateLineEdit.setFixedWidth(130)
        self.acquisitionRateValidator = QDoubleValidator(bottom=0.01, top=24.00, decimals=2)
        self.acquisitionRateLineEdit.setValidator(self.acquisitionRateValidator)

        # Settings layout.
        self.settingsGroupBoxLayout = QGridLayout()

        self.settingsGroupBoxLayout.addWidget(self.imageModeLabel, 0, 0)
        self.settingsGroupBoxLayout.addWidget(self.autoGainLabel, 0, 1)
        self.settingsGroupBoxLayout.addWidget(self.autoExposureLabel, 0, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningModeLabel, 0, 3)
        self.settingsGroupBoxLayout.addWidget(self.acquisitionModeLabel, 0, 4)

        self.settingsGroupBoxLayout.addWidget(self.imageModeComboBox, 1, 0)
        self.settingsGroupBoxLayout.addWidget(self.autoGainComboBox, 1, 1)
        self.settingsGroupBoxLayout.addWidget(self.autoExposureComboBox, 1, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningModeComboBox, 1, 3)
        self.settingsGroupBoxLayout.addWidget(self.acquisitionModeComboBox, 1, 4)

        self.settingsGroupBoxLayout.addWidget(self.autoWhiteBalanceLabel, 2, 0)
        self.settingsGroupBoxLayout.addWidget(self.gainLabel, 2, 1)
        self.settingsGroupBoxLayout.addWidget(self.exposureTimeLabel, 2, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningValueLabel, 2, 3)
        self.settingsGroupBoxLayout.addWidget(self.acquisitionRateLabel, 2, 4)

        self.settingsGroupBoxLayout.addWidget(self.autoWhiteBalanceComboBox, 3, 0)
        self.settingsGroupBoxLayout.addWidget(self.gainLineEdit, 3, 1)
        self.settingsGroupBoxLayout.addWidget(self.exposureTimeLineEdit, 3, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningValueComboBox, 3, 3)
        self.settingsGroupBoxLayout.addWidget(self.acquisitionRateLineEdit, 3, 4)

        self.settingsGroupBox.setLayout(self.settingsGroupBoxLayout)

        # Calibration and tracking layout.
        self.calibrationGroupBoxLayout = QGridLayout()

        # self.calibrationGroupBoxLayout.addWidget(self.calibrateButton, 0, 0)

        # self.calibrationGroupBoxLayout.addWidget(self.trackingButton, 1, 0)

        # self.calibrationGroupBoxLayout.addWidget(self.trackingLabel, n, 0)
        # self.calibrationGroupBoxLayout.addWidget(self.dictionaryLabel, n, 1)

        # self.calibrationGroupBoxLayout.addWidget(self.trackingComboBox, n, 0)
        # self.calibrationGroupBoxLayout.addWidget(self.dictionaryComboBox, n, 1)
        
        self.calibrationGroupBox.setLayout(self.calibrationGroupBoxLayout)

        # Main layout.
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.settingsGroupBox)
        self.layout.addWidget(self.calibrationGroupBox)

        self.setLayout(self.layout)

        # Connections.
        self.autoExposureComboBox.currentTextChanged.connect(self.toggle_exposure_time)
        self.autoGainComboBox.currentTextChanged.connect(self.toggle_gain)
        self.binningModeComboBox.currentTextChanged.connect(self.toggle_binning)
        self.trackingComboBox.currentIndexChanged.connect(self.toggle_dictionary)
        self.acquisitionModeComboBox.currentIndexChanged.connect(self.toggle_acquisition_rate)

        self.exposureTimeLineEdit.returnPressed.connect(self.set_exposure_time)
        self.acquisitionRateLineEdit.returnPressed.connect(self.set_acquisition_rate)
        self.gainLineEdit.returnPressed.connect(self.set_gain)
    
    def setConfiguration(self, configuration):
        """Set the configuration."""
        self.configuration = configuration
        self.cameraConfiguration = self.configuration["devices"][self.name]["settings"]
        self.setWindowTitle(self.name)
        self.initialise_auto_white_balance_mode(self.cameraConfiguration["autoWhiteBalance"])
        self.initialise_acquisition_mode(self.cameraConfiguration["acquisitionMode"])
        self.initialise_acquisition_rate(self.cameraConfiguration["acquisitionRate"])
        self.initialise_binning_mode(self.cameraConfiguration["binningMode"])
        self.initialise_binning(self.cameraConfiguration["binningValue"])
        self.initialise_auto_exposure_mode(self.cameraConfiguration["autoExposureMode"])
        self.initialise_auto_gain(self.cameraConfiguration["autoGain"])
        self.initialise_gain(self.cameraConfiguration["gain"])
        self.initialise_image_mode(self.cameraConfiguration["imageMode"])

    def initialise_acquisition_mode(self, text):
        self.setAcquisitionMode.emit(text)
        self.acquisitionModeComboBox.setCurrentText(text)
        self.acquisitionModeComboBox.currentTextChanged.connect(self.set_acquisition_mode)
        log.info("Acquisition mode on {device} set to {text}.".format(device=self.name, text=text))

    @Slot(str)
    def set_acquisition_mode(self, text):
        self.setAcquisitionMode.emit(text)
        self.cameraConfiguration["acquisitionMode"] = text
        log.info("Acquisition mode on {device} set to {text} in configuration.".format(device=self.name, text=text))

    def initialise_acquisition_rate(self, value):
        self.setAcquisitionRate.emit(value)
        text = "{value:.2f}".format(value=value)
        self.acquisitionRateLineEdit.setText(text)
        if self.cameraConfiguration["acquisitionMode"] == "Defined":
            log.info("Acquisition rate on {device} set to {text} Hz.".format(device=self.name, text=text))

    @Slot(float)
    def set_acquisition_rate(self):
        value = float(self.acquisitionRateLineEdit.text())
        text = "{value:.2f}".format(value=value)
        self.acquisitionRateLineEdit.setText(text)
        self.setAcquisitionRate.emit(value)
        self.cameraConfiguration["acquisitionRate"] = value
        log.info("Acquisition rate on {device} set to {text} Hz in configuration.".format(device=self.name, text=text))

    @Slot(float)
    def update_acquisition_rate(self, value):
        text = "{value:.2f}".format(value=value)
        self.acquisitionRateLineEdit.setText(text)
        
    def initialise_binning_mode(self, text):
        self.setBinningMode.emit(text)
        self.binningModeComboBox.setCurrentText(text)
        self.binningModeComboBox.currentTextChanged.connect(self.set_binning_mode)
        log.info("Binning mode on {device} set to {text}.".format(device=self.name, text=text))

    @Slot(str)
    def set_binning_mode(self, text):
        self.setBinningMode.emit(text)
        self.cameraConfiguration["binningMode"] = text
        log.info("Binning mode on {device} set to {text} in configuration.".format(device=self.name, text=text))

    def initialise_binning(self, value):
        self.setBinning.emit(value)        
        text = str(value)
        self.binningValueComboBox.setCurrentText(text)
        self.binningValueComboBox.currentTextChanged.connect(self.set_binning)
        log.info("Binning value on {device} set to {value}.".format(device=self.name, value=value))

    @Slot(str)
    def set_binning(self, text):
        value = int(text)
        self.setBinning.emit(value)
        self.cameraConfiguration["binningValue"] = value
        log.info("Binning value on {device} set to {value} in configuration.".format(device=self.name, value=value))

    def initialise_auto_exposure_mode(self, text):
        self.setAutoExposureMode.emit(text)
        self.autoExposureComboBox.setCurrentText(text)
        self.autoExposureComboBox.currentTextChanged.connect(self.set_auto_exposure_mode)
        log.info("Auto exposure mode on {device} set to {text}.".format(device=self.name, text=text))

    @Slot(str)
    def set_auto_exposure_mode(self, text):
        self.setAutoExposureMode.emit(text)
        self.cameraConfiguration["autoExposureMode"] = text
        log.info("Auto exposure mode on {device} set to {text} in configuration.".format(device=self.name, text=text))

    def initialise_auto_gain(self, text):
        self.setAutoGain.emit(text)
        self.autoGainComboBox.setCurrentText(text)
        self.autoGainComboBox.currentTextChanged.connect(self.set_auto_gain)
        if self.cameraConfiguration["autoGain"] == "Off":
            log.info("Auto gain mode on {device} set to {text}.".format(device=self.name, text=text))

    @Slot(str)
    def set_auto_gain(self, text):
        self.setAutoGain.emit(text)
        self.cameraConfiguration["autoGain"] = text
        log.info("Auto gain mode on {device} set to {text} in configuration.".format(device=self.name, text=text))

    def initialise_gain(self, value):
        self.setGain.emit(value)
        text = str(value)
        self.gainLineEdit.setText(text)
        if self.cameraConfiguration["autoGain"] == "Off":
            log.info("Gain on {device} set to {text}.".format(device=self.name, text=text))

    @Slot()
    def set_gain(self):
        value = float(self.gainLineEdit.text())
        text = "{value:.2f}".format(value=value)
        self.gainLineEdit.setText(text)
        self.setGain.emit(value)
        self.cameraConfiguration["gain"] = value
        log.info("Gain mode on {device} set to {text} in configuration.".format(device=self.name, text=text))
    
    @Slot(float)
    def update_gain(self, value):
        text = "{value:.2f}".format(value=value)
        self.gainLineEdit.setText(text)

    @Slot(str)
    def update_mode(self, text):
        index = self.imageModeComboBox.findText(text)
        self.imageModeComboBox.setCurrentIndex(index)
        
    def initialise_exposure_time(self, value):
        self.setExposureTime.emit(value)
        text = str(value)
        self.exposureTimeLineEdit.setText(text)
        if self.cameraConfiguration["autoExposureMode"] == "Off":
            log.info("Exposure time on {device} set to {text} us.".format(device=self.name, text=text))

    @Slot()
    def set_exposure_time(self):
        value = int(self.exposureTimeLineEdit.text())
        self.setExposureTime.emit(value)
        self.cameraConfiguration["exposureTime"] = value
        log.info("Exposure time on {device} set to {value:.2f} in configuration.".format(device=self.name, value=value))
    
    @Slot(int)
    def update_exposure_time(self, value):
        text = "{value:d}".format(value=value)
        self.exposureTimeLineEdit.setText(text)
        
    @Slot(str)
    def initialise_auto_white_balance_mode(self, text):
        self.setAutoWhiteBalanceMode.emit(text)
        self.autoWhiteBalanceComboBox.setCurrentText(text)
        self.autoWhiteBalanceComboBox.currentTextChanged.connect(self.set_auto_white_balance_mode)
        log.info("Auto white balance on {device} set to {text}.".format(device=self.name, text=text))

    def set_auto_white_balance_mode(self, text):
        self.setAutoWhiteBalanceMode.emit(text)
        self.cameraConfiguration["autoWhiteBalance"] = text
        log.info("Auto white balance on {device} set to {text} in configuration.".format(device=self.name, text=text))

    @Slot(str)
    def initialise_image_mode(self, text):
        """Method to initialise image mode."""
        self.setImageMode.emit(text)
        self.imageModeComboBox.setCurrentText(text)
        self.imageModeComboBox.currentTextChanged.connect(self.set_image_mode)
        log.info("Image mode on {device} set to {text}.".format(device=self.name, text=text))

    def set_image_mode(self, text):
        self.setImageMode.emit(text)
        self.cameraConfiguration["imageMode"] = text
        log.info("Image mode on {device} set to {text} in configuration.".format(device=self.name, text=text))

    def toggle_exposure_time(self, text):
        if text == "Off":
            self.exposureTimeLineEdit.setEnabled(True)
        else:
            self.exposureTimeLineEdit.setEnabled(False)
    
    def toggle_gain(self, text):
        if text == "Off":
            self.gainLineEdit.setEnabled(True)
        else:
            self.gainLineEdit.setEnabled(False)
    
    def toggle_binning(self, text):
        if text == "Off":
            self.binningValueComboBox.setEnabled(False)
        else:
            self.binningValueComboBox.setEnabled(True)

    def toggle_dictionary(self, index):
        if index == 1:
            self.dictionaryComboBox.setEnabled(True)
        else:
            self.dictionaryComboBox.setEnabled(False)
    
    def toggle_acquisition_rate(self, index):
        if index == 1:
            self.acquisitionRateLineEdit.setEnabled(True)
        else:
            self.acquisitionRateLineEdit.setEnabled(False)

        