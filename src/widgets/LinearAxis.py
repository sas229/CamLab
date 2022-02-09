from PySide6.QtWidgets import QWidget, QGroupBox, QLabel, QLineEdit, QCheckBox, QGridLayout, QVBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal, Slot
from src.widgets.GlobalControlsGroupBox import GlobalControlsGroupBox
from src.widgets.SettingsGroupBox import SettingsGroupBox
from src.widgets.JogGroupBox import JogGroupBox
from src.widgets.AdjustGroupBox import AdjustGroupBox
from src.widgets.PIDGroupBox import PIDGroupBox
from src.widgets.DemandGroupBox import DemandGroupBox
from src.widgets.SliderGroupBox import SliderGroupBox
import logging

log = logging.getLogger(__name__)

class LinearAxis(QWidget):
    primarySetPointChanged = Signal(str, float)
    primaryLeftLimitChanged = Signal(str, float)
    primaryRightLimitChanged = Signal(str, float)
    primaryMinimumRangeChanged = Signal(str, float)
    primaryMaximumRangeChanged = Signal(str, float)
    primaryLeftLimitStatus = Signal(str, bool)
    primaryRightLimitStatus = Signal(str, bool)
    feedbackSetPointChanged = Signal(str, float)
    feedbackLeftLimitChanged = Signal(str, float)
    feedbackRightLimitChanged = Signal(str, float)
    feedbackMinimumRangeChanged = Signal(str, float)
    feedbackMaximumRangeChanged = Signal(str, float)
    feedbackLeftLimitStatus = Signal(str, bool)
    feedbackRightLimitStatus = Signal(str, bool)
    secondarySetPointChanged = Signal(str, float)
    KPChanged = Signal(str, float)
    KIChanged = Signal(str, float)
    KDChanged = Signal(str, float)
    proportionalOnMeasurementChanged = Signal(str, bool)
    positiveJogEnabled = Signal(str)
    negativeJogEnabled = Signal(str) 
    positiveJogDisabled = Signal(str)
    negativeJogDisabled = Signal(str) 
    axisEnabled = Signal(str)
    axisDisabled = Signal(str)
    feedbackEnabled = Signal(str)
    feedbackDisabled = Signal(str)
    zeroEncoder = Signal(str)
    primaryUnitChanged = Signal(str)
    feedbackUnitChanged = Signal(str)
    secondaryUnitChanged = Signal(str)
    connectedChanged = Signal(str)
    limitChanged = Signal(str)

    def __init__(self, controlName, *args, **kwargs):
        super().__init__(*args, **kwargs)              

        # Inputs.
        self.controlName = controlName

        # Variables.
        self.previousPrimaryProcessVariable = 0
        self.previousFeedbackProcessVariable = 0

        # Controls.
        self.globalControls = GlobalControlsGroupBox("Global")
        self.settings = SettingsGroupBox("Settings")
        self.jog = JogGroupBox("Jog")
        self.adjust = AdjustGroupBox("Adjust")
        self.positionDemand = DemandGroupBox("Demand")
        self.positionStatus = SliderGroupBox("Position Status")
        self.PID = PIDGroupBox("PID Feedback Control")
        self.feedbackDemand = DemandGroupBox("Demand")
        self.feedbackStatus = SliderGroupBox("Feedback Status")

        # Main layout.
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.globalControls, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.settings, 0, 0, 1, 4)
        self.gridLayout.addWidget(self.jog, 1, 0)
        self.gridLayout.addWidget(self.adjust, 1, 1)
        self.gridLayout.addWidget(self.positionDemand, 1, 2)
        self.gridLayout.addWidget(self.positionStatus, 1, 3)
        self.gridLayout.addWidget(self.PID, 2, 0, 1, 2)
        self.gridLayout.addWidget(self.feedbackDemand, 2, 2)
        self.gridLayout.addWidget(self.feedbackStatus, 2, 3)        
        
        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch()

        self.setLayout(self.layout)

        # Connections.
        self.positionDemand.setPointLineEdit.returnPressed.connect(self.setPositionSetPoint)
        self.positionDemand.unitChanged.connect(self.emitPrimaryUnitChanged)
        self.positionStatus.axisSlider.setPointChanged.connect(self.setPositionSetPoint)
        self.positionStatus.leftLimitChanged.connect(self.emitPrimaryLeftLimitChanged)
        self.positionStatus.rightLimitChanged.connect(self.emitPrimaryRightLimitChanged)
        self.positionStatus.minimumRangeChanged.connect(self.emitPrimaryMinimumRangeChanged)
        self.positionStatus.maximumRangeChanged.connect(self.emitPrimaryMaximumRangeChanged)
        self.feedbackDemand.setPointLineEdit.returnPressed.connect(self.setFeedbackSetPoint)
        self.feedbackDemand.unitChanged.connect(self.emitFeedbackUnitChanged)
        self.feedbackStatus.axisSlider.setPointChanged.connect(self.setFeedbackSetPoint)
        self.feedbackStatus.leftLimitChanged.connect(self.emitFeedbackLeftLimitChanged)
        self.feedbackStatus.rightLimitChanged.connect(self.emitFeedbackRightLimitChanged)
        self.feedbackStatus.minimumRangeChanged.connect(self.emitFeedbackMinimumRangeChanged)
        self.feedbackStatus.maximumRangeChanged.connect(self.emitFeedbackMaximumRangeChanged)
        self.adjust.adjustSetPoint.connect(self.adjustPositionSetPoint)
        self.PID.KPLineEditChanged.connect(self.emitKPChanged)
        self.PID.KILineEditChanged.connect(self.emitKIChanged)
        self.PID.KDLineEditChanged.connect(self.emitKDChanged)
        self.PID.proportionalOnMeasurement.stateChanged.connect(self.emitProportionalOnMeasurement)
        self.jog.speedUnitChanged.connect(self.emitSecondaryUnitChanged)
        self.jog.speedLineEditChanged.connect(self.emitSecondarySetPointChanged)
        self.jog.jogPlusButton.pressed.connect(self.emitPositiveJogEnabled)
        self.jog.jogPlusButton.released.connect(self.emitPositiveJogDisabled)
        self.jog.jogMinusButton.pressed.connect(self.emitNegativeJogEnabled)
        self.jog.jogMinusButton.released.connect(self.emitNegativeJogDisabled)
        self.globalControls.enableButton.toggled.connect(self.emitAxisEnableState)
        self.globalControls.PIDControlButton.toggled.connect(self.emitPIDControlState)
        self.globalControls.zeroEncoderButton.clicked.connect(self.emitZeroEncoder)
        self.globalControls.settingsButton.clicked.connect(self.showSettings)
        self.globalControls.connectedIndicator.toggled.connect(self.emitConnectedChanged)
        self.globalControls.limitIndicator.toggled.connect(self.emitLimitChanged)
        self.settings.returnButton.clicked.connect(self.hideSettings)

    @Slot()
    def showSettings(self):
        self.globalControls.hide()
        self.settings.show()
    
    @Slot()
    def hideSettings(self):
        self.globalControls.show()
        self.settings.hide()

    @Slot()
    def emitZeroEncoder(self):
        self.zeroEncoder.emit(self.channel)
        
    @Slot()
    def emitAxisEnableState(self):
        enabled = self.globalControls.enableButton.isChecked()
        if enabled == True:
            self.axisEnabled.emit(self.channel)
            self.globalControls.settingsButton.setEnabled(False)
            self.globalControls.PIDControlButton.setEnabled(True)
        elif enabled == False:
            self.axisDisabled.emit(self.channel)
            self.globalControls.settingsButton.setEnabled(True)
            self.globalControls.PIDControlButton.setEnabled(False)
        self.configuration["controlWindow"][self.controlName]["enable"] = self.globalControls.enableButton.isChecked()

    @Slot()
    def emitPIDControlState(self):
        PIDControl = self.globalControls.PIDControlButton.isChecked()
        if PIDControl == True:
            self.feedbackEnabled.emit(self.channel)
        elif PIDControl == False:
            self.feedbackDisabled.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["PIDControl"] = self.globalControls.PIDControlButton.isChecked()

    @Slot()
    def emitPrimaryUnitChanged(self):
        self.primaryUnitChanged.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["primaryUnit"] = self.positionDemand.getUnit()

    @Slot()
    def emitFeedbackUnitChanged(self):
        self.feedbackUnitChanged.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["feedbackUnit"] = self.feedbackDemand.getUnit()

    @Slot()
    def emitSecondaryUnitChanged(self):
        self.secondaryUnitChanged.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["secondaryUnit"] = self.jog.getUnit()

    @Slot()
    def emitSecondarySetPointChanged(self, value):
        self.secondarySetPointChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["secondarySetPoint"] = self.jog.getSpeed()

    @Slot()
    def emitPositiveJogEnabled(self):
        self.positiveJogEnabled.emit(self.channel)
    
    @Slot()
    def emitNegativeJogEnabled(self):
        self.negativeJogEnabled.emit(self.channel)
    
    @Slot()
    def emitPositiveJogDisabled(self):
        self.positiveJogDisabled.emit(self.channel)
        
    @Slot()
    def emitNegativeJogDisabled(self):
        self.negativeJogDisabled.emit(self.channel)
    
    @Slot()
    def emitProportionalOnMeasurement(self, value):
        self.proportionalOnMeasurementChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["proportionalOnMeasurement"] = self.PID.getProportionalOnMeasurement()
    
    @Slot()
    def emitKPChanged(self, value):
        self.KPChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["KP"] = self.PID.getKP()
        
    @Slot()
    def emitKIChanged(self, value):
        self.KIChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["KI"] = self.PID.getKI()

    @Slot()
    def emitKDChanged(self, value):
        self.KDChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["KD"] = self.PID.getKD()
        
    @Slot()
    def emitPrimaryLeftLimitChanged(self, value):
        self.primaryLeftLimitChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["primaryLeftLimit"] = self.positionStatus.getLeftLimit()

    @Slot()
    def emitPrimaryRightLimitChanged(self, value):
        self.primaryRightLimitChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["primaryRightLimit"] = self.positionStatus.getRightLimit()
        
    @Slot()
    def emitPrimaryMinimumRangeChanged(self, value):
        self.primaryMinimumRangeChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["primaryMinimum"] = self.positionStatus.getMinimumRange()
    
    @Slot()
    def emitPrimaryMaximumRangeChanged(self, value):
        self.primaryMaximumRangeChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["primaryMaximum"] = self.positionStatus.getMaximumRange()
    
    @Slot()
    def emitFeedbackLeftLimitChanged(self, value):
        self.feedbackLeftLimitChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["feedbackLeftLimit"] = self.feedbackStatus.getLeftLimit()
    
    @Slot()
    def emitFeedbackRightLimitChanged(self, value):
        self.feedbackRightLimitChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["feedbackRightLimit"] = self.feedbackStatus.getRightLimit()
        
    @Slot()
    def emitFeedbackMinimumRangeChanged(self, value):
        self.feedbackMinimumRangeChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["feedbackMinimum"] = self.feedbackStatus.getMinimumRange()
        
    @Slot()
    def emitFeedbackMaximumRangeChanged(self, value):
        self.feedbackMaximumRangeChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["feedbackMaximum"] = self.feedbackStatus.getMaximumRange()

    @Slot()
    def emitConnectedChanged(self):
        self.connectedChanged.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["connected"] = self.globalControls.connectedIndicator.isChecked()

    @Slot()
    def emitLimitChanged(self):
        self.limitChanged.emit(self.channel)
        self.configuration["controlWindow"][self.controlName]["limit"] = self.globalControls.limitIndicator.isChecked()
        
    @Slot()
    def adjustPositionSetPoint(self, adjustment):
        currentSetPoint = float(self.positionDemand.setPointLineEdit.text())
        newSetPoint = currentSetPoint + adjustment
        self.setPositionSetPoint(newSetPoint)

    @Slot()
    def setFeedbackSetPoint(self, value=None):
        if value == None:
            # Signal sent from LineEdit.
            value = float(self.feedbackDemand.setPointLineEdit.text())
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.feedbackStatus.axisSlider.leftLimit)
        value = min(value, self.feedbackStatus.axisSlider.rightLimit)
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.feedbackStatus.setSetPoint(float(value))
        self.feedbackSetPointChanged.emit(self.channel, value)
        self.configuration["controlWindow"][self.controlName]["feedbackSetPoint"] = self.feedbackStatus.getSetPoint()
    
    @Slot()
    def setPositionSetPoint(self, value=None):
        origin = "device"
        if value == None:
            # Signal sent from LineEdit.
            origin = "UI"
            value = float(self.positionDemand.setPointLineEdit.text())
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.positionStatus.axisSlider.leftLimit)
        value = min(value, self.positionStatus.axisSlider.rightLimit)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.positionStatus.setSetPoint(value)
        # If the origin of the update is the UI, then send a signal back to the device to execute the move.
        if origin == "UI":
            self.primarySetPointChanged.emit(self.channel, value)
            print(value)
        self.configuration["controlWindow"][self.controlName]["primarySetPoint"] = self.positionStatus.getSetPoint()

    @Slot()
    def setPositionProcessVariable(self, value):
        # Set the process variable line edit text.
        self.positionStatus.axisSlider.setProcessVariable(value)
        self.positionDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))
        
        # If at the left limit, send out appropriate signals. If moving back into limits, allow that to happen.
        if self.positionStatus.axisSlider.processVariable <= self.positionStatus.axisSlider.leftLimit:
            if self.positionStatus.axisSlider.getProcessVariable() < self.previousPrimaryProcessVariable:
                self.globalControls.limitIndicator.setChecked(True)
                self.primaryLeftLimitStatus.emit(self.channel, True)
                self.limitChanged.emit(self.channel)
        # If at the right limit, send out appropriate signals. If moving back into limits, allow that to happen.
        elif self.positionStatus.axisSlider.processVariable >= self.positionStatus.axisSlider.rightLimit:
            if self.positionStatus.axisSlider.getProcessVariable() > self.previousPrimaryProcessVariable:
                self.globalControls.limitIndicator.setChecked(True)
                self.primaryRightLimitStatus.emit(self.channel, True)
                self.limitChanged.emit(self.channel)
        # Otherwise unset the limit indicator and emit both limit status signal booleans as false.
        else:
            if self.globalControls.limitIndicator.isChecked() == True:
                self.globalControls.limitIndicator.setChecked(False)
                self.primaryLeftLimitStatus.emit(self.channel, False)
                self.primaryRightLimitStatus.emit(self.channel, False)
        
        # Save the previous process variable.
        self.previousPrimaryProcessVariable = self.positionStatus.axisSlider.getProcessVariable()

        # Update the configuration.
        self.configuration["controlWindow"][self.controlName]["primaryProcessVariable"] = self.positionDemand.getProcessVariable()
    
    @Slot()
    def setFeedbackProcessVariable(self, value):
        # Set the process variable line edit text.
        self.feedbackStatus.axisSlider.setProcessVariable(value)
        self.feedbackDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))

        # If at the left limit, send out appropriate signals. If moving back into limits, allow that to happen.
        if self.feedbackStatus.axisSlider.processVariable <= self.feedbackStatus.axisSlider.leftLimit:
            if self.feedbackStatus.axisSlider.getProcessVariable() < self.previousFeedbackProcessVariable:
                self.globalControls.limitIndicator.setChecked(True)
                self.feedbackLeftLimitStatus.emit(self.channel, True)
                self.limitChanged.emit(self.channel)

        # If at the right limit, send out appropriate signals. If moving back into limits, allow that to happen.
        elif self.feedbackStatus.axisSlider.processVariable >= self.feedbackStatus.axisSlider.rightLimit:
            if self.feedbackStatus.axisSlider.getProcessVariable() > self.previousFeedbackProcessVariable:
                self.globalControls.limitIndicator.setChecked(True)
                self.feedbackRightLimitStatus.emit(self.channel, True)
                self.limitChanged.emit(self.channel)

        # Otherwise unset the limit indicator and emit both limit status signal booleans as false.
        else:
            if self.globalControls.limitIndicator.isChecked() == True:
                self.globalControls.limitIndicator.setChecked(False)
                self.feedbackLeftLimitStatus.emit(self.channel, False)
                self.feedbackRightLimitStatus.emit(self.channel, False)

        # Save the previous process variable.
        self.previousFeedbackProcessVariable = self.feedbackStatus.axisSlider.getProcessVariable()
        
        # Update the configuration.
        self.configuration["controlWindow"][self.controlName]["feedbackProcessVariable"] = self.feedbackDemand.getProcessVariable()

    @Slot()
    def setPIDControlButtonEnable(self, value):
        self.globalControls.PIDControlButton.setEnabled(value)
        self.configuration["controlWindow"][self.controlName]["enablePIDControl"] = self.getPIDControlButtonEnable()
    
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
                self.feedbackDemand.setUnit(settings["feedbackUnit"])
                self.feedbackStatus.setUnit(settings["feedbackUnit"])   
            elif setting == "primaryUnit":
                self.positionDemand.setUnit(settings["primaryUnit"])
                self.positionStatus.setUnit(settings["primaryUnit"])
                self.adjust.setUnit(settings["primaryUnit"]) 
            elif setting == "secondaryUnit":
                self.jog.setUnit(settings["secondaryUnit"])    
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
    
    def setConfiguration(self, configuration):
        self.configuration = configuration
        self.channel = self.configuration["controlWindow"][self.controlName]["channel"]
        self.positionStatus.setMinimumRange(self.configuration["controlWindow"][self.controlName]["primaryMinimum"])
        self.positionStatus.setMaximumRange(self.configuration["controlWindow"][self.controlName]["primaryMaximum"])
        self.positionStatus.setLeftLimit(self.configuration["controlWindow"][self.controlName]["primaryLeftLimit"])
        self.positionStatus.setRightLimit(self.configuration["controlWindow"][self.controlName]["primaryRightLimit"])
        self.setPositionSetPoint(self.configuration["controlWindow"][self.controlName]["primarySetPoint"])
        self.setPositionProcessVariable(self.configuration["controlWindow"][self.controlName]["primaryProcessVariable"])
        self.feedbackStatus.setMinimumRange(self.configuration["controlWindow"][self.controlName]["feedbackMinimum"])
        self.feedbackStatus.setMaximumRange(self.configuration["controlWindow"][self.controlName]["feedbackMaximum"])
        self.feedbackStatus.setLeftLimit(self.configuration["controlWindow"][self.controlName]["feedbackLeftLimit"])
        self.feedbackStatus.setRightLimit(self.configuration["controlWindow"][self.controlName]["feedbackRightLimit"])
        self.setFeedbackSetPoint(self.configuration["controlWindow"][self.controlName]["feedbackSetPoint"])
        self.setFeedbackProcessVariable(self.configuration["controlWindow"][self.controlName]["feedbackProcessVariable"])
        self.feedbackDemand.setUnit(self.configuration["controlWindow"][self.controlName]["feedbackUnit"])
        self.feedbackStatus.setUnit(self.configuration["controlWindow"][self.controlName]["feedbackUnit"])   
        self.positionDemand.setUnit(self.configuration["controlWindow"][self.controlName]["primaryUnit"])
        self.positionStatus.setUnit(self.configuration["controlWindow"][self.controlName]["primaryUnit"])
        self.adjust.setUnit(self.configuration["controlWindow"][self.controlName]["primaryUnit"]) 
        self.jog.setSpeed(self.configuration["controlWindow"][self.controlName]["secondarySetPoint"])
        self.jog.setUnit(self.configuration["controlWindow"][self.controlName]["secondaryUnit"])    
        self.globalControls.connectedIndicator.setChecked(self.configuration["controlWindow"][self.controlName]["connected"])
        self.PID.setKP(self.configuration["controlWindow"][self.controlName]["KP"])
        self.PID.setKI(self.configuration["controlWindow"][self.controlName]["KI"])
        self.PID.setKD(self.configuration["controlWindow"][self.controlName]["KD"])
        self.PID.setProportionalOnMeasurement(self.configuration["controlWindow"][self.controlName]["proportionalOnMeasurement"])
        self.setPIDControlButtonEnable(self.configuration["controlWindow"][self.controlName]["enablePIDControl"])
        self.globalControls.PIDControlButton.setChecked(self.configuration["controlWindow"][self.controlName]["PIDControl"])
        self.globalControls.enableButton.setChecked(self.configuration["controlWindow"][self.controlName]["enable"])