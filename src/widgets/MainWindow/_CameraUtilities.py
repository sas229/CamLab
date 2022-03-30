from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from src.widgets.CameraTab import CameraTab
import copy
import logging

log = logging.getLogger(__name__)

class CameraUtilities:

    @Slot(str)
    def addCameraTab(self, name):
        """Add camera tab."""
        # Store the widget.
        cameraTab = CameraTab(name)
        cameraTab.setConfiguration(self.manager.configuration)
        self.previews.update({name: cameraTab})

        # Add widget to tab and show if control enabled.
        tabName = "Preview (" + name + ")"
        self.tabs.addPersistentTab(self.previews[name], tabName) 
        index = self.tabs.indexOf(self.previews[name])
        self.tabs.setTabVisible(index, False)

        # Connections.
        self.previews[name].previewWindowClosed.connect(self.windowToTab)

    @Slot(str)
    def showCameraTab(self, name):
        """Show camera tab."""
        index = self.tabs.indexOf(self.previews[name])
        self.tabs.setTabVisible(index, True)

    @Slot(str)
    def hideCameraTab(self, name):
        """Hide camera tab."""
        index = self.tabs.indexOf(self.previews[name])
        self.tabs.setTabVisible(index, False)

    @Slot(str, bool)
    def updatePreviewVisibility(self, name, connect):
        """Update preview visibility."""
        if connect == True:
            if self.deviceConfigurationWidget[name].previewButton.isChecked() == True:
                self.showCameraTab(name)
        elif connect == False:
            self.hideCameraTab(name)