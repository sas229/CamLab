from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

class JogGroupBox(QGroupBox):
    speedLineEditChanged = Signal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        # Controls.
        self.speedLabel = QLabel("Speed")
        self.speedLineEdit = QLineEdit()
        self.speedLineEdit.setValidator(self.doubleValidator)
        self.speedLineEdit.setText("1.00")
        self.jogDirectionLabel = QLabel("Direction")
        self.jogPlusButton = QPushButton("+")
        self.jogMinusButton = QPushButton("-")

        # Button layout.
        self.jogButtonsLayout = QHBoxLayout()
        self.jogButtonsLayout.addWidget(self.jogMinusButton)
        self.jogButtonsLayout.addWidget(self.jogPlusButton)

        # Layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.speedLabel)
        self.layout.addWidget(self.speedLineEdit)
        self.layout.addWidget(self.jogDirectionLabel)
        self.layout.addLayout(self.jogButtonsLayout)
        self.setLayout(self.layout) 

        # Geometry.
        self.setFixedHeight(200)
        self.setFixedWidth(150)

        # Connections.
        self.speedLineEdit.returnPressed.connect(self.setSpeed)

    def setUnit(self, unit):
        self.unit = unit
        self.speedLabel.setText("Speed " + self.unit)

    def setSpeed(self):
        value = float(self.speedLineEdit.text())
        self.speedLineEdit.setText("{value:.2f}".format(value=value))
        self.speedLineEditChanged.emit(value)