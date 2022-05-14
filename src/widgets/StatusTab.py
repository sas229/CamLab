from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton
from PySide6.QtCore import Signal

class StatusTab(QWidget):
    statusWindowClosed = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self.setWhatsThis("status")

        self.runSequence = QPushButton("Run Jonathan's Sequence")
        self.runSequence.setFixedWidth(250)

        self.layout = QGridLayout()
        self.layout.addWidget(self.runSequence, 0, 0)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.statusWindowClosed.emit(self)