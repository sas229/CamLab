from PySide6.QtWidgets import QItemDelegate
from PySide6.QtCore import Qt, QEvent, QRect

class CheckBoxDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell into the column to which it's applied.
    """
    def __init__(self, key = None):
        super().__init__()
        self._key = key


    def createEditor(self, parent, option, index):
        # Important, otherwise an editor is created if the user clicks in this cell.
        return None

    def paint(self, painter, option, index):
        # Paint a checkbox with a label and adjust the lateral positioning.
        if self._key == None:
            # If no key is supplied then draw a centred checkbox.
            self.drawCheck(painter, option, option.rect, Qt.Unchecked if index.data() == False else Qt.Checked)
        else:
            # If a key is supplied, draw the text and (manually) re-centre everything.
            x1, y1, x2, y2 = option.rect.getCoords()
            adjRect = QRect()
            adjRect.setCoords(x1, y1, x2, y2)
            dx = -25
            adjRect.adjust(dx,0,dx,0)
            self.drawCheck(painter, option, adjRect, Qt.Unchecked if index.data() == False else Qt.Checked)
            model = index.model()
            item = model._data[index.row()]
            string = item[self._key]
            adjRect = QRect()
            adjRect.setCoords(x1, y1, x2, y2)
            dx = -int((x1-x2)/2)-5
            adjRect.adjust(dx,0,dx,0)
            self.drawDisplay(painter, option, adjRect, string)

    def editorEvent(self, event, model, option, index):
        # Change the data in the model and the state of the checkbox if the user 
        # presses the left mousebutton and this cell is editable. Otherwise do nothing.
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            # Change the checkbox-state.
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData (self, editor, model, index):
        # Change the underlying data model.
        model.setData(index, not index.data(), Qt.EditRole)