from PySide6.QtWidgets import QTreeView
from PySide6.QtCore import Signal, QModelIndex, QItemSelectionModel

class CommandTreeView(QTreeView):
    commandSelected = Signal(int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setExpandsOnDoubleClick(False)
        self.expanded = QModelIndex()
        self.setExpandsOnDoubleClick(True)

    def mousePressEvent(self, event):
        # Expand the selected command and collapse the previosuly selected command.
        position = event.position().toPoint()
        index = self.indexAt(position)
        model = index.model()
        # If a model is found (i.e. if the click was within the tree).
        if model != None:
            item = model.itemFromIndex(index)
            parent = item.parent()  
            self.setCurrentIndex(index)
            # If there is a parent item because a subcommand was clicked, select it, otherwise select the clicked command.
            if parent != None:
                self.selectionModel().setCurrentIndex(model.indexFromItem(parent), QItemSelectionModel.Select)
            elif parent == None: 
                if index.row() != self.expanded.row():
                    self.setExpanded(self.expanded, False)
                    self.setExpanded(index, True)
                    self.expanded = index
                    self.commandSelected.emit(index.row())
                else:
                    self.setExpanded(index, not self.isExpanded(index))    

    def setSpanningColumns(self):
        # Set the command name to span both columns.
        model = self.model()
        commands = len(model._data)
        for index in range(commands):
            self.setFirstColumnSpanned(index, QModelIndex(), True)
        self.setColumnWidth(0, 170)
        self.setColumnWidth(1, 170)

    def keyPressEvent(self, event):
        # Override keyPressEvent to disable standard key bindings.
        return