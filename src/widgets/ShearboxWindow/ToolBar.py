from PySide6.QtWidgets import QToolBar, QFileDialog, QWidget, QSizePolicy
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Signal, Qt
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

        # Setup test.
        self.setupButton = QAction()
        self.setupButton.setToolTip("Setup test.")
        self.setupButton.setVisible(False)
        self.setupButton.setEnabled(False)
        self.addAction(self.setupButton)

        self.addSeparator()

        # Spacer to fill toolbar.
        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.spacer.setVisible(True)
        self.addWidget(self.spacer)

        # Load previous results.
        self.loadResultsButton = QAction()
        self.loadResultsButton.setToolTip("Click to load previous results.")
        self.loadResultsButton.setVisible(True)
        self.addAction(self.loadResultsButton)

        # Save results.
        self.saveResultsButton = QAction()
        self.saveResultsButton.setToolTip("Click to save results.")
        self.saveResultsButton.setVisible(False)
        self.addAction(self.saveResultsButton)

        self.addSeparator()

        # Load configuration.
        self.loadButton = QAction()
        self.loadButton.setToolTip("Click to load a configuration.")
        self.loadButton.setVisible(True)
        self.addAction(self.loadButton)

        # Save configuration.
        self.saveButton = QAction()
        self.saveButton.setToolTip("Click to save the current configuration.")
        self.saveButton.setVisible(True)
        self.addAction(self.saveButton)

        self.addSeparator()

        # Run test.
        self.runButton = QAction()
        self.runButton.setToolTip("Run test.")
        self.runButton.setVisible(True)
        self.addAction(self.runButton)

        # Pause test.
        self.pauseButton = QAction()
        self.pauseButton.setToolTip("Pause test.")
        self.pauseButton.setVisible(False)
        self.addAction(self.pauseButton)

        # Stop test.
        self.stopButton = QAction()
        self.stopButton.setToolTip("Stop test.")
        self.stopButton.setVisible(False)
        self.addAction(self.stopButton)

        self.setIcons()

        self.saveButton.triggered.connect(self.emitSaveConfiguration, Qt.UniqueConnection)
        self.loadButton.triggered.connect(self.emitLoadConfiguration, Qt.UniqueConnection)

    def setIcons(self):
        self.setupButton.setIcon(QIcon("icon:/secondaryText/settings.svg"))
        self.runButton.setIcon(QIcon("icon:/secondaryText/play_circle.svg"))
        self.pauseButton.setIcon(QIcon("icon:/secondaryText/pause_circle.svg"))
        self.stopButton.setIcon(QIcon("icon:/secondaryText/stop.svg"))
        self.loadResultsButton.setIcon(QIcon("icon:/secondaryText/stacked_line_chart.svg"))
        self.saveResultsButton.setIcon(QIcon("icon:/secondaryText/save_alt.svg"))
        self.loadButton.setIcon(QIcon("icon:/secondaryText/file_upload.svg"))
        self.saveButton.setIcon(QIcon("icon:/secondaryText/file_download.svg"))

    def emitLoadConfiguration(self):
        # Method to select a configuration file to load and emit it as a signal.
        filename, _ = QFileDialog.getOpenFileName(self,"Open CamLab configuration file", "defaults","Yaml files (*.yaml)")
        self.loadConfiguration.emit(filename)

    def emitSaveConfiguration(self):
        # Method to select a configuration file to save to and emit it as a signal.
        filename, _ = QFileDialog.getSaveFileName(self,"Save CamLab configuration file", "","Yaml files (*.yaml)")
        self.saveConfiguration.emit(filename)