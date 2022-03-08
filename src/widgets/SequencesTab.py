from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal

class SequencesTab(QWidget):
    sequencesWindowClosed = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self.setWhatsThis("sequences")

    def closeEvent(self, event):
        self.sequencesWindowClosed.emit(self)