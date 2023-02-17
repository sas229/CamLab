from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog, QToolButton, QMenu, QGridLayout, QPushButton
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, Slot
import logging

log = logging.getLogger(__name__)

class ToolBar(QToolBar):
    configure = Signal() 
    run = Signal() 
    loadConfiguration = Signal(str)
    saveConfiguration = Signal(str)
    
    def __init__(self):
        """initialise Toolbar
        """
        super().__init__()

        self.addSeparator()

        # Load configuration QAction.
        self.loadConfigButton = QAction()
        self.loadConfigButton.setToolTip("Click to load a configuration.")
        self.loadConfigButton.setVisible(True)
        self.addAction(self.loadConfigButton)

        # Save configuration QAction.
        self.saveConfigButton = QAction()
        self.saveConfigButton.setToolTip("Click to save the current configuration.")
        self.saveConfigButton.setVisible(True)
        self.addAction(self.saveConfigButton)

        self.addSeparator()

        # Run test.
        self.runButton = QAction()
        self.runButton.setToolTip("Run test.")
        self.runButton.setVisible(True)
        self.addAction(self.runButton)

    def emitLoadConfiguration(self):
        # Method to select a configuration file to load and emit it as a signal.
        filename, _ = QFileDialog.getOpenFileName(self,"Open CamLab configuration file", "","Yaml files (*.yaml)")
        self.loadConfiguration.emit(filename)

    def emitSaveConfiguration(self):
        # Method to select a configuration file to save to and emit it as a signal.
        filename, _ = QFileDialog.getSaveFileName(self,"Save CamLab configuration file", "","Yaml files (*.yaml)")
        self.saveConfiguration.emit(filename)