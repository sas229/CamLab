from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QComboBox, QLineEdit, QSpinBox, QPushButton
from PySide6.QtCore import Slot, Signal

class CameraSettings(QWidget):
    showCameraPreview = Signal(str)
    hideCameraPreview = Signal(str)
    
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name

        self.settingsGroupBox = QGroupBox("Image Capture Settings")
        self.previewGroupBox = QGroupBox("Preview, Calibration and Tracking")

        # Image capture settings widgets.
        self.imageModeLabel = QLabel("Image Mode")

        self.imageModeComboBox = QComboBox()
        self.imageModeComboBox.addItems(["RGB", "Mono"])
        self.imageModeComboBox.setFixedWidth(150)
        self.imageModeComboBox.setCurrentIndex(0)

        self.autoExposureLabel = QLabel("Auto Exposure")
        
        self.autoExposureComboBox = QComboBox()
        self.autoExposureComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoExposureComboBox.setFixedWidth(150)
        self.autoExposureComboBox.setCurrentIndex(0)

        self.exposureTimeLabel = QLabel("Exposure Time (us)")
        
        self.exposureTimeLineEdit = QLineEdit()
        self.exposureTimeLineEdit.setEnabled(False)
        self.exposureTimeLineEdit.setFixedWidth(150)
        self.exposureTimeLineEdit.setText("10000")

        self.autoGainLabel = QLabel("Auto Gain")

        self.autoGainComboBox = QComboBox()
        self.autoGainComboBox.addItems(["On", "Off"])
        self.autoGainComboBox.setFixedWidth(150)
        self.autoGainComboBox.setCurrentIndex(0)

        self.gainLabel = QLabel("Gain (dB)")

        self.gainLineEdit = QLineEdit()
        self.gainLineEdit.setEnabled(False)
        self.gainLineEdit.setFixedWidth(150)
        self.gainLineEdit.setText("1")

        self.binningModeLabel = QLabel("Binning")

        self.binningModeComboBox = QComboBox()
        self.binningModeComboBox.addItems(["Off", "Average", "Sum"])
        self.binningModeComboBox.setFixedWidth(150)
        self.binningModeComboBox.setCurrentIndex(0)

        self.binningValueLabel = QLabel("Value")
        
        self.binningValueSpinBox = QSpinBox()
        self.binningValueSpinBox.setMinimum(1)
        self.binningValueSpinBox.setMaximum(4)
        self.binningValueSpinBox.setValue(1)
        self.binningValueSpinBox.setFixedWidth(150)
        self.binningValueSpinBox.setEnabled(False)

        self.autoWhiteBalanceLabel = QLabel("Auto White Balance")

        self.autoWhiteBalanceComboBox = QComboBox()
        self.autoWhiteBalanceComboBox.addItems(["Continuous", "Once", "Off"])
        self.autoWhiteBalanceComboBox.setFixedWidth(150)
        self.autoWhiteBalanceComboBox.setCurrentIndex(0)

        # Calibration and tracking widgets. 
        self.previewButton = QPushButton("Preview")
        self.previewButton.setCheckable(True)
        self.previewButton.setFixedWidth(150)

        self.calibrateButton = QPushButton("Calibrate")
        # self.calibrateButton.setCheckable(True)
        self.calibrateButton.setFixedWidth(150)

        self.trackingButton = QPushButton("Tracking")
        self.trackingButton.setCheckable(True)
        self.trackingButton.setFixedWidth(150)
        # self.trackingButton.setEnabled(False)

        self.trackingLabel = QLabel("Tracking")

        self.trackingComboBox = QComboBox()
        self.trackingComboBox.addItems(["Off", "On"])
        self.trackingComboBox.setFixedWidth(150)
        self.trackingComboBox.setCurrentIndex(0)

        self.dictionaryLabel = QLabel("Dictionary")

        self.dictionaryComboBox = QComboBox()
        self.dictionaryComboBox.addItems(["N/A", "DICT_4X4_50", "DICT_4X4_100", "DICT_4X4_250", "DICT_4X4_1000"])
        self.dictionaryComboBox.setFixedWidth(150)
        self.dictionaryComboBox.setCurrentIndex(0)
        self.dictionaryComboBox.setEnabled(False)

        self.calibrationLabel = QLabel("Calibration")

        self.calibrationModelComboBox = QComboBox()
        self.calibrationModelComboBox.addItems(["N/A", "4", "5", "8", "12", "14"])
        self.calibrationModelComboBox.setFixedWidth(150)
        self.calibrationModelComboBox.setCurrentIndex(0)
        self.calibrationModelComboBox.setEnabled(False)

        # Settings layout.
        self.settingsGroupBoxLayout = QGridLayout()

        self.settingsGroupBoxLayout.addWidget(self.imageModeLabel, 0, 0)
        self.settingsGroupBoxLayout.addWidget(self.autoGainLabel, 0, 1)
        self.settingsGroupBoxLayout.addWidget(self.autoExposureLabel, 0, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningModeLabel, 0, 3)

        self.settingsGroupBoxLayout.addWidget(self.imageModeComboBox, 1, 0)
        self.settingsGroupBoxLayout.addWidget(self.autoGainComboBox, 1, 1)
        self.settingsGroupBoxLayout.addWidget(self.autoExposureComboBox, 1, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningModeComboBox, 1, 3)

        self.settingsGroupBoxLayout.addWidget(self.autoWhiteBalanceLabel, 2, 0)
        self.settingsGroupBoxLayout.addWidget(self.gainLabel, 2, 1)
        self.settingsGroupBoxLayout.addWidget(self.exposureTimeLabel, 2, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningValueLabel, 2, 3)

        self.settingsGroupBoxLayout.addWidget(self.autoWhiteBalanceComboBox, 3, 0)
        self.settingsGroupBoxLayout.addWidget(self.gainLineEdit, 3, 1)
        self.settingsGroupBoxLayout.addWidget(self.exposureTimeLineEdit, 3, 2)
        self.settingsGroupBoxLayout.addWidget(self.binningValueSpinBox, 3, 3)

        self.settingsGroupBox.setLayout(self.settingsGroupBoxLayout)

        # Calibration and tracking layout.
        self.previewGroupBoxLayout = QGridLayout()

        self.previewGroupBoxLayout.addWidget(self.previewButton, 0, 0)

        self.previewGroupBoxLayout.addWidget(self.calibrateButton, 1, 0)

        self.previewGroupBoxLayout.addWidget(self.trackingButton, 2, 0)

        # self.previewGroupBoxLayout.addWidget(self.trackingLabel, n, 0)
        # self.previewGroupBoxLayout.addWidget(self.dictionaryLabel, n, 1)

        # self.previewGroupBoxLayout.addWidget(self.trackingComboBox, n, 0)
        # self.previewGroupBoxLayout.addWidget(self.dictionaryComboBox, n, 1)
        
        self.previewGroupBox.setLayout(self.previewGroupBoxLayout)

        # Main layout.
        self.layout = QVBoxLayout()

        self.layout.addWidget(self.settingsGroupBox)
        self.layout.addWidget(self.previewGroupBox)

        self.setLayout(self.layout)

        # Connections.
        self.autoExposureComboBox.currentIndexChanged.connect(self.toggle_exposure_time)
        self.autoGainComboBox.currentIndexChanged.connect(self.toggle_gain)
        self.binningModeComboBox.currentIndexChanged.connect(self.toggle_binning)
        self.trackingComboBox.currentIndexChanged.connect(self.toggle_dictionary)
        self.previewButton.clicked.connect(self.toggle_preview)

    def toggle_preview(self):
        if self.previewButton.isChecked() == True:
            self.showCameraPreview.emit(self.name)
        elif self.previewButton.isChecked() == False:
            self.hideCameraPreview.emit(self.name)

    def toggle_exposure_time(self, index):
        if index == 2:
            self.exposureTimeLineEdit.setEnabled(True)
        else:
            self.exposureTimeLineEdit.setEnabled(False)
    
    def toggle_gain(self, index):
        if index == 1:
            self.gainLineEdit.setEnabled(True)
        else:
            self.gainLineEdit.setEnabled(False)
    
    def toggle_binning(self, index):
        if index == 0:
            self.binningValueSpinBox.setEnabled(False)
        else:
            self.binningValueSpinBox.setEnabled(True)

    def toggle_dictionary(self, index):
        if index == 1:
            self.dictionaryComboBox.setEnabled(True)
        else:
            self.dictionaryComboBox.setEnabled(False)