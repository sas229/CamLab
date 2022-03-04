from PySide6.QtCore import Slot, Qt

class TabUtilities:
    
    @Slot()
    def windowToTab(self, widget):
        if self.tabs.indexOf(widget) == -1:
            tabType = widget.whatsThis()
            widget.setWindowFlags(Qt.Widget)
            widget.setTab()
            # Set order.
            if tabType == "configuration":
                self.tabs.insertPersistentTab(0, widget, "Configuration")
            elif tabType == "sequences":
                self.tabs.insertPersistentTab(1, widget, "Sequences")
            elif tabType == "status":
                self.tabs.insertPersistentTab(2, widget, "Status")
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
                            self.tabs.insertPersistentTab(index, widget, widget.windowTitle())
                            return
                        index += 1
            # Otherwise append on end of tab bar.
            elif tabType == "plot":
                self.tabs.addTab(widget, widget.windowTitle())    

    @Slot()
    def tabToWindow(self, widget, index):
        if index != -1:
            text = self.tabs.tabText(index)
            self.tabs.removeTab(index)
            widget.setWindowFlags(Qt.Window)
            widget.setWindowTitle(text)
            widget.setWindow()
            widget.show()
            self.tabs.setCurrentIndex(0)