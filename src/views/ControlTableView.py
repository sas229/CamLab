from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView
from src.delegates import CheckBoxDelegate, StringDelegate, ComboBoxDelegate

class ControlTableView(QTableView):

    def __init__(self, controlModeList, controlActuatorList, feedbackChannelList, parent = None):
        super().__init__(parent)
        # self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QAbstractItemView.NoSelection)

        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.checkBoxDelegate = CheckBoxDelegate(key="channel")
        self.nameDelegate = StringDelegate()
        self.controlModeComboBoxDelegate = ComboBoxDelegate(controlModeList)
        self.controlActuatorComboBoxDelegate = ComboBoxDelegate(controlActuatorList)
        self.feedbackChannelListComboBoxDelegate = ComboBoxDelegate(feedbackChannelList)

        self.setItemDelegateForColumn(0, self.checkBoxDelegate)
        self.setItemDelegateForColumn(1, self.nameDelegate)
        self.setItemDelegateForColumn(2, self.controlModeComboBoxDelegate)
        self.setItemDelegateForColumn(3, self.controlActuatorComboBoxDelegate)
        self.setItemDelegateForColumn(4, self.feedbackChannelListComboBoxDelegate)

        

    def updateFeedbackChannelList(self, feedbackChannelList):
        self.feedbackChannelListComboBoxDelegate = ComboBoxDelegate(feedbackChannelList)
        self.setItemDelegateForColumn(4, self.feedbackChannelListComboBoxDelegate)
