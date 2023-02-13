from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QGridLayout
from PySide6.QtCore import Slot, Signal
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
        self.hardware = QWidget()
        self.specimen = QWidget()
        self.consolidation = QWidget()
        self.shear = QWidget()

        self.add_persistent_tab(self.hardware, "Hardware")
        self.add_persistent_tab(self.specimen, "Specimen")
        self.add_persistent_tab(self.consolidation, "Consolidation setup")
        self.add_persistent_tab(self.shear, "Shear setup")

        self.build_tabs()

        # Connections.
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarDoubleClicked.connect(self.float_tab)

    def build_tabs(self):
        self.hardwareLayout = QGridLayout()
        self.hardware.setLayout(self.hardwareLayout)
        
        self.specimenLayout = QGridLayout()
        self.specimen.setLayout(self.specimenLayout)
        
        self.consolidationLayout = QGridLayout()
        self.consolidation.setLayout(self.consolidationLayout)
        
        self.shearLayout = QGridLayout()
        self.shear.setLayout(self.shearLayout)

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
    