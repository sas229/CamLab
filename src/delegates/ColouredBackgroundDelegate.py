from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class ColouredBackgroundDelegate(QStyledItemDelegate):
    """
    A delegate that displays a coloured square.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        painter.save()
        color = index.data(Qt.DecorationRole)
        painter.fillRect(option.rect, QColor(color))
        painter.restore()
