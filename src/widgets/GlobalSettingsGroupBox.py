from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QGridLayout, QFrame, QFileDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Signal, Slot
import logging

log = logging.getLogger(__name__)

class GlobalSettingsGroupBox(QGroupBox):
    darkModeChanged = Signal(bool)
    acquisitionRateChanged = Signal(str)
    controlRateChanged = Signal(str)
    averageSamplesChanged = Signal(str)
    pathChanged = Signal(str)
    filenameChanged = Signal(str)

    def __init__(self, configuration):
        super().__init__() 
        self.configuration = configuration
        self.setTitle("Global Settings")

        # Set path inputs.
        self.setPathLabel = QLabel("Output")
        self.setPathButton = QPushButton("Set Path")
        self.setPathAddressLabel = QLineEdit()
        self.setPathAddressLabel.setText(self.configuration["global"]["path"])
        self.setPathAddressLabel.setEnabled(False)
        self.setFilenameLineEdit = QLineEdit()
        self.setFilenameLineEdit.setText(self.configuration["global"]["filename"])

        # Control rate input and validator.
        self.controlRateLabel = QLabel("Control Rate (Hz)")
        self.controlRateLineEdit = QLineEdit()
        self.controlRateValidator = QDoubleValidator(bottom = 0.10, top = 1000.00, decimals=2)
        self.controlRateLineEdit.setValidator(self.controlRateValidator)
        self.controlRateLineEdit.setText(str(self.configuration["global"]["controlRate"]))

        # Acquisition rate input and validator.
        self.acquisitionRateLabel = QLabel("Acquisition Rate (Hz)")
        self.acquisitionRateLineEdit = QLineEdit()
        self.acquisitionRateValidator = QDoubleValidator(bottom = 0.01, top = 100.00, decimals=2)
        self.acquisitionRateLineEdit.setValidator(self.acquisitionRateValidator)
        self.acquisitionRateLineEdit.setText(str(self.configuration["global"]["acquisitionRate"]))

        # Sample averaging and validator.
        self.averageSamplesLabel = QLabel("Samples to average (-)")
        self.averageSamplesLineEdit = QLineEdit()
        self.averageSamplesValidator = QIntValidator(bottom = 1, top = 100)
        self.averageSamplesLineEdit.setValidator(self.averageSamplesValidator)
        self.averageSamplesLineEdit.setText(str(self.configuration["global"]["averageSamples"]))

        # Horizontal separator.
        self.horizontalSeparator = QFrame()
        self.horizontalSeparator.setFrameShape(QFrame.HLine)
        self.horizontalSeparator.setFixedHeight(4)
        self.horizontalSeparator.setFrameShadow(QFrame.Sunken)

        # Vertical separator.
        self.verticalSeparator = QFrame()
        self.verticalSeparator.setFrameShape(QFrame.VLine)
        self.verticalSeparator.setFixedHeight(2)
        self.verticalSeparator.setFrameShadow(QFrame.Sunken)

        # Assemble path layout.
        self.setPathLayout = QHBoxLayout()
        self.setPathLayout.addWidget(self.setPathButton)
        self.setPathLayout.addWidget(self.setPathAddressLabel, 4)
        self.setPathLayout.addWidget(self.setFilenameLineEdit)

        # Assemble rates layout.
        self.ratesLayout = QGridLayout()
        self.ratesLayout.addWidget(self.controlRateLabel, 0, 0)
        self.ratesLayout.addWidget(self.controlRateLineEdit, 1, 0)
        self.ratesLayout.addWidget(self.acquisitionRateLabel, 0, 1)
        self.ratesLayout.addWidget(self.acquisitionRateLineEdit, 1, 1)
        self.ratesLayout.addWidget(self.averageSamplesLabel, 0, 2)
        self.ratesLayout.addWidget(self.averageSamplesLineEdit, 1, 2)
        
        # Assemble nested layouts.
        self.globalSettingsVLayout = QVBoxLayout()
        self.globalSettingsVLayout.addLayout(self.ratesLayout)
        self.globalSettingsVLayout.addWidget(self.horizontalSeparator)
        self.globalSettingsVLayout.addWidget(self.setPathLabel)
        self.globalSettingsVLayout.addLayout(self.setPathLayout)

        # Set global settings groupbox layout.
        self.setLayout(self.globalSettingsVLayout)

        # Connections.
        self.acquisitionRateLineEdit.editingFinished.connect(self.emitAcquisitionRate)
        self.controlRateLineEdit.editingFinished.connect(self.emitControlRate)
        self.averageSamplesLineEdit.editingFinished.connect(self.emitAverageSamples)
        self.setPathButton.clicked.connect(self.emitPath)
        self.setFilenameLineEdit.editingFinished.connect(self.emitFilename)
    
    @Slot()
    def updateUI(self, newConfiguration):
        # Method to update UI after configuration changes.
        self.configuration = newConfiguration
        self.acquisitionRateLineEdit.setText(str(self.configuration["global"]["acquisitionRate"]))
        self.controlRateLineEdit.setText(str(self.configuration["global"]["controlRate"]))
        self.averageSamplesLineEdit.setText(str(self.configuration["global"]["averageSamples"]))
        self.setPathAddressLabel.setText(self.configuration["global"]["path"])
        self.setFilenameLineEdit.setText(self.configuration["global"]["filename"])

    def emitAcquisitionRate(self):
        # Method to emit the new acquisition rate.
        newAcquisitionRate =self.acquisitionRateLineEdit.text()
        self.acquisitionRateChanged.emit(newAcquisitionRate)

    def emitControlRate(self):
        # Method to emit the new control rate.
        newControlRate =self.controlRateLineEdit.text()
        self.controlRateChanged.emit(newControlRate)
    
    def emitAverageSamples(self):
        # Method to emit the new number of samples to average.
        newAverageSamples =self.averageSamplesLineEdit.text()
        self.averageSamplesChanged.emit(newAverageSamples)

    def emitPath(self):
        # Method to emit the new path.
        loadPath = QFileDialog.getExistingDirectory(self, 'Select the directory in which to save data')
        self.setPathAddressLabel.setText(loadPath)
        self.pathChanged.emit(loadPath)

    def emitFilename(self):
        # Method to emit the new filename.
        newFilename =self.setFilenameLineEdit.text()
        self.filenameChanged.emit(newFilename)