from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QVBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

class DemandGroupBox(QGroupBox):
    unitChanged = Signal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """DemandGroupBox init."""

        # Defaults.
        self.setPoint = 0
        self.processVariable = 0
        self.unit = ""

        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        # Controls.
        self.setPointLabel = QLabel("SP")
        self.setPointLineEdit = QLineEdit()
        self.setPointLineEdit.setValidator(self.doubleValidator)
        self.setPointLineEdit.setProperty("class", "setPoint")
        self.setPointLineEdit.setText(str(self.setPoint))
        self.setPointLineEdit.setFixedWidth(100)
        self.processVariableLabel = QLabel("PV")
        self.processVariableLineEdit = QLineEdit()
        self.processVariableLineEdit.setProperty("class", "processVariable")
        self.processVariableLineEdit.setText("")
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

    def set_unit(self, unit):
        """Method to set unit."""
        self.unit = unit
        self.setPointLabel.setText("SP ({unit})".format(unit=unit))
        self.processVariableLabel.setText("PV ({unit})".format(unit=unit))
        self.unitChanged.emit()

    def set_setpoint(self, value):
        """Method to set setpoint."""
        self.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.setPoint = value

    def get_setpoint(self):
        """Method to get setpoint."""
        return self.setPoint

    def set_process_variable(self, value):
        """Method to set process variable."""
        self.processVariableLineEdit.setText("{value:.2f}".format(value=value))
        self.processVariable = value

    def get_process_variable(self):
        """Method to get process variable."""
        return self.processVariable