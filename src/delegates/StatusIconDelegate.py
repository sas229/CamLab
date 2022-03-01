from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

class StatusIconDelegate(QStyledItemDelegate):
    """
    Show the appropriate status icon.
    """
    def __init__(self):
        super().__init__()

    def paint(self, painter, option, index):
        if index.data(Qt.DisplayRole) == True:
            icon = QIcon("icon:/secondaryText/link.svg")
        elif index.data(Qt.DisplayRole) == False:
            icon = QIcon("icon:/secondaryText/link_off.svg")
        icon.paint(painter, option.rect, Qt.AlignCenter)