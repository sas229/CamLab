from PySide6.QtWidgets import QItemDelegate, QLineEdit
from PySide6.QtCore import Qt, QRect

class StringDelegate(QItemDelegate):
    """
    A delegate that returns a string from a line edit.
    """
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        linedit = QLineEdit(parent)
        linedit.setAlignment(Qt.AlignCenter)
        return linedit

    def setModelData (self, editor, model, index):
        # Update the edited text in the model after validation by checking the string length is greater than zero.
        value = editor.text()
        self.text = value
        if len(value) != 0:
            model.setData(index, value, Qt.EditRole)

    def paint(self, painter, option, index):
        # Override paint method to put centered text in cell.
        x1, y1, x2, y2 = option.rect.getCoords()
        rect = QRect()
        rect.setCoords(x1, y1, x2, y2)
        model = index.model()
        string = str(model.data(index, role=Qt.DisplayRole))
        option.displayAlignment = Qt.AlignCenter
        self.drawDisplay(painter, option, rect, string)