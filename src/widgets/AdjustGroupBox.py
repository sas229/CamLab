from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal, Slot

class AdjustGroupBox(QGroupBox):
    adjustSetPoint = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)
        
        # Controls.
        self.incrementLabel = QLabel("Increment")
        self.incrementLineEdit = QLineEdit()
        self.incrementLineEdit.setValidator(self.doubleValidator)
        self.incrementLineEdit.setText("0.10")
        self.adjustDirectionLabel = QLabel("Direction")
        self.adjustPlusButton = QPushButton("+")
        self.adjustMinusButton = QPushButton("-")

        # Button layout.
        self.adjustButtonsLayout = QHBoxLayout()
        self.adjustButtonsLayout.addWidget(self.adjustMinusButton)
        self.adjustButtonsLayout.addWidget(self.adjustPlusButton)

        # Main layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.incrementLabel)
        self.layout.addWidget(self.incrementLineEdit)
        self.layout.addWidget(self.adjustDirectionLabel)
        self.layout.addLayout(self.adjustButtonsLayout)
        self.setLayout(self.layout) 

        #  Geometry.
        self.setFixedHeight(200)
        self.setFixedWidth(150)

        # Connections.
        self.adjustPlusButton.clicked.connect(self.increment_set_point)
        self.adjustMinusButton.clicked.connect(self.decrement_set_point)
        self.incrementLineEdit.returnPressed.connect(self.increment_changed)

    @Slot()
    def increment_changed(self):
        value = float(self.incrementLineEdit.text())
        self.incrementLineEdit.setText("{value:.2f}".format(value=value))

    @Slot()
    def increment_set_point(self):
        value = float(self.incrementLineEdit.text())
        self.adjustSetPoint.emit(value)

    @Slot()
    def decrement_set_point(self):
        value = -float(self.incrementLineEdit.text())
        self.adjustSetPoint.emit(value)

    def set_unit(self, unit):
        self.unit = unit
        self.incrementLabel.setText("Increment ({unit})".format(unit=unit))