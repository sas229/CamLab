from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QCheckBox, QGridLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

class PIDGroupBox(QGroupBox):
    KPLineEditChanged = Signal(float)
    KILineEditChanged = Signal(float)
    KDLineEditChanged = Signal(float)
    rampPIDLineEditChanged = Signal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Defaults.
        self.KP = 1.00
        self.KI = 1.00
        self.KD = 1.00

        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=3)

        # Controls.
        self.KPLabel = QLabel("KP (-)")
        self.KPLineEdit = QLineEdit()
        self.KPLineEdit.setValidator(self.doubleValidator)
        self.KPLineEdit.setText("1.000")
        self.KPLineEdit.setFixedWidth(80)
        self.KILabel = QLabel("KI (-)")
        self.KILineEdit = QLineEdit()
        self.KILineEdit.setValidator(self.doubleValidator)
        self.KILineEdit.setText("1.000")
        self.KILineEdit.setFixedWidth(80)
        self.KDLabel = QLabel("KD (-)")
        self.KDLineEdit = QLineEdit()
        self.KDLineEdit.setValidator(self.doubleValidator)
        self.KDLineEdit.setText("1.000")
        self.KDLineEdit.setFixedWidth(80)
        self.optionsLabel = QLabel("Ramp")
        self.checkboxLabel = QLabel("Ramp On/Off")
        # self.proportionalOnMeasurement = QCheckBox("Proportional on measurement")
        self.rampPID_checkbox = QCheckBox()
        self.rampPIDLineEdit = QLineEdit()
        self.rampPIDLineEdit.setValidator(self.doubleValidator)
        self.rampPIDLineEdit.setText("1.000")
        self.rampPIDLineEdit.setFixedWidth(80)

        # Layout.
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.KPLabel, 0, 0)
        self.Layout.addWidget(self.KILabel, 0, 1)
        self.Layout.addWidget(self.KDLabel, 0, 2)
        self.Layout.addWidget(self.KPLineEdit, 1, 0)
        self.Layout.addWidget(self.KILineEdit, 1, 1)
        self.Layout.addWidget(self.KDLineEdit, 1, 2)
        self.Layout.addWidget(self.optionsLabel, 2, 0)
        self.Layout.addWidget(self.checkboxLabel, 2, 1)
        self.Layout.addWidget(self.rampPID_checkbox, 3, 1)
        self.Layout.addWidget(self.rampPIDLineEdit, 3, 0)
        self.setLayout(self.Layout) 
        
        # Geometry.
        self.setFixedHeight(200)
        self.setFixedWidth(310)

        # Connections.
        self.KPLineEdit.returnPressed.connect(self.setKP)
        self.KILineEdit.returnPressed.connect(self.setKI)
        self.KDLineEdit.returnPressed.connect(self.setKD)
        self.rampPIDLineEdit.returnPressed.connect(self.setRampPID)

    def setKP(self, value=None):
        if value == None:
            value = float(self.KPLineEdit.text())
        self.KP = value
        self.KPLineEdit.setText("{value:.3f}".format(value=value))
        self.KPLineEditChanged.emit(value)

    def getKP(self):
        return self.KP
    
    def setKI(self, value=None):
        if value == None:
            value = float(self.KILineEdit.text())
        self.KI = value
        self.KILineEdit.setText("{value:.3f}".format(value=value))
        self.KILineEditChanged.emit(value)
        
    def getKI(self):
        return self.KI

    def setKD(self, value=None):
        if value == None:
            value = float(self.KDLineEdit.text())
        self.KD = value
        self.KDLineEdit.setText("{value:.3f}".format(value=value))
        self.KDLineEditChanged.emit(value)

    def getKD(self):
        return self.KD

    def setRampPID(self, value=None):
        if value == None:
            value = float(self.rampPIDLineEdit.text())
        self.rampPID = value
        self.rampPIDLineEdit.setText("{value:.3f}".format(value=value))
        self.rampPIDLineEditChanged.emit(value)

    def getRampPID(self):
        return self.rampPID

    # def setProportionalOnMeasurement(self, value):
    #     self.proportionalOnMeasurement.setChecked(value)

    # def getProportionalOnMeasurement(self):
    #     return self.proportionalOnMeasurement.isChecked()

    def setRampPID_checkbox(self, value):
        self.rampPID_checkbox.setChecked(value)

    def getRampPID_checkbox(self):
        return self.rampPID_checkbox.isChecked()

    def rampPIDLineEdit_setting(self, value):
        self.rampPIDLineEdit.setEnabled(value)

    def set_unit(self, unit):
        """Method to set unit."""
        self.unit = unit
        self.optionsLabel.setText("Ramp ({unit})".format(unit=unit))
        

