from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QComboBox, QApplication
from PySide6.QtCore import Qt

class ComboBoxDelegate(QStyledItemDelegate):
    """
    A delegate that displays a combobox populated with the supplied items.
    """
    def __init__(self, items, selected = []):
        super().__init__()
        self.items = items
        self.selected = selected

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.currentIndexChanged.connect(self.commit_editor)
        editor.addItems(self.items)
        if len(self.selected) > 1:
            index = self.items.index(self.selected[index.row()-1])
        else:
            index = 0
        editor.setCurrentIndex(index)
        return editor

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        value = index.model().data(index)
        text = str(index.model().data(index))
        # Perform check for feedback channel selection ComboBox application.
        if text not in self.items:
            text = self.items[0]
        option.text = text
        option.displayAlignment = Qt.AlignCenter
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)