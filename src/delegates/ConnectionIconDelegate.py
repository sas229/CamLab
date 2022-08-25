from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class ConnectionIconDelegate(QStyledItemDelegate):
    """
    Show the appropriate connection icon.
    """
    def __init__(self):
        super().__init__()
    
    def paint(self, painter, option, index):
        if index.data(Qt.DisplayRole) == 0:
            icon = QIcon("icon:/secondaryText/sensors_off.svg")
        elif index.data(Qt.DisplayRole) == 1:
            icon = QIcon("icon:/secondaryText/usb.svg")
        elif index.data(Qt.DisplayRole) == 3:
            icon = QIcon("icon:/secondaryText/lan.svg")
        elif index.data(Qt.DisplayRole) == 4:
            icon = QIcon("icon:/secondaryText/wifi.svg")
        elif index.data(Qt.DisplayRole) == 5:
            icon = QIcon("icon:/secondaryText/cable.svg")
        icon.paint(painter, option.rect, Qt.AlignCenter)