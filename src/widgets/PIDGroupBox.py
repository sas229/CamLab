from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QcheckBox, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

class PIDGroupBox(QGroupBox):
    KPLineEditChanged = Signal(float)
    KILineEditChanged = Signal(float)
    KDLineEditChanged = Signal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        # Controls.
        self.KPLabel = QLabel("KP (-)")
        self.KPLineEdit = QLineEdit()
        self.KPLineEdit.setValidator(self.doubleValidator)
        self.KPLineEdit.setText("1.00")
        self.KPLineEdit.setFixedWidth(80)
        self.KILabel = QLabel("KI (-)")
        self.KILineEdit = QLineEdit()
        self.KILineEdit.setValidator(self.doubleValidator)
        self.KILineEdit.setText("1.00")
        self.KILineEdit.setFixedWidth(80)
        self.KDLabel = QLabel("KD (-)")
        self.KDLineEdit = QLineEdit()
        self.KDLineEdit.setValidator(self.doubleValidator)
        self.KDLineEdit.setText("1.00")
        self.KDLineEdit.setFixedWidth(80)
        self.optionsLabel = QLabel("Options")
        self.derivativeOnMeasurement = QCheckBox("Derivative on measurement")

        # Layout.
        self.Layout = QGridLayout()
        self.Layout.addWidget(self.KPLabel, 0, 0)
        self.Layout.addWidget(self.KILabel, 0, 1)
        self.Layout.addWidget(self.KDLabel, 0, 2)
        self.Layout.addWidget(self.KPLineEdit, 1, 0)
        self.Layout.addWidget(self.KILineEdit, 1, 1)
        self.Layout.addWidget(self.KDLineEdit, 1, 2)
        self.Layout.addWidget(self.optionsLabel, 2, 0)
        self.Layout.addWidget(self.derivativeOnMeasurement, 3, 0, 1, 3)
        self.setLayout(self.Layout) 
        
        # Geometry.
        self.setFixedHeight(200)
        self.setFixedWidth(310)

        # Connections.
        self.KPLineEdit.returnPressed.connect(self.setKP)
        self.KILineEdit.returnPressed.connect(self.setKI)
        self.KDLineEdit.returnPressed.connect(self.setKD)

    def setKP(self, value=None):
        if value == None:
            value = float(self.KPLineEdit.text())
        self.KPLineEdit.setText("{value:.2f}".format(value=value))
        self.KPLineEditChanged.emit(value)
    
    def setKI(self, value=None):
        if value == None:
            value = float(self.KILineEdit.text())
        self.KILineEdit.setText("{value:.2f}".format(value=value))
        self.KILineEditChanged.emit(value)

    def setKD(self, value=None):
        if value == None:
            value = float(self.KDLineEdit.text())
        self.KDLineEdit.setText("{value:.2f}".format(value=value))
        self.KDLineEditChanged.emit(value)

    def setDerivativeOnMeasurement(self, value):
        self.derivativeOnMeasurement.setChecked(value)