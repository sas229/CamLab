from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor

class ChannelsTableModel(QAbstractTableModel):

    def __init__(self, data = [], parent=None):
        super().__init__(parent)
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