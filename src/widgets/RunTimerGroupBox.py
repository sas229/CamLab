from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QGridLayout, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy
from PySide6.QtCore import Signal, Slot, QTimer, Qt
from PySide6.QtGui import QIntValidator

class RunTimerGroupBox(QGroupBox):
    """
    Run duration timer (HH:MM:SS) for Speed mode.
    Blank (or total == 0) => indefinite.
    Emits:
      durationChanged(int total_seconds)
      countdownStarted(int remaining_seconds)
      countdownTick(int remaining_seconds)
      countdownCanceled()
      countdownFinished()
    """
    durationChanged = Signal(int)
    countdownStarted = Signal(int)
    countdownTick = Signal(int)
    countdownCanceled = Signal()
    countdownFinished = Signal()

    def __init__(self, title="Run Timer", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle(title)

        self._set_duration = 0        # armed duration (seconds, 0 = indefinite)
        self._remaining = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        # Inputs
        self.hoursLineEdit = QLineEdit()
        self.hoursLineEdit.setPlaceholderText("- -")
        self.hoursLineEdit.setValidator(QIntValidator(0, 999))
        self.hoursLineEdit.setMaxLength(3)

        self.minutesLineEdit = QLineEdit()
        self.minutesLineEdit.setPlaceholderText("- -")
        self.minutesLineEdit.setValidator(QIntValidator(0, 999))
        self.minutesLineEdit.setMaxLength(3)

        self.secondsLineEdit = QLineEdit()
        self.secondsLineEdit.setPlaceholderText("- -")
        self.secondsLineEdit.setValidator(QIntValidator(0, 999))
        self.secondsLineEdit.setMaxLength(3)

        # Countdown label
        self.countdownLabel = QLabel("Indefinite")
        self.countdownLabel.setObjectName("runTimerCountdownLabel")

        # Cancel button
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.cancel_countdown)
        self.cancelButton.setEnabled(False)

        # Top grid layout
        topGrid = QGridLayout()
        topGrid.setContentsMargins(12, 12, 12, 0)
        topGrid.setHorizontalSpacing(32)
        topGrid.setVerticalSpacing(4)

        # Labels (row 0)
        topGrid.addWidget(QLabel("Hours"),   0, 0, alignment=Qt.AlignHCenter)
        topGrid.addWidget(QLabel("Minutes"), 0, 1, alignment=Qt.AlignHCenter)
        topGrid.addWidget(QLabel("Seconds"), 0, 2, alignment=Qt.AlignHCenter)

        # Inputs (row 1)
        topGrid.addWidget(self.hoursLineEdit,   1, 0, alignment=Qt.AlignHCenter)
        topGrid.addWidget(self.minutesLineEdit, 1, 1, alignment=Qt.AlignHCenter)
        topGrid.addWidget(self.secondsLineEdit, 1, 2, alignment=Qt.AlignHCenter)

        for le in (self.hoursLineEdit, self.minutesLineEdit, self.secondsLineEdit):
            le.setFixedWidth(100)
            le.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Bottom of the widget
        bottomRow = QHBoxLayout()
        bottomRow.addWidget(QLabel("Remaining:"))
        bottomRow.addWidget(self.countdownLabel, 1)
        bottomRow.addWidget(self.cancelButton)

        # Main Layout
        outer = QVBoxLayout()
        outer.addStretch(1)        # flexible space at the top
        outer.addLayout(topGrid)
        outer.addStretch(1)        # flexible space between topGrid and bottomRow
        outer.addLayout(bottomRow)
        self.setLayout(outer)

        # Size controls
        self.setFixedSize(450, 320)

        # Enter key arms duration
        self.hoursLineEdit.returnPressed.connect(self._arm_from_fields)
        self.minutesLineEdit.returnPressed.connect(self._arm_from_fields)
        self.secondsLineEdit.returnPressed.connect(self._arm_from_fields)

    def _parse_field(self, le: QLineEdit):
        txt = le.text().strip()
        if not txt:
            return None
        try:
            return int(txt)
        except ValueError:
            return None

    @Slot()
    def _arm_from_fields(self):
        h = self._parse_field(self.hoursLineEdit)
        m = self._parse_field(self.minutesLineEdit)
        s = self._parse_field(self.secondsLineEdit)
        if h is None and m is None and s is None:
            self._set_duration = 0
            self.countdownLabel.setText("Indefinite")
            self.durationChanged.emit(0)
            return
        h = h or 0
        m = m or 0
        s = s or 0
        self._set_duration = h * 3600 + m * 60 + s
        if self._set_duration == 0:
            self.countdownLabel.setText("Indefinite")
        else:
            self.countdownLabel.setText(self._format_seconds(self._set_duration))
        self.durationChanged.emit(self._set_duration)

    def get_duration_seconds(self):
        return self._set_duration

    def start_countdown(self):
        """Start countdown if finite duration armed (>0)."""
        if self._set_duration <= 0:
            self.countdownLabel.setText("Indefinite")
            return
        self._remaining = self._set_duration
        self.countdownLabel.setText(self._format_seconds(self._remaining))
        self.cancelButton.setEnabled(True)
        self._timer.start()
        self.countdownStarted.emit(self._remaining)

    def stop_countdown(self, finished=False):
        if self._timer.isActive():
            self._timer.stop()
        if finished:
            self.countdownLabel.setText("Done")
            self.cancelButton.setEnabled(False)
            self.countdownFinished.emit()
        else:
            if self._set_duration == 0:
                self.countdownLabel.setText("Indefinite")
            else:
                self.countdownLabel.setText(self._format_seconds(self._set_duration))
            self.cancelButton.setEnabled(False)

    @Slot()
    def cancel_countdown(self):
        active = self._timer.isActive()
        self.stop_countdown(finished=False)
        self.clear_inputs()  # Clear all input fields and reset internal state to defaults
        if active:
            self.countdownCanceled.emit()

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self.stop_countdown(finished=True)
        else:
            self.countdownLabel.setText(self._format_seconds(self._remaining))
            self.countdownTick.emit(self._remaining)

    def _format_seconds(self, total):
        h = total // 3600
        rem = total % 3600
        m = rem // 60
        s = rem % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
    
    @Slot()
    def clear_inputs(self):
        """Clear HH:MM:SS inputs and reset to default 'Indefinite' state."""
        self.hoursLineEdit.clear()
        self.minutesLineEdit.clear()
        self.secondsLineEdit.clear()
        self._set_duration = 0
        self._remaining = 0
        self.countdownLabel.setText("Indefinite")
        self.cancelButton.setEnabled(False)
        # Notify listeners that duration is now zero (indefinite)
        self.durationChanged.emit(0)