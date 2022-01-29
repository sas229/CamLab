from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QTableView, QHeaderView, QAbstractItemView
from PySide6.QtCore import QModelIndex
from src.delegates import CheckBoxDelegate, ConnectionIconDelegate, StatusIconDelegate, FloatValidatorDelegate, StringDelegate, ComboBoxDelegate


class DeviceTableView(QTableView):

    def __init__(self, configuration, data=[], parent=None):
        super(DeviceTableView, self).__init__(parent)
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
        self.connectionIconDelegate.setIcon(self.darkMode)
        self.statusIconDelegate = StatusIconDelegate()
        self.statusIconDelegate.setIcon(self.darkMode) 

        self.setItemDelegateForColumn(0, self.nameCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.stringDelegate)
        self.setItemDelegateForColumn(2, self.connectionIconDelegate)
        self.setItemDelegateForColumn(3, self.stringDelegate)
        self.setItemDelegateForColumn(4, self.statusIconDelegate)

class AcquisitionTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(AcquisitionTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
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

class ChannelsTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(ChannelsTableView, self).__init__(parent)
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

class ColourPickerTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(ColourPickerTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)

        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setDefaultSectionSize(25)

class ControlTableView(QTableView):

    def __init__(self, controlModeList, controlActuatorList, feedbackChannelList, parent = None):
        super(ControlTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)

        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.checkBoxDelegate = CheckBoxDelegate("channel")
        self.stringDelegate = StringDelegate()
        self.floatValidatorDelegate = FloatValidatorDelegate()

        self.controlModeComboBoxDelegate = ComboBoxDelegate(controlModeList)
        self.controlActuatorComboBoxDelegate = ComboBoxDelegate(controlActuatorList)
        self.feedbackChannelListComboBoxDelegate = ComboBoxDelegate(feedbackChannelList)

        self.setItemDelegateForColumn(0, self.checkBoxDelegate)
        self.setItemDelegateForColumn(1, self.controlModeComboBoxDelegate)
        self.setItemDelegateForColumn(2, self.controlActuatorComboBoxDelegate)
        self.setItemDelegateForColumn(3, self.feedbackChannelListComboBoxDelegate)

    def persistentEditorOpen(self):
        self.openPersistentEditor(self.model().index(0, 1))
        self.openPersistentEditor(self.model().index(0, 2))
        self.openPersistentEditor(self.model().index(0, 3))
        self.openPersistentEditor(self.model().index(1, 1))
        self.openPersistentEditor(self.model().index(1, 2))
        self.openPersistentEditor(self.model().index(1, 3))

    def persistentEditorClose(self):
        self.closePersistentEditor(self.model().index(0, 1))
        self.closePersistentEditor(self.model().index(0, 2))
        self.closePersistentEditor(self.model().index(0, 3))
        self.closePersistentEditor(self.model().index(1, 1))
        self.closePersistentEditor(self.model().index(1, 2))
        self.closePersistentEditor(self.model().index(1, 3))


