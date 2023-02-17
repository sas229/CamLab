from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QGridLayout, QLineEdit, QLabel
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QDoubleValidator
from widgets.PlotWindow import PlotWindow
import logging 

log = logging.getLogger(__name__)

class SpecimenTabs(QTabWidget):
    tabToWindow = Signal(QWidget, int)
    remove_plot = Signal(str)

    def __init__(self):
        super().__init__()
        """TabInterface init."""

        # Settings.
        self.specimens = dict()

        for i in range(1,5):
            specimen = f"Specimen {i}"
            self.specimens[specimen] = dict()
            self.build_specimen(specimen)
            if i == 1:
                self.add_persistent_tab(self.specimens[specimen]["widget"], specimen)

        # Connections.
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarDoubleClicked.connect(self.float_tab)

    def build_specimen(self, specimen):
        self.specimens[specimen]["widget"] = QWidget()
        self.specimens[specimen]["layout"] = QGridLayout()
        num_validator = QDoubleValidator()
        
        self.specimens[specimen]["initial_height"] = QLineEdit()
        self.specimens[specimen]["initial_height"].setValidator(num_validator)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Height"), 0, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("H<sub>0</sub>"), 0, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_height"], 0, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("mm"), 0, 3)

        self.specimens[specimen]["initial_weight"] = QLineEdit()
        self.specimens[specimen]["initial_weight"].setValidator(num_validator)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Weight"), 1, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("W<sub>0</sub>"), 1, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_weight"], 1, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("g"), 1, 3)
        
        self.specimens[specimen]["initial_width"] = QLineEdit()
        self.specimens[specimen]["initial_width"].setValidator(num_validator)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Width"), 2, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("w<sub>0</sub>"), 2, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_width"], 2, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("mm"), 2, 3)
        
        self.specimens[specimen]["initial_depth"] = QLineEdit()
        self.specimens[specimen]["initial_depth"].setValidator(num_validator)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Depth"), 3, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("d<sub>0</sub>"), 3, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_depth"], 3, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("mm"), 3, 3)
        
        self.specimens[specimen]["particle_density"] = QLineEdit()
        self.specimens[specimen]["particle_density"].setValidator(num_validator)
        self.specimens[specimen]["layout"].addWidget(QLabel("Particle Density"), 4, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("\u03C1<sub>s</sub>"), 4, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["particle_density"], 4, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("g/cm<sup>3</sup>"), 4, 3)
        
        self.specimens[specimen]["initial_area"] = QLineEdit()
        self.specimens[specimen]["initial_area"].setReadOnly(True)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Area"), 5, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("A<sub>0</sub>"), 5, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_area"], 5, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("cm<sup>2</sup>"), 5, 3)
        
        self.specimens[specimen]["initial_volume"] = QLineEdit()
        self.specimens[specimen]["initial_volume"].setReadOnly(True)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Volume"), 6, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("V<sub>0</sub>"), 6, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_volume"], 6, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("cm<sup>3</sup>"), 6, 3)
        
        self.specimens[specimen]["initial_bulk_density"] = QLineEdit()
        self.specimens[specimen]["initial_bulk_density"].setReadOnly(True)
        self.specimens[specimen]["layout"].addWidget(QLabel("Initial Bulk Density"), 7, 0)
        self.specimens[specimen]["layout"].addWidget(QLabel("\u03C1<sub>0</sub>"), 7, 1)
        self.specimens[specimen]["layout"].addWidget(self.specimens[specimen]["initial_bulk_density"], 7, 2)
        self.specimens[specimen]["layout"].addWidget(QLabel("g/cm<sup>3</sup>"), 7, 3)

        self.specimens[specimen]["layout"].addWidget(QWidget(),8,0,1,4)

        self.specimens[specimen]["layout"].setRowStretch(0,0)
        self.specimens[specimen]["layout"].setRowStretch(1,0)
        self.specimens[specimen]["layout"].setRowStretch(2,0)
        self.specimens[specimen]["layout"].setRowStretch(3,0)
        self.specimens[specimen]["layout"].setRowStretch(4,0)
        self.specimens[specimen]["layout"].setRowStretch(5,0)
        self.specimens[specimen]["layout"].setRowStretch(6,0)
        self.specimens[specimen]["layout"].setRowStretch(7,0)
        self.specimens[specimen]["layout"].setRowStretch(8,1)
        self.specimens[specimen]["layout"].setColumnStretch(0,1)
        self.specimens[specimen]["layout"].setColumnStretch(1,1)
        self.specimens[specimen]["layout"].setColumnStretch(2,1)
        self.specimens[specimen]["layout"].setColumnStretch(3,0)
        self.specimens[specimen]["layout"].setHorizontalSpacing(15)
        self.specimens[specimen]["layout"].setVerticalSpacing(15)

        self.specimens[specimen]["widget"].setLayout(self.specimens[specimen]["layout"])

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
        log.info("Specimen tab added.")

    def close_tab(self, index):
        """Method to close tab."""
        self.removeTab(index)
        log.info("Specimen tab removed.")
    