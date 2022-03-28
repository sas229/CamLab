from PySide6.QtWidgets import QTableView, QHeaderView
from src.delegates import CheckBoxDelegate, ConnectionIconDelegate, StatusIconDelegate, StringDelegate, DeviceIconDelegate

class DeviceTableView(QTableView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        horizontalHeader.setStretchLastSection(True)

        self.nameCheckBoxDelegate = CheckBoxDelegate("name")
        self.stringDelegate = StringDelegate()
        self.connectionIconDelegate = ConnectionIconDelegate() 
        self.statusIconDelegate = StatusIconDelegate()
        self.deviceIconDelegate = DeviceIconDelegate()

        self.setItemDelegateForColumn(0, self.nameCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.deviceIconDelegate)
        self.setItemDelegateForColumn(2, self.stringDelegate)
        self.setItemDelegateForColumn(3, self.stringDelegate)
        self.setItemDelegateForColumn(4, self.connectionIconDelegate)
        self.setItemDelegateForColumn(5, self.statusIconDelegate)
        self.setItemDelegateForColumn(6, self.stringDelegate)