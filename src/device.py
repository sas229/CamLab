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
        self.KP_C1 = 0.0
        self.KI_C1 = 0.0
        self.KD_C1 = 0.0
        self.KP_C2 = 0.0
        self.KI_C2 = 0.0
        self.KD_C2 = 0.0
        self.statusPIDC1 = False
        self.statusPIDC2 = False
        self.enabledC1 = True
        self.enabledC2 = True
        self.motorEnabledC1 = False
        self.motorEnabledC2 = False
        self.feedbackC1 = True
        self.feedbackC2 = True
        self.feedbackIndexC1 = 0
        self.feedbackIndexC2 = 0
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
        self.feedbackLeftLimitC1 = -100
        self.feedbackLeftLimitC2 = -100
        self.feedbackRightLimitC1 = 100
        self.feedbackRightLimitC2 = 100
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
        self.max_rpm = 4000

        #  Initialise.
        self.open_connection()
        self.initialise_settings()
        self.load_lua_script()
        self.check_limits()
        self.disable_clock_0()
        self.set_speed_limit()

        # Set initial speeds.
        self.setSpeed("C1", self.speedC1)
        self.setSpeed("C2", self.speedC2)

        # PID instantiation.
        self.PID_C1 = PID()
        self.set_PID_tunings_C1()
        self.PID_C2 = PID()
        self.set_PID_tunings_C2()

    @Slot(str)
    def set_enable_C1(self, value):
        """Set enable state for control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            if value ==  True:
                self.positionSetPointC1 = self.positionProcessVariableC1
                self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
                ljm.eWriteName(self.handle, "EIO0", 1)
                self.motorEnabledC1 = True
            else:
                ljm.eWriteName(self.handle, "EIO0", 0)
                self.motorEnabledC1 = False
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
    @Slot(str)
    def set_enable_C2(self, value):
        """Set enable state for control channel C2."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            if value ==  True:
                self.positionSetPointC2 = self.positionProcessVariableC2
                self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
                ljm.eWriteName(self.handle, "EIO2", 1)
                self.motorEnabledC2 = True
            else:
                ljm.eWriteName(self.handle, "EIO2", 0)
                self.motorEnabledC2 = False
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def disable_clock_0(self):
        """Check clock 0 is disabled."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle,'DIO_EF_CLOCK0_ENABLE',0)
            log.info("Clock 0 disabled on {device}.".format(device=self.name))
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def turn_C1_PWM_on(self):
        """Turn control channel C1 PWM on."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 1)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def turn_C2_PWM_on(self):
        """Turn control channel C2 PWM on."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 1)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
    
    def turn_C1_PWM_off(self):
        """Turn control channel C1 PWM off."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def turn_C2_PWM_off(self):
        """Turn control channel C2 PWM off."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def set_PID_tunings_C1(self):
        """Set PID tunings for control channel C1."""
        self.PID_C1.tunings = (self.KP_C1, self.KI_C1, self.KD_C1)
        log.info("PID tunings updated for control channel C1 on {device}.".format(device=self.name))

    def set_PID_tunings_C2(self):
        """Set PID tunings for control channel C2."""
        self.PID_C2.tunings = (self.KP_C2, self.KI_C2, self.KD_C2)
        log.info("PID tunings updated for control channel C2 on {device}.".format(device=self.name))

    def set_clock(self, clock, freq):        
        """Define appropriate clock settings, selecting the minimum possible divisor 
        that does not result in a roll value that exceeds the bit depth of the clock.
        Clamp frequency to 426666, which is equivalent to 4000 RPM for a 6400 CPR encoder
        with a 16 bit clock and divisor value of 8."""
        try:
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
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

            return freq, roll, width

        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def refresh_connection(self):
        """Refresh connection to LabJack T7 device."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def check_connection_C1(self):
        """Check connection to control device on channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.connectedC1 = not bool(int(ljm.eReadName(self.handle, 'FIO0')))
            self.updateConnectionIndicatorC1.emit(self.connectedC1)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def check_connection_C2(self):
        """Check connection to control device on channel C2."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.connectedC2 = not bool(int(ljm.eReadName(self.handle, 'FIO2')))
            self.updateConnectionIndicatorC2.emit(self.connectedC2)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def check_connections(self):
        """Check connections to control devices."""
        self.check_connection_C1()
        self.check_connection_C2()

    def set_speed_limit(self):
        """Set speed limit for motors."""
        self.speed_limit = (self.CPR*self.max_rpm)/(60*self.countsPerUnitC2)
        log.info("Speed limit set on {device} for {rpm} RPM.".format(device=self.name, rpm=self.max_rpm))

    @Slot(bool)
    def set_PID_control_C1(self, value):
        """Set PID state for control channel C1."""
        self.statusPIDC1 = value
        if value == True:
            self.PID_C1.reset()
            self.PID_C1.output_limits = (-self.speed_limit, self.speed_limit)
            self.PID_C1.setpoint = self.feedbackSetPointC1
            self.PID_C1.set_auto_mode(True, last_output=0.001)
            self.turn_C1_PWM_on()
            log.info("PID control for control channel C1 on " + self.name + " turned on.")
        else:
            self.positionSetPointC1 = self.positionProcessVariableC1
            self.PID_C1.set_auto_mode(False)
            self.updatePositionSetPointC1.emit(self.positionSetPointC1)
            self.turn_C1_PWM_off()
            log.info("PID control for control channel C1 on " + self.name + " turned off.")

    @Slot(bool)
    def set_PID_control_C2(self, value):
        """Set PID state for control channel C2."""
        self.statusPIDC2 = value
        if value == True:
            self.PID_C2.reset()
            self.PID_C2.output_limits = (-self.speed_limit, self.speed_limit)
            self.PID_C2.setpoint = self.feedbackSetPointC2
            self.PID_C2.set_auto_mode(True, last_output=0.001)
            self.turn_C2_PWM_on()
            log.info("PID control for control channel C2 on " + self.name + " turned on.")
        else:
            self.positionSetPointC2 = self.positionProcessVariableC2
            self.PID_C2.set_auto_mode(False)
            self.updatePositionSetPointC1.emit(self.positionSetPointC2)
            self.turn_C2_PWM_off()
            log.info("PID control for control channel C2 on " + self.name + " turned off.")
    
    @Slot(float)
    def set_KP_C1(self, value):
        """Set PID proportional gain for control channel C1."""
        self.KP_C1 = value
        self.set_PID_tunings_C1()
        log.info("PID proportional gain for control channel C1 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    @Slot(float)
    def set_KI_C1(self, value):
        """Set PID integral gain for control channel C1."""
        self.KI_C1 = value
        self.set_PID_tunings_C1()
        log.info("PID integral gain for control channel C1 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    @Slot(float)
    def set_KD_C1(self, value):
        """Set PID derivative gain for control channel C1."""
        self.KD_C1 = value
        self.set_PID_tunings_C1()
        log.info("PID derivative gain for control channel C1 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    @Slot(float)
    def set_KP_C2(self, value):
        """Set PID proportional gain for control channel C2."""
        self.KP_C2 = value
        self.set_PID_tunings_C2()
        log.info("PID proportional gain for control channel C2 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    @Slot(float)
    def set_KI_C2(self, value):
        """Set PID integral gain for control channel C2."""
        self.KI_C2 = value
        self.set_PID_tunings_C2()
        log.info("PID integral gain for control channel C2 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    @Slot(float)
    def set_KD_C2(self, value):
        """Set PID derivative gain for control channel C2."""
        self.KD_C2 = value
        self.set_PID_tunings_C2()
        log.info("PID derivative gain for control channel C2 on {device} changed to {value:.2f}.".format(value=value, device=self.name))

    # @Slot(str, float)
    # def setKP(self, channel, value):
    #     if channel == "C1":
    #         self.KP_C1 = value
    #     elif channel == "C2":
    #         self.KPC2 = value
    #     self.set_PID_tunings(channel)

    # @Slot(str, float)
    # def setKI(self, channel, value):
    #     if channel == "C1":
    #         self.KI_C1 = value
    #     elif channel == "C2":
    #         self.KIC2 = value
    #     self.set_PID_tunings(channel)

    # @Slot(str, float)
    # def setKD(self, channel, value):
    #     if channel == "C1":
    #         self.KD_C1 = value
    #     elif channel == "C2":
    #         self.KDC2 = value
    #     self.set_PID_tunings(channel)

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
            self.feedbackIndexC1 = feedback
        elif channel == "C2":
            self.feedbackIndexC2 = feedback

    def check_limits(self):
        try:
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
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

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
        try:
            if channel == "C1":
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
                self.updatePositionSetPointC1.emit(self.positionProcessVariableC1)
            elif channel == "C2":
                ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
                self.updatePositionSetPointC2.emit(self.positionProcessVariableC2)
            log.info("Control stopped on device " + self.name + " control channel " + channel + ".")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str)
    def zeroPosition(self, channel):
        try:
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
            log.info("Position zeroed on device " + self.name + " control channel " + channel + ".")
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    

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
        try:
            # Refresh the connection.
            self.handle = ljm.open(7, self.connection, self.id)
            if channel == "C1":
                self.positionLeftLimitStatusC1 = status
                if status == True:
                    ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            elif channel == "C2":
                self.positionLeftLimitStatusC2 = status
                if status == True:
                    ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
    
    @Slot(str, bool)
    def updatePositionRightLimitStatus(self, channel, status):
        try:
            # Refresh the connection.
            self.handle = ljm.open(7, self.connection, self.id)
            if channel == "C1":
                self.positionRightLimitStatusC1 = status
                if status == True:
                    ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            elif channel == "C2":
                self.positionRightLimitStatusC2 = status
                if status == True:
                    ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
        except ljm.LJMError:
            # Otherwise log the exception.
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(str, float)
    def setSpeed(self, channel, speed):
        self.handle = ljm.open(7, self.connection, self.id)     
        if channel == "C1":
            targetFrequency = int(speed*self.countsPerUnitC1)
            self.freqC1, self.rollC1, self.widthC1 = self.set_clock(1, targetFrequency)
            ljm.eWriteName(self.handle, "DIO4_EF_CONFIG_A", self.widthC1)
            self.speedC1 = self.freqC1/self.countsPerUnitC1
            self.updateSpeedC1.emit(self.speedC1)
            if self.movingC1 == True:
                self.moveToPosition(channel, self.positionSetPointC1)
        if channel == "C2":
            targetFrequency = int(speed*self.countsPerUnitC2)
            self.freqC2, self.rollC2, self.widthC2 = self.set_clock(2, targetFrequency)
            ljm.eWriteName(self.handle, "DIO5_EF_CONFIG_A", self.widthC2)
            self.speedC2 = self.freqC2/self.countsPerUnitC2
            self.updateSpeedC2.emit(self.speedC2)
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
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
                    # Turn on PWM.
                    aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
                    aValues = [0, 0, 0, 1, self.widthC1, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
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
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")
                    # Turn on PWM.
                    aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_ENABLE"]
                    aValues = [0, 0, 0, 2, self.widthC2, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

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
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
                    # Turn on PWM.
                    aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
                    aValues = [0, 0, 0, 1, self.widthC1, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
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
                    # Reset pulse in counter.
                    ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")
                    # Turn on PWM.
                    aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_ENABLE"]
                    aValues = [0, 0, 0, 2, self.widthC2, 1]
                    numFrames = len(aNames)
                    results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)

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
        if self.feedbackIndexC1 != 0:
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
        if self.feedbackIndexC2 != 0:
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
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
                # Turn on PWM.
                aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
                aValues = [0, 0, 0, 1, self.widthC1, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC1 = True
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
                # Reset pulse in counter.
                ljm.eReadName(self.handle, "DIO3_EF_READ_A_AND_RESET")
                # Turn on PWM.
                aNames = ["DIO5_EF_ENABLE", "DIO5", "DIO5_EF_INDEX", "DIO5_EF_OPTIONS", "DIO5_EF_CONFIG_A", "DIO5_EF_ENABLE"]
                aValues = [0, 0, 0, 2, self.widthC2, 1]
                numFrames = len(aNames)
                results = ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
                self.movingC2 = True

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
        self.pulsesC1 = ljm.eReadName(self.handle, "DIO1_EF_READ_A")

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
        
        # If moving under jog control, stop if at limit.
        if self.jogC1 == True:
            if self.directionC1 == -1 and self.positionProcessVariableC1 < self.positionLeftLimitC1:
                self.moveToPosition("C1", self.positionLeftLimitC1)
                self.movingC1 = False
            elif self.directionC1 == 1 and self.positionProcessVariableC1 > self.positionRightLimitC1:
                self.moveToPosition("C1", self.positionRightLimitC1)
                self.movingC1 = False
            self.positionSetPointC1 = self.positionProcessVariableC1
        
        # Stop movement if at setpoint.
        if self.movingC1 == True and self.directionC1 == -1 and self.positionProcessVariableC1 < self.positionSetPointC1:
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            self.movingC1 = False
        elif self.movingC1 == True and self.directionC1 == 1 and self.positionProcessVariableC1 > self.positionSetPointC1:
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
            self.movingC1 = False
        
    def getPositionC2(self):
        self.handle = ljm.open(7, self.connection, self.id)
        self.pulsesC2 = ljm.eReadName(self.handle, "DIO3_EF_READ_A")

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
        
        # If moving under jog control, stop if at limit.
        if self.jogC2 == True:
            if self.directionC2 == -1 and self.positionProcessVariableC2 < self.positionLeftLimitC2:
                self.moveToPosition("C2", self.positionLeftLimitC2)
                self.movingC2 = False
            elif self.directionC2 == 1 and self.positionProcessVariableC2 > self.positionRightLimitC2:
                self.moveToPosition("C2", self.positionRightLimitC2)
                self.movingC2 = False
            self.positionSetPointC2 = self.positionProcessVariableC2

        # Stop movement if at setpoint.
        if self.movingC2 == True and self.directionC2 == -1 and self.positionProcessVariableC2 < self.positionSetPointC2:
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
            self.movingC2 = False
        elif self.movingC2 == True and self.directionC2 == 1 and self.positionProcessVariableC2 > self.positionSetPointC2:
            ljm.eWriteName(self.handle, "DIO5_EF_ENABLE", 0)
            self.movingC2 = False

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

    def open_connection(self):
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

    def initialise_settings(self):
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

    def load_lua_script(self):
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
            self.check_limits()
            self.raw = np.asarray(ljm.eReadAddresses(self.handle, self.numFrames, self.addresses, self.dataTypes))
            data = self.slopes*(self.raw - self.offsets)
            self.getPositionC1()
            self.getPositionC2()
            # If feedback is available.
            if self.feedbackC1 == True:
                self.feedbackProcessVariableC1 = data[self.feedbackIndexC1-1]
                if self.statusPIDC1 == True:
                    self.speedSetPointC1 = self.PID_C1(self.feedbackProcessVariableC1)
                    self.directionC1 = np.sign(self.speedSetPointC1)
                    demandSpeed = np.abs(self.speedSetPointC1)
                    self.setDirection("C1", self.directionC1)
                    self.setSpeed("C1", demandSpeed)
            if self.feedbackC2 == True:
                self.feedbackProcessVariableC2 = data[self.feedbackIndexC2-1]
                if self.statusPIDC2 == True:
                    self.speedSetPointC2 = self.PID_C2(self.feedbackProcessVariableC2)
                    self.directionC2 = np.sign(self.speedSetPointC2)
                    demandSpeed = np.abs(self.speedSetPointC2)
                    self.setDirection("C2", self.directionC2)
                    self.setSpeed("C2", demandSpeed)
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

        
