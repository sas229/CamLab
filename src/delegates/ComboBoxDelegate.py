from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QComboBox, QApplication
from PySide6.QtCore import Qt

class ComboBoxDelegate(QStyledItemDelegate):
    """
    A delegate that displays a combobox populated with the supplied items.
    """
    def __init__(self, items):
        super().__init__()
        self.items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.items)
        value = index.model().data(index)
        indexSelected = self.items.index(value)
        editor.setCurrentIndex(indexSelected)
        return editor

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        value = index.model().data(index)
        option.text = value
        option.displayAlignment = Qt.AlignCenter
        option.state = QStyle.State_NoChange
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)