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
        self.tabs.addPersistentTab(self.previews[name], name) 
        index = self.tabs.indexOf(self.previews[name])
        self.tabs.setTabVisible(index, True)

        # Convert tab to window if required by configuration.
        if self.manager.configuration["devices"][name]["preview"]["mode"] == "window":
            self.tabToWindow(self.previews[name], index)

        # Connections.
        self.previews[name].previewWindowClosed.connect(self.windowToTab)        

    @Slot(str, bool)
    def updatePreviewVisibility(self, name, connect):
        """Update preview visibility."""
        if name in self.previews:
            index = self.tabs.indexOf(self.previews[name])
            if connect == True:
                self.tabs.setTabVisible(index, True)
            elif connect == False:
                self.tabs.setTabVisible(index, False)