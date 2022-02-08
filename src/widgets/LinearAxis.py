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

class LinearAxis(QWidget):
    positionSetPointChanged = Signal(float)
    positionLeftLimitChanged = Signal(float)
    positionRightLimitChanged = Signal(float)
    positionMinimumRangeChanged = Signal(float)
    positionMaximumRangeChanged = Signal(float)
    feedbackSetPointChanged = Signal(float)
    feedbackLeftLimitChanged = Signal(float)
    feedbackRightLimitChanged = Signal(float)
    feedbackMinimumRangeChanged = Signal(float)
    feedbackMaximumRangeChanged = Signal(float)
    speedChanged = Signal(float)
    KPChanged = Signal(float)
    KIChanged = Signal(float)
    KDChanged = Signal(float)
    proportionalOnMeasurementChanged = Signal(bool)
    positiveJogEnabled = Signal()
    negativeJogEnabled = Signal() 
    positiveJogDisabled = Signal()
    negativeJogDisabled = Signal() 
    limitReached = Signal()
    axisEnabled = Signal()
    axisDisabled = Signal()
    feedbackEnabled = Signal()
    feedbackDisabled = Signal()
    zeroEncoder = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)              

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
        self.feedbackDemand.setPointLineEdit.returnPressed.connect(self.setFeedbackSetPoint)
        self.feedbackStatus.axisSlider.setPointChanged.connect(self.setFeedbackSetPoint)
        self.positionDemand.setPointLineEdit.returnPressed.connect(self.setPositionSetPoint)
        self.positionStatus.axisSlider.setPointChanged.connect(self.setPositionSetPoint)
        self.adjust.adjustSetPoint.connect(self.adjustPositionSetPoint)
        self.positionStatus.leftLimitChanged.connect(self.emitPositionLeftLimitChanged)
        self.positionStatus.rightLimitChanged.connect(self.emitPositionRightLimitChanged)
        self.positionStatus.minimumRangeChanged.connect(self.emitPositionMinimumRangeChanged)
        self.positionStatus.maximumRangeChanged.connect(self.emitPositionMaximumRangeChanged)
        self.feedbackStatus.leftLimitChanged.connect(self.emitFeedbackLeftLimitChanged)
        self.feedbackStatus.rightLimitChanged.connect(self.emitFeedbackRightLimitChanged)
        self.feedbackStatus.minimumRangeChanged.connect(self.emitFeedbackMinimumRangeChanged)
        self.feedbackStatus.maximumRangeChanged.connect(self.emitFeedbackMaximumRangeChanged)
        self.PID.KPLineEditChanged.connect(self.emitKPChanged)
        self.PID.KILineEditChanged.connect(self.emitKIChanged)
        self.PID.KDLineEditChanged.connect(self.emitKDChanged)
        self.PID.proportionalOnMeasurement.stateChanged.connect(self.emitProportionalOnMeasurement)
        self.jog.speedLineEditChanged.connect(self.emitSpeedChanged)
        self.jog.jogPlusButton.pressed.connect(self.emitPositiveJogEnabled)
        self.jog.jogPlusButton.released.connect(self.emitPositiveJogDisabled)
        self.jog.jogMinusButton.pressed.connect(self.emitPositiveJogEnabled)
        self.jog.jogMinusButton.released.connect(self.emitPositiveJogDisabled)
        self.globalControls.enableButton.toggled.connect(self.emitAxisEnableState)
        self.globalControls.PIDControlButton.toggled.connect(self.emitPIDControlState)
        self.globalControls.zeroEncoderButton.clicked.connect(self.emitZeroEncoder)
        self.globalControls.settingsButton.clicked.connect(self.showSettings)
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
        self.zeroEncoder.emit()
        
    @Slot()
    def emitAxisEnableState(self):
        enabled = self.globalControls.enableButton.isChecked()
        if enabled == True:
            self.axisEnabled.emit()
            self.globalControls.settingsButton.setEnabled(False)
            self.globalControls.PIDControlButton.setEnabled(True)
        elif enabled == False:
            self.axisDisabled.emit()
            self.globalControls.settingsButton.setEnabled(True)
            self.globalControls.PIDControlButton.setEnabled(False)
            
    @Slot()
    def emitPIDControlState(self):
        PIDControl = self.globalControls.PIDControlButton.isChecked()
        if PIDControl == True:
            self.feedbackEnabled.emit()
        elif PIDControl == False:
            self.feedbackDisabled.emit()
        
    @Slot()
    def emitPositiveJogEnabled(self):
        self.positiveJogEnabled.emit()
    
    @Slot()
    def emitNegativeJogEnabled(self):
        self.negativeJogEnabled.emit()
    
    @Slot()
    def emitPositiveJogDisabled(self):
        self.positiveJogDisabled.emit()
        
    @Slot()
    def emitNegativeJogDisabled(self):
        self.negativeJogDisabled.emit()

    @Slot()
    def emitSpeedChanged(self, value):
        self.speedChanged.emit(value)
    
    @Slot()
    def emitProportionalOnMeasurement(self, value):
        self.proportionalOnMeasurementChanged.emit(value)
    
    @Slot()
    def emitKPChanged(self, value):
        self.KPChanged.emit(value)
        
    @Slot()
    def emitKIChanged(self, value):
        self.KIChanged.emit(value)
    
    @Slot()
    def emitKDChanged(self, value):
        self.KDChanged.emit(value)

    @Slot()
    def emitPositionLeftLimitChanged(self, value):
        self.positionLeftLimitChanged.emit(value)

    @Slot()
    def emitPositionRightLimitChanged(self, value):
        self.positionRightLimitChanged.emit(value)
        
    @Slot()
    def emitPositionMinimumRangeChanged(self, value):
        self.positionMinimumRangeChanged.emit(value)   
    
    @Slot()
    def emitPositionMaximumRangeChanged(self, value):
        self.positionMaximumRangeChanged.emit(value)
    
    @Slot()
    def emitFeedbackLeftLimitChanged(self, value):
        self.feedbackLeftLimitChanged.emit(value)
    
    @Slot()
    def emitFeedbackRightLimitChanged(self, value):
        self.feedbackRightLimitChanged.emit(value)
        
    @Slot()
    def emitFeedbackMinimumRangeChanged(self, value):
        self.feedbackMinimumRangeChanged.emit(value)
        
    @Slot()
    def emitFeedbackMaximumRangeChanged(self, value):
        self.feedbackMaximumRangeChanged.emit(value)
        
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
        self.feedbackSetPointChanged.emit(value)
        if self.feedbackStatus.axisSlider.setPoint == self.feedbackStatus.axisSlider.leftLimit:
            self.globalControls.limitIndicator.setChecked(True)
            self.limitReached.emit()
        elif self.feedbackStatus.axisSlider.setPoint == self.feedbackStatus.axisSlider.rightLimit:
            self.globalControls.limitIndicator.setChecked(True)
            self.limitReached.emit()
        else:
            self.globalControls.limitIndicator.setChecked(False)
    
    @Slot()
    def setPositionSetPoint(self, value=None):
        if value == None:
            # Signal sent from LineEdit.
            value = float(self.positionDemand.setPointLineEdit.text())
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.positionStatus.axisSlider.leftLimit)
        value = min(value, self.positionStatus.axisSlider.rightLimit)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.positionStatus.setSetPoint(value)
        self.positionSetPointChanged.emit(value)
        if self.positionStatus.axisSlider.setPoint == self.positionStatus.axisSlider.leftLimit:
            self.globalControls.limitIndicator.setChecked(True)
            self.limitReached.emit()
        elif self.positionStatus.axisSlider.setPoint == self.positionStatus.axisSlider.rightLimit:
            self.globalControls.limitIndicator.setChecked(True)
            self.limitReached.emit()
        else:
            self.globalControls.limitIndicator.setChecked(False)

    @Slot()
    def setPositionProcessVariable(self, value):
        self.positionStatus.axisSlider.setProcessVariable(value)
        self.positionDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))
    
    @Slot()
    def setFeedbackProcessVariable(self, value):
        self.feedbackStatus.axisSlider.setProcessVariable(value)
        self.feedbackDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))

    @Slot()
    def setPIDControlButtonEnable(self, value):
        self.globalControls.PIDControlButton.setEnabled(value)

    def setValues(self, settings=None, **kwargs):
        if settings == None:
            settings = kwargs
        for setting in settings.keys():
            if setting == "positionMinimum":
                self.positionStatus.setMinimumRange(settings["positionMinimum"])
            elif setting == "positionMaximum":
                self.positionStatus.setMaximumRange(settings["positionMaximum"])
            elif setting == "positionLeft":
                self.positionStatus.setLeftLimit(settings["positionLeft"])
            elif setting == "positionRight":
                self.positionStatus.setRightLimit(settings["positionRight"])
            elif setting == "positionSetPoint":
                self.setPositionSetPoint(settings["positionSetPoint"])
            elif setting == "positionProcessVariable":
                self.setPositionProcessVariable(settings["positionProcessVariable"])
            elif setting == "feedbackMinimum":
                self.feedbackStatus.setMinimumRange(settings["feedbackMinimum"])
            elif setting == "feedbackMaximum":
                self.feedbackStatus.setMaximumRange(settings["feedbackMaximum"])
            elif setting == "feedbackLeft":
                self.feedbackStatus.setLeftLimit(settings["feedbackLeft"])
            elif setting == "feedbackRight":
                self.feedbackStatus.setRightLimit(settings["feedbackRight"])
            elif setting == "feedbackSetPoint":
                self.setFeedbackSetPoint(settings["feedbackSetPoint"])
            elif setting == "feedbackProcessVariable":
                self.setFeedbackProcessVariable(settings["feedbackProcessVariable"])
            elif setting == "feedbackUnit":
                self.feedbackDemand.setUnit(settings["feedbackUnit"])
                self.feedbackStatus.setUnit(settings["feedbackUnit"])   
            elif setting == "positionUnit":
                self.positionDemand.setUnit(settings["positionUnit"])
                self.positionStatus.setUnit(settings["positionUnit"])
                self.adjust.setUnit(settings["positionUnit"]) 
            elif setting == "speedUnit":
                self.jog.setUnit(settings["speedUnit"])    
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
            