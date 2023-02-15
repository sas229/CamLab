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
        self.specimen1 = QWidget()
        self.specimen2 = QWidget()
        self.specimen3 = QWidget()
        self.specimen4 = QWidget()

        self.add_persistent_tab(self.specimen1, "Specimen 1")
        # self.add_persistent_tab(self.specimen2, "Specimen 2")
        # self.add_persistent_tab(self.specimen3, "Specimen 3")
        # self.add_persistent_tab(self.specimen4, "Specimen 4")

        self.build_specimen1()
        self.build_specimen2()
        self.build_specimen3()
        self.build_specimen4()

        # Connections.
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarDoubleClicked.connect(self.float_tab)

    def build_specimen1(self):
        self.specimen1Layout = QGridLayout()
        num_validator = QDoubleValidator()
        
        self.specimen1_initial_height = QLineEdit()
        self.specimen1_initial_height.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Height"), 0, 0)
        self.specimen1Layout.addWidget(QLabel("H<sub>0</sub>"), 0, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_height, 0, 2)
        self.specimen1Layout.addWidget(QLabel("mm"), 0, 3)

        self.specimen1_initial_weight = QLineEdit()
        self.specimen1_initial_weight.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Weight"), 1, 0)
        self.specimen1Layout.addWidget(QLabel("W<sub>0</sub>"), 1, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_weight, 1, 2)
        self.specimen1Layout.addWidget(QLabel("g"), 1, 3)
        
        self.specimen1_initial_width = QLineEdit()
        self.specimen1_initial_width.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Width"), 2, 0)
        self.specimen1Layout.addWidget(QLabel("w<sub>0</sub>"), 2, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_width, 2, 2)
        self.specimen1Layout.addWidget(QLabel("mm"), 2, 3)
        
        self.specimen1_initial_depth = QLineEdit()
        self.specimen1_initial_depth.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Depth"), 3, 0)
        self.specimen1Layout.addWidget(QLabel("d<sub>0</sub>"), 3, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_depth, 3, 2)
        self.specimen1Layout.addWidget(QLabel("mm"), 3, 3)
        
        self.specimen1_particle_density = QLineEdit()
        self.specimen1_particle_density.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Particle Density"), 4, 0)
        self.specimen1Layout.addWidget(QLabel("\u03C1<sub>s</sub>"), 4, 1)
        self.specimen1Layout.addWidget(self.specimen1_particle_density, 4, 2)
        self.specimen1Layout.addWidget(QLabel("g/cm<sup>3</sup>"), 4, 3)
        
        self.specimen1_initial_area = QLineEdit()
        self.specimen1_initial_area.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Area"), 5, 0)
        self.specimen1Layout.addWidget(QLabel("A<sub>0</sub>"), 5, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_area, 5, 2)
        self.specimen1Layout.addWidget(QLabel("cm<sup>2</sup>"), 5, 3)
        
        self.specimen1_initial_volume = QLineEdit()
        self.specimen1_initial_volume.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Volume"), 6, 0)
        self.specimen1Layout.addWidget(QLabel("V<sub>0</sub>"), 6, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_volume, 6, 2)
        self.specimen1Layout.addWidget(QLabel("cm<sup>3</sup>"), 6, 3)
        
        self.specimen1_initial_bulk_density = QLineEdit()
        self.specimen1_initial_bulk_density.setValidator(num_validator)
        self.specimen1Layout.addWidget(QLabel("Initial Bulk Density"), 7, 0)
        self.specimen1Layout.addWidget(QLabel("\u03C1<sub>0</sub>"), 7, 1)
        self.specimen1Layout.addWidget(self.specimen1_initial_bulk_density, 7, 2)
        self.specimen1Layout.addWidget(QLabel("g/cm<sup>3</sup>"), 7, 3)

        self.specimen1Layout.addWidget(QWidget(),8,0,1,4)

        self.specimen1Layout.setRowStretch(0,0)
        self.specimen1Layout.setRowStretch(1,0)
        self.specimen1Layout.setRowStretch(2,0)
        self.specimen1Layout.setRowStretch(3,0)
        self.specimen1Layout.setRowStretch(4,0)
        self.specimen1Layout.setRowStretch(5,0)
        self.specimen1Layout.setRowStretch(6,0)
        self.specimen1Layout.setRowStretch(7,0)
        self.specimen1Layout.setRowStretch(8,1)
        self.specimen1Layout.setColumnStretch(0,1)
        self.specimen1Layout.setColumnStretch(1,1)
        self.specimen1Layout.setColumnStretch(2,1)
        self.specimen1Layout.setColumnStretch(3,0)
        self.specimen1Layout.setHorizontalSpacing(15)
        self.specimen1Layout.setVerticalSpacing(15)

        self.specimen1.setLayout(self.specimen1Layout)

    def build_specimen2(self):
        pass

    def build_specimen3(self):
        pass

    def build_specimen4(self):
        pass

    def float_tab(self, index):
        """Method to float plot, preview or control tab as window."""
        widget = self.widget(index)
        if widget.whatsThis() == "plot" or widget.whatsThis() == "control" or widget.whatsThis() == "preview":
            self.tabToWindow.emit(widget, index)
            log.info("Tab converted to window.")

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def insert_persistent_tab(self, index, widget, name):
        """Method to insert a persistent tab at the given index."""
        self.insertTab(index, widget, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def add_persistent_tab_icon(self, widget, name, icon):
        """Method to add persistent tab with icon."""
        self.addTab(widget, icon, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def insert_persistent_tab_icon(self, index, widget, name, icon):
        """Method to insert a persistent tab at the given index with icon."""
        self.insertTab(index, widget, icon, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)

    @Slot(int)
    def close_tab(self, index):
        """Method to close tab."""
        widget = self.widget(index)
        # Delete if a plot widget.
        if isinstance(widget, PlotWindow):
            plotNumber = widget.plotNumber
            self.remove_plot.emit(plotNumber)
        self.removeTab(index)
        log.info("Tab removed.")
    