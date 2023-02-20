from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QGroupBox
from PySide6.QtGui import QDoubleValidator
import logging 

log = logging.getLogger(__name__)

class MoistureTab(QWidget):

    def __init__(self):
        super().__init__()
        self.Layout = QGridLayout()
        num_validator = QDoubleValidator()
        
        self.initial_wet_weight = QLineEdit()
        self.initial_dry_weight = QLineEdit()
        self.tin_initial_weight = QLineEdit()
        self.initial_moisture = QLineEdit()
        self.initial_dry_density = QLineEdit()
        self.initial_voids_ratio = QLineEdit()
        self.initial_deg_of_sat = QLineEdit()
        
        self.initial_wet_weight.setValidator(num_validator)
        self.initial_dry_weight.setValidator(num_validator)
        self.tin_initial_weight.setValidator(num_validator)
        
        self.initial_moisture.setReadOnly(True)
        self.initial_dry_density.setReadOnly(True)
        self.initial_voids_ratio.setReadOnly(True)
        self.initial_deg_of_sat.setReadOnly(True)

        self.Layout = QGridLayout()
        self.calc_box = QGroupBox("Related Calculations")
        self.calc_box_layout = QGridLayout()

        self.Layout.addWidget(QLabel("Initial Wet Weight"), 0, 0)
        self.Layout.addWidget(QLabel("W \u03C9<sub>i</sub>"), 0, 1)
        self.Layout.addWidget(self.initial_wet_weight, 0, 2)
        self.Layout.addWidget(QLabel("g"), 0, 3)
        self.Layout.addWidget(QLabel("Initial Dry Weight"), 1, 0)
        self.Layout.addWidget(QLabel("D \u03C9<sub>i</sub>"), 1, 1)
        self.Layout.addWidget(self.initial_dry_weight, 1, 2)
        self.Layout.addWidget(QLabel("g"), 1, 3)
        self.Layout.addWidget(QLabel("Tin (initial) Weight"), 2, 0)
        self.Layout.addWidget(QLabel("T \u03C9<sub>i</sub>"), 2, 1)
        self.Layout.addWidget(self.tin_initial_weight, 2, 2)
        self.Layout.addWidget(QLabel("g"), 2, 3)

        self.calc_box_layout.addWidget(QLabel("Initial Moisture"), 0, 0)
        self.calc_box_layout.addWidget(QLabel("\u03C9<sub>i</sub>"), 0, 1)
        self.calc_box_layout.addWidget(self.initial_moisture, 0, 2)
        self.calc_box_layout.addWidget(QLabel("%"), 0, 3)

        self.calc_box_layout.addWidget(QLabel("Initial Dry Density"), 1, 0)
        self.calc_box_layout.addWidget(QLabel("\u03C1<sub>di</sub>"), 1, 1)
        self.calc_box_layout.addWidget(self.initial_dry_density, 1, 2)
        self.calc_box_layout.addWidget(QLabel("g/cm<sup>3</sup>"), 1, 3)

        self.calc_box_layout.addWidget(QLabel("Initial Voids Ratio"), 2, 0)
        self.calc_box_layout.addWidget(QLabel("e<sub>i</sub>"), 2, 1)
        self.calc_box_layout.addWidget(self.initial_voids_ratio, 2, 2)

        self.calc_box_layout.addWidget(QLabel("Initial Degree of Saturation"), 3, 0)
        self.calc_box_layout.addWidget(QLabel("S<sub>i</sub>"), 3, 1)
        self.calc_box_layout.addWidget(self.initial_deg_of_sat, 3, 2)
        self.calc_box_layout.addWidget(QLabel("%"), 3, 3)

        self.calc_box.setLayout(self.calc_box_layout)

        self.Layout.addWidget(self.calc_box, 3, 0, 1, 4)
        self.Layout.addWidget(QWidget(), 4, 0, 1, 4)

        self.Layout.setColumnStretch(0,4)
        self.Layout.setColumnStretch(1,6)
        self.Layout.setColumnStretch(2,5)
        self.Layout.setColumnStretch(3,1)
        self.Layout.setRowStretch(0,0)
        self.Layout.setRowStretch(1,0)
        self.Layout.setRowStretch(2,0)
        self.Layout.setRowStretch(3,0)
        self.Layout.setRowStretch(4,1)
        self.Layout.setHorizontalSpacing(15)
        self.Layout.setVerticalSpacing(15)
        self.calc_box_layout.setColumnStretch(0,4)
        self.calc_box_layout.setColumnStretch(1,6)
        self.calc_box_layout.setColumnStretch(2,5)
        self.calc_box_layout.setColumnStretch(3,1)
        self.calc_box_layout.setRowStretch(0,0)
        self.calc_box_layout.setRowStretch(1,0)
        self.calc_box_layout.setRowStretch(2,0)
        self.calc_box_layout.setRowStretch(3,0)
        self.calc_box_layout.setHorizontalSpacing(15)
        self.calc_box_layout.setVerticalSpacing(15)

        self.setLayout(self.Layout)
    