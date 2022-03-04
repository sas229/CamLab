from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from src.widgets.LinearAxis import LinearAxis
from src.widgets.PlotWindow import PlotWindow
import copy

class ControlUtilities:

    def addControlTab(self, name, channel):
        controlID = name + " C" + str(channel+1)
        control = self.manager.configuration["devices"][name]["control"][channel]["control"]
        controlType = self.manager.configuration["devices"][name]["control"][channel]["type"]
        controlName = self.manager.configuration["devices"][name]["control"][channel]["name"]
        controlChannel = self.manager.configuration["devices"][name]["control"][channel]["channel"]
        
        # Instantiate the appropriate widget.
        if control == "Linear" and controlType == "Digital":
            controlWidget = LinearAxis(controlID)
        
            # Connections.
            controlWidget.enable.connect(self.manager.devices[name].setEnable)
            controlWidget.secondarySetPointChanged.connect(self.manager.devices[name].setSpeed)
            controlWidget.positiveJogEnabled.connect(self.manager.devices[name].jogPositiveOn)
            controlWidget.positiveJogDisabled.connect(self.manager.devices[name].jogPositiveOff)
            controlWidget.negativeJogEnabled.connect(self.manager.devices[name].jogNegativeOn)
            controlWidget.negativeJogDisabled.connect(self.manager.devices[name].jogNegativeOff)
            controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[name].updatePositionLeftLimit)
            controlWidget.primaryRightLimitChanged.connect(self.manager.devices[name].updatePositionRightLimit)
            controlWidget.primarySetPointChanged.connect(self.manager.devices[name].moveToPosition)
            controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[name].updateFeedbackLeftLimit)
            controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[name].updateFeedbackRightLimit)
            controlWidget.feedbackSetPointChanged.connect(self.manager.devices[name].setFeedbackSetPoint)
            controlWidget.zeroPosition.connect(self.manager.devices[name].zeroPosition)
            controlWidget.stopCommand.connect(self.manager.devices[name].stopCommand)
            controlWidget.PIDControl.connect(self.manager.devices[name].setPIDControl)
            controlWidget.KPChanged.connect(self.manager.devices[name].setKP)
            controlWidget.KIChanged.connect(self.manager.devices[name].setKI)
            controlWidget.KDChanged.connect(self.manager.devices[name].setKD)
            controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[name].setPoM)
            controlWidget.axisWindowClosed.connect(self.windowToTab)
            self.checkTimer.timeout.connect(self.manager.devices[name].checkConnection)
            self.running.connect(self.manager.devices[name].setRunning)
            self.manager.devices[name].updateRunningIndicator.connect(controlWidget.setRunningIndicator)
            self.manager.controlTableModels[name].controlChannelNameChanged.connect(controlWidget.setTitle)
            if channel == 0:
                self.updateTimer.timeout.connect(self.manager.devices[name].updateControlPanelC1)
                self.manager.devices[name].updateLimitIndicatorC1.connect(controlWidget.setLimitIndicator)
                self.manager.devices[name].updateConnectionIndicatorC1.connect(controlWidget.setConnectedIndicator)
                self.manager.devices[name].updateSpeedC1.connect(controlWidget.jog.setSpeed)
                self.manager.devices[name].updatePositionSetPointC1.connect(controlWidget.setPositionSetPoint)
                self.manager.devices[name].updateFeedbackSetPointC1.connect(controlWidget.setFeedbackSetPoint)
                self.manager.devices[name].updatePositionProcessVariableC1.connect(controlWidget.setPositionProcessVariable)
                self.manager.devices[name].updateFeedbackProcessVariableC1.connect(controlWidget.setFeedbackProcessVariable)
            elif channel == 1:
                self.updateTimer.timeout.connect(self.manager.devices[name].updateControlPanelC2)
                self.manager.devices[name].updateLimitIndicatorC2.connect(controlWidget.setLimitIndicator)
                self.manager.devices[name].updateConnectionIndicatorC2.connect(controlWidget.setConnectedIndicator)
                self.manager.devices[name].updateSpeedC2.connect(controlWidget.jog.setSpeed)
                self.manager.devices[name].updatePositionSetPointC2.connect(controlWidget.setPositionSetPoint)
                self.manager.devices[name].updateFeedbackSetPointC2.connect(controlWidget.setFeedbackSetPoint)
                self.manager.devices[name].updatePositionProcessVariableC2.connect(controlWidget.setPositionProcessVariable)
                self.manager.devices[name].updateFeedbackProcessVariableC2.connect(controlWidget.setFeedbackProcessVariable)

            # Set the configuration.
            controlWidget.setConfiguration(configuration=self.manager.configuration)
            self.manager.devices[name].checkConnection()
            position = self.manager.configuration["devices"][name]["control"][channel]["settings"]["primaryProcessVariable"]
            channelString = "C" + str(channel+1)
            self.manager.devices[name].setPosition(channelString, position)
        else:
            controlWidget = QWidget()

        # Store the widget.
        self.controls[controlID] = controlWidget

        # Add widget to tab and show if control enabled.
        self.tabs.addPersistentTab(self.controls[controlID], controlName)
        index = self.tabs.indexOf(self.controls[controlID])
        self.tabs.setTabVisible(index, False)
        self.controls[controlID].setVisible(False)
        enabledControls = self.manager.controlTableModels[name].enabledControls()
        for control in enabledControls:
            if control["channel"] == controlChannel:
                self.tabs.setTabVisible(index, True)

        # Convert tab to window if required by configuration.
        if self.manager.configuration["devices"][name]["control"][channel]["settings"]["mode"] == "window":
            self.tabToWindow(self.controls[controlID], index)
            self.controls[controlID].setVisible(False)   
            for control in enabledControls:
                if control["channel"] == controlChannel: 
                    self.controls[controlID].setVisible(True)

    @Slot(str, int, str)
    def changeControlFeedbackChannel(self, device, channel, selectedFeedbackChannel):
        feedbackChannelList = self.manager.feedbackChannelLists[device]
        feedbackIndex = feedbackChannelList.index(selectedFeedbackChannel)
        self.manager.configuration["devices"][device]["control"][channel]["settings"]["feedbackIndex"] = feedbackIndex
        control = "C" + str(channel+1)
        self.manager.devices[device].setFeedbackChannels(control, feedbackIndex)

    @Slot(str, int, str)
    def changeControlWidget(self, device, channel, newWidget):
        # Delete current control widget and signals and instantiate the new selection.
        controlID = device + " C" + str(channel+1)
        widget = self.controls[controlID]
        index =  self.tabs.indexOf(widget)
        self.tabs.removeTab(index)
        self.controls[controlID].setParent(None)

        # Instantiate new control widget.
        if newWidget != "N/A":
            self.addControlTab(device, channel)

    @Slot(int, bool)
    def toggleControlChannel(self, device, channel, state):
        controlID = device + " C" + str(channel+1)
        widget = self.controls[controlID]
        index =  self.tabs.indexOf(widget)
        self.tabs.setTabVisible(index, state)
        self.controls[controlID].setVisible(state)

    @Slot()
    def clearControlTabs(self):
        # Remove all control tabs.
        tabs = self.tabs.count()
        for index in reversed(range(tabs)):
            widget = self.tabs.widget(index)
            text = self.tabs.tabText(index)
            if not isinstance(widget, PlotWindow):
                if text != "Status" and text != "Configuration" and text != "Sequences":
                    self.tabs.removeTab(index)