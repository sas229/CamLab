from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QDialogButtonBox
from PySide6.QtGui import QCursor
from PySide6.QtCore import Signal, QSize, QModelIndex, Qt
from src.models import ColourPickerTableModel
from src.views import ColourPickerTableView
from src.widgets.WaitingIndicator import WaitingIndicator 
import logging
from time import sleep

log = logging.getLogger(__name__)

class BusyDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 100)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.message = QLabel("Scanning for devices...")
        self.waitingIndicator = WaitingIndicator(centerOnParent=False)
        self.waitingIndicator.start()

        self.layout = QHBoxLayout()
        self.layout.addSpacing(20)
        self.layout.addWidget(self.waitingIndicator)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.message)
        self.setLayout(self.layout)

class ColourPickerDialog(QDialog):
    selectedColour = Signal(QModelIndex, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colourPickerTableModel = ColourPickerTableModel()
        self.colourPickerTableView = ColourPickerTableView()
        self.colourPickerTableView.setModel(self.colourPickerTableModel)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.colourPickerTableView)
        self.setLayout(self.layout)
        self.setFixedWidth(499)
        self.setFixedHeight(249)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.colourPickerTableView.clicked.connect(self.colourSelected)

    def colourSelected(self, index):
        model = index.model()
        colour = model._data[index.column()][index.row()]
        self.selectedColour.emit(self.targetIndex, colour)
        self.close()

    def showEvent(self, event):
        geom = self.frameGeometry()
        geom.moveTopRight(QCursor.pos())
        self.setGeometry(geom)
        super(ColourPickerDialog, self).showEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
            event.accept()
        else:
            super(ColourPickerDialog, self).keyPressEvent(event)

    def setTargetIndex(self, index):
        self.targetIndex = index

