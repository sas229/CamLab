from PySide6.QtCore import QObject, Signal, Slot
import logging
from labjack import ljm
import numpy as np
import time
import sys
from time import sleep
from simple_pid import PID
import serial


log = logging.getLogger(__name__)

class Press(QObject):
    emitData = Signal(str, np.ndarray)
    updateOffsets = Signal(str, list, list)
    updatePositionSetPointC1 = Signal(float)
    updateFeedbackSetPointC1 = Signal(float)
    updatePositionProcessVariableC1 = Signal(float)
    updateFeedbackProcessVariableC1 = Signal(float)
    updateConnectionIndicatorC1 = Signal(bool)
    updateLimitIndicatorC1 = Signal(bool)
    updateRunningIndicator = Signal(bool)
    updateSpeedC1 = Signal(float)
    updateEnablePIDControlC1 = Signal(bool)

    def __init__(self, name, id, connection):
        super().__init__()
        self.type = "Press"
        self.name = name
        self.id = id 
        self.connection = None
        self.handle = None

        # Configure the serial connections.
        # self.ser = serial.Serial(
        # port='COM4',
        # baudrate=57600,
        # parity=serial.PARITY_NONE,
        # stopbits=serial.STOPBITS_ONE,
        # bytesize=serial.EIGHTBITS)

        # Variables
        self.data = np.zeros(2)
        self.CPR = 6400
        self.KP_C1 = 0.0
        self.KI_C1 = 0.0
        self.KD_C1 = 0.0
        self.status_PID_C1 = False
        self.enabled_C1 = False
        self.motor_enabled_C1 = False
        self.feedback_C1 = False
        self.feedback_index_C1 = None
        self.running = False
        self.jog_C1 = False
        self.moving_C1 = False
        # self.count_C1 = 0
        # self.pulses_C1 = 0
        self.direction_C1 = 1
        self.position_process_variable_C1 = 0
        self.speed_C1 = 3
        self.initial_speed_C1 = 0.0
        self.feedback_setpoint_C1 = 0
        self.feedback_process_variable_C1 = 0
        self.feedback_left_limit_C1 = -100
        self.feedback_right_limit_C1 = 100
        # self.previous_count_C1 = 0
        # self.previous_pulses_C1 = 0
        # self.counts_per_unit_C1 = 32000
        # self.pulses_per_unit_C1 = 160
        self.position_setpoint_C1 = 0
        self.position_left_limit_C1 = 0
        self.position_right_limit_C1 = 0
        self.position_left_limit_status_C1 = False
        self.position_right_limit_status_C1 = False
        # self.max_rpm = 4000
        self.current_data = np.empty(0)
        self.sequence_running = False
        self.move_to_demanded_position = False
        self.is_stopped = True

        self.open_connection()

        # Instantiate PID controllers.
        self.PID_C1 = PID()

    # def open_serial_connection():
    #     """Connect to the device using the serial port."""
    #     try:
    #         ser = serial.Serial(
    #                 port=comport,
    #                 baudrate=57600,
    #                 parity=serial.PARITY_NONE,
    #                 stopbits=serial.STOPBITS_ONE,
    #                 bytesize=serial.EIGHTBITS
    #             )
    #           # Send check status command and check response...
    #     except Exception:
    #         e = sys.exc_info()[1]
    #         log.warning(e)

    @Slot()
    def run_sequence(self):
        # Hacky code to do a simple sequence on control channel C1 - only for Jonathan's usage!
        if self.running == True and self.motor_enabled_C1 == True:
            self.sequenceChannel = "C1"
            self.setpoint_list = [50, 0, 50, 0, 50, 0, 50, 0, 50, 0]
            self.setpoint_index = 0
            self.sequence_running = True
            self.current_setpoint = self.setpoint_list[self.setpoint_index]
            self.direction_C1 = np.sign(self.position_process_variable_C1 - self.current_setpoint)
            self.move_to_position_C1(self.current_setpoint)
            self.updatePositionSetPointC1.emit(self.current_setpoint)
            log.info("Running sequence.")

    def check_setpoint_C1(self):
        try:
            completed = ljm.eReadName(self.handle, "DIO4_EF_READ_A")
            target = ljm.eReadName(self.handle, "DIO4_EF_READ_B")
            if target == completed:
                log.info("Moving to next setpoint in sequence.")
                self.setpoint_index += 1
                if self.setpoint_index < len(self.setpoint_list):
                    self.current_setpoint = self.setpoint_list[self.setpoint_index]
                    self.move_to_position_C1(self.current_setpoint)
                    self.updatePositionSetPointC1.emit(self.current_setpoint)
                else:
                    log.info("Sequence finished.")
                    self.sequence_running = False
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        
    def set_enabled_C1(self, value):
        self.enabled_C1 = value

    @Slot()
    def initialise(self):
        #  Initialise device.
        self.set_speed_limit()
        self.set_speed_C1(self.speed_C1)
        # self.initialise_settings()
        # self.check_limits()
        

    def get_press_response(self, signal):

        ser = self.connection
        ser.write(bytes(signal + '\r', "utf-8"))
        out = ''
        time.sleep(0.02)

        while ser.inWaiting() > 0:

            out += ser.read(1).decode("utf-8")

        if out == '':
            out = "No response!"

        return out

    @Slot(str)
    def set_enable_C1(self, value):
        """Set enable state for control channel C1."""
    
        try:
            self.check_connections()
            if value ==  True:
                self.position_setpoint_C1 = self.position_process_variable_C1
                self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
                self.motor_enabled_C1 = True
            else:
                self.motor_enabled_C1 = False

        except ljm.LJMError:
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
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def turn_on_PWM_C1(self):
        """PWM output on control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_ENABLE"]
            aValues = [0, 0, 0, 1, self.width_C1, 1]
            numFrames = len(aNames)
            ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            log.info("Pulse width modulation configured on control channel C1 on device named {device}.".format(device=self.name))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def pulse_out_C1(self, pulses):
        """Setup pulse out on control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            aNames = ["DIO4_EF_ENABLE", "DIO4", "DIO4_EF_INDEX", "DIO4_EF_OPTIONS", "DIO4_EF_CONFIG_A", "DIO4_EF_CONFIG_C", "DIO4_EF_ENABLE"]
            aValues = [0, 0, 2, 1, self.width_C1, pulses, 1]
            numFrames = len(aNames)
            ljm.eWriteNames(self.handle, numFrames, aNames, aValues)
            log.info("Pulse out configured on control channel C1 on device named {device}.".format(device=self.name))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
    

    def turn_off_PWM_C1(self):
        """Turn control channel C1 PWM off."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def set_PID_tunings_C1(self):
        """Set PID tunings for control channel C1."""
        self.PID_C1.tunings = (self.KP_C1, self.KI_C1, self.KD_C1)
        log.info("PID tunings updated for control channel C1 on {device}.".format(device=self.name))

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
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def check_connection_C1(self):
        """Check connection to control device on channel C1."""
        try:
            status_press = self.get_press_response('I21TSF')
            if len(status_press) == 14 and status_press[:4] == "i21t":
                self.connectedC1 = True
                self.updateConnectionIndicatorC1.emit(self.connectedC1)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)
        


    def check_connections(self):
        """Check connections to control devices."""
        self.check_connection_C1()
        # self.check_connection_C2()

    def set_speed_limit(self):
        """Set speed limit for motors."""
        self.speed_limit = 99.99999
        log.info("Speed limit set on {device} for {speed} mm/min.".format(device=self.name, speed=self.speed_limit))

    @Slot(bool)
    def set_PID_control_C1(self, value):
        """Set PID state for control channel C1."""
        self.status_PID_C1 = value
        if value == True:
            self.PID_C1.reset()
            self.set_speed_limit()
            self.PID_C1.output_limits = (-self.speed_limit, self.speed_limit)
            self.PID_C1.setpoint = self.feedback_setpoint_C1
            self.PID_C1.set_auto_mode(True, last_output=0.001)
            # self.turn_on_PWM_C1()
            log.info("PID control for control channel C1 on " + self.name + " turned on.")
        else:
            self.position_setpoint_C1 = self.position_process_variable_C1
            self.PID_C1.set_auto_mode(False)
            self.updatePositionSetPointC1.emit(self.position_setpoint_C1)
            self.stop_press()
            log.info("PID control for control channel C1 on " + self.name + " turned off.")


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

    @Slot(bool)
    def set_pom_C1(self, value):
        self.PID_C1.proportional_on_measurement = value 
        log.info("Proportional on measurement toggled for control channel C1.")


    @Slot(float)
    def set_feedback_setpoint_C1(self, setpoint):
        """Set feedback setpoint for channel C1."""
        self.feedback_setpoint_C1 = setpoint
        self.PID_C1.setpoint = setpoint
        
        log.info("Feedback setpoint on control channel C1 on {device} set to {setpoint}.".format(device=self.name, setpoint=setpoint))

    def set_feedback_channel_C1(self, feedback, tot_chann_enabled):
        self.feedback_index_C1 = feedback
        self.tot_chann_enabled = tot_chann_enabled
        if self.feedback_index_C1 != None:
            self.feedback_C1 = True
        log.info("Feedback channel index set on control channel C1 on {device}.".format(device=self.name))


    def check_limits(self, status_code):
        try:
            # Refresh connection.
            # self.handle = ljm.open(7, self.connection, self.id)
            self.limit_C1 = False
            self.maximumLimitC1 = False
            self.minimumLimitC1 = False

            if status_code == "5":
                self.maximumLimitC1 = True
            
            if status_code == "6":
                self.minimumLimitC1 = True

            # Turn on indicator if on limits.
            if self.minimumLimitC1 == True or self.maximumLimitC1 == True:
                self.limit_C1 = True

            # Check position limits.
            if self.position_process_variable_C1 <= self.position_left_limit_C1 and self.is_stopped == False and self.direction_C1 == -1:
                self.stop_command_C1()
                if self.status_PID_C1 == True:
                    self.updateEnablePIDControlC1.emit(False)
                    # self.set_PID_control_C1(False)
                self.limit_C1 = True
                
            if self.position_process_variable_C1 >= self.position_right_limit_C1 and self.is_stopped == False and self.direction_C1 == 1:
                self.stop_command_C1()
                if self.status_PID_C1 == True:
                    self.updateEnablePIDControlC1.emit(False)
                    # self.set_PID_control_C1(False)
                self.limit_C1 = True

            # Check feedback limits.
            if self.feedback_process_variable_C1 <= self.feedback_left_limit_C1 and self.is_stopped == False and self.direction_C1 == -1:
                self.stop_command_C1()
                self.limit_C1 = True
            if self.feedback_process_variable_C1 >= self.feedback_right_limit_C1 and self.is_stopped == False and self.direction_C1 == 1:
                self.stop_command_C1()
                self.limit_C1 = True

            # Set indicator.
            if self.limit_C1 == True:
                self.updateLimitIndicatorC1.emit(True)
            else:
                self.updateLimitIndicatorC1.emit(False)

        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    def set_position_C1(self, value):
        """Set position for control C1."""
        self.position_process_variable_C1 = value
        self.position_setpoint_C1 = value


    @Slot(bool)
    def set_running(self, running):
        """Set running boolean."""
        self.running = running
        self.updateRunningIndicator.emit(self.running)

    @Slot()
    def stop_command_C1(self):
        """Stop command for control channel C1."""
        try:
            # self.handle = ljm.open(7, self.connection, self.id)
            # self.turn_off_PWM_C1()
            self.stop_press()
            # sleep(0.1)
            # self.get_position_C1()
            self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
            log.info("Control stopped on device {device} control channel C1.".format(device=self.name))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


    @Slot()
    def zero_position_C1(self):
        """Zero position command for control channel C1."""
        try:
            self.position_process_variable_C1 = 0
            self.position_setpoint_C1 = 0
            self.previous_count_C1 = 0
            self.updatePositionSetPointC1.emit(self.position_process_variable_C1) 
            self.updatePositionProcessVariableC1.emit(self.position_process_variable_C1)
            # ljm.eReadName(self.handle, "DIO1_EF_READ_A_AND_RESET")
            log.info("Position zeroed on device " + self.name + " control channel C1.")
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


    @Slot(float)
    def update_position_left_limit_C1(self, value):
        """Update position left limit on control channel C1."""
        self.position_left_limit_C1 = value


    @Slot(float)
    def update_position_right_limit_C1(self, value):
        """Update position right limit on control channel C1."""
        self.position_right_limit_C1 = value


    @Slot(float)
    def update_feedback_left_limit_C1(self, value):
        """Update feedback left limit on control channel C1."""
        self.feedback_left_limit_C1 = value


    @Slot(float)
    def update_feedback_right_limit_C1(self, value):
        """Update feedback right limit on control channel C1."""
        self.feedback_right_limit_C1 = value


    @Slot(bool)
    def update_position_left_limit_status_C1(self, status):
        """Update position left limit status on control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.position_left_limit_status_C1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


    @Slot(bool)
    def update_position_right_limit_status_C1(self, status):
        """Update position right limit status on control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            self.position_right_limit_status_C1 = status
            if status == True:
                ljm.eWriteName(self.handle, "DIO4_EF_ENABLE", 0)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)


    @Slot(float)
    def set_speed_C1(self, speed=0.0):
        """Set speed on control channel C1."""
        # Convert mm/s to mm/min
  
        self.speed_C1 = speed

        if self.speed_C1 > 99.99999:

            self.speed_C1 = 99.99999
            log.warning("Speed cannot exceed 99.99999")
        
        self.set_press_speed_signal()

    def set_press_speed_signal(self):
        
        speed = self.speed_C1
        speed_string = str(int(speed*10**5))
        if speed < 10:
            
            speed_string_signal = "I21TSP0"+ speed_string
        
        else:
            speed_string_signal= "I21TSP"+speed_string
        
        # if self.connection != None:
        out = self.get_press_response(speed_string_signal)

        log.info("Speed on control channel C1 set to " + "{:.5f}".format(speed))

        if self.status_PID_C1 == True or self.move_to_demanded_position == True:

            if self.direction_C1 == 1:
                self.move_press_up()

            elif self.direction_C1 == -1:
                self.move_press_down()
            

    @Slot(str)
    def jog_positive_on_C1(self):
        """Turn positive jog on for control channel C1."""
        # if self.running == True and self.maximumLimitC1 == False and self.motor_enabled_C1 == True:
        if self.running == True and self.motor_enabled_C1 == True:
        # Check status of press
            if self.position_process_variable_C1 <= self.position_right_limit_C1:
                # Set direction.
                self.direction_C1 = 1
                self.jog_C1 = True
                self.move_press_up()

                log.info("Jog positive turned on for control channel C1 on {device}.".format(device=self.name))

    @Slot(str)
    def jog_negative_on_C1(self):
        """Turn negative jog on for control channel C1."""
        # if self.running == True and self.maximumLimitC1 == False and self.motor_enabled_C1 == True:
        if self.running == True and self.motor_enabled_C1 == True:
            #Check status of press
            if self.position_process_variable_C1 >= self.position_left_limit_C1:
                # Set direction.
                self.direction_C1 = -1
                self.jog_C1 = True
                self.move_press_down()

                log.info("Jog negative turned on for control channel C1 on {device}.".format(device=self.name))


    @Slot(str)
    def jog_positive_off_C1(self):
        """Turn positive jog off for control channel C1."""
        if self.jog_C1 == True:
            # self.handle = ljm.open(7, self.connection, self.id)
            self.jog_C1 = False
            self.stop_press()
            # sleep(0.1)
            # self.get_position_C1()
            # self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
            log.info("Jog positive turned off for control channel C1 on {device}.".format(device=self.name))

    @Slot(str)
    def jog_negative_off_C1(self):
        """Turn negative jog off for control channel C1."""
        if self.jog_C1 == True:
            # self.handle = ljm.open(7, self.connection, self.id)
            self.jog_C1 = False
            self.stop_press()
            # sleep(0.1)
            # self.get_position_C1()
            # self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
            log.info("Jog positive turned off for control channel C1 on {device}.".format(device=self.name))

    def move_press_up(self):

        self.direction_C1 = 1
        self.is_stopped = False
        up_press_signal = "I21TUP"
        out = self.get_press_response(up_press_signal)
    
    def move_press_down(self):
        
        self.direction_C1 = -1
        self.is_stopped = False
        down_press_signal = "I21TDN"
        out = self.get_press_response(down_press_signal)
    
    def stop_press(self):

        self.is_stopped = True
        stop_press_signal = "I21THT"
        out = self.get_press_response(stop_press_signal)
        self.move_to_demanded_position = False


    @Slot()
    def updateControlPanelC1(self):
        """Update control panel for channel C1."""
        if self.jog_C1 == True: 
            self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
        self.updatePositionProcessVariableC1.emit(self.position_process_variable_C1)
        if self.feedback_index_C1 != None:
            self.updateFeedbackProcessVariableC1.emit(self.feedback_process_variable_C1)
            if self.status_PID_C1 == True:
                self.updateSpeedC1.emit(self.speed_C1)
                self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
            elif self.status_PID_C1 == False:
                self.updateFeedbackSetPointC1.emit(self.feedback_process_variable_C1) 

    
    @Slot(str, float)
    def move_to_position_C1(self, position):
        """Move to demanded position for channel C1."""
        if self.running == True and self.motor_enabled_C1 == True:
            # Calculate increment.
            currentPosition = self.position_process_variable_C1
            increment = position - currentPosition
            # Set direction.
            if increment > 0:
                self.direction_C1 = 1
                self.move_press_up()

            elif increment < 0:   
                self.direction_C1 = -1
                self.move_press_down()

            # self.set_direction_C1(self.direction_C1)
            self.position_setpoint_C1 = position
            self.move_to_demanded_position = True

            # Reset counters.
            # self.count_C1 = 0
            # self.previous_count_C1 = 0
            # self.pulses_C1 = 0
            # self.previous_pulses_C1 = 0
            # self.reset_pulse_counter_C1()
            # # Turn on PWM.
            # pulses = int(abs(increment*self.counts_per_unit_C1))
            # self.pulse_out_C1(pulses)
            # self.moving_C1 = True

    def check_position_C1_for_demand(self):

        if self.direction_C1 == 1:
            if self.position_process_variable_C1 >= self.position_setpoint_C1:
                self.stop_press()
        
        elif self.direction_C1 == -1:
            if self.position_process_variable_C1 <= self.position_setpoint_C1:
                self.stop_press()


    def set_direction_C1(self, direction):
        """Set motor direction on control channel C1."""
        try:
            self.handle = ljm.open(7, self.connection, self.id)
            if direction == 1:
                ljm.eWriteName(self.handle, "EIO1", 0)
            elif direction == -1:
                ljm.eWriteName(self.handle, "EIO1", 1)
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)        


    # def read_pulses_C1(self):
    #     """Read pulses for control channel C1."""
    #     try:
    #         self.handle = ljm.open(7, self.connection, self.id)
    #         self.pulses_C1 = ljm.eReadName(self.handle, "DIO1_EF_READ_A")
    #     except ljm.LJMError:
    #         ljme = sys.exc_info()[1]
    #         log.warning(ljme) 
    #     except Exception:
    #         e = sys.exc_info()[1]
    #         log.warning(e)


    def get_position_C1(self, current_speed_C1):
        """Get position of control channel C1."""
        # # Read pulses.
        # self.read_pulses_C1()    

        # # Check motor status by comparing pulses count output with pulses returned.
        # if self.pulses_C1 == 0:
        #     incrementPulses = 0
        # else:
        #     incrementPulses = (self.pulses_C1-self.previous_pulses_C1)/self.pulses_per_unit_C1
        # self.previous_pulses_C1 = self.pulses_C1
        increment_position = np.trapz(y = [self.initial_speed_C1, current_speed_C1], dx = (1/self.controlRate)/60 ) # Conver s in min
        # Increment position process variable.
        if self.direction_C1 == 1:
            self.position_process_variable_C1 += increment_position
        elif self.direction_C1 == -1:
            self.position_process_variable_C1 -= increment_position            


    def check_position_C1(self):
        """Check position for control channel C1."""
        # If moving under jog or PID control, stop if at limit.
        if self.jog_C1 == True or self.status_PID_C1 == True:
            if self.direction_C1 == -1 and self.position_process_variable_C1 < self.position_left_limit_C1:
                self.turn_off_PWM_C1()
                self.jog_C1 = False
                sleep(0.1)
                self.get_position_C1()
                self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
            elif self.direction_C1 == 1 and self.position_process_variable_C1 > self.position_right_limit_C1:
                self.turn_off_PWM_C1()
                self.jog_C1 = False
                sleep(0.1)
                self.get_position_C1()
                self.updatePositionSetPointC1.emit(self.position_process_variable_C1)
        

    # def configure_pulse_counters(self):
    #     """Setup pulse counters. Set to mode 2 which counts both rising and falling edges. 
    #     400 microsecond debounce period, which is just less than the time between rising and
    #     falling edges for 16 PPR at 4000 RPM."""
    #     self.handle = ljm.open(7, self.connection, self.id)
    #     aNamesC1 = ["DIO1_EF_ENABLE", "DIO1_EF_INDEX", "DIO1_EF_CONFIG_A", "DIO1_EF_CONFIG_B", "DIO1_EF_ENABLE"]
    #     aValues = [0, 9, 400, 2, 1]
    #     numFrames = 5
    #     ljm.eWriteNames(self.handle, numFrames, aNamesC1, aValues)


    #     log.info("Pulse counters configured on device named " + self.name + ".")

    # def configure_ADC(self):
    #     """Set the ADC settings."""
    #     self.handle = ljm.open(7, self.connection, self.id)
    #     names = ["AIN_ALL_RANGE", "AIN_ALL_RESOLUTION_INDEX", "AIN_ALL_SETTLING_US"]
    #     aValues = [10, 2, 0] # No amplification; 16.5 effective bits; auto settling time.
    #     numFrames = len(names)
    #     ljm.eWriteNames(self.handle, numFrames, names, aValues) 

    def set_acquisition_variables(self, controlRate):
        """Set the acquisition variables."""
        # self.channels = channels
        # self.addresses = addresses
        # self.dataTypes = dataTypes
        # self.slopes = np.asarray(slopes)
        # self.offsets = np.asarray(offsets)
        # self.autozero = np.asarray(autozero)
        # self.numFrames = len(self.addresses)
        self.controlRate = controlRate

    def open_connection(self):
        """Method to open a device connection."""
        # try:
        #     self.handle = ljm.open(7, self.connection, self.id)
        #     log.info("Connected to {name}.".format(name=self.name))
        # except ljm.LJMError:
        #     ljme = sys.exc_info()[1]
        #     log.warning(ljme) 
        # except Exception:
        #     e = sys.exc_info()[1]
        #     log.warning(e)
        if self.connection == None:
            self.connection = serial.Serial(
            port='COM4',
            baudrate=57600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS)

    def close_connection(self):
        """Method to close the device connection."""
        try:
            self.connection.close()
            self.connection = None
            
            log.info("Disconnected from {name}.".format(name=self.name))
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    # def initialise_settings(self):
    #     """Method to initialise the device."""
    #     if self.handle != None:
    #         try:
    #             self.configure_ADC()
    #             self.configure_pulse_counters()
    #             self.set_speed_C1(self.speed_C1)
    #             self.enabled_C1 = False
    #         except ljm.LJMError:
    #             ljme = sys.exc_info()[1]
    #             log.warning(ljme)
    #         except Exception:
    #             e = sys.exc_info()[1]
    #             log.warning(e)

    def load_lua_script(self):
        """Method to load the Lua failsafe script into the device."""
        try:
            lua =(
                "-- Declarations.\n"
                "failsafe = 0\n"
                "-- Functions.\n"
                "local checkInterval = LJ.CheckInterval\n"
                "local read = MB.R\n"
                "local write = MB.W\n"
                "-- Check the failsafe register every 1000ms.\n"
                "LJ.IntervalConfig(0, 1000)\n"
                "-- Main loop.\n"
                "while true do\n"
                "   if checkInterval(0) then\n"
                "       -- Check USER_RAM for communications boolean.\n"
                "       failsafe = read(46180, 0)\n"
                "       if failsafe == 1 then\n"
                "           -- Communication confirmed. Reset register.\n"
                "           write(46180, 0, 0)\n"
                "       else\n"
                "           -- Communication lost. Stop output movement.\n"
                "           write(44008, 1, 0)\n"
                "           write(44010, 1, 0)\n"
                "       end\n"
                "   end\n"
                "end\n"
                )
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

            # Execute the Lua script.
            ljm.eWriteName(self.handle, "LUA_RUN", 1)
            log.info("Lua script executed.")
        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot(np.ndarray)
    def get_latest_data(self, latest_data):

        if self.feedback_C1 == True:
            self.current_data = latest_data[0][:self.tot_chann_enabled]          

    def update_PID_C1(self):
        """Update PID on control channel C1."""
        self.feedback_process_variable_C1 = self.current_data[self.feedback_index_C1]
        
        if self.status_PID_C1 == True:
            self.speedSetPointC1 = self.PID_C1(self.feedback_process_variable_C1)
            self.direction_C1 = np.sign(self.speedSetPointC1)
            demandSpeed = np.abs(self.speedSetPointC1)
            # self.set_direction_C1(self.direction_C1)
            self.set_speed_C1(demandSpeed)


    def send_data(self):
        """Send output data."""
        # Assemble output data for each control channel with or without feedback.
        if self.feedback_C1 == False:
            self.data_C1 = np.hstack((self.position_setpoint_C1, self.position_process_variable_C1, int(self.direction_C1), self.speed_C1))
        elif self.feedback_C1 == True:
            self.data_C1 = np.hstack((self.position_setpoint_C1, self.position_process_variable_C1, int(self.direction_C1), self.speed_C1, self.feedback_setpoint_C1, self.feedback_process_variable_C1))

        # If control channel enabled, concatenate data.
        # if self.enabled_C1 == True:
        #     if self.current_data.size == 0:
                
        #         self.current_data = self.data_C1
        #     else:
                
        #         self.current_data = np.concatenate((self.current_data, self.data_C1))

        self.data = self.data_C1
        # Emit data signal.
        self.emitData.emit(self.name, np.atleast_2d(self.data))    

    def process(self):
        """Method to process timed commands."""
        try:
            # self.check_position_C1()
            
            #Send a signal to the press asking for its status I21TSF and then decompose the signal recieved to get direction and speed of press
            status_press_signal = "I21TSF"
            status_press = self.get_press_response(status_press_signal)

            if status_press == "No response!":
                print(status_press)
                self.stop_press()

            #status code 0 = Stop, 1 = Up, 2 = Down, 3 = FastUp, 4 = FastDown, 5 = UpLimit, 6 = DownLimit (4 and 5 not used)
            if len(status_press) == 14:
                status_code = status_press[4]
                
                if self.is_stopped == False: # If the press is  moving then do  check the limits
                    self.check_limits(status_code)
                    
                current_speed_C1 = status_press[5:]
                current_speed_C1 = current_speed_C1.replace(".","")
                current_speed_C1 = float(current_speed_C1)/10**5
            else:
                current_speed_C1 = self.initial_speed_C1

            self.get_position_C1(current_speed_C1)
            self.initial_speed_C1 = current_speed_C1
            
            

            if self.jog_C1 == False and self.status_PID_C1 == False:
                self.check_position_C1_for_demand()
            
            # Check setpoint.
            # if self.sequence_running == True:
            #     self.check_setpoint_C1()
            # If feedback is available.
            
            if self.feedback_C1 == True and self.current_data.size!=0:
                
                self.update_PID_C1()
            
            self.send_data()

            # Concatenate output data.
            

        except ljm.LJMError:
            ljme = sys.exc_info()[1]
            log.warning(ljme) 
        except Exception:
            e = sys.exc_info()[1]
            log.warning(e)

    @Slot()
    def recalculate_offsets(self):
        """Method to autozero channels as required by the configuration."""
        # Autozero as required.
        adjustOffsets = (self.raw-self.offsets)*self.autozero
        self.offsets = self.offsets + adjustOffsets

        # Update the device configuration.
        self.updateOffsets.emit(self.name, self.channels, self.offsets.tolist())
        log.info("Autozero applied to device.")

        
