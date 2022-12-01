from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

class JogGroupBox(QGroupBox):
    speedLineEditChanged = Signal(float)
    speedUnitChanged = Signal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Defaults.
        self.unit = ""

        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=6, bottom=0.000001)

        # Controls.
        self.speedLabel = QLabel("Speed")
        self.speedLineEdit = QLineEdit()
        self.speedLineEdit.setValidator(self.doubleValidator)
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

    def set_unit(self, unit):
        self.speedLabel.setText("Speed ({unit})".format(unit=unit))
        self.speedUnitChanged.emit()
        self.unit = unit

    def setSpeed(self, value=None):
        if value == None:
            value = self.getSpeed()
        self.speedLineEdit.setText("{value:.6f}".format(value=value))

    def getSpeed(self):
        return float(self.speedLineEdit.text())