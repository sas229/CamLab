from PySide6.QtWidgets import QTableView, QHeaderView
from src.delegates import CheckBoxDelegate, ConnectionIconDelegate, StatusIconDelegate, StringDelegate

class DeviceTableView(QTableView):

    def __init__(self, configuration, data=[], parent=None):
        super().__init__(parent)
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.nameCheckBoxDelegate = CheckBoxDelegate("name")
        self.stringDelegate = StringDelegate()
        self.connectionIconDelegate = ConnectionIconDelegate() 
        self.statusIconDelegate = StatusIconDelegate()

        self.setItemDelegateForColumn(0, self.nameCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.stringDelegate)
        self.setItemDelegateForColumn(2, self.stringDelegate)
        self.setItemDelegateForColumn(3, self.connectionIconDelegate)
        self.setItemDelegateForColumn(4, self.stringDelegate)
        self.setItemDelegateForColumn(5, self.statusIconDelegate)