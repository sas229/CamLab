from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel, QGroupBox, QRadioButton, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Slot
import logging 

log = logging.getLogger(__name__)

class DimensionTab(QWidget):

    def __init__(self):
        super().__init__()
        num_validator = QDoubleValidator(bottom=0)
        
        self.initial_height = QLineEdit()
        self.initial_weight = QLineEdit()
        self.rectangular = QRadioButton("Rectangular Shape")
        self.circular = QRadioButton("Circular Shape")
        self.initial_width = QLineEdit()
        self.initial_depth = QLineEdit()
        self.initial_radius = QLineEdit()
        self.particle_density = QLineEdit()
        self.initial_area = QLineEdit()
        self.initial_volume = QLineEdit()
        self.initial_bulk_density = QLineEdit()
        
        self.initial_height.setValidator(num_validator)
        self.initial_weight.setValidator(num_validator)
        self.initial_width.setValidator(num_validator)
        self.initial_depth.setValidator(num_validator)
        self.initial_radius.setValidator(num_validator)
        self.particle_density.setValidator(num_validator)

        self.initial_area.setReadOnly(True)
        self.initial_volume.setReadOnly(True)
        self.initial_bulk_density.setReadOnly(True)

        self.rectangular.setChecked(True)

        self.Layout = QGridLayout()
        self.button_box = QHBoxLayout()
        self.calc_box = QGroupBox("Related Calculations")
        self.calc_box_layout = QGridLayout()

        self.button_box.addWidget(self.rectangular, 1)
        self.button_box.addWidget(self.circular, 4)

        self.width_label1 = QLabel("Initial Width")
        self.width_label2 = QLabel("w<sub>0</sub>")
        self.width_label3 = QLabel("mm")
        self.depth_label1 = QLabel("Initial Depth")
        self.depth_label2 = QLabel("d<sub>0</sub>")
        self.depth_label3 = QLabel("mm")
        self.radius_label1 = QLabel("Initial Radius")
        self.radius_label2 = QLabel("r<sub>0</sub>")
        self.radius_label3 = QLabel("mm")

        self.Layout.addWidget(QLabel("Initial Weight"), 0, 0)
        self.Layout.addWidget(QLabel("W<sub>0</sub>"), 0, 1)
        self.Layout.addWidget(self.initial_weight, 0, 2)
        self.Layout.addWidget(QLabel("g"), 0, 3)
        self.Layout.addWidget(QLabel("Initial Height"), 1, 0)
        self.Layout.addWidget(QLabel("H<sub>0</sub>"), 1, 1)
        self.Layout.addWidget(self.initial_height, 1, 2)
        self.Layout.addWidget(QLabel("mm"), 1, 3)
        self.Layout.addLayout(self.button_box, 2, 0, 1, 4)
        self.Layout.addWidget(self.width_label1, 3, 0)
        self.Layout.addWidget(self.width_label2, 3, 1)
        self.Layout.addWidget(self.initial_width, 3, 2)
        self.Layout.addWidget(self.width_label3, 3, 3)
        self.Layout.addWidget(self.depth_label1, 4, 0)
        self.Layout.addWidget(self.depth_label2, 4, 1)
        self.Layout.addWidget(self.initial_depth, 4, 2)
        self.Layout.addWidget(self.depth_label3, 4, 3)

        self.calc_box_layout.addWidget(QLabel("Particle Density"), 0, 0)
        self.calc_box_layout.addWidget(QLabel("\u03C1<sub>s</sub>"), 0, 1)
        self.calc_box_layout.addWidget(self.particle_density, 0, 2)
        self.calc_box_layout.addWidget(QLabel("g/cm<sup>3</sup>"), 0, 3)
        self.calc_box_layout.addWidget(QLabel("Initial Area"), 1, 0)
        self.calc_box_layout.addWidget(QLabel("A<sub>0</sub>"), 1, 1)
        self.calc_box_layout.addWidget(self.initial_area, 1, 2)
        self.calc_box_layout.addWidget(QLabel("cm<sup>2</sup>"), 1, 3)
        self.calc_box_layout.addWidget(QLabel("Initial Volume"), 2, 0)
        self.calc_box_layout.addWidget(QLabel("V<sub>0</sub>"), 2, 1)
        self.calc_box_layout.addWidget(self.initial_volume, 2, 2)
        self.calc_box_layout.addWidget(QLabel("cm<sup>3</sup>"), 2, 3)
        self.calc_box_layout.addWidget(QLabel("Initial Bulk Density"), 3, 0)
        self.calc_box_layout.addWidget(QLabel("\u03C1<sub>0</sub>"), 3, 1)
        self.calc_box_layout.addWidget(self.initial_bulk_density, 3, 2)
        self.calc_box_layout.addWidget(QLabel("g/cm<sup>3</sup>"), 3, 3)

        self.calc_box.setLayout(self.calc_box_layout)

        self.Layout.addWidget(self.calc_box, 5, 0, 1, 4)
        self.Layout.addWidget(QWidget(), 6, 0, 1, 4)

        self.Layout.setColumnStretch(0,4)
        self.Layout.setColumnStretch(1,6)
        self.Layout.setColumnStretch(2,5)
        self.Layout.setColumnStretch(3,1)
        self.Layout.setRowStretch(0,0)
        self.Layout.setRowStretch(1,0)
        self.Layout.setRowStretch(2,0)
        self.Layout.setRowStretch(3,0)
        self.Layout.setRowStretch(4,0)
        self.Layout.setRowStretch(5,0)
        self.Layout.setRowStretch(6,1)
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