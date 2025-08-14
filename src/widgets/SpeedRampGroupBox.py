from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QGridLayout
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QDoubleValidator

class SpeedRampGroupBox(QGroupBox):
    """
    Speed Ramp Control with single Start/Stop toggle button.

    Inputs:
      Target Speed (RPM)      : 0 .. 9999  (float, 3 dp)
      Speed Increment (RPM)   : 0 .. 9999 (float, 3 dp, magnitude only; direction is auto-determined)
      Step Interval (s)       : 0 < interval <= 9999 (float seconds, 3 dp)

    Signals:
      speedStep(float new_speed)  emitted each applied step (including final target)
      rampFinished()              emitted when ramp stops (completed or user stop)

    Usage:
      - Call set_current_speed(current_rpm) before starting (so direction logic works).
      - Optionally call matchJogButtonStyle(self.jog.jogPlusButton) after constructing to copy jog button styling.
    """
    speedStep = Signal(float)
    rampFinished = Signal()

    def __init__(self, title="Speed Ramp Control", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle(title)

        # Internal state
        self._current_speed: float = 0.0
        self._target: float = 0.0
        self._increment: float = 0.0
        self._active: bool = False
        self._max_rpm: float = 3000.0  # Default max RPM

        # Timer (ms resolution)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._apply_step)

        # Validators
        self._target_validator = QDoubleValidator(0.0, 9999.0, 3, self)
        self._target_validator.setNotation(QDoubleValidator.StandardNotation)

        self._increment_validator = QDoubleValidator(0.0, 9999.0, 3, self)
        self._increment_validator.setNotation(QDoubleValidator.StandardNotation)

        self._interval_validator = QDoubleValidator(0.0, 9999.0, 3, self)
        self._interval_validator.setNotation(QDoubleValidator.StandardNotation)

        # Inputs
        self.targetLineEdit = QLineEdit()
        self.targetLineEdit.setValidator(self._target_validator)
        self.targetLineEdit.setMaxLength(8)  # e.g. '9999.999'
        self.targetLineEdit.setPlaceholderText("")

        self.incrementLineEdit = QLineEdit()
        self.incrementLineEdit.setValidator(self._increment_validator)
        self.incrementLineEdit.setMaxLength(8)
        self.incrementLineEdit.setPlaceholderText("")

        self.intervalLineEdit = QLineEdit()
        self.intervalLineEdit.setValidator(self._interval_validator)
        self.intervalLineEdit.setMaxLength(8)
        self.intervalLineEdit.setPlaceholderText("")

        # Toggle button (will adopt jog button style via matchJogButtonStyle)
        self.toggleButton = QPushButton("Start")
        self.toggleButton.setCheckable(True)
        self.toggleButton.setObjectName("speedRampToggle")
        self.toggleButton.toggled.connect(self._on_toggle)

        # Layout
        layout = QGridLayout()
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(4)

        layout.addWidget(QLabel("Target Speed (RPM)"),    0, 0)
        layout.addWidget(self.targetLineEdit,             0, 1)
        layout.addWidget(QLabel("Speed Increment (RPM)"), 1, 0)
        layout.addWidget(self.incrementLineEdit,          1, 1)
        layout.addWidget(QLabel("Step Interval (s)"),     2, 0)
        layout.addWidget(self.intervalLineEdit,           2, 1)
        layout.addWidget(self.toggleButton,               3, 0, 1, 2)

        self.setLayout(layout)

        # Size controls
        self.setFixedSize(330, 320)

    # Public API -------------------------------------------------------------

    def set_current_speed(self, speed: float):
        """Set starting speed (call this whenever external speed changes)."""
        self._current_speed = speed

    def set_max_rpm(self, value: float):
        """Set maximum allowed RPM. Ramp will never exceed this."""
        try:
            self._max_rpm = float(value)
        except (TypeError, ValueError):
            return
        # If running, enforce new cap immediately
        if self._active:
            # Clamp target to new cap
            self._target = min(self._target, self._max_rpm)
            # If already beyond cap and increment is positive, stop at cap
            if self._increment > 0 and self._current_speed >= self._max_rpm:
                self._current_speed = self._max_rpm
                self.speedStep.emit(self._current_speed)
                self.stop_ramp()

    # Internal ---------------------------------------------------------------

    @Slot(bool)
    def _on_toggle(self, checked: bool):
        if checked:
            self.toggleButton.setText("Stop")
            started = self.start_ramp()
            if not started:
                # revert if failed to start
                self.toggleButton.blockSignals(True)
                self.toggleButton.setChecked(False)
                self.toggleButton.blockSignals(False)
                self.toggleButton.setText("Start")
        else:
            self.toggleButton.setText("Start")
            self.stop_ramp()

    def start_ramp(self) -> bool:
        """Validate inputs and start ramp timer. Returns True if ramp started."""
        if self._active:
            return True
        try:
            t_txt = self.targetLineEdit.text().strip()
            inc_txt = self.incrementLineEdit.text().strip()
            intv_txt = self.intervalLineEdit.text().strip()
            if not t_txt or not inc_txt or not intv_txt:
                return False
            target = float(t_txt)
            inc_mag = abs(float(inc_txt))
            interval_s = float(intv_txt)
        except ValueError:
            return False

        # Validation
        if not (0.0 <= target <= 9999.0):
            return False
        if interval_s <= 0.0 or interval_s > 9999.0:
            return False
        if inc_mag < 1e-12:
            return False
        if inc_mag > 9999.0:
            return False
        
        # Enforce max RPM cap
        effective_target = min(target, self._max_rpm)

        # Increment is magnitude-only; assign sign from direction to target
        inc = inc_mag if effective_target >= self._current_speed else -inc_mag

        # Already satisfied
        if (inc > 0 and self._current_speed >= effective_target) or (inc < 0 and self._current_speed <= effective_target):
            self._current_speed = effective_target
            self.speedStep.emit(effective_target)
            return False

        self._target = effective_target
        self._increment = inc
        self._active = True

        interval_ms = max(1, int(round(interval_s * 1000)))
        self._timer.start(interval_ms)

        # Immediate first step
        self._apply_step()
        return True

    def stop_ramp(self):
        """Stop ramp (user or completion)."""
        if self._timer.isActive():
            self._timer.stop()
        was_active = self._active
        self._active = False
        if self.toggleButton.isChecked():
            self.toggleButton.blockSignals(True)
            self.toggleButton.setChecked(False)
            self.toggleButton.blockSignals(False)
            self.toggleButton.setText("Start")
        if was_active:
            self.rampFinished.emit()

    def _apply_step(self):
        """Perform one increment toward target."""
        if not self._active:
            return

        # Pre-check completion
        if (self._increment > 0 and self._current_speed >= self._target) or \
           (self._increment < 0 and self._current_speed <= self._target):
            self.stop_ramp()
            return

        next_speed = self._current_speed + self._increment
        if self._increment > 0:
            # Respect both dynamic max cap and target
            cap = min(self._target, self._max_rpm)
            if next_speed >= cap:
                next_speed = cap
        else:
            if next_speed <= self._target:
                next_speed = self._target

        self._current_speed = next_speed
        self.speedStep.emit(self._current_speed)

        # Post-check
        if self._current_speed == self._target or \
           (self._increment > 0 and self._current_speed >= self._target) or \
           (self._increment < 0 and self._current_speed <= self._target):
            self.stop_ramp()