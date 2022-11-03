from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot
from widgets.LinearAxis import LinearAxis
from widgets.PlotWindow import PlotWindow
import copy
import logging

log = logging.getLogger(__name__)

class ControlUtilities:

    def add_control_tab(self, name, channel):
        controlID = name + " C" + str(channel+1)
        control = self.manager.configuration["devices"][name]["control"][channel]["control"]
        controlType = self.manager.configuration["devices"][name]["control"][channel]["type"]
        controlName = self.manager.configuration["devices"][name]["control"][channel]["name"]
        controlChannel = self.manager.configuration["devices"][name]["control"][channel]["channel"]
        controlFeedback = self.manager.configuration["devices"][name]["control"][channel]["feedback"]
        # Instantiate the appropriate widget.
        if control == "N/A" or controlType == "N/A":
            controlWidget = QWidget()
        elif control == "Linear" and controlType == "Digital":
            if controlFeedback != "N/A": 
                feedback = True
            else:
                feedback = False
            controlWidget = LinearAxis(controlID, feedback)

            # Connections. 
            controlWidget.axisWindowClosed.connect(self.window_to_tab)
            # self.checkTimer.timeout.connect(self.manager.devices[name].check_connections)
            self.running.connect(self.manager.devices[name].set_running)
            self.manager.devices[name].updateRunningIndicator.connect(controlWidget.setRunningIndicator)
            self.statusTab.runSequence.clicked.connect(self.manager.devices[name].run_sequence)


            if name == "VJT":

                self.deviceConfigurationWidget[name].setFeedbackLinearAxis.connect(
                    controlWidget.toggleFeedbackControl)
                self.deviceConfigurationWidget[name].setFeedbackLinearAxis.connect(self.manager.updatePlotWindowChannelsData)
                
            else:
                self.manager.controlTableModels[name].controlChannelNameChanged.connect(controlWidget.setTitle)

            if channel == 0:
                controlWidget.enable.connect(self.manager.devices[name].set_enable_C1)
                controlWidget.PIDControl.connect(self.manager.devices[name].set_PID_control_C1)
                controlWidget.KPChanged.connect(self.manager.devices[name].set_KP_C1)
                controlWidget.KIChanged.connect(self.manager.devices[name].set_KI_C1)
                controlWidget.KDChanged.connect(self.manager.devices[name].set_KD_C1)
                controlWidget.rampPIDChanged.connect(self.manager.devices[name].set_rampPID_C1)
                # controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[name].set_pom_C1)
                controlWidget.rampPID_checkboxChanged.connect(self.manager.devices[name].rampPID_checkbox_C1)
                controlWidget.secondarySetPointChanged.connect(self.manager.devices[name].set_speed_C1)
                controlWidget.positiveJogEnabled.connect(self.manager.devices[name].jog_positive_on_C1)
                controlWidget.positiveJogDisabled.connect(self.manager.devices[name].jog_positive_off_C1)
                controlWidget.negativeJogEnabled.connect(self.manager.devices[name].jog_negative_on_C1)
                controlWidget.negativeJogDisabled.connect(self.manager.devices[name].jog_negative_off_C1)
                controlWidget.feedbackSetPointChanged.connect(self.manager.devices[name].set_feedback_setpoint_C1)
                controlWidget.primarySetPointChanged.connect(self.manager.devices[name].move_to_position_C1)
                controlWidget.stopCommand.connect(self.manager.devices[name].stop_command_C1)
                controlWidget.zeroPosition.connect(self.manager.devices[name].zero_position_C1)
                controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[name].update_position_left_limit_C1)
                controlWidget.primaryRightLimitChanged.connect(self.manager.devices[name].update_position_right_limit_C1)
                controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[name].update_feedback_left_limit_C1)
                controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[name].update_feedback_right_limit_C1)
                self.manager.timing.controlDevices.connect(self.manager.devices[name].updateControlPanelC1)
                self.manager.devices[name].updateLimitIndicatorC1.connect(controlWidget.setLimitIndicator)
                self.manager.devices[name].updateConnectionIndicatorC1.connect(controlWidget.setConnectedIndicator)
                self.manager.devices[name].updateSpeedC1.connect(controlWidget.jog.setSpeed)
                self.manager.devices[name].updatePositionSetPointC1.connect(controlWidget.setPositionSetPoint)
                self.manager.devices[name].updateFeedbackSetPointC1.connect(controlWidget.setFeedbackSetPoint)
                self.manager.devices[name].updatePositionProcessVariableC1.connect(controlWidget.setPositionProcessVariable)
                self.manager.devices[name].updateFeedbackProcessVariableC1.connect(controlWidget.setFeedbackProcessVariable)
                self.manager.devices[name].updateEnablePIDControlC1.connect(controlWidget.emitStopCommand)
            elif channel == 1:
                controlWidget.enable.connect(self.manager.devices[name].set_enable_C2)
                controlWidget.PIDControl.connect(self.manager.devices[name].set_PID_control_C2)
                controlWidget.KPChanged.connect(self.manager.devices[name].set_KP_C2)
                controlWidget.KIChanged.connect(self.manager.devices[name].set_KI_C2)
                controlWidget.KDChanged.connect(self.manager.devices[name].set_KD_C2)
                controlWidget.rampPIDChanged.connect(self.manager.devices[name].set_rampPID_C2)
                # controlWidget.proportionalOnMeasurementChanged.connect(self.manager.devices[name].set_pom_C2)
                controlWidget.rampPID_checkboxChanged.connect(self.manager.devices[name].rampPID_checkbox_C2)
                controlWidget.secondarySetPointChanged.connect(self.manager.devices[name].set_speed_C2)
                controlWidget.positiveJogEnabled.connect(self.manager.devices[name].jog_positive_on_C2)
                controlWidget.positiveJogDisabled.connect(self.manager.devices[name].jog_positive_off_C2)
                controlWidget.negativeJogEnabled.connect(self.manager.devices[name].jog_negative_on_C2)
                controlWidget.negativeJogDisabled.connect(self.manager.devices[name].jog_negative_off_C2)
                controlWidget.feedbackSetPointChanged.connect(self.manager.devices[name].set_feedback_setpoint_C2)
                controlWidget.primarySetPointChanged.connect(self.manager.devices[name].move_to_position_C2)
                controlWidget.stopCommand.connect(self.manager.devices[name].stop_command_C2)
                controlWidget.zeroPosition.connect(self.manager.devices[name].zero_position_C2)
                controlWidget.primaryLeftLimitChanged.connect(self.manager.devices[name].update_position_left_limit_C2)
                controlWidget.primaryRightLimitChanged.connect(self.manager.devices[name].update_position_right_limit_C2)
                controlWidget.feedbackLeftLimitChanged.connect(self.manager.devices[name].update_feedback_left_limit_C2)
                controlWidget.feedbackRightLimitChanged.connect(self.manager.devices[name].update_feedback_right_limit_C2)
                self.manager.timing.controlDevices.connect(self.manager.devices[name].updateControlPanelC2)
                self.manager.devices[name].updateLimitIndicatorC2.connect(controlWidget.setLimitIndicator)
                self.manager.devices[name].updateConnectionIndicatorC2.connect(controlWidget.setConnectedIndicator)
                self.manager.devices[name].updateSpeedC2.connect(controlWidget.jog.setSpeed)
                self.manager.devices[name].updatePositionSetPointC2.connect(controlWidget.setPositionSetPoint)
                self.manager.devices[name].updateFeedbackSetPointC2.connect(controlWidget.setFeedbackSetPoint)
                self.manager.devices[name].updatePositionProcessVariableC2.connect(controlWidget.setPositionProcessVariable)
                self.manager.devices[name].updateFeedbackProcessVariableC2.connect(controlWidget.setFeedbackProcessVariable)
                self.manager.devices[name].updateEnablePIDControlC2.connect(controlWidget.emitStopCommand)
            
            # Set the configuration and initial position.
            controlWidget.set_configuration(configuration=self.manager.configuration)
            self.manager.devices[name].check_connections()
            position = self.manager.configuration["devices"][name]["control"][channel]["settings"]["primaryProcessVariable"]
            speed = self.manager.configuration["devices"][name]["control"][channel]["settings"]["secondarySetPoint"]
            if channel == 0:
                self.manager.devices[name].set_position_C1(position)
                self.manager.devices[name].set_speed_C1(speed)
            elif channel == 1:
                self.manager.devices[name].set_position_C2(position)
                self.manager.devices[name].set_speed_C2(speed)

        # Store the widget.
        self.controls.update({controlID: controlWidget})

        # Add widget to tab and show if control enabled.
        self.tabs.add_persistent_tab(self.controls[controlID], controlName)
        index = self.tabs.indexOf(self.controls[controlID])
        self.tabs.setTabVisible(index, False)
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        for device in enabledDevices:

            enabledControls = self.manager.controlTableModels[name].enabledControls()
            for control in enabledControls:
                if control["channel"] == controlChannel:
                    self.tabs.setTabVisible(index, True)

        # Convert tab to window if required by configuration.
        if self.manager.configuration["devices"][name]["control"][channel]["settings"]["mode"] == "window":
            self.tab_to_window(self.controls[controlID], index)
            self.controls[controlID].setVisible(False)   
            for control in enabledControls:
                if control["channel"] == controlChannel: 
                    self.controls[controlID].setVisible(True)

        log.info("Device control tab added for {id}.".format(id=controlID))

    @Slot(str, bool)
    def toggle_press_control_tab(self, name, state):
        if name == "VJT":
            controlID = name + " C1"
            index = self.tabs.indexOf(self.controls[controlID])
            self.tabs.setTabVisible(index, state)

    @Slot(str, int, str)
    def change_control_feedback_channel(self, device, channel, selectedFeedbackChannel):
        """Change control feedback channel."""
        # Set feedback channel.
        feedbackChannelList = self.manager.feedbackChannelLists[device]
        feedbackIndex = feedbackChannelList.index(selectedFeedbackChannel)
        self.manager.configuration["devices"][device]["control"][channel]["settings"]["feedbackIndex"] = feedbackIndex
        if channel == 0:
            if device in self.manager.devices:
                self.manager.devices[device].set_feedback_channel_C1(feedbackIndex)
        elif channel == 1:
            if device in self.manager.devices:
                self.manager.devices[device].set_feedback_channel_C2(feedbackIndex)
        
        # Toggle feedback control.
        if selectedFeedbackChannel != "N/A":
            feedback = True
        else:
            feedback = False
        controlID = device + " C" + str(channel+1)
        if hasattr(self.controls[controlID], "controlType"):
            if self.controls[controlID].controlType == "Linear":
                self.controls[controlID].toggleFeedbackControl(feedback)


    @Slot(str, int, str)
    def change_control_widget(self, device, channel, newWidget):
        # Delete current control widget and signals and instantiate the new selection.
        controlID = device + " C" + str(channel+1)
        widget = self.controls[controlID]
        index =  self.tabs.indexOf(widget)
        self.tabs.removeTab(index)
        self.controls[controlID].setParent(None)

        # Instantiate new control widget.
        if newWidget != "N/A":
            self.add_control_tab(device, channel)

    @Slot(int, bool)
    def toggle_control_channel(self, device, channel, state):
        # Toggle enable in Device class for toggled control channel.
        if channel == 0:
            self.manager.devices[device].enabled_C1 = state
        elif channel == 1:
            self.manager.devices[device].enabled_C2 = state
        # Toggle the control channel tab.
        controlID = device + " C" + str(channel+1)
        widget = self.controls[controlID]
        index =  self.tabs.indexOf(widget)
        self.tabs.setTabVisible(index, state)
        self.controls[controlID].setVisible(state)
        self.tabs.setCurrentIndex(index)
        self.tabs.setCurrentIndex(0)

    @Slot()
    def clear_tabs(self):
        # Close windows into tabs.
        for controlID in self.controls:
            self.controls[controlID].close()
        # Remove all control tabs.
        tabs = self.tabs.count()
        for index in reversed(range(tabs)):
            widget = self.tabs.widget(index)
            text = self.tabs.tabText(index)
            if not isinstance(widget, PlotWindow):
                if text != "Status" and text != "Configuration" and text != "Sequence":
                    self.tabs.removeTab(index)

    @Slot(str, bool)
    def update_control_visibility(self, device, show):
        # Set control visibility.
        controlID = device + " C1"
        if controlID in self.controls:
            self.controls[controlID].setVisible(show)
        controlID = device + " C2"
        if controlID in self.controls:
            self.controls[controlID].setVisible(show)