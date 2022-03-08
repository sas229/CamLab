from PySide6.QtWidgets import QItemDelegate, QStyle, QLineEdit
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt, QLocale

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