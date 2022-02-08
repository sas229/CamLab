from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QColor
import operator

class DeviceTableModel(QAbstractTableModel):
    """Methods for data and setData also emit signals to add and remove tabs from the acquisition tab widget when enabled or disabled."""
    deviceConnectStatusUpdated = Signal(str, int, int, bool)

    def __init__(self, data=[], parent=None):
        super(DeviceTableModel, self).__init__(parent)
        data = sorted(data, key=operator.itemgetter(0))
        self._data = data
        self._column_name = [
            "Name",
            "ID",
            "Connection",
            "Address",
            "Status"
        ] 

    def rowCount(self, parent=QModelIndex()):
        if self._data == []:
            return 0
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if self._data == []:
            return 0
        return 5
    
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            if index.isValid():
                if self._data != []:
                    item = self._data[index.row()]
                    if index.column() == 0:
                        return item["connect"]
                    elif index.column() == 1:
                        return item["id"]
                    elif index.column() == 2:
                        return item["connection"]
                    elif index.column() == 3:
                        return item["address"]
                    elif index.column() == 4:
                        return item["status"]
        elif role == Qt.CheckStateRole and index.column()==0:
            if index.isValid():
                item = self._data[index.row()]
                return Qt.Checked if item["connect"] else Qt.Unchecked
        
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            if index.column() == 0:
                item["connect"] = value
                self.deviceConnectStatusUpdated.emit(item['name'], item['id'], item['connection'], item['connect'])
            elif index.column() == 4:
                item["status"] = value
            self.dataChanged.emit(index, index, [])
            return True
        else:
            return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._column_name[section]
    
    def flags(self, index):
        if index.isValid():
            if index.column() == 0:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable
            else:
                return Qt.ItemIsEnabled

    def appendRow(self, device):
        # Sort list of devices alphabetically after append operation.
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append(device)
        self._data = sorted(self._data, key=operator.itemgetter("name"))
        self.endInsertRows()

        return True

    def clearData(self):
        """Method to clear data."""
        self.beginResetModel()       
        self._data.clear()
        self.endResetModel()

        return True

    def enabledDevices(self):
        """Method to return a list of dicts of target device IDs with status currently enabled."""
        enabledDevices = []
        for device in self._data:
            if device["connect"] == True and device["status"] == True:
                enabledDevices.append(device)
        return enabledDevices   
    
    def redrawIcons(self):
        """Method to redraw icons as a workaround."""
        index_begin = self.index(0, 0)
        index_end = self.index(self.rowCount(), self.columnCount())
        self.dataChanged.emit(index_begin, index_end, [])

class AcquisitionTableModel(QAbstractTableModel):

    acquisitionChannelTableUpdated = Signal()
    acquisitionChannelToggled = Signal(int)

    def __init__(self, data=[], parent=None):
        super(AcquisitionTableModel, self).__init__(parent)
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
                self.acquisitionChannelToggled.emit(index.row())
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

    def enabledChannels(self):
        """Return two lists containing enabled channels, names and units."""
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

class ChannelsTableModel(QAbstractTableModel):

    def __init__(self, data = [], parent=None):
        super(ChannelsTableModel, self).__init__(parent)
        self._data = data

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
        if  len(self._data) == 0:
            return 0
        else:
            return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft
        elif role == Qt.DisplayRole:
            if index.isValid():
                item = self._data[index.row()]
                if index.column() == 0:
                    return item["plot"]
                elif index.column() == 2:
                    return item["name"]
                elif index.column() == 3:
                    return item["device"]
                elif index.column() == 4:
                    return item["value"]
                elif index.column() == 5:
                    return item["unit"]
        elif role == Qt.DecorationRole:
            if index.isValid():
                item = self._data[index.row()]
                if index.column() == 1:
                    return QColor(item["colour"])
        elif role == Qt.CheckStateRole:
            if index.isValid():
                if index.column()==0:
                    item = self._data[index.row()]
                    return Qt.Checked if item["plot"] else Qt.Unchecked

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            if index.column() == 0:
                item["plot"] = value
            elif index.column() == 1:
                item["colour"] = value
            elif index.column() == 2:
                item["name"] = value
            elif index.column() == 3:
                item["device"] = value
            elif index.column() == 4:
                item["value"] = value
            elif index.column() == 5:
                item["unit"] = value
            self.dataChanged.emit(index, index, [])
            return True
        else:
            return False

    def flags(self, index):
        if index.isValid():
            if index.column() == 0:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable
            else:
                return Qt.ItemIsEnabled

class ColourPickerTableModel(QAbstractTableModel):

    def __init__(self, data=None, parent=None):
        super(ColourPickerTableModel, self).__init__(parent)
        self._data = [
            ["#ffcdd2", "#ef9a9a", "#e57373", "#ef5350", "#f44336", "#e53935", "#d32f2f", "#c62828", "#b71c1c"],
            ["#f8bbd0", "#f48fb1", "#f06292", "#ec407a", "#e91e63", "#d81b60", "#c2185b", "#ad1457", "#880e4f"],
            ["#e1bee7", "#ce93d8", "#ba68c8", "#ab47bc", "#9c27b0", "#8e24aa", "#7b1fa2", "#6a1b9a", "#4a148c"],
            ["#d1c4e9", "#b39ddb", "#9575cd", "#7e57c2", "#673ab7", "#5e35b1", "#512da8", "#4527a0", "#311b92"],
            ["#c5cae9", "#9fa8da", "#7986cb", "#5c6bc0", "#3f51b5", "#3949ab", "#303f9f", "#283593", "#1a237e"],
            ["#bbdefb", "#90caf9", "#64b5f6", "#42a5f5", "#2196f3", "#1e88e5", "#1976d2", "#1565c0", "#0d47a1"],
            ["#b3e5fc", "#81d4fa", "#4fc3f7", "#29b6f6", "#03a9f4", "#039be5", "#0288d1", "#0277bd", "#01579b"],
            ["#b2ebf2", "#80deea", "#4dd0e1", "#26c6da", "#00bcd4", "#00acc1", "#0097a7", "#00838f", "#006064"],
            ["#b2dfdb", "#80cbc4", "#4db6ac", "#26a69a", "#009688", "#00897b", "#00796b", "#00695c", "#004d40"],
            ["#c8e6c9", "#a5d6a7", "#81c784", "#66bb6a", "#4caf50", "#43a047", "#388e3c", "#2e7d32", "#1b5e20"],
            ["#dcedc8", "#c5e1a5", "#aed581", "#9ccc65", "#8bc34a", "#7cb342", "#689f38", "#558b2f", "#33691e"],
            ["#f0f4c3", "#e6ee9c", "#dce775", "#d4e157", "#cddc39", "#c0ca33", "#afb42b", "#9e9d24", "#827717"],
            ["#fff9c4", "#fff59d", "#fff176", "#ffee58", "#ffeb3b", "#fdd835", "#fbc02d", "#f9a825", "#f57f17"],
            ["#ffecb3", "#ffe082", "#ffd54f", "#ffca28", "#ffc107", "#ffb300", "#ffa000", "#ff8f00", "#ff6f00"],
            ["#ffe0b2", "#ffcc80", "#ffb74d", "#ffa726", "#ff9800", "#fb8c00", "#f57c00", "#ef6c00", "#e65100"],
            ["#ffccbc", "#ffab91", "#ff8a65", "#ff7043", "#ff5722", "#f4511e", "#e64a19", "#d84315", "#bf360c"],
            ["#d7ccc8", "#bcaaa4", "#a1887f", "#8d6e63", "#795548", "#6d4c41", "#5d4037", "#4e342e", "#3e2723"],
            ["#f5f5f5", "#eeeeee", "#e0e0e0", "#bdbdbd", "#9e9e9e", "#757575", "#616161", "#424242", "#212121"],
            ["#cfd8dc", "#b0bec5", "#90a4ae", "#78909c", "#607d8b", "#546e7a", "#455a64", "#37474f", "#263238"]
        ]

    def rowCount(self, index):
        return len(self._data[0])

    def columnCount(self, index):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DecorationRole:
            if index.isValid():
                return QColor(self._data[index.column()][index.row()])

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEnabled


class ControlTableModel(QAbstractTableModel):
    controlChannelToggled = Signal(int)
    controlChannelNameChanged = Signal (str, str)

    def __init__(self, data=[], parent=None):
        super(ControlTableModel, self).__init__(parent)
        self._data = data

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
            elif index.column() == 1:
                self.controlChannelNameChanged.emit(item["name"], value)
                item["name"] = value
            elif index.column() == 2:
                item["type"] = value
            elif index.column() == 3:
                item["control"] = value
            elif index.column() == 4:
                item["feedback"] = value
            self.controlChannelToggled.emit(index.row())
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

