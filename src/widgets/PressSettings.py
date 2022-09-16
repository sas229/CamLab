from PySide6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QDoubleValidator, QIntValidator
import numpy as np
import logging

log = logging.getLogger(__name__)

class PressSettings(QWidget):
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
    setFeedbackLinearAxis = Signal(bool)
    pressFeedbackUpdated = Signal(str, str)

    
    def __init__(self, name, *args, **kwargs):
        """PressSettings init."""
        super().__init__(*args, **kwargs)
        self.name = name
        self.device_list = []
        self.feedback_channel_lists = {}
        self.feedbackDevice = "N/A"
        self.feedbackChannel = "N/A"

        self.feedbackLabel = QLabel("Press Feedback Channel:")

        self.deviceComboBox = QComboBox()
        self.deviceComboBox.addItems(["None"])
        self.deviceComboBox.setFixedWidth(130)

        self.channelComboBox = QComboBox()
        self.channelComboBox.addItems(["N/A"])
        self.channelComboBox.setFixedWidth(130)

        # Settings layout.
        self.settingsLayout = QGridLayout()

        self.settingsLayout.addWidget(self.feedbackLabel, 0, 0)
        self.settingsLayout.addWidget(self.deviceComboBox, 1, 0)
        self.settingsLayout.addWidget(self.channelComboBox, 1, 1)
        self.settingsLayout.setRowStretch(self.settingsLayout.rowCount(), 1)
        self.settingsLayout.setColumnStretch(self.settingsLayout.columnCount(), 1)

        self.setLayout(self.settingsLayout)

        # Connections.
        self.deviceComboBox.currentTextChanged.connect(self.update_selected_channel_list)
        self.channelComboBox.currentTextChanged.connect(self.feedback_channel_updated)

    @Slot(dict) 
    def set_configuration(self, configuration):
        """Method to set the configuration."""
        self.configuration = configuration
        self.pressConfiguration = self.configuration["devices"][self.name]["control"][0]
        self.initialise_feedback_device(self.pressConfiguration["deviceFeedback"])
        self.initialise_feedback_channel(self.pressConfiguration["feedback"])
        self.setWindowTitle(self.name)

    def initialise_feedback_device(self, text):
        """Method to initialise the feedback device."""
        self.deviceComboBox.setCurrentText(text)
        log.info("Feedback on {press} set to device called {device}.".format(press=self.name, device=text))

    def initialise_feedback_channel(self, text):
        """Method to initialise the feedback device."""
        self.channelComboBox.setCurrentText(text)
        log.info("Feedback on {press} set to channel {channel}.".format(press=self.name, channel=text))

    def set_device_list(self, device_list):
        """Method to set the device list."""
        self.device_list = device_list
        self.deviceComboBox.clear()
        self.deviceComboBox.addItem("N/A")
        self.deviceComboBox.addItems(self.device_list)

    def set_channel_lists(self, feedback_channel_lists):
        """Method to set the feedback channel lists."""
        self.feedback_channel_lists = feedback_channel_lists

    @Slot()
    def update_selected_channel_list(self):
        """Method to update the selected feedback channel list."""
        selected_device = self.deviceComboBox.currentText()
        self.channelComboBox.clear()
        self.channelComboBox.addItem("N/A")
        if selected_device in self.feedback_channel_lists:
            if selected_device != "N/A":
                self.channelComboBox.addItems(self.feedback_channel_lists[selected_device])

    def feedback_channel_updated(self, channel):
        """Method to update the feedback channel."""
        device = self.deviceComboBox.currentText()
        
        if channel != "N/A":
            feedback = True
        else:
            feedback = False

        self.setFeedbackLinearAxis.emit(feedback)
        self.pressFeedbackUpdated.emit(device, channel)

        # if hasattr(self, 'pressConfiguration'):
        #     if self.pressConfiguration["deviceFeedback"] != "N/A": 
        #         self.pressConfiguration["deviceFeedback"] = device
        #     if self.pressConfiguration["feedback"] != "N/A":
        #         self.pressConfiguration["feedback"] = channel

        log.info("Feedback device set to {} on channel {}".format(device, channel))

        

        # 1. Add logic that enables / disables the feedback row of the LinearAxis depending on whether a feedback channel or "N/A" is selected here by sending a boolean signal to LinearAxis.toggleFeedbackControl.
        # 2. Add logic to calculate the index within latestData of the target feedback channel and emit it. 
        # 3. Then catch it and send it to the Press class instance via a connection / disconnection in the manager.toggleDeviceConnection method.
        