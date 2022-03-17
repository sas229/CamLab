from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, Slot
import logging

log = logging.getLogger(__name__)

class SequenceToolBar(QToolBar):
    
    def __init__(self):
        super().__init__()
        self.darkMode = True
        self.running = False

        # Add command QAction.
        self.addButton = QAction()
        self.addButton.setToolTip("Click to add a command.")
        self.addAction(self.addButton)

        # Remove command QAction.
        self.removeButton = QAction()
        self.removeButton.setToolTip("Click to remove the selected command.")
        self.removeButton.setVisible(True)
        self.addAction(self.removeButton)

        # Move up QAction.
        self.moveUpButton = QAction()
        self.moveUpButton.setToolTip("Move the selected command up.")
        self.moveUpButton.setVisible(True)
        self.addAction(self.moveUpButton)

        # Move down QAction.
        self.moveDownButton = QAction()
        self.moveDownButton.setToolTip("Move the selected command down.")
        self.moveDownButton.setVisible(True)
        self.addAction(self.moveDownButton)

        # self.addSeparator()

        # Load sequence QAction.
        self.loadSequenceButton = QAction()
        self.loadSequenceButton.setToolTip("Click to load a sequence.")
        self.addAction(self.loadSequenceButton)

        # Save sequence QAction.
        self.saveSequenceButton = QAction()
        self.saveSequenceButton.setToolTip("Click to save the sequence.")
        self.addAction(self.saveSequenceButton)

    @Slot()
    def updateIcons(self):
        # Change appearance between light and dark modes.
        self.loadSequenceButton.setIcon(QIcon("icon:/secondaryText/read_more.svg"))
        self.saveSequenceButton.setIcon(QIcon("icon:/secondaryText/save_alt.svg"))
        self.addButton.setIcon(QIcon("icon:/secondaryText/add_circle.svg"))
        self.moveUpButton.setIcon(QIcon("icon:/secondaryText/move_up.svg"))
        self.moveDownButton.setIcon(QIcon("icon:/secondaryText/move_down.svg"))
        self.removeButton.setIcon(QIcon("icon:/secondaryText/remove_circle.svg"))