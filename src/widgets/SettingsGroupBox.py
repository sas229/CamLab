from PySide6.QtWidgets import QGroupBox, QPushButton, QLabel, QLineEdit, QVBoxLayout
from PySide6.QtGui import QDoubleValidator

class SettingsGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        #  Controls.
        self.returnButton = QPushButton("Return")
        self.positionUnitsLabel = QLabel("Position Unit")
        self.positionUnitsLineEdit = QLineEdit()
        self.positionUnitsLineEdit.setText("mm")
        # self.positionUnitsLineEdit.setFixedWidth(100)
        self.countsPerUnitLabel = QLabel("Counts per unit")
        self.countsPerUnitLineEdit = QLineEdit()
        self.countsPerUnitLineEdit.setText("1000")
        self.countsPerUnitLineEdit.setValidator(self.doubleValidator)
        # self.countsPerUnitLineEdit.setFixedWidth(100)
        self.speedUnitLabel = QLabel("Speed unit")
        self.speedUnitLineEdit = QLineEdit()
        self.speedUnitLineEdit.setText("mm/s")
        # self.speedUnitLineEdit.setFixedWidth(100)
        self.feedbackUnitLabel = QLabel("Feedback unit")
        self.feedbackUnitLineEdit = QLineEdit()
        self.feedbackUnitLineEdit.setText("N")
        # self.feedbackUnitLineEdit.setFixedWidth(100)
        
        # Layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.returnButton)
        self.layout.addWidget(self.positionUnitsLabel)
        self.layout.addWidget(self.positionUnitsLineEdit)
        self.layout.addWidget(self.countsPerUnitLabel)
        self.layout.addWidget(self.countsPerUnitLineEdit)
        self.layout.addWidget(self.speedUnitLabel)
        self.layout.addWidget(self.speedUnitLineEdit)
        self.layout.addWidget(self.feedbackUnitLabel)
        self.layout.addWidget(self.feedbackUnitLineEdit)
        self.setLayout(self.layout)

        # Geometry.
        # self.setFixedHeight(200)
        self.setFixedWidth(200)
        self.hide()