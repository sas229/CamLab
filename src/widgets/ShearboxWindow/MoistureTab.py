from PySide6.QtWidgets import QWidget, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QDoubleValidator
import logging 

log = logging.getLogger(__name__)

class MoistureTab(QWidget):

    def __init__(self):
        super().__init__()
        self.Layout = QGridLayout()
        num_validator = QDoubleValidator()
        
        # self.initial_height = QLineEdit()
        # self.initial_height.setValidator(num_validator)
        # self.Layout.addWidget(QLabel("Initial Height"), 0, 0)
        # self.Layout.addWidget(QLabel("H<sub>0</sub>"), 0, 1)
        # self.Layout.addWidget(self.initial_height, 0, 2)
        # self.Layout.addWidget(QLabel("mm"), 0, 3)

        # self.initial_weight = QLineEdit()
        # self.initial_weight.setValidator(num_validator)
        # self.Layout.addWidget(QLabel("Initial Weight"), 1, 0)
        # self.Layout.addWidget(QLabel("W<sub>0</sub>"), 1, 1)
        # self.Layout.addWidget(self.initial_weight, 1, 2)
        # self.Layout.addWidget(QLabel("g"), 1, 3)
        
        # self.initial_width = QLineEdit()
        # self.initial_width.setValidator(num_validator)
        # self.Layout.addWidget(QLabel("Initial Width"), 2, 0)
        # self.Layout.addWidget(QLabel("w<sub>0</sub>"), 2, 1)
        # self.Layout.addWidget(self.initial_width, 2, 2)
        # self.Layout.addWidget(QLabel("mm"), 2, 3)
        
        # self.initial_depth = QLineEdit()
        # self.initial_depth.setValidator(num_validator)
        # self.Layout.addWidget(QLabel("Initial Depth"), 3, 0)
        # self.Layout.addWidget(QLabel("d<sub>0</sub>"), 3, 1)
        # self.Layout.addWidget(self.initial_depth, 3, 2)
        # self.Layout.addWidget(QLabel("mm"), 3, 3)
        
        # self.particle_density = QLineEdit()
        # self.particle_density.setValidator(num_validator)
        # self.Layout.addWidget(QLabel("Particle Density"), 4, 0)
        # self.Layout.addWidget(QLabel("\u03C1<sub>s</sub>"), 4, 1)
        # self.Layout.addWidget(self.particle_density, 4, 2)
        # self.Layout.addWidget(QLabel("g/cm<sup>3</sup>"), 4, 3)
        
        # self.initial_area = QLineEdit()
        # self.initial_area.setReadOnly(True)
        # self.Layout.addWidget(QLabel("Initial Area"), 5, 0)
        # self.Layout.addWidget(QLabel("A<sub>0</sub>"), 5, 1)
        # self.Layout.addWidget(self.initial_area, 5, 2)
        # self.Layout.addWidget(QLabel("cm<sup>2</sup>"), 5, 3)
        
        # self.initial_volume = QLineEdit()
        # self.initial_volume.setReadOnly(True)
        # self.Layout.addWidget(QLabel("Initial Volume"), 6, 0)
        # self.Layout.addWidget(QLabel("V<sub>0</sub>"), 6, 1)
        # self.Layout.addWidget(self.initial_volume, 6, 2)
        # self.Layout.addWidget(QLabel("cm<sup>3</sup>"), 6, 3)
        
        # self.initial_bulk_density = QLineEdit()
        # self.initial_bulk_density.setReadOnly(True)
        # self.Layout.addWidget(QLabel("Initial Bulk Density"), 7, 0)
        # self.Layout.addWidget(QLabel("\u03C1<sub>0</sub>"), 7, 1)
        # self.Layout.addWidget(self.initial_bulk_density, 7, 2)
        # self.Layout.addWidget(QLabel("g/cm<sup>3</sup>"), 7, 3)

        # self.Layout.addWidget(QWidget(),8,0,1,4)

        # self.Layout.setRowStretch(0,0)
        # self.Layout.setRowStretch(1,0)
        # self.Layout.setRowStretch(2,0)
        # self.Layout.setRowStretch(3,0)
        # self.Layout.setRowStretch(4,0)
        # self.Layout.setRowStretch(5,0)
        # self.Layout.setRowStretch(6,0)
        # self.Layout.setRowStretch(7,0)
        # self.Layout.setRowStretch(8,1)
        # self.Layout.setColumnStretch(0,1)
        # self.Layout.setColumnStretch(1,1)
        # self.Layout.setColumnStretch(2,1)
        # self.Layout.setColumnStretch(3,0)
        # self.Layout.setHorizontalSpacing(15)
        # self.Layout.setVerticalSpacing(15)

        self.setLayout(self.Layout)
    