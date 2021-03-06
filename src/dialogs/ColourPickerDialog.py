from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtGui import QCursor
from PySide6.QtCore import Signal, QModelIndex, Qt
from models import ColourPickerTableModel
from views import ColourPickerTableView
import logging

log = logging.getLogger(__name__)

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

