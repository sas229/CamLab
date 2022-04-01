from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator

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
    setAcquisitionRate = Signal(int)
    
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        self.settingsGroupBox = QGroupBox("Image Capture Settings")
        self.calibrationGroupBox = QGroupBox("Calibration and Tracking")

        # Image capture settings widgets.
        self.imageModeLabel = QLabel("Image Mode")

        self.imageModeComboBox = QComboBox()
        self.imageModeComboBox.addItems(["RGB", "Mono"])
        self.imageModeComboBox.setFixedWidth(140)
        self.imageModeComboBox.setCurrentIndex(1)

        self.autoExposureLabel = QLabel("Auto Exposure")
        
        self.autoExposureComboBox = QComboBox()
        self.autoExposureComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoExposureComboBox.setFixedWidth(140)
        self.autoExposureComboBox.setCurrentIndex(0)

        self.exposureTimeLabel = QLabel("Exposure Time (us)")
        
        self.exposureTimeLineEdit = QLineEdit()
        self.exposureTimeLineEdit.setEnabled(False)
        self.exposureTimeLineEdit.setFixedWidth(140)
        self.exposureTimeValidator = QIntValidator(bottom=24, top=1000000)
        self.exposureTimeLineEdit.setValidator(self.exposureTimeValidator)
        self.exposureTimeLineEdit.setText("10000")

        self.autoGainLabel = QLabel("Auto Gain")

        self.autoGainComboBox = QComboBox()
        self.autoGainComboBox.addItems(["On", "Off"])
        self.autoGainComboBox.setFixedWidth(140)
        self.autoGainComboBox.setCurrentIndex(0)

        self.gainLabel = QLabel("Gain (dB)")

        self.gainLineEdit = QLineEdit()
        self.gainLineEdit.setEnabled(False)
        self.gainLineEdit.setFixedWidth(140)
        self.gainLineEdit.setText("0.00")
        self.gainValidator = QDoubleValidator(bottom=0.00, top=24.00, decimals=2)
        self.gainLineEdit.setValidator(self.gainValidator)

        self.binningModeLabel = QLabel("Binning")

        self.binningModeComboBox = QComboBox()
        self.binningModeComboBox.addItems(["Off", "Average", "Sum"])
        self.binningModeComboBox.setFixedWidth(140)
        self.binningModeComboBox.setCurrentIndex(0)

        self.binningValueLabel = QLabel("Value")
        
        self.binningValueComboBox = QComboBox()
        self.binningValueComboBox.addItems(["1", "2", "4"])
        self.binningValueComboBox.setCurrentIndex(0)
        self.binningValueComboBox.setFixedWidth(140)
        self.binningValueComboBox.setEnabled(False)

        self.autoWhiteBalanceLabel = QLabel("Auto White Balance")

        self.autoWhiteBalanceComboBox = QComboBox()
        self.autoWhiteBalanceComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoWhiteBalanceComboBox.setFixedWidth(140)
        self.autoWhiteBalanceComboBox.setCurrentIndex(0)

        # Calibration and tracking widgets. 
        self.calibrateButton = QPushButton("Calibrate")
        # self.calibrateButton.setCheckable(True)
        self.calibrateButton.setFixedWidth(140)

        self.trackingButton = QPushButton("Tracking")
        self.trackingButton.setCheckable(True)
        self.trackingButton.setFixedWidth(140)
        # self.trackingButton.setEnabled(False)

        self.trackingLabel = QLabel("Tracking")

        self.trackingComboBox = QComboBox()
        self.trackingComboBox.addItems(["Off", "On"])
        self.trackingComboBox.setFixedWidth(140)
        self.trackingComboBox.setCurrentIndex(0)

        self.dictionaryLabel = QLabel("Dictionary")

        self.dictionaryComboBox = QComboBox()
        self.dictionaryComboBox.addItems(["N/A", "DICT_4X4_50", "DICT_4X4_100", "DICT_4X4_250", "DICT_4X4_1000"])
        self.dictionaryComboBox.setFixedWidth(140)
        self.dictionaryComboBox.setCurrentIndex(0)
        self.dictionaryComboBox.setEnabled(False)

        self.calibrationLabel = QLabel("Calibration")

        self.calibrationModelComboBox = QComboBox()
        self.calibrationModelComboBox.addItems(["N/A", "4", "5", "8", "12", "14"])
        self.calibrationModelComboBox.setFixedWidth(140)
        self.calibrationModelComboBox.setCurrentIndex(0)
        self.calibrationModelComboBox.setEnabled(False)

        self.acquisitionModeLabel = QLabel("Acquisition Mode")

        self.acquisitionModeComboBox = QComboBox()
        self.acquisitionModeComboBox.addItems(["Max", "Defined"])
        self.acquisitionModeComboBox.setFixedWidth(140)
        self.acquisitionModeComboBox.setCurrentIndex(0)

        self.acquisitionRateLabel = QLabel("Rate (Hz)")

        self.acquisitionRateLineEdit = QLineEdit()
        self.acquisitionRateLineEdit.setEnabled(False)
        self.acquisitionRateLineEdit.setFixedWidth(140)
        self.acquisitionRateLineEdit.setText("10.00")
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

        self.calibrationGroupBoxLayout.addWidget(self.calibrateButton, 0, 0)

        self.calibrationGroupBoxLayout.addWidget(self.trackingButton, 1, 0)

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
        self.imageModeComboBox.currentTextChanged.connect(self.get_image_mode)
        self.autoWhiteBalanceComboBox.currentTextChanged.connect(self.get_auto_white_balance_mode)
        self.autoExposureComboBox.currentTextChanged.connect(self.get_auto_exposure_mode)
        self.exposureTimeLineEdit.returnPressed.connect(self.get_exposure_time)
        self.gainLineEdit.returnPressed.connect(self.get_gain)
        self.autoGainComboBox.currentTextChanged.connect(self.get_auto_gain)
        self.binningModeComboBox.currentTextChanged.connect(self.get_binning_mode)
        self.binningValueComboBox.currentTextChanged.connect(self.get_binning)
        self.acquisitionModeComboBox.currentTextChanged.connect(self.get_acquisition_mode)
        self.acquisitionRateLineEdit.returnPressed.connect(self.get_acquisition_rate)
    
    @Slot(str)
    def set_acquisition_mode(self, text):
        self.acquisitionModeComboBox.setCurrentText(text)

    def get_acquisition_mode(self, text):
        self.setAcquisitionMode.emit(text)

    @Slot(str)
    def set_acquisition_rate(self, value):
        text = str(value)
        self.acquisitionRateLineEdit.setText(text)

    def get_acquisition_rate(self):
        value = float(self.acquisitionRateLineEdit.text())
        text = "{value:.2f}".format(value=value)
        self.acquisitionRateLineEdit.setText(text)
        self.setAcquisitionRate.emit(value)

    @Slot(str)
    def set_binning_mode(self, text):
        self.binningModeComboBox.setCurrentText(text)

    def get_binning_mode(self, text):
        self.setBinningMode.emit(text)

    @Slot(str)
    def set_binning(self, text):
        value = int(text)
        self.binningValueComboBox.setCurrentText(value)

    def get_binning(self, text):
        value = int(text)
        self.setBinning.emit(value)

    @Slot(str)
    def set_auto_exposure_mode(self, text):
        self.autoExposureComboBox.setCurrentText(text)

    def get_auto_exposure_mode(self, text):
        self.setAutoExposureMode.emit(text)

    @Slot(str)
    def set_auto_gain(self, text):
        self.autoGainComboBox.setCurrentText(text)

    def get_auto_gain(self, text):
        self.setAutoGain.emit(text)

    @Slot(str)
    def set_gain(self, value):
        self.gainLineEdit.setText(str(value))

    def get_gain(self):
        value = float(self.gainLineEdit.text())
        text = "{value:.2f}".format(value=value)
        self.gainLineEdit.setText(text)
        self.setGain.emit(value)

    @Slot(str)
    def set_exposure_time(self, value):
        self.exposureTimeLineEdit.setText(str(value))

    def get_exposure_time(self):
        value = int(self.exposureTimeLineEdit.text())
        self.setExposureTime.emit(value)

    @Slot(str)
    def set_auto_white_balance_mode(self, text):
        self.autoWhiteBalanceComboBox.setCurrentText(text)

    def get_auto_white_balance_mode(self, text):
        self.setAutoWhiteBalanceMode.emit(text)

    @Slot(str)
    def set_image_mode(self, text):
        self.imageModeComboBox.setCurrentText(text)

    def get_image_mode(self, text):
        self.setImageMode.emit(text)

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