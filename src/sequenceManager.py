from PySide6.QtCore import QObject, Signal
import logging
import numpy as np
import time
from simple_pid import PID
import sequenceManagerTestData
import copy
import sys

log = logging.getLogger(__name__)

class SequenceManager(QObject):
    updatePositionSetPointC1 = Signal(float)

    def __init__(self):
        super().__init__()
        self.command_index = 0
        self.commands_default = sequenceManagerTestData.commands2

    def run(self, device, commands=None):
        if commands:
            self.commands = copy.deepcopy(commands)
        else:
            self.commands = copy.deepcopy(self.commands_default)
        log.info("SequenceManager initialised.")
        log.warning(self.commands)
        self.command_index = 0
        if (
            device.running == True
            and device.motor_enabled_C1 == True
            and self.commands
        ):
            self.labels = {}
            self.device = device
            self.device.command_completed.connect(self.execute_next_command)
            # TODO decide on connecting commands
            #self.add_connecting_commands()

            self.device.sequence_running = True
            self.execute_next_command()

    def execute_next_command(self):
        log.info("Command running.")
        if self.command_index >= len(self.commands):
            self.device.sequence_running = False
            log.info("Sequence successfully completed.")
            self.device.command_completed.disconnect(self.execute_next_command)
            return
        command = self.commands[self.command_index]
        self.command_index += 1
        self.device.sequenceChannel = command["channel"]

        if command["variable"] == "Create Label":
            log.info("Creating label.")
            self.create_label(command)
            return
        
        if command["command"] == "Feedback":
            log.info("Running feedback command.")
            self.execute_feedback_command(command)
            return
        
        command = self.check_labels(command)
        

        if command["command"] == "Ramp":
            log.info("Running RAMP command.")
            setpoint_list = self.generate_ramp(
                command["amplitude"],
                command["offset"],
            )
            self.execute_linear_command(command, setpoint_list)

        elif command["command"] == "Triangle":
            log.info("Running TRIANGLE WAVE command.")
            setpoint_list = self.generate_triangle(
                command["amplitude"],
                command["repeat"],
                command["offset"],
            )
            self.execute_linear_command(command, setpoint_list)

        elif command["command"] == "Sine":
            log.info("Running SINE WAVE command.")
            setpoint_list, speed_function = self.generate_sine(
                command["amplitude"],
                command["period"],
                command["repeat"],
                command["offset"],
            )
            self.execute_timed_command(
                command, setpoint_list, speed_function, "position"
            )

        elif command["command"] == "Custom":
            log.info("Running CUSTOM command.")
            # TODO SWAP AWAT FROM EVAL THIS IS EVIL
            # TODO it will literally crash and die
            # TODO also sanitise input
            setpoint_list, speed_function = self.generate_custom(
                command["function"],
                command["max"],
                command["repeat"],
                command["offset"],
            )
            self.execute_timed_command(
                command, setpoint_list, speed_function, "time"
            )
            
        else:
            log.error("Invalid command type.")

    def generate_ramp(self, amplitude, offset=0):
        lower = offset
        upper = offset + amplitude
        setpoint_list = [lower, upper]
        return setpoint_list

    def generate_triangle(self, amplitude, repeat, offset):
        lower = offset - amplitude
        upper = offset + amplitude
        setpoint_list = [offset] + [upper, lower] * repeat + [offset]
        return setpoint_list

    def generate_sine(self, A, T, repeat, offset):
        lower = offset - A
        upper = offset + A
        setpoint_list = [offset] + [upper, lower] * repeat + [offset]
        f = 1 / T

        # Need a minimum speed to avoid it being too slow
        # TODO remove this if speed is changed to position based
        minimum_speed = 0.05
        # TODO might have to deconstruct this a bit
        speed_function = lambda t: max(
            minimum_speed,
            np.abs(2 * np.pi * A * f * np.cos(2 * np.pi * f * t)),
        )
        velocity = lambda x: max(
            minimum_speed, 0.95*2 * np.pi * f * np.sqrt(max(0, A**2 - (x-offset)**2))
        )
        return setpoint_list, velocity

    def generate_custom(self, function, max, repeat, offset):
        # TODO SWAP AWAT FROM EVAL THIS IS EVIL
        # TODO it will literally crash and die
        # TODO also sanitise input
        upper = offset + max
        setpoint_list = [offset, upper] * repeat
        speed_function = lambda t: eval(function)
        return setpoint_list, speed_function

    def execute_linear_command(self, command, setpoint_list):
        self.device.setpoint_list = setpoint_list
        self.device.speed_function_x = 0
        self.device.speed_function_t = 0
        self.device.set_speed_C1(command["rate"])
        self.device.setpoint_index = 0
        self.device.sequence_running = True
        self.device.current_setpoint = self.device.setpoint_list[
            self.device.setpoint_index
        ]
        self.device.direction_C1 = np.sign(
            self.device.position_process_variable_C1
            - self.device.current_setpoint
        )
        self.device.move_to_position_C1(self.device.current_setpoint)
        self.device.updatePositionSetPointC1.emit(self.device.current_setpoint)

    def execute_timed_command(
        self, command, setpoint_list, speed_function, type
    ):
        self.device.setpoint_list = setpoint_list
        if type == "time":
            self.device.speed_function_t = speed_function
        if type == "position":
            self.device.speed_function_x = speed_function
        self.device.setpoint_index = 0
        self.device.sequence_running = True
        self.device.initial_time = time.time()
        self.device.current_setpoint = self.device.setpoint_list[
            self.device.setpoint_index
        ]
        self.device.direction_C1 = np.sign(
            self.device.position_process_variable_C1
            - self.device.current_setpoint
        )
        self.device.move_to_position_C1(self.device.current_setpoint)
        self.device.updatePositionSetPointC1.emit(self.device.current_setpoint)
        pass

    def add_connecting_commands(self):
        i = 0
        number_of_commands = len(self.commands)
        while (i < number_of_commands) and (self.commands[i]["variable"] == "Create Label"):
            i += 1
        if i >= number_of_commands:
            return
        initial_value = self.commands[i]["offset"]
        current_pos = self.device.position_process_variable_C1
        

        commands_added = 1
        while i < number_of_commands - 1:
            command = self.commands[i]
            if command["variable"] == "Create Label":
                i += 1
                continue

            next_command = self.commands[i + 1]
            while next_command["variable"] == "Create Label":
                # If comparing to label, go next
                if i+2 >= number_of_commands:
                    return
                next_command = self.commands[i + 2]
                i += 1

            command_end_value = self.get_end_value(command)

            command_start_value = next_command["offset"]

            if command_end_value != command_start_value:
                log.info(
                    f"Adding a connecting command between {command['name']} and {next_command['name']}"
                )
                connecting_command = {
                    "name": f"CONNECTING COMMAND {commands_added}",
                    "device": command["device"],
                    "channel": command["channel"],
                    "variable": "Position",
                    "command": "Ramp",
                    "rate": 3.0,
                    "amplitude": command_start_value - command_end_value,
                    "trigger": "completion",
                    "offset": command_end_value,
                }
                commands_added += 1
                self.commands.insert(i + 1, connecting_command)
                i += 2
                continue
            i += 1
        if initial_value != 0:
            log.info("Adding a connecting command to the first command.")
            connecting_command = {
                "name": "INITIAL CONNECTING COMMAND",
                "device": self.commands[0]["device"],
                "channel": self.commands[0]["channel"],
                "variable": "Position",
                "command": "Ramp",
                "rate": 3.0,
                "amplitude": initial_value,
                "trigger": "completion",
                "offset": 0,
            }
            self.commands.insert(0, connecting_command)
        
        if current_pos != 0:
            log.info("Adding a connecting command to amplitude 0.")
            connecting_command = {
                "name": "ZERO CONNECTING COMMAND",
                "device": self.commands[0]["device"],
                "channel": self.commands[0]["channel"],
                "variable": "Position",
                "command": "Ramp",
                "rate": 3.0,
                "amplitude": -current_pos,
                "trigger": "completion",
                "offset": current_pos,
            }
            self.commands.insert(0, connecting_command)

    def get_end_value(self, command):
        if command["command"] == "Ramp":
            return command["offset"] + command["amplitude"]
        elif command["command"] == "Triangle":
            return command["offset"]
        elif command["command"] == "Sine":
            return command["offset"]
        elif command["command"] == "Custom":
            return command["offset"] + command["max"]
        else:
            log.error("Invalid command type.")
            return None
        
    def create_label(self, command):
        if command["name"] in self.labels.keys():
            log.error("Label already exists.")
            return
        current_pos = self.device.position_process_variable_C1
        self.labels[command["name"]] = current_pos
        log.info(f"Label {command['name']} created at {current_pos}.")

    def check_labels(self, command):
        if not command["amplitude"].lstrip("-").isdigit():
            mult = 1.0
            label_name = command["amplitude"]
            if label_name[0] == "-":
                label_name = label_name[1:]
                mult = -1.0
            if label_name in self.labels.keys():
                command["amplitude"] = mult*float(self.labels[label_name])
            else:
                log.error(f"Label {label_name} not found.")
                return command
        else:
            command["amplitude"] = float(command["amplitude"])
        if not command["offset"].lstrip("-").isdigit():
            mult = 1.0
            label_name = command["offset"]
            if label_name[0] == "-":
                label_name = label_name[1:]
                mult = -1.0
            if label_name in self.labels.keys():
                command["offset"] = mult*float(self.labels[label_name])
            else:
                log.error(f"Label {label_name} not found.")
                return command
        else:
            command["offset"] = float(command["offset"])
        return command

    def execute_feedback_command(self, command):
        self.device.setpoint_list = []
        self.device.sequence_feedback_C1 = command["feedback"]
        self.device.speed_function_x = 0
        self.device.speed_function_t = 0
        self.device.set_speed_C1(command["rate"])
        self.device.direction_C1 = np.sign(
            self.device.feedback_process_variable_C1
            - self.device.sequence_feedback_C1
        )
        self.device.jog_positive_on_C1()