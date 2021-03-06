from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
import operator
import logging 

log = logging.getLogger(__name__)

class DeviceTableModel(QAbstractTableModel):
    """Methods for data and setData also emit signals to add and remove tabs from the acquisition tab widget when enabled or disabled."""
    deviceConnectStatusUpdated = Signal(str, bool)
    numberDevicesEnabled = Signal(int)

    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        data = sorted(data, key=operator.itemgetter(0))
        self._data = data
        self._column_name = [
            "Name",
            "Type",
            "Model",
            "ID",
            "Cxn",
            "Conn",
            "Address"
        ] 

        log.info("Device table model instantiated.")

    def rowCount(self, parent=QModelIndex()):
        if self._data == []:
            return 0
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        if self._data == []:
            return 0
        return 7
    
    def data(self, index, role):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.DisplayRole:
            if index.isValid():
                if self._data != []:
                    item = self._data[index.row()]
                    if index.column() == 0:
                        self.numberDevicesEnabled.emit(len(self.enabledDevices()))
                        return item["connect"]
                    elif index.column() == 1:
                        return item["type"]
                    elif index.column() == 2:
                        return item["model"]
                    elif index.column() == 3:
                        return item["id"]
                    elif index.column() == 4:
                        return item["connection"]
                    elif index.column() == 5:
                        return item["status"]
                    elif index.column() == 6:
                        return item["address"]
        elif role == Qt.CheckStateRole and index.column()==0:
            if index.isValid():
                item = self._data[index.row()]
                return Qt.Checked if item["connect"] else Qt.Unchecked
        
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            item = self._data[index.row()]
            if index.column() == 0:
                item["connect"] = value
                self.deviceConnectStatusUpdated.emit(item['name'], item['connect'])
                self.numberDevicesEnabled.emit(len(self.enabledDevices())) 
            elif index.column() == 6:
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