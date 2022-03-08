from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
import logging 

log = logging.getLogger(__name__)

class ControlTableModel(QAbstractTableModel):
    controlChannelToggled = Signal(str, int, bool)
    controlChannelNameChanged = Signal (str, str)
    controlWidgetChanged = Signal(str, int, str)
    controlFeedbackChannelChanged = Signal(str, int, str)
    
    def __init__(self, device, data=[], parent=None):
        super().__init__(parent)
        self._device = device
        self._data = data

        log.info("Control table model instantiated.")

        if self._data != None:
            self._column_name = [
                "channel",
                "name",
                "type",
                "control",
                "feedback",
                "enable"
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
        return 6

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            if index.isValid():
                item = self._data[index.row()]
                if index.column() == 0:
                    return item["channel"]
                elif index.column() == 1:
                    return item["name"]
                elif index.column() == 2:
                    return item["type"]
                elif index.column() == 3:
                    return item["control"]
                elif index.column() == 4:
                    return item["feedback"]
                elif index.column() == 5:
                    return item["enable"]
        elif role == Qt.CheckStateRole:
            if index.isValid():
                if index.column()==5:
                    item = self._data[index.row()]
                    return Qt.Checked if item["enable"] else Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            if index.column() == 1:
                self.controlChannelNameChanged.emit(item["name"], value)
                item["name"] = value
            elif index.column() == 2:
                item["type"] = value
                self.controlWidgetChanged.emit(self._device, index.row(), value)
                if item["enable"] == True and value == "N/A":
                    item["enable"] = False
                    self.controlChannelToggled.emit(self._device, index.row(), False)
            elif index.column() == 3:
                item["control"] = value
                self.controlWidgetChanged.emit(self._device, index.row(), value)
                if item["enable"] == True and value == "N/A":
                    item["enable"] = False
                    self.controlChannelToggled.emit(self._device, index.row(), False)
            elif index.column() == 4:
                item["feedback"] = value
                self.controlFeedbackChannelChanged.emit(self._device, index.row(), value)
            elif index.column() == 5:
                # Only allow the checkbox to be toggled if type and control are specified.
                if item["type"] != "N/A" and item["control"] != "N/A":
                    item["enable"] = value
                    self.controlChannelToggled.emit(self._device, index.row(), value)
            self.dataChanged.emit(index, index, [])
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if section < self.columnCount():
                if orientation == Qt.Horizontal:
                    return self._column_name[section]
                elif orientation == Qt.Vertical:
                    return self._row_name[section]

    def flags(self, index):
        if index.column() == 0:
            return Qt.ItemIsEnabled
        elif index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsEditable
        

    def enabledControls(self):
        """Method to return a list of dicts of enabled controls."""
        enabledControls = []
        for control in self._data:
            if control["enable"] == True:
                enabledControls.append(control)
        return enabledControls
