from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide6.QtCore import Slot

class GlobalControlsGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Controls.
        self.controlsLabel = QLabel("Controls")
        self.enableButton = QPushButton("Enable")
        self.enableButton.setFixedWidth(125)
        self.enableButton.setCheckable(True)
        self.enableButton.setEnabled(False)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setFixedWidth(125)
        self.stopButton.setVisible(False)
        self.PIDControlButton = QPushButton("PID Control")
        self.PIDControlButton.setFixedWidth(125)
        self.PIDControlButton.setCheckable(True)
        self.PIDControlButton.setVisible(False)
        self.PIDControlButton.setEnabled(False)
        self.settingsButton = QPushButton("Settings")
        self.settingsButton.setFixedWidth(125)
        self.zeroButton = QPushButton("Zero")
        self.zeroButton.setFixedWidth(125)
        self.statusLabel = QLabel("Status")
        self.runningIndicator = QPushButton("Not running")
        self.runningIndicator.setFixedWidth(150)
        self.runningIndicator.setProperty("class", "runningIndicator")
        self.runningIndicator.setCheckable(True)
        self.runningIndicator.setChecked(False)
        self.runningIndicator.setEnabled(False)
        self.connectedIndicator = QPushButton("Connected")
        self.connectedIndicator.setFixedWidth(150)
        self.connectedIndicator.setProperty("class", "indicator")
        self.connectedIndicator.setCheckable(True)
        self.connectedIndicator.setChecked(False)
        self.connectedIndicator.setEnabled(False)
        self.limitIndicator = QPushButton("Within Limits")
        self.limitIndicator.setFixedWidth(150)
        self.limitIndicator.setProperty("class", "limitIndicator")
        self.limitIndicator.setCheckable(True)
        self.limitIndicator.setChecked(False)
        self.limitIndicator.setEnabled(False)
        
        # Layout.
        self.layout = QGridLayout()
        self.layout.addWidget(self.controlsLabel, 0, 0)
        self.layout.addWidget(self.enableButton, 1, 0)
        self.layout.addWidget(self.stopButton, 1, 1)
        self.layout.addWidget(self.PIDControlButton, 1, 2)
        self.layout.addWidget(self.zeroButton, 1, 3)
        self.layout.addWidget(self.settingsButton, 1, 4)
        self.layout.setColumnStretch(5, 1)
        self.layout.addWidget(self.statusLabel, 0, 6)
        self.layout.addWidget(self.runningIndicator, 1, 6)
        self.layout.addWidget(self.connectedIndicator, 1, 7)
        self.layout.addWidget(self.limitIndicator, 1, 8)
        self.layout.setHorizontalSpacing(25)
        self.setLayout(self.layout)
        
        # Geometry.
        self.setFixedHeight(130)

        # Connections.
        self.runningIndicator.toggled.connect(self.setRunningIndicatorText)
        self.connectedIndicator.toggled.connect(self.setConnectedIndicatorText)
        self.limitIndicator.toggled.connect(self.setLimitIndicatorText)
        self.connectedIndicator.toggled.connect(self.setEnableButtonState)
        self.enableButton.toggled.connect(self.setZeroButtonState)
        self.enableButton.toggled.connect(self.setStopButtonState)
    
    @Slot()
    def setRunningIndicatorText(self):
        if self.runningIndicator.isChecked() == True:
            self.runningIndicator.setText("Running")
        elif self.runningIndicator.isChecked() == False:
            self.runningIndicator.setText("Not running")

    @Slot()
    def setConnectedIndicatorText(self):
        if self.connectedIndicator.isChecked() == False:
            self.connectedIndicator.setText("Not connected")
        elif self.connectedIndicator.isChecked() == True:
            self.connectedIndicator.setText("Connected") 

    @Slot()
    def setLimitIndicatorText(self):
        if self.limitIndicator.isChecked() == False:
            self.limitIndicator.setText("Within limits")
        elif self.limitIndicator.isChecked() == True:
            self.limitIndicator.setText("Hard limit")

    @Slot()
    def setEnableButtonState(self):
        if self.connectedIndicator.isChecked() == False:
            self.enableButton.setChecked(False)
            self.enableButton.setEnabled(False)
        elif self.connectedIndicator.isChecked() == True:
            self.enableButton.setEnabled(True)
            
    @Slot()
    def setZeroButtonState(self):
        if self.enableButton.isEnabled() == False:
            self.zeroButton.setVisible(False)
        elif self.enableButton.isChecked() == True:
            self.zeroButton.setVisible(False)
        else:
            self.zeroButton.setVisible(True)

    @Slot()
    def setStopButtonState(self):
        if self.enableButton.isChecked() == True:
            self.stopButton.setVisible(True)
        else:
            self.stopButton.setVisible(False)
    


