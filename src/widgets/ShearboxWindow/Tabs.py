from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QVBoxLayout
from PySide6.QtCore import Slot, Signal
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
        self.specimen1 = QWidget()
        self.specimen2 = QWidget()
        self.specimen3 = QWidget()
        self.specimen4 = QWidget()

        self.add_persistent_tab(self.specimen1, "Specimen 1")
        self.add_persistent_tab(self.specimen2, "Specimen 2")
        self.add_persistent_tab(self.specimen3, "Specimen 3")
        self.add_persistent_tab(self.specimen4, "Specimen 4")

        self.build_tabs()

        # Connections.
        self.tabCloseRequested.connect(self.close_tab)
        self.tabBarDoubleClicked.connect(self.float_tab)

    def build_tabs(self):
        for tab in [self.specimen1,self.specimen2,self.specimen3,self.specimen4]:
            tab.Layout = QVBoxLayout()
            tab.steps = SpecimenTabs()
            tab.Layout.addWidget(tab.steps)
            tab.setLayout(tab.Layout)

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
    