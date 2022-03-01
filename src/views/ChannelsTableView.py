from PySide6.QtWidgets import QTableView
from src.delegates import CheckBoxDelegate

class ChannelsTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setStretchLastSection(True)

        self.channelCheckBoxDelegate = CheckBoxDelegate()

        self.setItemDelegateForColumn(0, self.channelCheckBoxDelegate)
