from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal
from src.widgets.CommandBuilder import CommandBuilder
from src.widgets.CommandPreview import CommandPreview
from src.widgets.CommandTree import CommandTree

class SequenceTab(QWidget):
    sequenceWindowClosed = Signal(QWidget)

    def __init__(self):
        super().__init__()
        self.setWhatsThis("sequence")

        self.commandBuilder = CommandBuilder("Command Builder")
        self.commandBuilder.setVisible(False)
        self.commandPreview = CommandPreview("Command Preview")
        self.commandTree = CommandTree("Sequence")

        self.layout = QGridLayout()

        self.layout.addWidget(self.commandBuilder, 0, 2, 1, 1)
        self.layout.addWidget(self.commandTree, 1, 1)
        self.layout.addWidget(self.commandPreview, 1, 2)
        self.setLayout(self.layout)

        # Connections.
        self.commandBuilder.commandPreview.connect(self.commandPreview.previewCommand)
        self.commandBuilder.clearPreview.connect(self.commandPreview.clearPreview)
        self.commandBuilder.addCommandToSequence.connect(self.commandTree.appendCommand)
        self.commandBuilder.addCommandToSequence.connect(self.hideBuilder)

        self.commandTree.toolbar.addButton.triggered.connect(self.showBuilder)

    def showBuilder(self):
        self.commandBuilder.clearCommand()
        self.commandBuilder.setVisible(True)
        self.commandTree.setVisible(False)

    def hideBuilder(self):
        self.commandBuilder.setVisible(False)
        self.commandTree.setVisible(True)

    def updateTab(self):
        self.commandTree.toolbar.updateIcons()
        self.commandBuilder.updateIcons()
        self.commandTree.updateBackground()
        self.commandPreview.updateColours()

    def closeEvent(self, event):
        self.sequenceWindowClosed.emit(self)