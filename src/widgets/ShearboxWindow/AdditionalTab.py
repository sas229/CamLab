from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QDoubleValidator, QRegularExpressionValidator
import logging 

log = logging.getLogger(__name__)

class AdditionalTab(QWidget):

    def __init__(self):
        super().__init__()
        self.Layout = QGridLayout()
        # num_validator = QDoubleValidator(bottom=0)
        num_validator = QRegularExpressionValidator("^([1-9][0-9]*(\.[0-9]+)?|0+\.[0-9]*[1-9][0-9]*)$")
        
        self.platen_weight = QLineEdit()
        self.platen_weight.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Platen Weight"), 0, 0)
        self.Layout.addWidget(QLabel("M<sub>tp</sub>"), 0, 1)
        self.Layout.addWidget(self.platen_weight, 0, 2)
        self.Layout.addWidget(QLabel("g"), 0, 3)

        self.platen_corr = QLineEdit()
        self.platen_corr.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Platen Correction"), 1, 0)
        # self.Layout.addWidget(QLabel(""), 1, 1)
        self.Layout.addWidget(self.platen_corr, 1, 2)
        self.Layout.addWidget(QLabel("kPa"), 1, 3)
        
        self.est_strain_at_fail = QLineEdit()
        self.est_strain_at_fail.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Estimated Strain at Shear Failure"), 2, 0)
        self.Layout.addWidget(QLabel("s<sub>f</sub>"), 2, 1)
        self.Layout.addWidget(self.est_strain_at_fail, 2, 2)
        self.Layout.addWidget(QLabel("%"), 2, 3)

        self.Layout.addWidget(QWidget(),3,0,1,4)

        self.Layout.setRowStretch(0,0)
        self.Layout.setRowStretch(1,0)
        self.Layout.setRowStretch(2,0)
        self.Layout.setRowStretch(3,1)
        self.Layout.setColumnStretch(0,4)
        self.Layout.setColumnStretch(1,6)
        self.Layout.setColumnStretch(2,5)
        self.Layout.setColumnStretch(3,1)
        self.Layout.setHorizontalSpacing(15)
        self.Layout.setVerticalSpacing(15)

        self.setLayout(self.Layout)
    