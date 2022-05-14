import os
from PySide6.QtWidgets import QGroupBox, QWidget, QVBoxLayout
from models.CommandTreeModel import CommandTreeModel
from views.CommandTreeView import CommandTreeView
from widgets.SequenceToolBar import SequenceToolBar

class CommandTree(QGroupBox):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = []

        self.background = QWidget()
        color = os.environ['QTMATERIAL_SECONDARYCOLOR']
        style = "background-color:" + color + ";"
        self.background.setStyleSheet(style)
        self.toolbar = SequenceToolBar()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.background)
        self.layout.setStretch(0, 1)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.commandTreeModel = CommandTreeModel() 
        self.commandTreeModel.setModelData(self._data)

        self.commandTreeView = CommandTreeView()
        self.commandTreeView.setModel(self.commandTreeModel)
        self.commandTreeView.setSpanningColumns()

        self.treeViewLayout = QVBoxLayout()
        self.treeViewLayout.setSpacing(0)
        self.treeViewLayout.setContentsMargins(0,0,0,0)
        self.treeViewLayout.addWidget(self.commandTreeView)
        self.background.setLayout(self.treeViewLayout)

        self.setFixedWidth(387)

    def appendCommand(self, command):
        self.commandTreeModel.appendCommand(command)
        self.commandTreeView.setSpanningColumns()

    def updateBackground(self):
        color = os.environ['QTMATERIAL_SECONDARYCOLOR']
        style = "background-color:" + color + ";"
        self.background.setStyleSheet(style)
