from PySide6.QtWidgets import QDialog, QProgressDialog, QVBoxLayout, QLabel
from PySide6.QtGui import QCursor
from PySide6.QtCore import Signal, QSize, QModelIndex, Qt
from src.models import ColourPickerTableModel
from src.views import ColourPickerTableView
import logging

log = logging.getLogger(__name__)

class RefreshDevicesDialog(QProgressDialog):
    
    def __init__(self, parent):
        super(RefreshDevicesDialog, self).__init__(parent)  
        self.setParent(parent)
        # self.setWindowTitle("Finding devices...")
        self.setLabel(QLabel("Finding devices..."))
        # self.setModal(False)
        self.setRange(0,0)
        # self.setCancelButton(None)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.exec()
        # self.setVisible(False)
        # self.setWindowFlags(Qt.CustomizeWindowHint)   

class ColourPickerDialog(QDialog):
    selectedColour = Signal(QModelIndex, str)

    def __init__(self, parent=None):
        super(ColourPickerDialog, self).__init__(parent)
        self.colourPickerTableModel = ColourPickerTableModel()
        self.colourPickerTableView = ColourPickerTableView()
        self.colourPickerTableView.setModel(self.colourPickerTableModel)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.colourPickerTableView)
        self.setLayout(self.layout)
        self.setFixedWidth(500)
        self.setFixedHeight(250)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.colourPickerTableView.clicked.connect(self.colourSelected)

    #index of colour table
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

    #Index channel I clicked
    def setTargetIndex(self, index):
        self.targetIndex = index

