from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from widgets.CameraTab import CameraTab
import copy
import logging

log = logging.getLogger(__name__)

class CameraUtilities:

    @Slot(str)
    def add_camera_tab(self, name):
        """Add camera tab."""
        # Store the widget.
        cameraTab = CameraTab(name)
        cameraTab.set_configuration(self.manager.configuration)
        self.previews.update({name: cameraTab})

        # Add widget to tab and show if control enabled.
        self.tabs.addPersistentTab(self.previews[name], name) 
        index = self.tabs.indexOf(self.previews[name])
        self.tabs.setTabVisible(index, True)

        # Convert tab to window if required by configuration.
        if self.manager.configuration["devices"][name]["preview"]["mode"] == "window":
            self.tab_to_window(self.previews[name], index)

        # Connections.
        self.previews[name].previewWindowClosed.connect(self.window_to_tab)        

    @Slot(str, bool)
    def upate_preview_visibility(self, name, connect):
        """Update preview visibility."""
        if name in self.previews:
            index = self.tabs.indexOf(self.previews[name])
            if connect == True:
                self.tabs.setTabVisible(index, True)
            elif connect == False:
                self.tabs.setTabVisible(index, False)