from PySide6.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout

class GlobalControlsGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Controls.
        self.controlsLabel = QLabel("Controls")
        self.enableButton = QPushButton("Enable")
        self.enableButton.setCheckable(True)
        self.PIDControlButton = QPushButton("PID Control")
        self.PIDControlButton.setCheckable(True)
        self.settingsButton = QPushButton("Settings")
        self.zeroEncoderButton = QPushButton("Zero Encoder")
        self.statusLabel = QLabel("Status")
        self.connectedIndicator = QPushButton("Connected")
        self.connectedIndicator.setProperty("class", "indicator")
        self.connectedIndicator.setCheckable(True)
        self.connectedIndicator.setChecked(True)
        # self.connectedIndicator.setEnabled(False)
        self.limitIndicator = QPushButton("Reached Limit")
        self.limitIndicator.setProperty("class", "limitIndicator")
        self.limitIndicator.setCheckable(True)
        self.limitIndicator.setChecked(False)
        # self.limitIndicator.setEnabled(False)

        # Layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.controlsLabel)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.enableButton)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.PIDControlButton)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.zeroEncoderButton)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.settingsButton)
        self.layout.addStretch()
        self.layout.addWidget(self.statusLabel)
        self.layout.addWidget(self.connectedIndicator)
        self.layout.addWidget(self.limitIndicator)
        self.setLayout(self.layout)

        # Geometry.
        self.setFixedWidth(200)

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