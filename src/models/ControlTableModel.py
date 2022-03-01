from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
import logging 

log = logging.getLogger(__name__)

class ControlTableModel(QAbstractTableModel):
    controlChannelToggled = Signal(int, bool)
    controlChannelNameChanged = Signal (str, str)
    controlWidgetChanged = Signal(int, int)
    controlFeedbackChannelChanged = Signal(int, int)
    
    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self._data = data

        log.info("Control table model instantiated.")

        if self._data != None:
            self._column_name = [
                "channel",
                "name",
                "type",
                "control",
                "feedback"
            ]

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        elif self._data == None:
            return 0
        else:
            return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._data[0])-1

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            if index.isValid():
                item = self._data[index.row()]
                if index.column() == 0:
                    return item["enable"]
                elif index.column() == 1:
                    return item["name"]
                elif index.column() == 2:
                    return item["type"]
                elif index.column() == 3:
                    return item["control"]
                elif index.column() == 4:
                    return item["feedback"]
        elif role == Qt.CheckStateRole:
            if index.isValid():
                if index.column()==0:
                    item = self._data[index.row()]
                    return Qt.Checked if item["enable"] else Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            self.index = index.row()
            if index.column() == 0:
                item["enable"] = value
                self.controlChannelToggled.emit(index.row(), value)
            elif index.column() == 1:
                self.controlChannelNameChanged.emit(item["name"], value)
                item["name"] = value
            elif index.column() == 2:
                item["type"] = value
                self.controlWidgetChanged.emit(index.row(), value)
            elif index.column() == 3:
                item["control"] = value
                self.controlWidgetChanged.emit(index.row(), value)
            elif index.column() == 4:
                item["feedback"] = value
                self.controlFeedbackChannelChanged.emit(index.row(), value)
            self.dataChanged.emit(index, index, [])
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._column_name[section]
            elif orientation == Qt.Vertical:
                return self._row_name[section]

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsEditable

    def enabledControls(self):
        """Method to return a list of dicts of enabled controls."""
        enabledControls = []
        for control in self._data:
            if control["enable"] == True:
                enabledControls.append(control)
        return enabledControls
