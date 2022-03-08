from PySide6.QtWidgets import QTableView
from src.delegates import ColouredBackgroundDelegate

class ColourPickerTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)

        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setDefaultSectionSize(25)

        self.colouredBackgroundDelegate = ColouredBackgroundDelegate()

        self.setItemDelegate(self.colouredBackgroundDelegate)