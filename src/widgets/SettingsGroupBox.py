from PySide6.QtWidgets import QGroupBox, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtCore import Signal

class SettingsGroupBox(QGroupBox):
    positionUnitChanged = Signal(str)
    speedUnitChanged = Signal(str)
    feedbackUnitChanged = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)
        self.intValidator = QIntValidator(bottom = 1)

        #  Controls.
        self.maxRPMLabel = QLabel("Maximum RPM")
        self.maxRPMLineEdit = QLineEdit()
        self.maxRPMLineEdit.setValidator(self.intValidator)
        self.maxRPMLineEdit.setFixedWidth(100)

        self.CPRLabel = QLabel("CPR")
        self.CPRLineEdit = QLineEdit()
        self.CPRLineEdit.setValidator(self.intValidator)
        self.CPRLineEdit.setFixedWidth(100)

        self.PPRLabel = QLabel("PPR")
        self.PPRLineEdit = QLineEdit()
        self.PPRLineEdit.setValidator(self.intValidator)
        self.PPRLineEdit.setFixedWidth(100)

        self.ratioLabel = QLabel("Ratio")
        self.ratioLineEdit = QLineEdit()
        self.ratioLineEdit.setValidator(self.doubleValidator)
        self.ratioLineEdit.setFixedWidth(100)

        self.positionUnitLabel = QLabel("Position unit")
        self.positionUnitLineEdit = QLineEdit()
        self.positionUnitLineEdit.setFixedWidth(100)

        self.speedUnitLabel = QLabel("Speed unit")
        self.speedUnitLineEdit = QLineEdit()
        self.speedUnitLineEdit.setFixedWidth(100)

        self.feedbackUnitLabel = QLabel("Feedback unit")
        self.feedbackUnitLineEdit = QLineEdit()
        self.feedbackUnitLineEdit.setFixedWidth(100)
        
        self.returnButton = QPushButton("Return")
        self.returnButton.setFixedWidth(100)
        
        # Layout.
        self.gridLayout = QGridLayout()
        n = 0
        self.gridLayout.addWidget(self.maxRPMLabel, 0, n)
        self.gridLayout.addWidget(self.maxRPMLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.CPRLabel, 0, n)
        self.gridLayout.addWidget(self.CPRLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.PPRLabel, 0, n)
        self.gridLayout.addWidget(self.PPRLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.ratioLabel, 0, n)
        self.gridLayout.addWidget(self.ratioLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.positionUnitLabel, 0, n)
        self.gridLayout.addWidget(self.positionUnitLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.speedUnitLabel, 0, n)
        self.gridLayout.addWidget(self.speedUnitLineEdit, 1, n)
        n += 1
        self.gridLayout.addWidget(self.feedbackUnitLabel, 0, n)
        self.gridLayout.addWidget(self.feedbackUnitLineEdit, 1, n)
        self.gridLayout.setHorizontalSpacing(25)

        self.returnLayout = QVBoxLayout()
        self.returnLayout.addStretch()
        self.returnLayout.addWidget(self.returnButton)

        self.layout = QHBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch()
        self.layout.addLayout(self.returnLayout)
        self.setLayout(self.layout)

        # Geometry.
        self.setFixedHeight(130)
        self.hide()

        # Connections.
        self.positionUnitLineEdit.returnPressed.connect(self.setPositionUnit)
        self.speedUnitLineEdit.returnPressed.connect(self.setSpeedUnit)
        self.feedbackUnitLineEdit.returnPressed.connect(self.setFeedbackUnit)

    def setMaxRPM(self, value):
        self.maxRPMLineEdit.setText("{value}".format(value=value))

    def setCPR(self, value):
        self.CPRLineEdit.setText("{value}".format(value=value))
    
    def setPPR(self, value):
        self.PPRLineEdit.setText("{value}".format(value=value))

    def setRatio(self, value):
        self.ratioLineEdit.setText("{value:.2f}".format(value=value))

    def setPositionUnit(self, value=None):
        if value == None:
            value = self.positionUnitLineEdit.text()
        self.positionUnitLineEdit.setText(value)
        self.positionUnitChanged.emit(value)
    
    def setSpeedUnit(self, value=None):
        if value == None:
            value = self.speedUnitLineEdit.text()
        self.speedUnitLineEdit.setText(value)
        self.speedUnitChanged.emit(value)

    def setFeedbackUnit(self, value=None):
        if value == None:
            value = self.feedbackUnitLineEdit.text()
        self.feedbackUnitLineEdit.setText(value)
        self.feedbackUnitChanged.emit(value)