from PySide6.QtWidgets import QItemDelegate, QStyle, QLineEdit
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt, QLocale, QRect

class FloatValidatorDelegate(QItemDelegate):
    """
    A delegate that validates float input from a table cell.
    """
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        linedit = QLineEdit(parent)
        linedit.setAlignment(Qt.AlignCenter)
        validator = QDoubleValidator(self, decimals=3)
        validator.setNotation(QDoubleValidator.StandardNotation)
        locale = QLocale("en")
        locale.setNumberOptions(QLocale.IncludeTrailingZeroesAfterDot)
        validator.setLocale(locale)
        linedit.setValidator(validator)
        return linedit

    def setModelData (self, editor, model, index):
        # Change the underlying data model by updating the value as a float.
        value = float(editor.text())        
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