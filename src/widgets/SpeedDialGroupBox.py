from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from .styles.CustomDial import CustomDial

class SpeedDialGroupBox(QGroupBox):
    def __init__(self, title="Speed Dial", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle(title)

        # Raw widgets (JogGroupBoxSpeed will drive them)
        self.dial = CustomDial()
        self.dial.setMinimum(0)
        self.dial.setMaximum(3000)
        self.dial.setNotchesVisible(True)
        self.dial.setWrapping(False)
        self.dial.setSingleStep(10)
        self.dial.setPageStep(100)
        self.dial.setTracking(True)
        self.dial.setFixedSize(200, 200)

        self.valueLabel = QLabel("0.0 RPM")
        self.valueLabel.setAlignment(Qt.AlignCenter)
        self.valueLabel.setStyleSheet("font-size: 11pt; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.dial, alignment=Qt.AlignHCenter)
        layout.addWidget(self.valueLabel, alignment=Qt.AlignHCenter)
        layout.setSpacing(10)
        self.setLayout(layout)

        # Size controls
        self.setFixedSize(300, 280)