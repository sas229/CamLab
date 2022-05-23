from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtCore import Slot, Signal
from widgets.PlotWindow import PlotWindow
import logging 

log = logging.getLogger(__name__)

class TabInterface(QTabWidget):
    tab_to_window = Signal(QWidget, int)
    remove_plot = Signal(str)

    def __init__(self):
        super().__init__()
        
        # Settings.
        self.setTabsClosable(True)

        # Connections.
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBarDoubleClicked.connect(self.floatTab)

    def floatTab(self, index):
        # Add logic to only float tab if a plot, preview or control.
        widget = self.widget(index)
        self.tab_to_window.emit(widget, index)
        log.info("Tab converted to window.")

    def addPersistentTab(self, widget, name):
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def insertPersistentTab(self, index, widget, name):
        self.insertTab(index, widget, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def addPersistentTabIcon(self, widget, name, icon):
        self.addTab(widget, icon, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def insertPersistentTabIcon(self, index, widget, name, icon):
        self.insertTab(index, widget, icon, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)

    @Slot(int)
    def closeTab(self, index):
        widget = self.widget(index)
        # Delete if a plot widget.
        if isinstance(widget, PlotWindow):
            plotNumber = widget.plotNumber
            self.remove_plot.emit(plotNumber)
        self.removeTab(index)
        log.info("Tab removed.")
    