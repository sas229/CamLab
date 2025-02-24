from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView
from delegates import CheckBoxDelegate, FloatValidatorDelegate, StringDelegate

class AcquisitionTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.channelCheckBoxDelegate = CheckBoxDelegate("channel")
        self.stringDelegate = StringDelegate()
        self.floatValidatorDelegate = FloatValidatorDelegate()
        self.checkBoxDelegate = CheckBoxDelegate()

        self.setItemDelegateForColumn(0, self.channelCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.stringDelegate)
        self.setItemDelegateForColumn(2, self.stringDelegate)
        self.setItemDelegateForColumn(3, self.floatValidatorDelegate)
        self.setItemDelegateForColumn(4, self.floatValidatorDelegate)
        self.setItemDelegateForColumn(5, self.checkBoxDelegate)