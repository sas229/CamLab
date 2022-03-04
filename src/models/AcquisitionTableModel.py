from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
import logging 

log = logging.getLogger(__name__)

class AcquisitionTableModel(QAbstractTableModel):
    acquisitionChannelTableUpdated = Signal()
    acquisitionChannelToggled = Signal()

    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self._data = data
        if self._data != None:
            self._column_name = [
                "channel",
                "name",
                "unit",
                "slope",
                "offset",
                "autozero",
            ]    

        log.info("Acquisition table model instantiated.")

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

    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            if index.isValid():
                item = self._data[index.row()]
                if index.column() == 0:
                    return item["connect"]
                elif index.column() == 1:
                    return item["name"]
                elif index.column() == 2:
                    return item["unit"]
                elif index.column() == 3:
                    return float(item["slope"])
                elif index.column() == 4:
                    return float(item["offset"])
                elif index.column() == 5:
                    return item["autozero"]
        elif role == Qt.CheckStateRole:
            if index.isValid():
                if index.column()==0:
                    item = self._data[index.row()]
                    return Qt.Checked if item["connect"] else Qt.Unchecked
                if index.column()==5:
                    item = self._data[index.row()]
                    return Qt.Checked if item["autozero"] else Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            self.index = index.row()
            if index.column() == 0:
                item["connect"] = value
                # Emit a custom signal here to notify that the enabled channels have changed.
                self.acquisitionChannelTableUpdated.emit()
                self.acquisitionChannelToggled.emit()
            elif index.column() == 1:
                item["name"] = value
                # Emit a custom signal here to notify that the enabled channels have changed.
                self.acquisitionChannelTableUpdated.emit()
            elif index.column() == 2:
                item["unit"] = value
                # Emit a custom signal here to notify that the enabled channels have changed.
                self.acquisitionChannelTableUpdated.emit()
            elif index.column() == 3:
                item["slope"] = value
            elif index.column() == 4:
                item["offset"] = value
            elif index.column() == 5:
                item["autozero"] = value
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

    def acquisitionSettings(self):
        """Return lists containing the acquisition settings."""
        enabledChannels = []
        enabledNames = []
        enabledUnits = []
        enabledSlopes = []
        enabledOffsets = []
        enabledAutozero = []
        for channel in self._data:
            if channel["connect"] == True:
                enabledChannels.append(channel["channel"])
                enabledNames.append(channel["name"])
                enabledUnits.append(channel["unit"])
                enabledSlopes.append(channel["slope"])
                enabledOffsets.append(channel["offset"])
                enabledAutozero.append(channel["autozero"])
        return enabledChannels, enabledNames, enabledUnits, enabledSlopes, enabledOffsets, enabledAutozero

    def enabledChannels(self):
        """Return a list containing the enabled channels."""
        enabledChannels = []
        for channel in self._data:
            if channel["connect"] == True:
                enabledChannels.append(channel["channel"])
        return enabledChannels