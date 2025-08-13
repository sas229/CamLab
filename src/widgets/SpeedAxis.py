from PySide6.QtWidgets import QWidget, QGroupBox, QLabel, QLineEdit, QCheckBox, QGridLayout, QVBoxLayout, QLayout
from PySide6.QtCore import Signal, Slot
from widgets.GlobalControlsGroupBox import GlobalControlsGroupBox
from widgets.SettingsGroupBox import SettingsGroupBox
from widgets.JogGroupBox import JogGroupBox
from widgets.AdjustGroupBox import AdjustGroupBox
from widgets.PIDGroupBox import PIDGroupBox
from widgets.DemandGroupBox import DemandGroupBox
from widgets.SliderGroupBox import SliderGroupBox
import logging
import math
from widgets.JogGroupBoxSpeed import JogGroupBox
from widgets.RunTimerGroupBox import RunTimerGroupBox

log = logging.getLogger(__name__)

class SpeedAxis(QWidget):
    primarySetPointChanged = Signal(float)
    primaryLeftLimitChanged = Signal(float)
    primaryRightLimitChanged = Signal(float)
    primaryMinimumRangeChanged = Signal(float)
    primaryMaximumRangeChanged = Signal(float)
    primaryLeftLimitStatus = Signal(bool)
    primaryRightLimitStatus = Signal(bool)
    feedbackSetPointChanged = Signal(float)
    feedbackLeftLimitChanged = Signal(float)
    feedbackRightLimitChanged = Signal(float)
    feedbackMinimumRangeChanged = Signal(float)
    feedbackMaximumRangeChanged = Signal(float)
    feedbackLeftLimitStatus = Signal(bool)
    feedbackRightLimitStatus = Signal(bool)
    secondarySetPointChanged = Signal(float)
    KPChanged = Signal(float)
    KIChanged = Signal(float)
    KDChanged = Signal(float)
    proportionalOnMeasurementChanged = Signal(bool)
    positiveJogEnabled = Signal()
    negativeJogEnabled = Signal() 
    positiveJogDisabled = Signal()
    negativeJogDisabled = Signal() 
    enable = Signal(bool)
    PIDControl = Signal(bool)
    zeroPosition = Signal()
    connectedChanged = Signal()
    stopCommand = Signal()
    axisWindowClosed = Signal(QWidget)
    # Forward the RPM jog signals
    positiveJogRPMEnabled = Signal(float)  # New signal for RPM mode
    negativeJogRPMEnabled = Signal(float)  # New signal for RPM mode
    positiveJogRPMDisabled = Signal()  # New signal for RPM mode
    negativeJogRPMDisabled = Signal()  # New signal for RPM mode

    def __init__(self, ID, feedback=False, *args, **kwargs):
        super().__init__(*args, **kwargs)              
        log.info("Speed instantiated.")

        # Add radius parameter (in mm)
        self.radius = 10.0  # Default radius in mm
        self.rpm_conversion_factor = 60 / (2 * math.pi * self.radius)  # Convert mm/s to RPM

        # Inputs.
        self.ID = ID
        self.controlType = "Speed"
        self.feedback = feedback
        self.device = self.ID[0:3]
        self.channel = self.ID[-2:]
        self.control = int(self.ID[-1])-1
        self.setWhatsThis("control")

        # Variables.
        self.previousPrimaryProcessVariable = 0
        self.previousFeedbackProcessVariable = 0

        # Controls.
        self.globalControls = GlobalControlsGroupBox("Global")
        self.settings = SettingsGroupBox("Settings")
        self.jog = JogGroupBox("Jog Speed")
        self.adjust = AdjustGroupBox("Adjust")  # Kept for internal logic, hidden for Speed mode
        self.positionDemand = DemandGroupBox("Demand")  # Kept for internal logic, hidden for Speed mode
        self.positionStatus = SliderGroupBox("Position Status")  # Kept for internal logic, hidden for Speed mode
        self.PID = PIDGroupBox("PID Feedback Control")
        self.feedbackDemand = DemandGroupBox("Demand")  # Kept for internal logic, hidden for Speed mode
        self.feedbackStatus = SliderGroupBox("Feedback Status")
        self.runTimer = RunTimerGroupBox("Run Timer")

        # Grid layout.
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.globalControls, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.settings, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.jog, 1, 0)
        # Hidden: self.gridLayout.addWidget(self.adjust, 1, 1)
        # Hidden: self.gridLayout.addWidget(self.positionDemand, 1, 2)
        # Hidden: self.gridLayout.addWidget(self.positionStatus, 1, 3)
        self.gridLayout.addWidget(self.PID, 2, 0, 1, 2)
        # Hidden: self.gridLayout.addWidget(self.feedbackDemand, 2, 2)
        self.gridLayout.addWidget(self.feedbackStatus, 2, 3)    
        self.gridLayout.addWidget(self.runTimer, 1, 1)    
        
        # Main layout.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch()  
        self.setLayout(self.layout)

        # Hide position status widget so it is not shown in Speed tab
        self.positionStatus.hide()

        # Hide Demand widget so it is not shown in Speed tab 
        self.positionDemand.hide()
        self.feedbackDemand.hide()

        # Hide Adjust widget so it is not shown in Speed tab 
        self.adjust.hide() 

        # Connections.
        self.positionDemand.setPointLineEdit.returnPressed.connect(self.emitPrimarySetPointChanged)
        self.positionStatus.setPointChanged.connect(self.updatePositionSetPointLineEdit)
        self.positionStatus.leftLimitChanged.connect(self.emitPrimaryLeftLimitChanged)
        self.positionStatus.rightLimitChanged.connect(self.emitPrimaryRightLimitChanged)
        self.positionStatus.minimumRangeChanged.connect(self.emitPrimaryMinimumRangeChanged)
        self.positionStatus.maximumRangeChanged.connect(self.emitPrimaryMaximumRangeChanged)
        self.runTimer.durationChanged.connect(self.setRunDuration)
        self.runTimer.countdownFinished.connect(self._onCountdownFinished)
        self.runTimer.countdownCanceled.connect(self._onCountdownCanceled)

        self.feedbackDemand.setPointLineEdit.returnPressed.connect(self.emitFeedbackSetPointChanged)
        self.feedbackStatus.setPointChanged.connect(self.updateFeedbackSetPointLineEdit)
        self.feedbackStatus.leftLimitChanged.connect(self.emitFeedbackLeftLimitChanged)
        self.feedbackStatus.rightLimitChanged.connect(self.emitFeedbackRightLimitChanged)
        self.feedbackStatus.minimumRangeChanged.connect(self.emitFeedbackMinimumRangeChanged)
        self.feedbackStatus.maximumRangeChanged.connect(self.emitFeedbackMaximumRangeChanged)

        self.adjust.adjustSetPoint.connect(self.adjustPositionSetPoint)

        self.PID.KPLineEditChanged.connect(self.emitKPChanged)
        self.PID.KILineEditChanged.connect(self.emitKIChanged)
        self.PID.KDLineEditChanged.connect(self.emitKDChanged)
        self.PID.proportionalOnMeasurement.stateChanged.connect(self.emitProportionalOnMeasurement)

        # Update jog connections to use RPM signals
        self.jog.speedLineEdit.returnPressed.connect(self.emitSecondarySetPointChanged)
        self.jog.jogPlusButton.toggled.connect(self.handlePositiveJogRPM)
        self.jog.jogMinusButton.toggled.connect(self.handleNegativeJogRPM)
        self.jog.speedDialChanged.connect(self.handleSpeedChange)

        self.globalControls.enableButton.toggled.connect(self.emitEnable)
        self.globalControls.stopButton.pressed.connect(self.emitStopCommand)
        self.globalControls.PIDControlButton.toggled.connect(self.emitPIDControl)
        self.globalControls.zeroButton.clicked.connect(self.emitZeroPosition)
        self.globalControls.settingsButton.clicked.connect(self.showSettings)
        self.globalControls.connectedIndicator.toggled.connect(self.emitConnectedChanged)

        self.settings.returnButton.clicked.connect(self.hideSettings)
        self.settings.maxRPMLineEdit.returnPressed.connect(self.updateMaxRPM)
        self.settings.CPRLineEdit.returnPressed.connect(self.updateCPR)
        self.settings.PPRLineEdit.returnPressed.connect(self.updatePPR)
        self.settings.ratioLineEdit.returnPressed.connect(self.updateRatio)
        self.settings.positionUnitChanged.connect(self.updatePrimaryUnit)
        self.settings.speedUnitChanged.connect(self.updateSecondaryUnit)
        self.settings.feedbackUnitChanged.connect(self.updateFeedbackUnit)

    @Slot(bool)
    def toggleFeedbackControl(self, feedback):
        self.PID.setVisible(feedback)
        self.feedbackDemand.setVisible(feedback)
        self.feedbackStatus.setVisible(feedback)
        self.feedback = feedback
        if self.controlConfiguration["settings"]["mode"] == "window":
            self.set_window()

    def set_window(self):
        # Set the window size.
        x = int(self.controlConfiguration["settings"]["x"])
        y = int(self.controlConfiguration["settings"]["y"])
        w = int(self.controlConfiguration["settings"]["width"])
        # Fix the height depending on whether feedback is enabled. 
        if self.feedback == False:
            h = 354
        else:
            h = 564
        self.setFixedHeight(h)
        self.setGeometry(x, y, w, h)
        self.controlConfiguration["settings"]["mode"] = "window"

    def moveEvent(self, event):
        # Save updated position in configuration if currently in window mode.
        if self.controlConfiguration["settings"]["mode"] == "window":
            position = self.geometry()
            self.controlConfiguration["settings"]["x"] = int(position.x())
            self.controlConfiguration["settings"]["y"] = int(position.y())  

    def resizeEvent(self, event):
        # Save updated size in configuration if currently in window mode.
        if self.controlConfiguration["settings"]["mode"] == "window":
            self.controlConfiguration["settings"]["width"] = int(self.width())
            self.controlConfiguration["settings"]["height"] = int(self.height())

    def set_tab(self):
        self.controlConfiguration["settings"]["mode"] = "tab"

    @Slot(str, str)
    def setTitle(self, currentTitle, newTitle):
        if self.windowTitle() == currentTitle:
            self.setWindowTitle(newTitle)

    def closeEvent(self, event):
        self.axisWindowClosed.emit(self)

    @Slot()
    def showSettings(self):
        self.globalControls.hide()
        self.settings.show()
    
    @Slot()
    def hideSettings(self):
        self.globalControls.show()
        self.settings.hide()

    @Slot(bool)
    def setLimitIndicator(self, value):
        self.globalControls.limitIndicator.setChecked(value)

    @Slot(bool)
    def setRunningIndicator(self, value):
        self.globalControls.runningIndicator.setChecked(value)
        if value == False:
            self.globalControls.PIDControlButton.setChecked(False)

    @Slot(bool)
    def setConnectedIndicator(self, value):
        self.globalControls.connectedIndicator.setChecked(value)

    @Slot()
    def emitStopCommand(self):
        self.stopCommand.emit()
        self.globalControls.PIDControlButton.setChecked(False)

    @Slot()
    def emitZeroPosition(self):
        self.zeroPosition.emit()
        
    @Slot()
    def emitEnable(self):
        enabled = self.globalControls.enableButton.isChecked()
        self.enable.emit(enabled)
        if enabled == True:
            self.globalControls.settingsButton.setVisible(False)
            self.globalControls.PIDControlButton.setVisible(True)
        elif enabled == False:
            self.globalControls.settingsButton.setVisible(True)
            self.globalControls.PIDControlButton.setChecked(False)
            self.globalControls.PIDControlButton.setVisible(False)
        
    @Slot()
    def emitPIDControl(self):
        PIDControl = self.globalControls.PIDControlButton.isChecked()
        self.PIDControl.emit(PIDControl)
        if PIDControl == True:
            self.emitFeedbackSetPointChanged()
            self.jog.speedLineEdit.setReadOnly(True)
        else:
            self.jog.speedLineEdit.setReadOnly(False)

    @Slot()
    def updateMaxRPM(self):
        value = int(self.settings.maxRPMLineEdit.text())
        self.controlConfiguration["settings"]["maxRPM"] = value
        # Update the jog dial maximum
        self.jog.setMaxRPM(value)
        log.info("Maximum RPM updated for control channel {channel} on {device} to {value}.".format(
            channel=self.channel, device=self.device, value=value))

    @Slot()
    def updateCPR(self):
        value = int(self.settings.CPRLineEdit.text())
        self.controlConfiguration["settings"]["CPR"] = value
        log.info("CPR updated for control channel {channel} on {device} to {value}.".format(channel=self.channel, device=self.device, value=value))

    @Slot()
    def updatePPR(self):
        value = int(self.settings.PPRLineEdit.text())
        self.controlConfiguration["settings"]["PPR"] = value
        log.info("PPR updated for control channel {channel} on {device} to {value}.".format(channel=self.channel, device=self.device, value=value))

    @Slot()
    def updateRatio(self):
        value = float(self.settings.ratioLineEdit.text())
        self.controlConfiguration["settings"]["ratio"] = value
        log.info("Ratio updated for control channel {channel} on {device} to {value}.".format(channel=self.channel, device=self.device, value=value))

    @Slot()
    def updatePrimaryUnit(self, unit):
        self.adjust.set_unit(unit)
        self.positionDemand.set_unit(unit)
        self.positionStatus.set_unit(unit)
        self.controlConfiguration["settings"]["primaryUnit"] = unit
        log.info("Position unit updated for control channel {channel} on {device} to {unit}.".format(channel=self.channel, device=self.device, unit=unit))

    @Slot()
    def updateFeedbackUnit(self, unit):
        self.feedbackDemand.set_unit(unit)
        self.feedbackStatus.set_unit(unit)
        self.controlConfiguration["settings"]["feedbackUnit"] = unit
        log.info("Feedback unit updated for control channel {channel} on {device} to {unit}.".format(channel=self.channel, device=self.device, unit=unit))

    @Slot()
    def updateSecondaryUnit(self, unit):
        self.jog.set_unit(unit)
        self.controlConfiguration["settings"]["secondaryUnit"] = unit
        log.info("Speed unit updated for control channel {channel} on {device} to {unit}.".format(channel=self.channel, device=self.device, unit=unit))

    @Slot()
    def emitSecondarySetPointChanged(self):
        """Handle speed input in RPM"""
        rpm_value = float(self.jog.speedLineEdit.text())
        
        # Check if either jog button is active
        if self.jog.jogPlusButton.isChecked():
            # Update positive jog with new RPM value
            self.positiveJogRPMEnabled.emit(rpm_value)
        elif self.jog.jogMinusButton.isChecked():
            # Update negative jog with new RPM value
            self.negativeJogRPMEnabled.emit(-rpm_value)
        else:
            # No jog active, convert to mm/s for normal speed control
            linear_speed = self.rpm_to_linear(rpm_value)
            self.secondarySetPointChanged.emit(linear_speed)
            self.controlConfiguration["settings"]["secondarySetPoint"] = round(linear_speed, 3)

    @Slot()
    def emitPositiveJogEnabled(self):
        self.positiveJogEnabled.emit()
        self.globalControls.PIDControlButton.setChecked(False)
    
    @Slot()
    def emitNegativeJogEnabled(self):
        self.negativeJogEnabled.emit()
        self.globalControls.PIDControlButton.setChecked(False)
    
    @Slot()
    def emitPositiveJogDisabled(self):
        self.positiveJogDisabled.emit()
        
    @Slot()
    def emitNegativeJogDisabled(self):
        self.negativeJogDisabled.emit()
    
    @Slot()
    def emitProportionalOnMeasurement(self, value):
        self.proportionalOnMeasurementChanged.emit(value)
        self.controlConfiguration["settings"]["proportionalOnMeasurement"] = self.PID.getProportionalOnMeasurement()
    
    @Slot()
    def emitKPChanged(self, value):
        self.KPChanged.emit(value)
        self.controlConfiguration["settings"]["KP"] = round(self.PID.getKP(), 2)
        
    @Slot()
    def emitKIChanged(self, value):
        self.KIChanged.emit(value)
        self.controlConfiguration["settings"]["KI"] = round(self.PID.getKI(), 2)

    @Slot()
    def emitKDChanged(self, value):
        self.KDChanged.emit(value)
        self.controlConfiguration["settings"]["KD"] = round(self.PID.getKD(), 2)
        
    @Slot()
    def emitPrimaryLeftLimitChanged(self, value):
        self.primaryLeftLimitChanged.emit(value)
        self.controlConfiguration["settings"]["primaryLeftLimit"] = round(self.positionStatus.getLeftLimit(), 2)

    @Slot()
    def emitPrimaryRightLimitChanged(self, value):
        self.primaryRightLimitChanged.emit(value)
        self.controlConfiguration["settings"]["primaryRightLimit"] = round(self.positionStatus.getRightLimit(), 2)
        
    @Slot()
    def emitPrimaryMinimumRangeChanged(self, value):
        self.primaryMinimumRangeChanged.emit(value)
        self.controlConfiguration["settings"]["primaryMinimum"] = round(self.positionStatus.getMinimumRange(), 2)
    
    @Slot()
    def emitPrimaryMaximumRangeChanged(self, value):
        self.primaryMaximumRangeChanged.emit(value)
        self.controlConfiguration["settings"]["primaryMaximum"] = round(self.positionStatus.getMaximumRange(), 2)
    
    @Slot()
    def emitFeedbackLeftLimitChanged(self, value):
        self.feedbackLeftLimitChanged.emit(value)
        self.controlConfiguration["settings"]["feedbackLeftLimit"] = round(self.feedbackStatus.getLeftLimit(), 2)
    
    @Slot()
    def emitFeedbackRightLimitChanged(self, value):
        self.feedbackRightLimitChanged.emit(value)
        self.controlConfiguration["settings"]["feedbackRightLimit"] = round(self.feedbackStatus.getRightLimit(), 2)
        
    @Slot()
    def emitFeedbackMinimumRangeChanged(self, value):
        self.feedbackMinimumRangeChanged.emit(value)
        self.controlConfiguration["settings"]["feedbackMinimum"] = round(self.feedbackStatus.getMinimumRange(), 2)
        
    @Slot()
    def emitFeedbackMaximumRangeChanged(self, value):
        self.feedbackMaximumRangeChanged.emit(value)
        self.controlConfiguration["settings"]["feedbackMaximum"] = round(self.feedbackStatus.getMaximumRange(), 2)

    @Slot()
    def emitConnectedChanged(self):
        self.connectedChanged.emit()
        self.controlConfiguration["settings"]["connected"] = self.globalControls.connectedIndicator.isChecked()

    @Slot()
    def adjustPositionSetPoint(self, adjustment):
        currentSetPoint = float(self.positionDemand.setPointLineEdit.text())
        newSetPoint = currentSetPoint + adjustment
        self.positionStatus.set_setpoint(newSetPoint) 
        self.updatePositionSetPointLineEdit(newSetPoint)
        self.globalControls.PIDControlButton.setChecked(False)

    @Slot()
    def updatePositionSetPointLineEdit(self, value):
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.primarySetPointChanged.emit(value)

    @Slot()
    def updateFeedbackSetPointLineEdit(self, value):
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.feedbackSetPointChanged.emit(value)

    @Slot()
    def emitPrimarySetPointChanged(self):
        value = float(self.positionDemand.setPointLineEdit.text())
        value = max(value, self.positionStatus.getLeftLimit())
        value = min(value, self.positionStatus.getRightLimit())
        self.positionStatus.set_setpoint(value)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.primarySetPointChanged.emit(value)

    @Slot()
    def emitFeedbackSetPointChanged(self):
        value = float(self.feedbackDemand.setPointLineEdit.text())
        value = max(value, self.feedbackStatus.getLeftLimit())
        value = min(value, self.feedbackStatus.getRightLimit())
        self.feedbackStatus.set_setpoint(value)
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.feedbackSetPointChanged.emit(value)

    @Slot()
    def setPositionSetPoint(self, value):
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.positionStatus.getLeftLimit())
        value = min(value, self.positionStatus.getRightLimit())
        self.positionStatus.set_setpoint(value)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.controlConfiguration["settings"]["primarySetPoint"] = round(self.positionStatus.get_setpoint(), 2)

    @Slot()
    def setPositionProcessVariable(self, value):
        # Set the process variable line edit text.
        self.positionStatus.set_process_variable(value)
        self.positionDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))

        # Update the configuration.
        self.controlConfiguration["settings"]["primaryProcessVariable"] = round(self.previousPrimaryProcessVariable, 2)
    
    @Slot()
    def setFeedbackSetPoint(self, value):
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.feedbackStatus.getLeftLimit())
        value = min(value, self.feedbackStatus.getRightLimit())
        self.feedbackStatus.set_setpoint(value)
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.controlConfiguration["settings"]["feedbackSetPoint"] = round(self.feedbackStatus.get_setpoint(), 2)
    
    @Slot()
    def setFeedbackProcessVariable(self, value):
        # Set the process variable line edit text.
        self.feedbackStatus.set_process_variable(value)
        self.feedbackDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))
        
        # Update the configuration.
        self.controlConfiguration["settings"]["feedbackProcessVariable"] = round(self.feedbackDemand.get_process_variable(), 2)

    @Slot()
    def setPIDControlButtonEnable(self, value):
        self.globalControls.PIDControlButton.setEnabled(value)
        self.controlConfiguration["settings"]["enablePIDControl"] = self.getPIDControlButtonEnable()
    
    def getPIDControlButtonEnable(self):
        return self.globalControls.PIDControlButton.isEnabled()

    def setValues(self, settings=None, **kwargs):
        if settings == None:
            settings = kwargs
        for setting in settings.keys():
            if setting == "primaryMinimum":
                self.positionStatus.setMinimumRange(settings["primaryMinimum"])
            elif setting == "primaryMaximum":
                self.positionStatus.setMaximumRange(settings["primaryMaximum"])
            elif setting == "primaryLeftLimit":
                self.positionStatus.setLeftLimit(settings["primaryLeftLimit"])
            elif setting == "primaryRightLimit":
                self.positionStatus.setRightLimit(settings["primaryRightLimit"])
            elif setting == "primarySetPoint":
                self.setPositionSetPoint(settings["primarySetPoint"])
            elif setting == "primaryProcessVariable":
                self.setPositionProcessVariable(settings["primaryProcessVariable"])
            elif setting == "feedbackMinimum":
                self.feedbackStatus.setMinimumRange(settings["feedbackMinimum"])
            elif setting == "feedbackMaximum":
                self.feedbackStatus.setMaximumRange(settings["feedbackMaximum"])
            elif setting == "feedbackLeftLimit":
                self.feedbackStatus.setLeftLimit(settings["feedbackLeftLimit"])
            elif setting == "feedbackRightLimit":
                self.feedbackStatus.setRightLimit(settings["feedbackRightLimit"])
            elif setting == "feedbackSetPoint":
                self.setFeedbackSetPoint(settings["feedbackSetPoint"])
            elif setting == "feedbackProcessVariable":
                self.setFeedbackProcessVariable(settings["feedbackProcessVariable"])
            elif setting == "feedbackUnit":
                self.feedbackDemand.set_unit(settings["feedbackUnit"])
                self.feedbackStatus.set_unit(settings["feedbackUnit"])
                self.settings.feedbackUnitLineEdit.setText(settings["feedbackUnit"]) 
            elif setting == "primaryUnit":
                self.positionDemand.set_unit(settings["primaryUnit"])
                self.positionStatus.set_unit(settings["primaryUnit"])
                self.adjust.set_unit(settings["primaryUnit"]) 
                self.settings.positionUnitLineEdit.setText(settings["primaryUnit"])
            elif setting == "secondaryUnit":
                self.jog.set_unit(settings["secondaryUnit"])
                self.settings.speedUnitLineEdit.setText(settings["secondaryUnit"])
            elif setting == "connected":
                self.globalControls.connectedIndicator.setChecked(settings["connected"])
            elif setting == "KP":
                self.PID.setKP(settings["KP"])
            elif setting == "KI":
                self.PID.setKI(settings["KI"])
            elif setting == "KD":
                self.PID.setKD(settings["KD"])
            elif setting == "proportionalOnMeasurement":
                self.PID.setProportionalOnMeasurement(settings["proportionalOnMeasurement"])
            elif setting == "enablePIDControl":
                self.setPIDControlButtonEnable(settings["enablePIDControl"])
            elif setting == "PIDControl":
                self.globalControls.PIDControlButton.setChecked(settings["PIDControl"])
            elif setting == "enable":
                self.globalControls.enableButton.setChecked(settings["enable"])
            elif setting == "maxRPM":
                self.settings.setMaxRPM(settings["maxRPM"])
            elif setting == "CPR":
                self.settings.setCPR(settings["CPR"])
            elif setting == "PPR":
                self.settings.setPPR(settings["PPR"])
            elif setting == "ratio":
                self.settings.setRatio(settings["ratio"])
    
    def set_configuration(self, configuration):
        self.configuration = configuration
        self.controlConfiguration = self.configuration["devices"][self.device]["control"][self.control]
        self.setWindowTitle(self.controlConfiguration["name"])
        self.positionStatus.setMinimumRange(self.controlConfiguration["settings"]["primaryMinimum"])
        self.positionStatus.setMaximumRange(self.controlConfiguration["settings"]["primaryMaximum"])
        self.positionStatus.setLeftLimit(self.controlConfiguration["settings"]["primaryLeftLimit"])
        self.positionStatus.setRightLimit(self.controlConfiguration["settings"]["primaryRightLimit"])
        self.setPositionSetPoint(self.controlConfiguration["settings"]["primarySetPoint"])
        self.setPositionProcessVariable(self.controlConfiguration["settings"]["primaryProcessVariable"])
        self.feedbackStatus.setMinimumRange(self.controlConfiguration["settings"]["feedbackMinimum"])
        self.feedbackStatus.setMaximumRange(self.controlConfiguration["settings"]["feedbackMaximum"])
        self.feedbackStatus.setLeftLimit(self.controlConfiguration["settings"]["feedbackLeftLimit"])
        self.feedbackStatus.setRightLimit(self.controlConfiguration["settings"]["feedbackRightLimit"])
        self.setFeedbackSetPoint(self.controlConfiguration["settings"]["feedbackSetPoint"])
        self.setFeedbackProcessVariable(self.controlConfiguration["settings"]["feedbackProcessVariable"])
        self.jog.setSpeed(self.controlConfiguration["settings"]["secondarySetPoint"])
        self.PID.setKP(self.controlConfiguration["settings"]["KP"])
        self.PID.setKI(self.controlConfiguration["settings"]["KI"])
        self.PID.setKD(self.controlConfiguration["settings"]["KD"])
        self.PID.setProportionalOnMeasurement(self.controlConfiguration["settings"]["proportionalOnMeasurement"])
        self.settings.setMaxRPM(self.controlConfiguration["settings"]["maxRPM"])
        self.settings.setCPR(self.controlConfiguration["settings"]["CPR"])
        self.settings.setPPR(self.controlConfiguration["settings"]["PPR"])
        self.settings.setRatio(self.controlConfiguration["settings"]["ratio"])
        self.settings.setPositionUnit(self.controlConfiguration["settings"]["primaryUnit"])
        self.settings.setSpeedUnit(self.controlConfiguration["settings"]["secondaryUnit"])
        self.settings.setFeedbackUnit(self.controlConfiguration["settings"]["feedbackUnit"])
        self.toggleFeedbackControl(self.feedback)
        self.enableUnlimitedPositionRange()  # Add unlimited position range for Speed tab only

    def enableUnlimitedPositionRange(self):
        """
        Expand position limits so the speed-controlled motor effectively has no travel limits.
        This does NOT touch LinearAxis; only SpeedAxis invokes this.
        """
        if getattr(self, "_unlimited_range_applied", False):
            return
        huge = 1e12
        self._unlimited_range_applied = True

        # Update configuration store
        self.controlConfiguration["settings"]["primaryMinimum"] = -huge
        self.controlConfiguration["settings"]["primaryMaximum"] = huge
        self.controlConfiguration["settings"]["primaryLeftLimit"] = -huge
        self.controlConfiguration["settings"]["primaryRightLimit"] = huge

        # Apply to UI components (order matters: set ranges before limits)
        self.positionStatus.setMinimumRange(-huge)
        self.positionStatus.setMaximumRange(huge)
        self.positionStatus.setLeftLimit(-huge)
        self.positionStatus.setRightLimit(huge)

        # If current setpoint was clamped earlier, restore it unchanged (now always within range)
        current_sp = self.positionStatus.get_setpoint()
        self.positionStatus.set_setpoint(current_sp)

    def linear_to_rpm(self, speed_mm_s):
        """Convert linear speed (mm/s) to RPM"""
        return speed_mm_s * self.rpm_conversion_factor

    def rpm_to_linear(self, speed_rpm):
        """Convert RPM to linear speed (mm/s)"""
        return speed_rpm / self.rpm_conversion_factor

    def set_radius(self, radius_mm):
        """Update the radius and conversion factor"""
        self.radius = radius_mm
        self.rpm_conversion_factor = 60 / (2 * math.pi * self.radius)

    def updateSpeedDisplay(self, linear_speed):
        """Update speed display showing RPM"""
        rpm_speed = self.linear_to_rpm(linear_speed)
        self.jog.speedLineEdit.setText(f"{rpm_speed:.1f}")
        # Update label to show RPM
        self.jog.speedLabel.setText("Speed (RPM)")
    
    @Slot()
    def emitPositiveJogRPMEnabled(self):
        """Emit current speed in RPM for positive jogging"""
        rpm_speed = float(self.jog.speedLineEdit.text())
        self.positiveJogRPMEnabled.emit(rpm_speed)
        self.globalControls.PIDControlButton.setChecked(False)
    
    @Slot()
    def emitNegativeJogRPMEnabled(self):
        """Emit current speed in RPM for negative jogging"""
        rpm_speed = float(self.jog.speedLineEdit.text())
        self.negativeJogRPMEnabled.emit(-rpm_speed)  # Negative for reverse direction
        self.globalControls.PIDControlButton.setChecked(False)
    
    @Slot()
    def emitPositiveJogRPMDisabled(self):
        """Stop positive RPM jogging"""
        self.positiveJogRPMDisabled.emit()
        
    @Slot()
    def emitNegativeJogRPMDisabled(self):
        """Stop negative RPM jogging"""
        self.negativeJogRPMDisabled.emit()

    def handlePositiveJogRPM(self, checked):
        """Handle positive direction jog button toggle."""
        if checked:
            rpm_speed = float(self.jog.speedLineEdit.text())
            self.positiveJogRPMEnabled.emit(rpm_speed)
            # Start countdown only if finite duration armed
            if self.runTimer.get_duration_seconds() > 0:
                self.runTimer.start_countdown()
        else:
            self.positiveJogRPMDisabled.emit()
            # Stop countdown (not 'finished')
            self.runTimer.stop_countdown(finished=False)
        self.globalControls.PIDControlButton.setChecked(False)

    def handleNegativeJogRPM(self, checked):
        """Handle negative direction jog button toggle."""
        if checked:
            rpm_speed = float(self.jog.speedLineEdit.text())
            self.negativeJogRPMEnabled.emit(-rpm_speed)
            if self.runTimer.get_duration_seconds() > 0:
                self.runTimer.start_countdown()
        else:
            self.negativeJogRPMDisabled.emit()
            self.runTimer.stop_countdown(finished=False)
        self.globalControls.PIDControlButton.setChecked(False)

    def handleSpeedChange(self, rpm_value):
        """Handle real-time speed changes from dial"""
        if self.jog.jogPlusButton.isChecked():
            self.positiveJogRPMEnabled.emit(rpm_value)
        elif self.jog.jogMinusButton.isChecked():
            self.negativeJogRPMEnabled.emit(-rpm_value)

    @Slot(int)
    def setRunDuration(self, seconds):
        """
        Store selected duration (seconds). 0 => indefinite.
        If a jog is active when a finite duration is (re)entered, restart countdown.
        """
        # Store only if other code still references it; otherwise you can omit this attribute.
        self._run_duration_seconds = seconds
        if seconds > 0 and (self.jog.jogPlusButton.isChecked() or self.jog.jogMinusButton.isChecked()):
            # Restart countdown
            self.runTimer.start_countdown()
        else:
            # Stop (shows armed value or 'Indefinite')
            self.runTimer.stop_countdown(finished=False)

    def _onCountdownFinished(self):
        """Triggered when the run timer reaches zero."""
        # Uncheck jog buttons to invoke existing stop logic
        if self.jog.jogPlusButton.isChecked():
            self.jog.jogPlusButton.setChecked(False)
        if self.jog.jogMinusButton.isChecked():
            self.jog.jogMinusButton.setChecked(False)

    def _onCountdownCanceled(self):
        """User canceled countdown. Do NOT force stop; just leave jog state."""
        pass