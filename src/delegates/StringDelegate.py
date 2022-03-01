from PySide6.QtWidgets import QItemDelegate, QLineEdit
from PySide6.QtCore import Qt

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
        if len(value) != 0:
            model = index.model()
            model.setData(index, value, Qt.EditRole)
