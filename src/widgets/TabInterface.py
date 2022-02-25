from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar
from PySide6.QtCore import Slot

class TabInterface(QTabWidget):

    def __init__(self):
        super().__init__()
        
        # Settings.
        self.setMovable(True)
        self.setTabsClosable(True)

        # Set default persistent tabs.
        self.addTab(QWidget(), "Dashboard")
        self.addTab(QWidget(), "Configuration")
        self.addTab(QWidget(), "Sequence")
        self.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tabBar().setTabButton(1, QTabBar.RightSide, None)
        self.tabBar().setTabButton(2, QTabBar.RightSide, None)

        # Connections.
        self.tabCloseRequested.connect(self.closeTab)

    def addPersistentTab(self, widget, name):
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)

    @Slot(int)
    def closeTab(self, index):
        currentWidget = self.widget(index)
        # currentWidget.deleteLater()
        self.removeTab(index)
    