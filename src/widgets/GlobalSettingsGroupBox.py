from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QGridLayout, QFrame, QFileDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Signal, Slot
import logging

log = logging.getLogger(__name__)

class GlobalSettingsGroupBox(QGroupBox):

    def __init__(self, configuration):
        super().__init__() 
        self.globalConfiguration = configuration["global"]
        self.setTitle("Global Settings")
        self.setMinimumWidth(600)
        self.setFixedHeight(200)

        # Set path inputs.
        self.setPathLabel = QLabel("Output")
        self.setPathButton = QPushButton("Set Path")
        self.setPathAddressLineEdit = QLineEdit()
        self.setPathAddressLineEdit.setText(self.globalConfiguration["path"])
        self.setPathAddressLineEdit.setEnabled(False)
        self.setFilenameLineEdit = QLineEdit()
        self.setFilenameLineEdit.setText(self.globalConfiguration["filename"])

        # Control rate input and validator.
        self.controlRateLabel = QLabel("Control Rate (Hz)")
        self.controlRateLineEdit = QLineEdit()
        self.controlRateValidator = QDoubleValidator(bottom = 0.10, top = 1000.00, decimals=2)
        self.controlRateLineEdit.setValidator(self.controlRateValidator)
        self.controlRateLineEdit.setText(str(self.globalConfiguration["controlRate"]))

        # Skip samples input and validator.
        self.skipSamplesLabel = QLabel("Downsample (-)")
        self.skipSamplesLineEdit = QLineEdit()
        self.skipSamplesValidator = QIntValidator(bottom = 1, top = 100)
        self.skipSamplesLineEdit.setValidator(self.skipSamplesValidator)
        self.skipSamplesLineEdit.setText(str(self.globalConfiguration["skipSamples"]))

        # Sample averaging and validator.
        self.averageSamplesLabel = QLabel("Average (-)")
        self.averageSamplesLineEdit = QLineEdit()
        self.averageSamplesValidator = QIntValidator(bottom = 1, top = 100)
        self.averageSamplesLineEdit.setValidator(self.averageSamplesValidator)
        self.averageSamplesLineEdit.setText(str(self.globalConfiguration["averageSamples"]))

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
        self.setPathLayout.addWidget(self.setPathAddressLineEdit, 4)
        self.setPathLayout.addWidget(self.setFilenameLineEdit, 2)

        # Assemble rates layout.
        self.ratesLayout = QGridLayout()
        self.ratesLayout.addWidget(self.controlRateLabel, 0, 0)
        self.ratesLayout.addWidget(self.controlRateLineEdit, 1, 0)
        self.ratesLayout.addWidget(self.skipSamplesLabel, 0, 1)
        self.ratesLayout.addWidget(self.skipSamplesLineEdit, 1, 1)
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
        self.skipSamplesLineEdit.editingFinished.connect(self.update_skip_samples)
        self.controlRateLineEdit.editingFinished.connect(self.update_control_rate)
        self.averageSamplesLineEdit.editingFinished.connect(self.update_average_samples)
        self.setPathButton.clicked.connect(self.update_path)
        self.setFilenameLineEdit.editingFinished.connect(self.update_filename)
    
    @Slot()
    def set_configuration(self, newConfiguration):
        # Method to update UI after configuration changes.
        self.globalConfiguration = newConfiguration["global"]
        self.skipSamplesLineEdit.setText(str(self.globalConfiguration["skipSamples"]))
        self.controlRateLineEdit.setText(str(self.globalConfiguration["controlRate"]))
        self.averageSamplesLineEdit.setText(str(self.globalConfiguration["averageSamples"]))
        self.setPathAddressLineEdit.setText(self.globalConfiguration["path"])
        self.setFilenameLineEdit.setText(self.globalConfiguration["filename"])

    def update_skip_samples(self):
        # Method to update the new acquisition rate.
        newSkipSamples = self.skipSamplesLineEdit.text()
        self.globalConfiguration["skipSamples"] = int(newSkipSamples)
        log.info("New acquisition rate = " + str(newSkipSamples) + " Hz")

    def update_control_rate(self):
        # Method to update the new control rate.
        newControlRate = float(self.controlRateLineEdit.text())
        newControlRate = "{value:.2f}".format(value=newControlRate)
        self.controlRateLineEdit.setText(newControlRate)
        self.globalConfiguration["controlRate"] = float(newControlRate)
        log.info("New control rate = " + str(newControlRate) + " Hz")
    
    def update_average_samples(self):
        # Method to update the new number of samples to average.
        newAverageSamples =self.averageSamplesLineEdit.text()
        self.globalConfiguration["averageSamples"] = int(newAverageSamples)
        log.info("New average samples = " + newAverageSamples)

    def update_path(self):
        # Method to update the new path.
        newPath = QFileDialog.getExistingDirectory(self, 'Select the directory in which to save data')
        self.globalConfiguration["path"] = newPath
        self.setPathAddressLineEdit.setText(newPath)
        log.info("New path = " + newPath)


    def update_filename(self):
        # Method to update the new filename.
        newFilename =self.setFilenameLineEdit.text()
        self.globalConfiguration["filename"] = newFilename
        log.info("New filename = " + newFilename)