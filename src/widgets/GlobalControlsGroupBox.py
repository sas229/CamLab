from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout

class GlobalControlsGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Controls.
        self.controlsLabel = QLabel("Controls")
        self.enableButton = QPushButton("Enable")
        self.enableButton.setFixedWidth(150)
        self.enableButton.setCheckable(True)
        self.PIDControlButton = QPushButton("PID Control")
        self.PIDControlButton.setFixedWidth(150)
        self.PIDControlButton.setCheckable(True)
        self.settingsButton = QPushButton("Settings")
        self.settingsButton.setFixedWidth(150)
        self.zeroEncoderButton = QPushButton("Zero Encoder")
        self.zeroEncoderButton.setFixedWidth(150)
        self.statusLabel = QLabel("Status")
        self.connectedIndicator = QPushButton("Connected")
        self.connectedIndicator.setFixedWidth(150)
        self.connectedIndicator.setProperty("class", "indicator")
        self.connectedIndicator.setCheckable(True)
        self.connectedIndicator.setChecked(True)
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
        self.layout.addWidget(self.PIDControlButton, 1, 1)
        self.layout.addWidget(self.zeroEncoderButton, 1, 2)
        self.layout.addWidget(self.settingsButton, 1, 3)
        self.layout.setColumnStretch(4, 1)
        self.layout.addWidget(self.statusLabel, 0, 5)
        self.layout.addWidget(self.connectedIndicator, 1, 5)
        self.layout.addWidget(self.limitIndicator, 1, 6)
        self.layout.setHorizontalSpacing(25)
        self.setLayout(self.layout)
        
        # Geometry.
        self.setFixedHeight(130)

        # Connections
        self.limitIndicator.toggled.connect(self.setLimitIndicatorText)
        self.connectedIndicator.toggled.connect(self.setConnectedIndicatorText)

    def setLimitIndicatorText(self):
        if self.limitIndicator.isChecked() == False:
            self.limitIndicator.setText("Within limits")
        elif self.limitIndicator.isChecked() == True:
            self.limitIndicator.setText("Reached limit")

    def setConnectedIndicatorText(self):
        if self.connectedIndicator.isChecked() == False:
            self.connectedIndicator.setText("Not connected")
        elif self.connectedIndicator.isChecked() == True:
            self.connectedIndicator.setText("Connected") 