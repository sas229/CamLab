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
    primarySetPointChanged = Signal(float)
    primaryLeftLimitChanged = Signal(str, float)
    primaryRightLimitChanged = Signal(str, float)
    primaryMinimumRangeChanged = Signal(str, float)
    primaryMaximumRangeChanged = Signal(str, float)
    primaryLeftLimitStatus = Signal(str, bool)
    primaryRightLimitStatus = Signal(str, bool)
    feedbackSetPointChanged = Signal(float)
    feedbackLeftLimitChanged = Signal(str, float)
    feedbackRightLimitChanged = Signal(str, float)
    feedbackMinimumRangeChanged = Signal(str, float)
    feedbackMaximumRangeChanged = Signal(str, float)
    feedbackLeftLimitStatus = Signal(str, bool)
    feedbackRightLimitStatus = Signal(str, bool)
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
    primaryUnitChanged = Signal(str)
    feedbackUnitChanged = Signal(str)
    secondaryUnitChanged = Signal(str)
    connectedChanged = Signal(str)
    stopCommand = Signal()
    axisWindowClosed = Signal(QWidget)

    def __init__(self, ID, *args, **kwargs):
        super().__init__(*args, **kwargs)              
        log.info("Linear axis instantiated.")

        # Inputs.
        self.ID = ID
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
        self.jog = JogGroupBox("Jog")
        self.adjust = AdjustGroupBox("Adjust")
        self.positionDemand = DemandGroupBox("Demand")
        self.positionStatus = SliderGroupBox("Position Status")
        self.PID = PIDGroupBox("PID Feedback Control")
        self.feedbackDemand = DemandGroupBox("Demand")
        self.feedbackStatus = SliderGroupBox("Feedback Status")

        # Grid layout.
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
        
        # Main layout.
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch()
        self.setLayout(self.layout)
        self.setMinimumSize(1400, 565)

        # Connections.
        self.positionDemand.setPointLineEdit.returnPressed.connect(self.emitPrimarySetPointChanged)
        self.positionDemand.unitChanged.connect(self.emitPrimaryUnitChanged)
        self.positionStatus.setPointChanged.connect(self.updatePositionSetPointLineEdit)
        self.positionStatus.leftLimitChanged.connect(self.emitPrimaryLeftLimitChanged)
        self.positionStatus.rightLimitChanged.connect(self.emitPrimaryRightLimitChanged)
        self.positionStatus.minimumRangeChanged.connect(self.emitPrimaryMinimumRangeChanged)
        self.positionStatus.maximumRangeChanged.connect(self.emitPrimaryMaximumRangeChanged)

        self.feedbackDemand.setPointLineEdit.returnPressed.connect(self.emitFeedbackSetPointChanged)
        self.feedbackDemand.unitChanged.connect(self.emitFeedbackUnitChanged)
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

        self.jog.speedUnitChanged.connect(self.emitSecondaryUnitChanged)
        self.jog.speedLineEdit.returnPressed.connect(self.emitSecondarySetPointChanged)
        self.jog.jogPlusButton.pressed.connect(self.emitPositiveJogEnabled)
        self.jog.jogPlusButton.released.connect(self.emitPositiveJogDisabled)
        self.jog.jogMinusButton.pressed.connect(self.emitNegativeJogEnabled)
        self.jog.jogMinusButton.released.connect(self.emitNegativeJogDisabled)

        self.globalControls.enableButton.toggled.connect(self.emitEnable)
        self.globalControls.stopButton.pressed.connect(self.emitStopCommand)
        self.globalControls.PIDControlButton.toggled.connect(self.emitPIDControl)
        self.globalControls.zeroButton.clicked.connect(self.emitZeroPosition)
        self.globalControls.settingsButton.clicked.connect(self.showSettings)
        self.globalControls.connectedIndicator.toggled.connect(self.emitConnectedChanged)

        self.settings.returnButton.clicked.connect(self.hideSettings)

    def moveEvent(self, event):
        # Save updated position in configuration.
        position = self.geometry()
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["x"] = int(position.x())
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["y"] = int(position.y())

    def setWindow(self):
        x = int(self.configuration["devices"][self.device]["control"][self.control]["settings"]["x"])
        y = int(self.configuration["devices"][self.device]["control"][self.control]["settings"]["y"])
        w = int(self.configuration["devices"][self.device]["control"][self.control]["settings"]["width"])
        h = int(self.configuration["devices"][self.device]["control"][self.control]["settings"]["height"])
        self.setGeometry(x, y, w, h)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["mode"] = "window"

    def setTab(self):
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["mode"] = "tab"

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
            self.globalControls.settingsButton.setEnabled(False)
            self.globalControls.PIDControlButton.setEnabled(True)
        elif enabled == False:
            self.globalControls.settingsButton.setEnabled(True)
            self.globalControls.PIDControlButton.setEnabled(False)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["enable"] = self.globalControls.enableButton.isChecked()

    @Slot()
    def emitPIDControl(self):
        PIDControl = self.globalControls.PIDControlButton.isChecked()
        self.PIDControl.emit(PIDControl) 
        if PIDControl == True:
            self.emitFeedbackSetPointChanged()
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["PIDControl"] = self.globalControls.PIDControlButton.isChecked()

    @Slot()
    def emitPrimaryUnitChanged(self):
        self.primaryUnitChanged.emit(self.channel)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryUnit"] = self.positionDemand.getUnit()

    @Slot()
    def emitFeedbackUnitChanged(self):
        self.feedbackUnitChanged.emit(self.channel)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackUnit"] = self.feedbackDemand.getUnit()

    @Slot()
    def emitSecondaryUnitChanged(self):
        self.secondaryUnitChanged.emit(self.channel)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["secondaryUnit"] = self.jog.getUnit()

    @Slot()
    def emitSecondarySetPointChanged(self):
        value = float(self.jog.speedLineEdit.text())
        self.secondarySetPointChanged.emit(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["secondarySetPoint"] = round(self.jog.getSpeed(), 3)

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
    def emitProportionalOnMeasurement(self, value):
        self.proportionalOnMeasurementChanged.emit(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["proportionalOnMeasurement"] = self.PID.getProportionalOnMeasurement()
    
    @Slot()
    def emitKPChanged(self, value):
        self.KPChanged.emit(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["KP"] = round(self.PID.getKP(), 2)
        
    @Slot()
    def emitKIChanged(self, value):
        self.KIChanged.emit(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["KI"] = round(self.PID.getKI(), 2)

    @Slot()
    def emitKDChanged(self, value):
        self.KDChanged.emit(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["KD"] = round(self.PID.getKD(), 2)
        
    @Slot()
    def emitPrimaryLeftLimitChanged(self, value):
        self.primaryLeftLimitChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryLeftLimit"] = round(self.positionStatus.getLeftLimit(), 2)

    @Slot()
    def emitPrimaryRightLimitChanged(self, value):
        self.primaryRightLimitChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryRightLimit"] = round(self.positionStatus.getRightLimit(), 2)
        
    @Slot()
    def emitPrimaryMinimumRangeChanged(self, value):
        self.primaryMinimumRangeChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryMinimum"] = round(self.positionStatus.getMinimumRange(), 2)
    
    @Slot()
    def emitPrimaryMaximumRangeChanged(self, value):
        self.primaryMaximumRangeChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryMaximum"] = round(self.positionStatus.getMaximumRange(), 2)
    
    @Slot()
    def emitFeedbackLeftLimitChanged(self, value):
        self.feedbackLeftLimitChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackLeftLimit"] = round(self.feedbackStatus.getLeftLimit(), 2)
    
    @Slot()
    def emitFeedbackRightLimitChanged(self, value):
        self.feedbackRightLimitChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackRightLimit"] = round(self.feedbackStatus.getRightLimit(), 2)
        
    @Slot()
    def emitFeedbackMinimumRangeChanged(self, value):
        self.feedbackMinimumRangeChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackMinimum"] = round(self.feedbackStatus.getMinimumRange(), 2)
        
    @Slot()
    def emitFeedbackMaximumRangeChanged(self, value):
        self.feedbackMaximumRangeChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackMaximum"] = round(self.feedbackStatus.getMaximumRange(), 2)

    @Slot()
    def emitConnectedChanged(self):
        self.connectedChanged.emit(self.channel)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["connected"] = self.globalControls.connectedIndicator.isChecked()

    @Slot()
    def adjustPositionSetPoint(self, adjustment):
        currentSetPoint = float(self.positionDemand.setPointLineEdit.text())
        newSetPoint = currentSetPoint + adjustment
        self.positionStatus.setSetPoint(newSetPoint) 
        self.updatePositionSetPointLineEdit(newSetPoint)

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
        self.positionStatus.setSetPoint(value)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.primarySetPointChanged.emit(value)

    @Slot()
    def emitFeedbackSetPointChanged(self):
        value = float(self.feedbackDemand.setPointLineEdit.text())
        value = max(value, self.feedbackStatus.getLeftLimit())
        value = min(value, self.feedbackStatus.getRightLimit())
        self.feedbackStatus.setSetPoint(value)
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.feedbackSetPointChanged.emit(value)

    @Slot()
    def setPositionSetPoint(self, value):
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.positionStatus.getLeftLimit())
        value = min(value, self.positionStatus.getRightLimit())
        self.positionStatus.setSetPoint(value)
        self.positionDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primarySetPoint"] = round(self.positionStatus.getSetPoint(), 2)

    @Slot()
    def setPositionProcessVariable(self, value):
        # Set the process variable line edit text.
        self.positionStatus.setProcessVariable(value)
        self.positionDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))

        # Update the configuration.
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryProcessVariable"] = round(self.previousPrimaryProcessVariable, 2)
    
    @Slot()
    def setFeedbackSetPoint(self, value):
        # Signal sent from slider. Ensure within limits.
        value = max(value, self.feedbackStatus.getLeftLimit())
        value = min(value, self.feedbackStatus.getRightLimit())
        self.feedbackStatus.setSetPoint(value)
        self.feedbackDemand.setPointLineEdit.setText("{value:.2f}".format(value=value))
        # self.feedbackSetPointChanged.emit(self.channel, value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackSetPoint"] = round(self.feedbackStatus.getSetPoint(), 2)
    
    @Slot()
    def setFeedbackProcessVariable(self, value):
        # Set the process variable line edit text.
        self.feedbackStatus.setProcessVariable(value)
        self.feedbackDemand.processVariableLineEdit.setText("{value:.2f}".format(value=value))
        
        # Update the configuration.
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackProcessVariable"] = round(self.feedbackDemand.getProcessVariable(), 2)

    @Slot()
    def setPIDControlButtonEnable(self, value):
        self.globalControls.PIDControlButton.setEnabled(value)
        self.configuration["devices"][self.device]["control"][self.control]["settings"]["enablePIDControl"] = self.getPIDControlButtonEnable()
    
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
        self.setWindowTitle(self.configuration["devices"][self.device]["control"][self.control]["name"])
        self.positionStatus.setMinimumRange(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryMinimum"])
        self.positionStatus.setMaximumRange(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryMaximum"])
        self.positionStatus.setLeftLimit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryLeftLimit"])
        self.positionStatus.setRightLimit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryRightLimit"])
        self.setPositionSetPoint(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primarySetPoint"])
        self.setPositionProcessVariable(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryProcessVariable"])
        self.feedbackStatus.setMinimumRange(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackMinimum"])
        self.feedbackStatus.setMaximumRange(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackMaximum"])
        self.feedbackStatus.setLeftLimit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackLeftLimit"])
        self.feedbackStatus.setRightLimit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackRightLimit"])
        self.setFeedbackSetPoint(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackSetPoint"])
        self.setFeedbackProcessVariable(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackProcessVariable"])
        self.feedbackDemand.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackUnit"])
        self.feedbackStatus.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["feedbackUnit"])   
        self.positionDemand.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryUnit"])
        self.positionStatus.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryUnit"])
        self.adjust.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["primaryUnit"]) 
        self.jog.setSpeed(self.configuration["devices"][self.device]["control"][self.control]["settings"]["secondarySetPoint"])
        self.jog.setUnit(self.configuration["devices"][self.device]["control"][self.control]["settings"]["secondaryUnit"])    
        self.PID.setKP(self.configuration["devices"][self.device]["control"][self.control]["settings"]["KP"])
        self.PID.setKI(self.configuration["devices"][self.device]["control"][self.control]["settings"]["KI"])
        self.PID.setKD(self.configuration["devices"][self.device]["control"][self.control]["settings"]["KD"])
        self.PID.setProportionalOnMeasurement(self.configuration["devices"][self.device]["control"][self.control]["settings"]["proportionalOnMeasurement"])