from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal
from widgets.CommandBuilder import CommandBuilder
from widgets.CommandPreview import CommandPreview
from widgets.CommandTree import CommandTree

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
        self.commandBuilder.commandPreview.connect(self.commandPreview.preview_command)
        self.commandBuilder.clearPreview.connect(self.commandPreview.clear_preview)
        self.commandBuilder.addCommandToSequence.connect(self.commandTree.append_command)
        self.commandBuilder.addCommandToSequence.connect(self.hide_builder)

        self.commandTree.toolbar.addButton.triggered.connect(self.show_builder)

    def show_builder(self):
        self.commandBuilder.clear_command()
        self.commandBuilder.setVisible(True)
        self.commandTree.setVisible(False)

    def hide_builder(self):
        self.commandBuilder.setVisible(False)
        self.commandTree.setVisible(True)

    def save_sequence(self):
        print("Test")

    def update_tab(self):
        self.commandTree.toolbar.update_icons()
        self.commandBuilder.update_icons()
        self.commandTree.update_background()
        self.commandPreview.update_colours()

    def closeEvent(self, event):
        self.sequenceWindowClosed.emit(self)