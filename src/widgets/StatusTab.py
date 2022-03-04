from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal

class StatusTab(QWidget):
    statusWindowClosed = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self.setWhatsThis("status")

    def closeEvent(self, event):
        self.statusWindowClosed.emit(self)