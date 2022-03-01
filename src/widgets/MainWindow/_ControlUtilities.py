from PySide6.QtCore import Slot
from src.widgets.LinearAxis import LinearAxis
from src.widgets.PlotWindow import PlotWindow
import copy

class ControlUtilities:

    def addControlTab(self, name, channel):
        controlID = name + " C" + str(channel+1)
        control = self.manager.configuration["devices"][name]["control"][channel]["control"]
        controlType = self.manager.configuration["devices"][name]["control"][channel]["type"]
        controlName = self.manager.configuration["devices"][name]["control"][channel]["name"]
        
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
        
        # Store the widget.
        self.controls[controlID] = controlWidget

        # # Check for feedback channel.
        # if self.manager.configuration["control"][channel]["feedback"] == "N/A":
        #     self.manager.configuration["control"][channel]["settings"]["enablePIDControl"] = False
        #     self.manager.configuration["control"][channel]["settings"]["feedbackChannel"] = "N/A"
        # else:
        #     self.manager.configuration["control"][channel]["settings"]["feedbackChannel"] = "AIN" + str(control["feedback"])
        # #  Update control name.
        # self.manager.configuration["control"][channel]["settings"]["name"] = controlName
        
        # Set the configuration.
        controlWidget.setConfiguration(configuration=self.manager.configuration)
        self.manager.devices[name].checkConnection()
        position = self.manager.configuration["devices"][name]["control"][channel]["settings"]["primaryProcessVariable"]
        channel = "C" + str(channel+1)
        self.manager.devices[name].setPosition(channel, position)

        # Add widget to tab.
        self.tabs.addPersistentTab(self.controls[controlID], controlName)
        index = self.tabs.indexOf(self.controls[controlID])
        self.tabs.setTabVisible(index, False)

    @Slot(int, bool)
    def toggleControlChannel(self, device, channel, state):
        control = device + " C" + str(channel+1)
        widget = self.controls[control]
        index =  self.tabs.indexOf(widget)
        self.tabs.setTabVisible(index, state)

    @Slot(str)
    def removeControlTable(self, name):
        self.controlTableViews[name].setParent(None)

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

    @Slot() 
    def updateControlTab(self, index):
        # Method to update a control tab widgets.
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

                #  Create control widget.
                if control["control"] == 0:
                    controlWidget = LinearAxis(controlName)

                    # Connections.
                    controlWidget.enable.connect(self.manager.devices[deviceName].setEnable)
                    controlWidget.secondarySetPointChanged.connect(self.manager.devices[deviceName].setSpeed)
                    controlWidget.positiveJogEnabled.connect(self.manager.devices[deviceName].jogPositiveOn)
                    controlWidget.positiveJogDisabled.connect(self.manager.devices[deviceName].jogPositiveOff)
                    controlWidget.negativeJogEnabled.connect(self.manager.devices[deviceName].jogNegativeOn)
                    controlWidget.negativeJogDisabled.connect(self.manager.devices[deviceName].jogNegativeOff)
                    controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[deviceName].updatePositionLeftLimit)
                    controlWidget.primaryRightLimitChanged.connect(self.manager.devices[deviceName].updatePositionRightLimit)
                    controlWidget.primarySetPointChanged.connect(self.manager.devices[deviceName].moveToPosition)
                    controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackLeftLimit)
                    controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackRightLimit)
                    controlWidget.feedbackSetPointChanged.connect(self.manager.devices[deviceName].setFeedbackSetPoint)
                    controlWidget.zeroPosition.connect(self.manager.devices[deviceName].zeroPosition)
                    controlWidget.stopCommand.connect(self.manager.devices[deviceName].stopCommand)
                    controlWidget.PIDControl.connect(self.manager.devices[deviceName].setPIDControl)
                    controlWidget.KPChanged.connect(self.manager.devices[deviceName].setKP)
                    controlWidget.KIChanged.connect(self.manager.devices[deviceName].setKI)
                    controlWidget.KDChanged.connect(self.manager.devices[deviceName].setKD)
                    controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[deviceName].setPoM)
                    controlWidget.axisWindowClosed.connect(self.windowToTab)
                    self.checkTimer.timeout.connect(self.manager.devices[deviceName].checkConnection)
                    self.running.connect(self.manager.devices[deviceName].setRunning)
                    self.manager.devices[deviceName].updateRunningIndicator.connect(controlWidget.setRunningIndicator)
                    if control["channel"] == "C1":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC1)
                        self.manager.devices[deviceName].updateLimitIndicatorC1.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC1.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC1.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC1.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC1.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC1.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC1.connect(controlWidget.setFeedbackProcessVariable)
                    elif control["channel"] == "C2":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC2)
                        self.manager.devices[deviceName].updateLimitIndicatorC2.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC2.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC2.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC2.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC2.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC2.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC2.connect(controlWidget.setFeedbackProcessVariable)
                else:
                    controlWidget = QWidget()

                # Check configuration for previous settings, otherwise take defaults.
                if controlName not in self.manager.configuration["controlWindow"]:
                    self.defaultControlSettings = {
                        "name": controlChannelName,
                        "device": deviceName,
                        "channel": controlChannel,
                        "primaryMinimum": -100.00,
                        "primaryMaximum": 100.00,
                        "primaryLeftLimit": -80.00,
                        "primaryRightLimit": 80.00,
                        "primarySetPoint": 0.00,
                        "primaryProcessVariable": 0.00,
                        "primaryUnit": "(mm)",
                        "secondarySetPoint": 3.000,
                        "secondaryUnit": "(mm/s)",
                        "feedbackMinimum": -20.00,
                        "feedbackMaximum": 100.00,
                        "feedbackLeftLimit": -10.00,
                        "feedbackRightLimit": 90.00,
                        "feedbackSetPoint": 0.00,
                        "feedbackProcessVariable": 0.00,
                        "feedbackUnit": "(N)",
                        "feedbackChannel": "N/A",
                        "KP": 1.00,
                        "KI": 1.00,
                        "KD": 1.00,
                        "proportionalOnMeasurement": False
                    }
                    self.manager.configuration["controlWindow"][controlName] = copy.deepcopy(self.defaultControlSettings)

                # Check for feedback channel.
                if control["feedback"] == 0:
                    self.manager.configuration["controlWindow"][controlName]["enablePIDControl"] = False
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "N/A"
                else:
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "AIN" + str(control["feedback"])
                #  Update control name.
                self.manager.configuration["controlWindow"][controlName]["name"] = controlChannelName
                
                # Set the configuration.
                controlWidget.setConfiguration(configuration=self.manager.configuration)
                self.manager.devices[deviceName].checkConnection()
                self.manager.devices[deviceName].setPosition(controlChannel, self.manager.configuration["controlWindow"][controlName]["primaryProcessVariable"])
                
                # Add to tab bar.
                self.tabs.insertPersistentTab(index, controlWidget, controlChannelName)
                index += 1

    @Slot() 
    def updateControlTabs(self):
        # Method to update control tab widgets.
        self.clearControlTabs()
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

                #  Create control widget.
                if control["control"] == 0:
                    controlWidget = LinearAxis(controlName)

                    # Connections.
                    controlWidget.enable.connect(self.manager.devices[deviceName].setEnable)
                    controlWidget.secondarySetPointChanged.connect(self.manager.devices[deviceName].setSpeed)
                    controlWidget.positiveJogEnabled.connect(self.manager.devices[deviceName].jogPositiveOn)
                    controlWidget.positiveJogDisabled.connect(self.manager.devices[deviceName].jogPositiveOff)
                    controlWidget.negativeJogEnabled.connect(self.manager.devices[deviceName].jogNegativeOn)
                    controlWidget.negativeJogDisabled.connect(self.manager.devices[deviceName].jogNegativeOff)
                    controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[deviceName].updatePositionLeftLimit)
                    controlWidget.primaryRightLimitChanged.connect(self.manager.devices[deviceName].updatePositionRightLimit)
                    controlWidget.primarySetPointChanged.connect(self.manager.devices[deviceName].moveToPosition)
                    controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackLeftLimit)
                    controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[deviceName].updateFeedbackRightLimit)
                    controlWidget.feedbackSetPointChanged.connect(self.manager.devices[deviceName].setFeedbackSetPoint)
                    controlWidget.zeroPosition.connect(self.manager.devices[deviceName].zeroPosition)
                    controlWidget.stopCommand.connect(self.manager.devices[deviceName].stopCommand)
                    controlWidget.PIDControl.connect(self.manager.devices[deviceName].setPIDControl)
                    controlWidget.KPChanged.connect(self.manager.devices[deviceName].setKP)
                    controlWidget.KIChanged.connect(self.manager.devices[deviceName].setKI)
                    controlWidget.KDChanged.connect(self.manager.devices[deviceName].setKD)
                    controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[deviceName].setPoM)
                    controlWidget.axisWindowClosed.connect(self.windowToTab)
                    self.checkTimer.timeout.connect(self.manager.devices[deviceName].checkConnection)
                    self.running.connect(self.manager.devices[deviceName].setRunning)
                    self.manager.devices[deviceName].updateRunningIndicator.connect(controlWidget.setRunningIndicator)
                    if control["channel"] == "C1":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC1)
                        self.manager.devices[deviceName].updateLimitIndicatorC1.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC1.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC1.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC1.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC1.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC1.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC1.connect(controlWidget.setFeedbackProcessVariable)
                    elif control["channel"] == "C2":
                        self.updateTimer.timeout.connect(self.manager.devices[deviceName].updateControlPanelC2)
                        self.manager.devices[deviceName].updateLimitIndicatorC2.connect(controlWidget.setLimitIndicator)
                        self.manager.devices[deviceName].updateConnectionIndicatorC2.connect(controlWidget.setConnectedIndicator)
                        self.manager.devices[deviceName].updateSpeedC2.connect(controlWidget.jog.setSpeed)
                        self.manager.devices[deviceName].updatePositionSetPointC2.connect(controlWidget.setPositionSetPoint)
                        self.manager.devices[deviceName].updateFeedbackSetPointC2.connect(controlWidget.setFeedbackSetPoint)
                        self.manager.devices[deviceName].updatePositionProcessVariableC2.connect(controlWidget.setPositionProcessVariable)
                        self.manager.devices[deviceName].updateFeedbackProcessVariableC2.connect(controlWidget.setFeedbackProcessVariable)
                else:
                    controlWidget = QWidget()

                # Check configuration for previous settings, otherwise take defaults.
                if controlName not in self.manager.configuration["controlWindow"]:
                    self.defaultControlSettings = {
                        "name": controlChannelName,
                        "device": deviceName,
                        "channel": controlChannel,
                        "primaryMinimum": -100.00,
                        "primaryMaximum": 100.00,
                        "primaryLeftLimit": -80.00,
                        "primaryRightLimit": 80.00,
                        "primarySetPoint": 0.00,
                        "primaryProcessVariable": 0.00,
                        "primaryUnit": "(mm)",
                        "secondarySetPoint": 3.000,
                        "secondaryUnit": "(mm/s)",
                        "feedbackMinimum": -20.00,
                        "feedbackMaximum": 100.00,
                        "feedbackLeftLimit": -10.00,
                        "feedbackRightLimit": 90.00,
                        "feedbackSetPoint": 0.00,
                        "feedbackProcessVariable": 0.00,
                        "feedbackUnit": "(N)",
                        "feedbackChannel": "N/A",
                        "KP": 1.00,
                        "KI": 1.00,
                        "KD": 1.00,
                        "proportionalOnMeasurement": False
                    }
                    self.manager.configuration["controlWindow"][controlName] = copy.deepcopy(self.defaultControlSettings)

                # Check for feedback channel.
                if control["feedback"] == 0:
                    self.manager.configuration["controlWindow"][controlName]["enablePIDControl"] = False
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "N/A"
                else:
                    self.manager.configuration["controlWindow"][controlName]["feedbackChannel"] = "AIN" + str(control["feedback"])
                #  Update control name.
                self.manager.configuration["controlWindow"][controlName]["name"] = controlChannelName
                
                # Set the configuration.
                controlWidget.setConfiguration(configuration=self.manager.configuration)
                self.manager.devices[deviceName].checkConnection()
                self.manager.devices[deviceName].setPosition(controlChannel, self.manager.configuration["controlWindow"][controlName]["primaryProcessVariable"])
                
                # Add to tab bar.
                self.tabs.insertPersistentTab(index, controlWidget, controlChannelName)
                index += 1