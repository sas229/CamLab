from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtCore import Slot
from src.widgets import PlotWindow

class TabInterface(QTabWidget):

    def __init__(self):
        super().__init__()
        
        # Settings.
        self.setMovable(True)
        self.setTabsClosable(True)

        # Connections.
        self.tabCloseRequested.connect(self.closeTab)

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
    