from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
import re

class CommandTreeModel(QStandardItemModel):
    
    def __init__(self, data=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = data

    def setModelData(self, data):
        # Set the model data.
        self.clear()
        self._data = data
        self.root = self.invisibleRootItem()
        self.setHorizontalHeaderLabels(["Command", "Value"])
        self.expanded = None
        for command in self._data:
            for key in command.keys():
                value = command[key]
                if key == "name":
                    parent = self.root
                    parent.appendRow([QStandardItem(value), QStandardItem(" ")])
                else:
                    parent = self.root.child(self.root.rowCount()-1)
                    words = self.camel_case_split(key)
                    string = words[-1].capitalize()
                    parent.appendRow([QStandardItem(string), QStandardItem(str(value))])

    def appendCommand(self, command):
        self._data.append(command)
        self.setModelData(self._data)

    def removeCommand(self, index):
        self._data.pop(index)
        self.setModelData(self._data)

    def flags(self, index):
        # Set flags.
        item = self.itemFromIndex(index)
        if not index.isValid():
            return Qt.NoItemFlags
        if item.parent() == None:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEnabled 
    
    def camel_case_split(self, identifier):
        matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
        return [m.group(0) for m in matches]