from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtCore import Slot, Signal
from src.widgets import PlotWindow

class TabInterface(QTabWidget):
    tabToWindow = Signal(QWidget, int)

    def __init__(self):
        super().__init__()
        
        # Settings.
        self.setTabsClosable(True)

        # Connections.
        self.tabCloseRequested.connect(self.closeTab)
        self.tabBarDoubleClicked.connect(self.floatTab)

    def floatTab(self, index):
        widget = self.widget(index)
        self.tabToWindow.emit(widget, index)

    def addPersistentTab(self, widget, name):
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
    
    def insertPersistentTab(self, index, widget, name):
        self.insertTab(index, widget, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)

    @Slot(int)
    def closeTab(self, index):
        widget = self.widget(index)
        if isinstance(widget, PlotWindow):
            widget.close()
            widget.deleteLater()
            widget = None
        self.removeTab(index)
    