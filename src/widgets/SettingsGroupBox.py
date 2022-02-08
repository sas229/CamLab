from PySide6.QtWidgets import QGroupBox, QPushButton, QLabel, QLineEdit, QGridLayout, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QDoubleValidator

class SettingsGroupBox(QGroupBox):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        #  Controls.
        self.positionUnitsLabel = QLabel("Position unit")
        self.positionUnitsLineEdit = QLineEdit()
        self.positionUnitsLineEdit.setText("mm")
        self.positionUnitsLineEdit.setFixedWidth(100)
        self.countsPerUnitLabel = QLabel("Counts per unit")
        self.countsPerUnitLineEdit = QLineEdit()
        self.countsPerUnitLineEdit.setText("1000")
        self.countsPerUnitLineEdit.setValidator(self.doubleValidator)
        self.countsPerUnitLineEdit.setFixedWidth(100)
        self.speedUnitLabel = QLabel("Speed unit")
        self.speedUnitLineEdit = QLineEdit()
        self.speedUnitLineEdit.setText("mm/s")
        self.speedUnitLineEdit.setFixedWidth(100)
        self.feedbackUnitLabel = QLabel("Feedback unit")
        self.feedbackUnitLineEdit = QLineEdit()
        self.feedbackUnitLineEdit.setText("N")
        self.feedbackUnitLineEdit.setFixedWidth(100)
        self.returnButton = QPushButton("Return")
        self.returnButton.setFixedWidth(100)
        
        # Layout.
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.positionUnitsLabel, 0, 0)
        self.gridLayout.addWidget(self.positionUnitsLineEdit, 1, 0)
        self.gridLayout.addWidget(self.countsPerUnitLabel, 0, 1)
        self.gridLayout.addWidget(self.countsPerUnitLineEdit, 1, 1)
        self.gridLayout.addWidget(self.speedUnitLabel, 0, 2)
        self.gridLayout.addWidget(self.speedUnitLineEdit, 1, 2)
        self.gridLayout.addWidget(self.feedbackUnitLabel, 0, 3)
        self.gridLayout.addWidget(self.feedbackUnitLineEdit, 1, 3)
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
        # self.setFixedWidth(200)
        self.hide()