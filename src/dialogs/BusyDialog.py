from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from widgets.WaitingIndicator import WaitingIndicator 
import logging

log = logging.getLogger(__name__)

class BusyDialog(QDialog):

    def __init__(self, parent, message):
        super().__init__(parent)
        self.setFixedSize(400, 100)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.message = QLabel(message)
        self.waitingIndicator = WaitingIndicator(centerOnParent=False)
        self.waitingIndicator.start()

        self.layout = QHBoxLayout()
        self.layout.addSpacing(20)
        self.layout.addWidget(self.waitingIndicator)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.message)
        self.setLayout(self.layout)