from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QGridLayout, QVBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Slot, Signal, Qt
from widgets.PlotWindow import PlotWindow
from widgets.ShearboxWindow.SpecimenTab import SpecimenTabs
import logging 

log = logging.getLogger(__name__)

class TabInterface(QTabWidget):
    tabToWindow = Signal(QWidget, int)
    remove_plot = Signal(str)

    def __init__(self):
        super().__init__()
        """TabInterface init."""

        # Settings.
        self.hardware = QWidget()
        self.specimen = QWidget()
        self.consolidation = QWidget()
        self.shear = QWidget()

        self.add_persistent_tab(self.hardware, "Hardware")
        self.add_persistent_tab(self.specimen, "Specimen")
        self.add_persistent_tab(self.consolidation, "Consolidation setup")
        self.add_persistent_tab(self.shear, "Shear setup")

        self.build_hardware_tab()
        self.build_specimen_tab()
        self.build_consolidation_tab()
        self.build_shear_tab()

        # Connections.
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarDoubleClicked.connect(self.float_tab)

    def build_hardware_tab(self):
        self.hardwareLayout = QGridLayout()

        self.hardwareLayout.addWidget(QLabel("Controllers & Transducer Inputs"), 0, 0, 1, 2, Qt.AlignCenter)
        self.hardwareLayout.addWidget(QLabel("Instrument"), 0, 2, Qt.AlignCenter)
        self.hardwareLayout.addWidget(QLabel("Channel"), 0, 3, Qt.AlignCenter)

        self.horiz_load_ins = QComboBox()
        self.horiz_load_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal load input"), 1, 0)
        self.hardwareLayout.addWidget(QLabel("N"), 1, 1)
        self.hardwareLayout.addWidget(self.horiz_load_ins, 1, 2)
        self.hardwareLayout.addWidget(self.horiz_load_chan, 1, 3)
        
        self.horiz_disp_ins = QComboBox()
        self.horiz_disp_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal displacement input"), 2, 0)
        self.hardwareLayout.addWidget(QLabel("mm"), 2, 1)
        self.hardwareLayout.addWidget(self.horiz_disp_ins, 2, 2)
        self.hardwareLayout.addWidget(self.horiz_disp_chan, 2, 3)
        
        self.vert_load_ins = QComboBox()
        self.vert_load_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical load input"), 3, 0)
        self.hardwareLayout.addWidget(QLabel("N"), 3, 1)
        self.hardwareLayout.addWidget(self.vert_load_ins, 3, 2)
        self.hardwareLayout.addWidget(self.vert_load_chan, 3, 3)
        
        self.vert_disp_ins = QComboBox()
        self.vert_disp_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical displacement input"), 4, 0)
        self.hardwareLayout.addWidget(QLabel("mm"), 4, 1)
        self.hardwareLayout.addWidget(self.vert_disp_ins, 4, 2)
        self.hardwareLayout.addWidget(self.vert_disp_chan, 4, 3)
        
        self.horiz_cont_ins = QComboBox()
        self.horiz_cont_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal Control Machine"), 5, 0)
        self.hardwareLayout.addWidget(self.horiz_cont_ins, 5, 2)
        self.hardwareLayout.addWidget(self.horiz_cont_chan, 5, 3)
        
        self.vert_cont_ins = QComboBox()
        self.vert_cont_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical Control Machine"), 6, 0)
        self.hardwareLayout.addWidget(self.vert_cont_ins, 6, 2)
        self.hardwareLayout.addWidget(self.vert_cont_chan, 6, 3)

        self.hardwareLayout.addWidget(QWidget(),7,0,1,4)

        self.hardwareLayout.setRowStretch(0,0)
        self.hardwareLayout.setRowStretch(1,1)
        self.hardwareLayout.setRowStretch(2,1)
        self.hardwareLayout.setRowStretch(3,1)
        self.hardwareLayout.setRowStretch(4,1)
        self.hardwareLayout.setRowStretch(5,1)
        self.hardwareLayout.setRowStretch(6,1)
        self.hardwareLayout.setRowStretch(7,1)
        self.hardwareLayout.setColumnStretch(0,0)
        self.hardwareLayout.setColumnStretch(1,0)
        self.hardwareLayout.setColumnStretch(2,1)
        self.hardwareLayout.setColumnStretch(3,1)
        self.hardwareLayout.setHorizontalSpacing(15)
        self.hardwareLayout.setVerticalSpacing(15)

        self.hardware.setLayout(self.hardwareLayout)
        
    def build_specimen_tab(self):
        self.specimenLayout = QVBoxLayout()
        self.specimen.tabs = SpecimenTabs()
        self.specimenLayout.addWidget(self.specimen.tabs)
        self.specimen.setLayout(self.specimenLayout)
        
    def build_consolidation_tab(self):
        self.consolidationLayout = QGridLayout()
        self.consolidation.setLayout(self.consolidationLayout)
        
    def build_shear_tab(self):
        self.shearLayout = QGridLayout()
        self.shear.setLayout(self.shearLayout)

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
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
    