from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class DeviceIconDelegate(QStyledItemDelegate):
    """
    Show the appropriate device icon.
    """
    def __init__(self):
        super().__init__()

    def paint(self, painter, option, index):
        if index.data(Qt.DisplayRole) == "Hub":
            icon = QIcon("icon:/secondaryText/device_hub.svg")
        elif index.data(Qt.DisplayRole) == "Camera":
            icon = QIcon("icon:/secondaryText/camera.svg")
        elif index.data(Qt.DisplayRole) == "Press":
            icon = QIcon("icon:/secondaryText/press.svg")
        elif index.data(Qt.DisplayRole) == "RPi-PicoW-FHA":
            icon = QIcon("icon:/secondaryText/thermostat.svg")
        icon.paint(painter, option.rect, Qt.AlignCenter)