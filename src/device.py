from PySide6.QtCore import QObject, Signal, Slot
import logging
import ruamel.yaml
from labjack import ljm
import numpy as np
import time
import sys
from time import sleep
from simple_pid import PID

log = logging.getLogger(__name__)

class Device(QObject):
    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)
    updatePositionSetPointC1 = Signal(float)
    updatePositionSetPointC2 = Signal(float)
    updateFeedbackSetPointC1 = Signal(float)
    updateFeedbackSetPointC2 = Signal(float)
    updatePositionProcessVariableC1 = Signal(float)
    updatePositionProcessVariableC2 = Signal(float)
    updateFeedbackProcessVariableC1 = Signal(float)
    updateFeedbackProcessVariableC2 = Signal(float)
    updateConnectionIndicatorC1 = Signal(bool)
    updateConnectionIndicatorC2 = Signal(bool)
    updateLimitIndicatorC1 = Signal(bool)
    updateLimitIndicatorC2 = Signal(bool)
    updateRunningIndicator = Signal(bool)
    updateSpeedC1 = Signal(float)
    updateSpeedC2 = Signal(float)

    def __init__(self, name, id, connection):
        super().__init__()
        self.name = name
        self.id = id 
        self.connection = connection
        self.handle = None

        # Variables
        self.data = np.zeros(2)
        self.CPR = 6400
        self.KPC1 = 0.0
        self.KIC1 = 0.0
        self.KDC1 = 0.0
        self.KPC2 = 0.0
        self.KIC2 = 0.0
        self.KDC2 = 0.0
        self.statusPIDC1 = False
        self.statusPIDC2 = False
        self.enabledC1 = True
        self.enabledC2 = False
        self.motorEnabledC1 = False
        self.motorEnabledC2 = False
        self.feedbackC1 = True
        self.feedbackC2 = False
        self.feedbackChannelC1 = 0
        self.feedbackChannelC2 = 0
        self.running = False
        self.jogC1 = False
        self.jogC2 = False
        self.movingC1 = False
        self.movingC2 = False
        self.countC1 = 0
        self.countC2 = 0
        self.pulsesC1 = 0
        self.pulsesC2 = 0
        self.directionC1 = 1
        self.directionC2 = 1
        self.positionProcessVariableC1 = 0
        self.positionProcessVariableC2 = 0
        self.speedC1 = 3
        self.speedC2 = 3
        self.feedbackSetPointC1 = 0
        self.feedbackSetPointC2 = 0
        self.feedbackProcessVariableC1 = 0
        self.feedbackProcessVariableC2 = 0
        self.feedbackLeftLimitC1 = 0
        self.feedbackLeftLimitC2 = 0
        self.feedbackRightLimitC1 = 0
        self.feedbackRightLimitC2 = 0
        self.previousCountC1 = 0
        self.previousCountC2 = 0
        self.previousPulsesC1 = 0
        self.previousPulsesC2 = 0
        self.countsPerUnitC1 = 32000
        self.countsPerUnitC2 = 32000
        self.pulsesPerUnitC1 = 160
        self.pulsesPerUnitC2 = 160
        self.positionSetPointC1 = 0
        self.positionSetPointC2 = 0
        self.positionLeftLimitC1 = 0
        self.positionLeftLimitC2 = 0
        self.positionRightLimitC1 = 0
        self.positionRightLimitC2 = 0
        self.positionLeftLimitStatusC1 = False
        self.positionLeftLimitStatusC2 = False
        self.positionRightLimitStatusC1 = False
        self.positionRightLimitStatusC2 = False

        #  Initialise.
        self.openConnection()
        self.initialiseSettings()
        self.loadLuaScript()
        self.checkLimits()
        self.setSpeed("C1", self.speedC1)
        self.setSpeed("C2", self.speedC2)

        self.PID_C1 = PID()
        self.setTuningsPID("C1")
        self.PID_C2 = PID()
        self.setTuningsPID("C2")

        # Check Clock 0 is disabled.
        ljm.eWriteName(self.handle,'DIO_EF_CLOCK0_ENABLE',0)

    def setTuningsPID(self, channel):
        if channel == "C1":
            self.PID_C1.tunings = (self.KPC1, self.KIC1, self.KDC1)
        elif channel == "C2":
            self.PID_C2.tunings = (self.KPC2, self.KIC2, self.KDC2)

    @Slot(str, bool)
    def setPIDControl(self, channel, value):
        if channel == "C1":
            self.statusPIDC1 = value
            if value == True:
                speedLimit = (self.CPR*4000)/(60*self.countsPerUnitC1)
                self.PID_C1.reset()
                self.PID_C1.output_limits = (-speedLimit, speedLimit)
                self.PID_C1.setpoint = self.feedbackSetPointC1
                self.PID_C1.set_auto_mode(True, last_output=0.001)
                aNames = ["DIO4_EF_ENABLE", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
                aValues = [0, 0, 1, self.widthC1, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            else:
                self.positionSetPointC1 = self.positionProcessVariableC1
                self.PID_C1.set_auto_mode(False)
                self.updatePositionSetPointC1.emit(self.positionSetPointC1)
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.statusPIDC2 = value
    
    @Slot(str, float)
    def setKP(self, channel, value):
        if channel == "C1":
            self.KPC1 = value
        elif channel == "C2":
            self.KPC2 = value
        self.setTuningsPID(channel)

    @Slot(str, float)
    def setKI(self, channel, value):
        if channel == "C1":
            self.KIC1 = value
        elif channel == "C2":
            self.KIC2 = value
        self.setTuningsPID(channel)

    @Slot(str, float)
    def setKD(self, channel, value):
        if channel == "C1":
            self.KDC1 = value
        elif channel == "C2":
            self.KDC2 = value
        self.setTuningsPID(channel)

    @Slot(str, bool)
    def setPoM(self, channel, value):
        if channel == "C1":
            self.PID_C1.proportional_on_measurement = value 
        elif channel == "C2":
            self.PID_C2.proportional_on_measurement = value 

    @Slot(str, float)
    def setFeedbackSetPoint(self, channel, setPoint):
        if channel == "C1":
            self.feedbackSetPointC1 = setPoint
            self.PID_C1.setpoint = setPoint
        elif channel == "C2":
            self.feedbackSetPointC2 = setPoint
            self.PID_C2.setpoint = setPoint

    def setFeedbackChannels(self, channel, feedback):
        if channel == "C1":
            self.feedbackChannelC1 = feedback
        elif channel == "C2":
            self.feedbackChannelC2 = feedback

    def checkLimits(self):
        # Refresh connection.
        self.handle = ljm.open(7, self.connection, self.id)
        self.limitC1 = False
        self.limitC2 = False

        # Check position limits.
        self.minimumLimitC1 = bool(ljm.eReadName(self.handle, "CIO2"))
        self.maximumLimitC1 = bool(ljm.eReadName(self.handle, "CIO0"))
        self.minimumLimitC2 = bool(ljm.eReadName(self.handle, "CIO3"))
        self.maximumLimitC2 = bool(ljm.eReadName(self.handle, "CIO1"))
        
        #  Check if motor moving and stop if moving in the direction of the hard limit for C1.
        moving = ljm.eReadName(self.handle, "DIO4_EF_ENABLE")
        if moving == 1 and self.directionC1 == -1 and self.minimumLimitC1 == True:
            self.stopCommand("C1")
        elif moving == 1 and self.directionC1 == 1 and self.maximumLimitC1 == True:
            self.stopCommand("C1")

        #  Check if motor moving and stop if moving in the direction of the hard limit for C2.
        moving = ljm.eReadName(self.handle, "DIO5_EF_ENABLE")
        if moving == 1 and self.directionC2 == -1 and self.minimumLimitC2 == True:
            self.stopCommand("C2")
        elif moving == 1 and self.directionC2 == 1 and self.maximumLimitC2 == True:
            self.stopCommand("C2")

        # Turn on indicator if on limits.
        if self.minimumLimitC1 == True or self.maximumLimitC1 == True:
            self.limitC1 = True
        if self.minimumLimitC2 == True or self.maximumLimitC2 == True:
            self.limitC2 = True

        # Check feedback limits.
        if self.feedbackProcessVariableC1 <= self.feedbackLeftLimitC1:
            self.limitC1 = True
        if self.feedbackProcessVariableC1 >= self.feedbackRightLimitC1:
            self.limitC1 = True
        if self.feedbackProcessVariableC2 <= self.feedbackLeftLimitC2:
            self.limitC2 = True
        if self.feedbackProcessVariableC2 >= self.feedbackRightLimitC2:
            self.limitC2 = True

        # Set indicator.
        if self.limitC1 == True:
            self.updateLimitIndicatorC1.emit(True)
        else:
            self.updateLimitIndicatorC1.emit(False)
        if self.limitC2 == True:
            self.updateLimitIndicatorC2.emit(True)
        else:
            self.updateLimitIndicatorC2.emit(False)

    @Slot(str, float)
    def setPosition(self, channel, value):
        if channel == "C1":
            self.positionProcessVariableC1 = value
            self.positionSetPointC1 = value
        elif channel == "C2":
            self.positionProcessVariableC2 = value
            self.positionSetPointC2 = value

    @Slot(bool)
    def setRunning(self, running):
        self.running = running
        self.updateRunningIndicator.emit(self.running)

    @Slot(str)
    def stopCommand(self, channel):
        if channel == "C1":
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
        elif channel == "C2":
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)

    @Slot(str)
    def zeroPosition(self, channel):
        if channel == "C1":
            self.positionProcessVariableC1 = 0
            self.positionSetPointC1 = 0
            self.previousCountC1 = 0
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1) 
            self.updatePositionProcessVariableC1.emit(self.positionProcessVariableC1)
            ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
        elif channel == "C2":
            self.positionProcessVariableC2 = 0
            self.positionSetPointC2 = 0
            self.previousCountC2 = 0
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2) 
            self.updatePositionProcessVariableC2.emit(self.positionProcessVariableC2)
            ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    def setClock(self, clock, freq):        
        # Define appropriate clock settings, selecting the minimum possible divisor 
        # that does not result in a roll value that exceeds the bit depth of the clock.
        # Clamp frequency to 426666, which is equivalent to 4000 RPM for a 6400 CPR encoder
        # with a 16 bit clock and divisor value of 8.
        core_freq = 80000000
        max_roll = 2**16
        divisor = 8
        width = 10  
        max_freq = 426666
        min_freq = (core_freq/(divisor*max_roll))
        if freq > max_freq:
            freq = max_freq
        elif freq < min_freq:
            freq = np.ceil(min_freq)
        roll = int(min(max(1,core_freq/(freq*divisor)), max_roll))

        # Set the clock.
        aNames = ['DIO_EF_CLOCK' + str(clock) + '_ENABLE',
                'DIO_EF_CLOCK' + str(clock) + '_DIVISOR',
                'DIO_EF_CLOCK' + str(clock) + '_ROLL_VALUE',
                'DIO_EF_CLOCK' + str(clock) + '_ENABLE']
        aValues = [0, divisor, roll, 1]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
        # log.info("Clock {clock} set to {freq} Hz.".format(clock=clock, freq=freq))

        return freq, roll, width

    def updateClock(self, clock, freq):        
        # Define appropriate clock settings, selecting the minimum possible divisor 
        # that does not result in a roll value that exceeds the bit depth of the clock.
        # Clamp frequency to 426666, which is equivalent to 4000 RPM for a 6400 CPR encoder
        # with a 16 bit clock and divisor value of 8.
        core_freq = 80000000
        max_roll = 2**16
        divisor = 8
        width = 10
        max_freq = 426666
        min_freq = (core_freq/(divisor*max_roll))
        if freq > max_freq:
            freq = max_freq
        elif freq < min_freq:
            freq = np.ceil(min_freq)
        roll = int(min(max(1,core_freq/(freq*divisor)), max_roll))
        
        # Updates the clock.
        aNames = ['DIO_EF_CLOCK' + str(clock) + '_DIVISOR',
                'DIO_EF_CLOCK' + str(clock) + '_ROLL_VALUE']
        aValues = [divisor, roll]
        numFrames = len(aNames)
        ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
        
        # log.info("Clock {clock} set to {freq} Hz.".format(clock=clock, freq=freq))

        return freq, roll, width

    def checkConnection(self):
        self.handle = ljm.open(7, self.connection, self.id)
        
        connectedC1 = not bool(int(ljm.eReadName(self.handle, 'FIO0')))
        self.updateConnectionIndicatorC1.emit(connectedC1)

        connectedC2 = not bool(int(ljm.eReadName(self.handle, 'FIO2')))
        self.updateConnectionIndicatorC2.emit(connectedC2)
        
        return connectedC1, connectedC2

    @Slot(str, float)
    def updatePositionLeftLimit(self, channel, value):
        if channel == "C1":
            self.positionLeftLimitC1 = value
        elif channel == "C2":
            self.positionLeftLimitC2 = value
        
    @Slot(str, float)
    def updatePositionRightLimit(self, channel, value):
        if channel == "C1":
            self.positionRightLimitC1 = value
        elif channel == "C2":
            self.positionRightLimitC2 = value

    @Slot(str, float)
    def updateFeedbackLeftLimit(self, channel, value):
        if channel == "C1":
            self.feedbackLeftLimitC1 = value
        elif channel == "C2":
            self.feedbackLeftLimitC2 = value
        
    @Slot(str, float)
    def updateFeedbackRightLimit(self, channel, value):
        if channel == "C1":
            self.feedbackRightLimitC1 = value
        elif channel == "C2":
            self.feedbackRightLimitC2 = value

    @Slot(str, bool)
    def updatePositionLeftLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionLeftLimitStatusC1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.positionLeftLimitStatusC2 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
    
    @Slot(str, bool)
    def updatePositionRightLimitStatus(self, channel, status):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.positionRightLimitStatusC1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.positionRightLimitStatusC2 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)

    @Slot(str)
    def setEnable(self, channel, value):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1" and value == True:
            self.positionSetPointC1 = self.positionProcessVariableC1
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
            ljm.eWriteName(self.handle, "EIO0", 1)
            self.motorEnabledC1 = True
        elif channel == "C1" and value == False:
            ljm.eWriteName(self.handle, "EIO0", 0)
            self.motorEnabledC1 = False
        elif channel == "C2" and value == True:
            self.positionSetPointC2 = self.positionProcessVariableC2
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
            ljm.eWriteName(self.handle, "EIO2", 1)
            self.motorEnabledC2 = True
        elif channel == "C2" and value == False:
            ljm.eWriteName(self.handle, "EIO2", 0)
            self.motorEnabledC2 = False

    @Slot(str, float)
    def setSpeed(self, channel, speed):
        self.handle = ljm.open(7, self.connection, self.id)     
        if channel == "C1":
            self.speedC1 = speed
            targetFrequency = speed*self.countsPerUnitC1
            self.freqC1, self.rollC1, self.widthC1 = self.updateClock(1, targetFrequency)
            ljm.eWriteName(self.handle, "DIO4_EF_CONFIG_A", self.widthC1)
            outputSpeed = self.freqC1/self.countsPerUnitC1
            self.updateSpeedC1.emit(outputSpeed)
            if self.movingC1 == True:
                self.moveToPosition(channel, self.positionSetPointC1)
        if channel == "C2":
            self.speedC2 = speed
            targetFrequency = speed*self.countsPerUnitC2 
            self.freqC2, self.rollC2, self.widthC2 = self.updateClock(2, targetFrequency)
            ljm.eWriteName(self.handle, "DIO5_EF_CONFIG_A", self.widthC2)
            outputSpeed = self.freqC2/self.countsPerUnitC2
            self.updateSpeedC2.emit(outputSpeed)
            if self.movingC2 == True:
                self.moveToPosition(channel, self.positionSetPointC2)
        
    @Slot(str)
    def jogPositiveOn(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            if self.running == True and self.maximumLimitC1 == False and self.motorEnabledC1 == True:
                if self.positionProcessVariableC1 <= self.positionRightLimitC1:
                    # Set direction.
                    self.directionC1 = 1
                    self.jogC1 = True
                    self.setDirection("C1", self.directionC1)
                    # Reset counters.
                    self.countC1 = 0
                    self.previousCountC1 = 0
                    self.pulsesC1 = 0
                    self.previousPulsesC1 = 0
                    # Emit number of pulses required to travel full range of movement.
                    pulses = int(abs(self.positionRightLimitC1-self.positionLeftLimitC1)*self.countsPerUnitC1)
                    aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_CONFIG_C", "DIO4_EF_ENABLE"]
                    aValues = [0, 0, 2, 1, self.widthC1, pulses, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
        elif channel == "C2":
            if self.running == True and self.maximumLimitC2 == False and self.motorEnabledC2 == True:
                if self.positionProcessVariableC2 <= self.positionRightLimitC2:
                    # Set direction.
                    self.directionC2 = 1
                    self.jogC2 = True
                    self.setDirection("C2", self.directionC2)
                    # Reset counters.
                    self.countC2 = 0
                    self.previousCountC2 = 0
                    self.pulsesC2 = 0
                    self.previousPulsesC2 = 0
                    # Emit number of pulses required to travel full range of movement.
                    pulses = int(abs(self.positionRightLimitC2-self.positionLeftLimitC2)*self.countsPerUnitC2)
                    aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_CONFIG_C", "DIO5_EF_ENABLE"]
                    aValues = [0, 0, 2, 1, self.widthC2, pulses, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    @Slot(str)
    def jogPositiveOff(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.jogC1 = False
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.jogC2 = False
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)  
    
    @Slot(str)
    def jogNegativeOn(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            if self.running == True and self.maximumLimitC1 == False and self.motorEnabledC1 == True:
                if self.positionLeftLimitC1 <= self.positionProcessVariableC1:
                    # Set direction.
                    self.directionC1 = -1
                    self.jogC1 = True
                    self.setDirection("C1", self.directionC1)
                    # Reset counters.
                    self.countC1 = 0
                    self.previousCountC1 = 0
                    self.pulsesC1 = 0
                    self.previousPulsesC1 = 0
                    # Emit number of pulses required to travel full range of movement.
                    pulses = int(abs(self.positionRightLimitC1-self.positionLeftLimitC1)*self.countsPerUnitC1)
                    aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_CONFIG_C", "DIO4_EF_ENABLE"]
                    aValues = [0, 0, 2, 1, self.widthC1, pulses, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
        elif channel == "C2":
            if self.running == True and self.maximumLimitC2 == False and self.motorEnabledC2 == True:
                if self.positionLeftLimitC2 <= self.positionProcessVariableC2:
                    # Set direction.
                    self.directionC2 = -1
                    self.jogC2 = True
                    self.setDirection("C2", self.directionC2)
                    # Reset counters.
                    self.countC2 = 0
                    self.previousCountC2 = 0
                    self.pulsesC2 = 0
                    self.previousPulsesC2 = 0
                    # Emit number of pulses required to travel full range of movement.
                    pulses = int(abs(self.positionRightLimitC2-self.positionLeftLimitC2)*self.countsPerUnitC2)
                    aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_CONFIG_C", "DIO5_EF_ENABLE"]
                    aValues = [0, 0, 2, 1, self.widthC2, pulses, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    @Slot(str)
    def jogNegativeOff(self, channel):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            self.jogC1 = False
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        elif channel == "C2":
            self.jogC2 = False
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)

    @Slot()
    def updateControlPanelC1(self):
        if self.jogC1 == True: 
            self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
        self.updatePositionProcessVariableC1.emit(self.positionProcessVariableC1)
        if self.feedbackChannelC1 > 0:
            self.updateFeedbackProcessVariableC1.emit(self.feedbackProcessVariableC1)
            if self.statusPIDC1 == True:
                self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
            elif self.statusPIDC1 == False:
                self.updateFeedbackSetPointC1.emit(self.feedbackProcessVariableC1) 
        
    @Slot()
    def updateControlPanelC2(self):   
        if self.jogC2 == True:
            self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
        self.updatePositionProcessVariableC2.emit(self.positionProcessVariableC2)
        if self.feedbackChannelC2 > 0:
            self.updateFeedbackProcessVariableC2.emit(self.feedbackProcessVariableC2)
            if self.statusPIDC1 == True:
                self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
            elif self.statusPIDC2 == False:
                self.updateFeedbackSetPointC2.emit(self.feedbackProcessVariableC2) 
        
    @Slot(str, float)
    def moveToPosition(self, channel, position):
        if self.running == True:
            if channel == "C1" and self.motorEnabledC1 == True:
                # Calculate increment.
                currentPosition = self.positionProcessVariableC1
                increment = position - currentPosition
                # Set direction.
                if increment > 0:
                    self.directionC1 = 1
                elif increment < 0:   
                    self.directionC1 = -1
                self.setDirection(channel, self.directionC1)
                self.positionSetPointC1 = position
                # Reset counters.
                self.countC1 = 0
                self.previousCountC1 = 0
                self.pulsesC1 = 0
                self.previousPulsesC1 = 0
                # Emit required number of pulses.
                pulses = int(abs(increment*self.countsPerUnitC1))
                aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_CONFIG_C", "DIO4_EF_ENABLE"]
                aValues = [0, 0, 2, 1, self.widthC1, pulses, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC1 = True
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
            elif channel == "C2" and self.motorEnabledC2 == True:
                # Calculate increment.
                currentPosition = self.positionProcessVariableC2
                increment = position - currentPosition
                # Set direction.
                if increment > 0:
                    self.directionC2 = 1
                elif increment < 0:   
                    self.directionC2 = -1
                self.setDirection(channel, self.directionC2)
                self.positionSetPointC2 = position
                # Reset counters.
                self.countC2 = 0
                self.previousCountC2 = 0
                self.pulsesC2 = 0
                self.previousPulsesC2 = 0
                # Emit required number of pulses.
                pulses = int(abs(increment*self.countsPerUnitC2))
                aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_CONFIG_C", "DIO5_EF_ENABLE"]
                aValues = [0, 0, 2, 1, self.widthC2, pulses, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC2 = True
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    def emitPulses(self, channel):
        if self.running == True:
            if channel == "C1" and self.motorEnabledC1 == True:
                # Reset counters.
                self.countC1 = 0
                self.previousCountC1 = 0
                self.pulsesC1 = 0
                self.previousPulsesC1 = 0
                # Emit number of pulses required to travel full range of movement.
                pulses = int(abs(self.positionRightLimitC1-self.positionLeftLimitC1)*self.countsPerUnitC1)
                aNames = ["DIO4_EF_ENABLE", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_CONFIG_C", "DIO4_EF_ENABLE"]
                aValues = [0, 2, 1, self.widthC1, pulses, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC1 = True
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
            elif channel == "C2" and self.motorEnabledC2 == True:
                # Reset counters.
                self.countC2 = 0
                self.previousCountC2 = 0
                self.pulsesC2 = 0
                self.previousPulsesC2 = 0
                # Emit required number of pulses.
                pulses = int(abs(self.positionRightLimitC2-self.positionLeftLimitC2)*self.countsPerUnitC2)
                aNames = ["DIO5_EF_ENABLE", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_CONFIG_C", "DIO5_EF_ENABLE"]
                aValues = [0, 2, 1, self.widthC2, pulses, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC2 = True
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")

    def setDirection(self, channel, direction):
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            name = "EIO1"
        elif channel == "C2":
            name = "EIO3"
        if direction == 1:
            ljm.eWriteName(self.handle, name, 0)
        elif direction == -1:
            ljm.eWriteName(self.handle, name, 1)

    def getPositionC1(self):
        self.handle = ljm.open(7, self.connection, self.id)
        self.countC1 = ljm.eReadName(self.handle, "DIO4_EF_READ_A")
        self.pulsesC1 = ljm.eReadName(self.handle, "DIO1_EF_READ_A")
        if self.countC1 == 0:
            incrementCount = 0
        else:
            incrementCount = (self.countC1-self.previousCountC1)/self.countsPerUnitC1
        self.previousCountC1 = self.countC1

        # # Increment position process variable.
        # if self.directionC1 == 1:
        #     self.positionProcessVariableC1 += incrementCount
        # elif self.directionC1 == -1:
        #     self.positionProcessVariableC1 -= incrementCount

        # Check motor status by comparing pulses count output with pulses returned.
        if self.pulsesC1 == 0:
            incrementPulses = 0
        else:
            incrementPulses = (self.pulsesC1-self.previousPulsesC1)/self.pulsesPerUnitC1
        self.previousPulsesC1 = self.pulsesC1

        # Increment position process variable.
        if self.directionC1 == 1:
            self.positionProcessVariableC1 += incrementPulses
        elif self.directionC1 == -1:
            self.positionProcessVariableC1 -= incrementPulses

        # Check positional error using feedback pulses and reset motor if required.
        err = abs(incrementPulses-incrementCount)
        if err > 1:
            log.warning("Returned position on C1 does not match demand.")
        
        # If moving under jog control, stop if target limit.
        if self.jogC1 == True:
            if self.directionC1 == -1 and self.positionProcessVariableC1 < self.positionLeftLimitC1:
                self.moveToPosition("C1", self.positionLeftLimitC1)
                self.movingC1 = False
            elif self.directionC1 == 1 and self.positionProcessVariableC1 > self.positionRightLimitC1:
                self.moveToPosition("C1", self.positionRightLimitC1)
                self.movingC1 = False
            self.positionSetPointC1 = self.positionProcessVariableC1
        
    def getPositionC2(self):
        self.handle = ljm.open(7, self.connection, self.id)
        self.countC2 = ljm.eReadName(self.handle, "DIO5_EF_READ_A")
        self.pulsesC2 = ljm.eReadName(self.handle, "DIO3_EF_READ_A")
        if self.countC2 == 0:
            incrementCount = 0
        else:
            incrementCount = (self.countC2-self.previousCountC2)/self.countsPerUnitC2
        self.previousCountC2 = self.countC2

        # Check motor status by comparing pulses count output with pulses returned.
        if self.pulsesC2 == 0:
            incrementPulses = 0
        else:
            incrementPulses = (self.pulsesC2-self.previousPulsesC2)/self.pulsesPerUnitC2
        self.previousPulsesC2 = self.pulsesC2

        # Increment position process variable.
        if self.directionC2 == 1:
            self.positionProcessVariableC2 += incrementPulses
        elif self.directionC2 == -1:
            self.positionProcessVariableC2 -= incrementPulses

        # Check positional error using feedback pulses and reset motor if required.
        err = abs(incrementPulses-incrementCount)
        if err > 1:
            log.warning("Returned position on C2 does not match demand.")
        
        # If moving under jog control, stop if target limit.
        if self.jogC2 == True:
            if self.directionC2 == -1 and self.positionProcessVariableC2 < self.positionLeftLimitC2:
                self.moveToPosition("C2", self.positionLeftLimitC2)
                self.movingC2 = False
            elif self.directionC2 == 1 and self.positionProcessVariableC2 > self.positionRightLimitC2:
                self.moveToPosition("C2", self.positionRightLimitC2)
                self.movingC2 = False
            self.positionSetPointC2 = self.positionProcessVariableC2

    def resetMotor(self, channel):
        # Reset motor for given control channel.
        self.handle = ljm.open(7, self.connection, self.id)
        if channel == "C1":
            name = "EIO0"
        elif channel == "C2":
            name = "EIO2"
        ljm.eWriteName(self.handle, name, 0)
        ljm.eWriteName(self.handle, name, 1)
        log.info("Motor reset on control channel " + channel + ".")

    def configurePulseCounters(self):
        #  Refresh device connection.
        self.handle = ljm.open(7, self.connection, self.id)

        # Setup pulse counters. Set to mode 2 which counts both rising and falling edges. 
        # 400 microsecond debounce period, which is just less than the time between rising and
        # falling edges for 16 PPR at 4000 RPM.
        aNamesC1 = ["DIO1_EF_ENABLE", "DIO1_EF_INDEX", "DIO1_EF_CONFIG_A", "DIO1_EF_CONFIG_B", "DIO1_EF_ENABLE"]
        aNamesC2 = ["DIO3_EF_ENABLE", "DIO3_EF_INDEX", "DIO3_EF_CONFIG_A", "DIO3_EF_CONFIG_B", "DIO3_EF_ENABLE"]
        aValues = [0, 9, 400, 2, 1]
        numFrames = 5
        ljm.eWriteNames(self.handle, numFrames, aNamesC1, aValues)
        ljm.eWriteNames(self.handle, numFrames, aNamesC2, aValues)

        log.info("Pulse counters configured on device named " + self.name + ".")

    def configureADC(self):
        #  Refresh device connection.
        self.handle = ljm.open(7, self.connection, self.id)

        # Set the ADC settings.
        names = ["AIN_ALL_RANGE", "AIN_ALL_RESOLUTION_INDEX", "AIN_ALL_SETTLING_US"]
        aValues = [10, 2, 0] # No amplification; 16.5 effective bits; auto settling time.
        numFrames = len(names)
        ljm.eWriteNames(self.handle, numFrames, names, aValues) 

    def setAcquisition(self, channels, addresses, dataTypes, slopes, offsets, autozero, controlRate):
        self.channels = channels
        self.addresses = addresses
        self.dataTypes = dataTypes
        self.slopes = np.asarray(slopes)
        self.offsets = np.asarray(offsets)
        self.autozero = np.asarray(autozero)
        self.numFrames = len(self.addresses)
        self.controlRate = controlRate

    def openConnection(self):
        # Method to open a device connection
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.name = ljm.eReadNameString(self.handle, "DEVICE_NAME_DEFAULT")
            log.info("Connected to " + self.name + ".")
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def initialiseSettings(self):
        # Method to initialise the device.
        if self.handle != None:
            try:
                self.configureADC()
                self.configurePulseCounters()
            except ljm.LJMError:
                # Otherwise log the exception.
                ljme = sys.exc_info()[1]
                log.warning(ljme) 
            except Exception:
                e = sys.exc_info()[1]
                log.warning(e)

    def loadLuaScript(self):
        self.script = "src/failsafe.lua"
        self.loadLua()
        self.executeLua()
    
    def loadLua(self):
        try:
            # Read the Lua script.
            with open(self.script, "r") as f:
                lua = f.read()
            lua_length = len(lua)

            # Disable a running script by writing 0 to LUA_RUN twice. Wait for the Lua VM to shut down (and some T7 firmware versions need
            # a longer time to shut down than others) in between the repeated commands.
            ljm.eWriteName(self.handle, "LUA_RUN", 0)
            sleep(2)
            ljm.eWriteName(self.handle, "LUA_RUN", 0)

            # Write the size and the Lua Script to the device.
            ljm.eWriteName(self.handle, "LUA_SOURCE_SIZE", lua_length)
            ljm.eWriteNameByteArray(
                self.handle, "LUA_SOURCE_WRITE", lua_length, bytearray(lua, encoding="utf8")
            )

            # Start the script with debug output disabled.
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE", 1)
            ljm.eWriteName(self.handle, "LUA_DEBUG_ENABLE_DEFAULT", 1)
            log.info("Lua script loaded.")

            # Set the failsafe boolean to unity.
            ljm.eWriteName(self.handle, "USER_RAM0_U16", int(1))
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def executeLua(self):
        # Method to execute a Lua script.
        try:
            ljm.eWriteName(self.handle, "LUA_RUN", 1)
            log.info("Lua script executed.")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
    def readValues(self):
        # Method to read registers on device.
        try:
            # Read from the device and apply slope and offsets.
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "USER_RAM0_U16", 1) 
            self.checkLimits()
            self.raw = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.addresses, self.dataTypes))
            data = self.slopes*(self.raw - self.offsets)
            self.getPositionC1()
            self.getPositionC2()
            # If feedback is available.
            if self.feedbackC1 == True:
                self.feedbackProcessVariableC1 = self.data[self.feedbackChannelC1-1]
                if self.statusPIDC1 == True:
                    self.speedSetPointC1 = self.PID_C1(self.feedbackProcessVariableC1)
                    # print(self.speedSetPointC1)
                    self.directionC1 = int(np.sign(self.speedSetPointC1))
                    demandSpeed = np.abs(self.speedSetPointC1)
                    # print(self.speedSetPointC1, demandSpeed, self.directionC1)
                    self.setDirection("C1", self.directionC1)
                    self.setSpeed("C1", demandSpeed)
                    # ljm.eWriteName(self.handle, "DIO4_EF_CONFIG_A", width)
                    # aNames = ["DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
                    # aValues = [0, 1, width, 1]
                    # numFrames = len(aNames)
                    # results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                    # self.emitPulses("C1")
            if self.feedbackC2 == True:
                self.feedbackProcessVariableC2 = self.data[self.feedbackChannelC2-1]
                if self.statusPIDC2 == True:
                    self.speedSetPointC2 = PID_C2(self.feedbackProcessVariableC2)
            # Concatenate output data.
            if self.feedbackC1 == False:
                dataC1 = np.hstack((self.positionSetPointC1, self.positionProcessVariableC1, int(self.directionC1), self.speedC1))
            elif self.feedbackC1 == True:
                dataC1 = np.hstack((self.positionSetPointC1, self.positionProcessVariableC1, int(self.directionC1), self.speedC1, self.feedbackSetPointC1, self.feedbackProcessVariableC1))
            if self.feedbackC2 == False:
                dataC2 = np.hstack((self.positionSetPointC2, self.positionProcessVariableC2, int(self.directionC2), self.speedC2))
            elif self.feedbackC2 == True:
                dataC2 = np.hstack((self.positionSetPointC2, self.positionProcessVariableC2, int(self.directionC2), self.speedC2, self.feedbackSetPointC2, self.feedbackProcessVariableC2))
            if self.enabledC1 == True:
                data = np.concatenate((data, dataC1))
            if self.enabledC2 == True:
                data = np.concatenate((data, dataC2))
            self.data = data
            self.emitData.emit(self.name, self.data)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot()
    def recalculateOffsets(self):
        # Method to autozero channels as required by the configuration.
        adjustOffsets = (self.raw-self.offsets)*self.autozero
        self.offsets = self.offsets + adjustOffsets

        # Update the device configuration.
        self.updateOffsets.emit(self.name, self.channels, self.offsets.tolist())
        log.info("Autozero applied to device.")

        
