from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QVBoxLayout
from PySide6.QtGui import QDoubleValidator

class DemandGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        # Controls.
        self.setPointLabel = QLabel("SP")
        self.setPointLineEdit = QLineEdit()
        self.setPointLineEdit.setValidator(self.doubleValidator)
        self.setPointLineEdit.setProperty("class", "setPoint")
        self.setPointLineEdit.setText("50.00")
        self.setPointLineEdit.setFixedWidth(100)
        self.processVariableLabel = QLabel("PV")
        self.processVariableLineEdit = QLineEdit()
        self.processVariableLineEdit.setProperty("class", "processVariable")
        self.processVariableLineEdit.setText("50.00")
        self.processVariableLineEdit.setFixedWidth(100)
        self.processVariableLineEdit.setReadOnly(True)

        # Layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.setPointLabel)
        self.layout.addWidget(self.setPointLineEdit)
        self.layout.addWidget(self.processVariableLabel)
        self.layout.addWidget(self.processVariableLineEdit)
        self.setLayout(self.layout)

        # Geometry.
        self.setFixedHeight(200)
        self.setFixedWidth(150)

    def setUnit(self, unit):
        self.unit = unit
        self.setPointLabel.setText("SP " + self.unit)
        self.processVariableLabel.setText("PV " + self.unit)

    def setSetPoint(self, value):
        self.setPointLineEdit.setText("{value:.2f}".format(value=value))