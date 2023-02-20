from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QDoubleValidator
import logging 

log = logging.getLogger(__name__)

class MoistureTab(QWidget):

    def __init__(self):
        super().__init__()
        self.Layout = QGridLayout()
        num_validator = QDoubleValidator()
        
        self.initial_wet_weight = QLineEdit()
        self.initial_wet_weight.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Initial Wet Weight"), 0, 0)
        self.Layout.addWidget(QLabel("W \u03C9<sub>i</sub>"), 0, 1)
        self.Layout.addWidget(self.initial_wet_weight, 0, 2)
        self.Layout.addWidget(QLabel("g"), 0, 3)

        self.initial_dry_weight = QLineEdit()
        self.initial_dry_weight.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Initial Dry Weight"), 1, 0)
        self.Layout.addWidget(QLabel("D \u03C9<sub>i</sub>"), 1, 1)
        self.Layout.addWidget(self.initial_dry_weight, 1, 2)
        self.Layout.addWidget(QLabel("g"), 1, 3)
        
        self.tin_initial_weight = QLineEdit()
        self.tin_initial_weight.setValidator(num_validator)
        self.Layout.addWidget(QLabel("Tin (initial) Weight"), 2, 0)
        self.Layout.addWidget(QLabel("T \u03C9<sub>i</sub>"), 2, 1)
        self.Layout.addWidget(self.tin_initial_weight, 2, 2)
        self.Layout.addWidget(QLabel("g"), 2, 3)
        
        self.initial_moisture = QLineEdit()
        self.initial_moisture.setReadOnly(True)
        self.Layout.addWidget(QLabel("Initial Moisture"), 3, 0)
        self.Layout.addWidget(QLabel("\u03C9<sub>i</sub>"), 3, 1)
        self.Layout.addWidget(self.initial_moisture, 3, 2)
        self.Layout.addWidget(QLabel("%"), 3, 3)
        
        self.initial_dry_density = QLineEdit()
        self.initial_dry_density.setReadOnly(True)
        self.Layout.addWidget(QLabel("Initial Dry Density"), 4, 0)
        self.Layout.addWidget(QLabel("\u03C1<sub>di</sub>"), 4, 1)
        self.Layout.addWidget(self.initial_dry_density, 4, 2)
        self.Layout.addWidget(QLabel("g/cm<sup>3</sup>"), 4, 3)
        
        self.initial_voids_ratio = QLineEdit()
        self.initial_voids_ratio.setReadOnly(True)
        self.Layout.addWidget(QLabel("Initial Voids Ratio"), 5, 0)
        self.Layout.addWidget(QLabel("e<sub>i</sub>"), 5, 1)
        self.Layout.addWidget(self.initial_voids_ratio, 5, 2)
        
        self.initial_deg_of_sat = QLineEdit()
        self.initial_deg_of_sat.setReadOnly(True)
        self.Layout.addWidget(QLabel("Initial Degree of Saturation"), 6, 0)
        self.Layout.addWidget(QLabel("S<sub>i</sub>"), 6, 1)
        self.Layout.addWidget(self.initial_deg_of_sat, 6, 2)
        self.Layout.addWidget(QLabel("%"), 6, 3)

        self.Layout.addWidget(QWidget(),7,0,1,4)

        self.Layout.setRowStretch(0,0)
        self.Layout.setRowStretch(1,0)
        self.Layout.setRowStretch(2,0)
        self.Layout.setRowStretch(3,0)
        self.Layout.setRowStretch(4,0)
        self.Layout.setRowStretch(5,0)
        self.Layout.setRowStretch(6,0)
        self.Layout.setRowStretch(7,1)
        self.Layout.setColumnStretch(0,1)
        self.Layout.setColumnStretch(1,1)
        self.Layout.setColumnStretch(2,1)
        self.Layout.setColumnStretch(3,0)
        self.Layout.setHorizontalSpacing(15)
        self.Layout.setVerticalSpacing(15)

        self.setLayout(self.Layout)
    