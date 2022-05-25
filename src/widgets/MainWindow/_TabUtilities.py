from PySide6.QtCore import Slot, Qt

class TabUtilities:
    
    @Slot()
    def window_to_tab(self, widget):
        """Method to convert window to tab."""
        if self.tabs.indexOf(widget) == -1:
            tabType = widget.whatsThis()
            widget.setWindowFlags(Qt.Widget)
            widget.set_tab()
            # Set order.
            if tabType == "configuration":
                self.tabs.insert_persistent_tab(0, widget, "Configuration")
            elif tabType == "sequence":
                self.tabs.insert_persistent_tab(1, widget, "Sequence")
            elif tabType == "status":
                self.tabs.insert_persistent_tab(2, widget, "Status")
            elif tabType == "control":
                controlDevice, channel = widget.ID.split(' ')
                devices = self.manager.deviceTableModel.enabledDevices()
                #  For each device get a list of enabled control channels.
                index = 3
                for device in devices:
                    deviceName = device["name"]
                    controls = self.manager.controlTableModels[deviceName].enabledControls()
                    for control in controls:
                        controlChannel = control["channel"]
                        controlChannelName = control["name"]
                        controlName = deviceName + " " + controlChannel
                        if deviceName == controlDevice and controlChannel == channel:
                            self.tabs.insert_persistent_tab(index, widget, widget.windowTitle())
                            return
                        index += 1
            # Otherwise append on end of tab bar.
            elif tabType == "plot":
                self.tabs.addTab(widget, widget.windowTitle())    
            elif tabType == "camera":
                self.tabs.add_persistent_tab(widget, widget.windowTitle())
    @Slot()
    def tab_to_window(self, widget, index):
        """Method to convert tab to window."""
        if index != -1:
            text = self.tabs.tabText(index)
            self.tabs.removeTab(index)
            widget.setWindowFlags(Qt.Window)
            widget.setWindowTitle(text)
            widget.set_window()
            widget.show()
            self.tabs.setCurrentIndex(0)