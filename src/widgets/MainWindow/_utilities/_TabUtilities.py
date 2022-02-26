from PySide6.QtCore import Slot, Qt
from src.widgets.PlotWindow import PlotWindow

class TabUtilities:
    
    @Slot()
    def windowToTab(self, widget):
        if self.tabs.indexOf(widget) == -1:
            widget.setWindowFlags(Qt.Widget)
            # If not a PlotWindow, insert in order.
            if not isinstance(widget, PlotWindow):
                controlDevice, channel = widget.controlName.split(' ')
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
                        index += 1
            # Otherwise append on end of tab bar.
            else:
                self.tabs.addTab(widget, widget.windowTitle())    

    @Slot()
    def tabToWindow(self, widget, index):
        if index != -1:
            text = self.tabs.tabText(index)
            self.tabs.removeTab(index)
            widget.setWindowFlags(Qt.Window)
            widget.setWindowTitle(text)
            widget.setConfiguration(self.configuration)
            widget.move(400, 400)
            widget.show()