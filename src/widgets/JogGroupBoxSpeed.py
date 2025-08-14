from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal
import math
from PySide6.QtWidgets import QDial
from PySide6.QtCore import Qt
from .styles.DialStyles import get_dial_label_style
from .styles.CustomDial import CustomDial

class JogGroupBox(QGroupBox):
    speedLineEditChanged = Signal(float)
    speedUnitChanged = Signal()
    speedRPMChanged = Signal(float)  # For direct RPM control
    positiveJogRPMEnabled = Signal(float)  # Sends current RPM value
    negativeJogRPMEnabled = Signal(float)
    positiveJogRPMDisabled = Signal()
    negativeJogRPMDisabled = Signal()
    speedDialChanged = Signal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Defaults
        self.unit = "RPM"
        self.radius = 10.0  # Default radius in mm
        self.rpm_conversion_factor = 60 / (2 * math.pi * self.radius)

        # Create controls first
        self.create_controls()
        
        # Then create layouts
        self.create_layouts()
        
        # Set geometry
        self.set_geometry()
        
        # Finally set connections
        self.create_connections()

    def create_controls(self):
        """Initialize all control widgets"""
        # Validator for RPM
        self.doubleValidator = QDoubleValidator(decimals=1, bottom=0.0, top=3000.0)
        
        # Controls with RPM label
        self.speedLabel = QLabel("Speed (RPM)")
        self.speedLineEdit = QLineEdit()
        self.speedLineEdit.setValidator(self.doubleValidator)
        self.jogDirectionLabel = QLabel("Direction")
        # Make buttons checkable for continuous rotation
        self.jogPlusButton = QPushButton("+")
        self.jogMinusButton = QPushButton("-")
        self.jogPlusButton.setCheckable(True)
        self.jogMinusButton.setCheckable(True)

        # Add RPM dial control
        self.speedDial = CustomDial()
        self.speedDial.setMinimum(0)  # Start from 0 RPM
        self.speedDial.setMaximum(3000)  # Max 3000 RPM
        self.speedDial.setNotchesVisible(True)
        self.speedDial.setWrapping(False)
        self.speedDial.setSingleStep(10)  # 10 RPM per step
        self.speedDial.setPageStep(100)   # 100 RPM per page
        self.speedDial.setTracking(True)  # Enable real-time updates
        self.speedDial.setFixedSize(100, 100)
        
        # Initialize dial value label to 0
        self.dialValueLabel = QLabel("0.0 RPM")
        self.dialValueLabel.setAlignment(Qt.AlignCenter)
        self.dialValueLabel.setStyleSheet("font-size: 11pt; font-weight: bold;")

    def create_layouts(self):
        """Set up the widget layouts"""
        # Button layout
        self.jogButtonsLayout = QHBoxLayout()
        self.jogButtonsLayout.addWidget(self.jogMinusButton)
        self.jogButtonsLayout.addWidget(self.jogPlusButton)

        # Create a container for dial and its value
        self.dialContainer = QVBoxLayout()
        self.dialContainer.addWidget(self.speedDial, alignment=Qt.AlignHCenter)
        self.dialContainer.addWidget(self.dialValueLabel, alignment=Qt.AlignHCenter)
        self.dialContainer.setSpacing(10)  # Add some space between dial and value

        # Main layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.speedLabel)
        self.mainLayout.addWidget(self.speedLineEdit)
        self.mainLayout.addWidget(self.jogDirectionLabel)
        self.mainLayout.addLayout(self.jogButtonsLayout)
        self.mainLayout.addLayout(self.dialContainer)
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.mainLayout)

    def set_geometry(self):
        """Set widget geometry"""
        self.setFixedHeight(320)
        self.setFixedWidth(170)

    def create_connections(self):
        """Set up signal connections"""
        self.speedLineEdit.returnPressed.connect(self.setSpeed)
        # Use toggled instead of clicked for checkable buttons
        self.jogPlusButton.toggled.connect(self.handlePositiveJog)
        self.jogMinusButton.toggled.connect(self.handleNegativeJog)

        # Connect dial
        self.speedDial.valueChanged.connect(self.handleDialChange)
        self.speedLineEdit.returnPressed.connect(self.updateDialFromInput)

    def emitPositiveJogRPM(self):
        """Emit current speed in RPM for positive jogging"""
        rpm_speed = self.getSpeed() # Gets current speed from input field
        self.positiveJogRPMEnabled.emit(rpm_speed) # Emits the RPM value

    def emitNegativeJogRPM(self):
        """Emit current speed in RPM for negative jogging"""
        rpm_speed = -self.getSpeed()  # Gets current speed from input field
        self.negativeJogRPMEnabled.emit(rpm_speed) # Emits the RPM value

    def emitPositiveJogRPMDisabled(self):
        self.positiveJogRPMDisabled.emit()

    def emitNegativeJogRPMDisabled(self):
        self.negativeJogRPMDisabled.emit()

    def set_radius(self, radius_mm):
        """Set the radius for mm/s to RPM conversion"""
        self.radius = radius_mm
        self.rpm_conversion_factor = 60 / (2 * math.pi * self.radius)

    def linear_to_rpm(self, speed_mm_s):
        """Convert linear speed (mm/s) to RPM"""
        return speed_mm_s * self.rpm_conversion_factor

    def rpm_to_linear(self, speed_rpm):
        """Convert RPM to linear speed (mm/s)"""
        return speed_rpm / self.rpm_conversion_factor

    def setSpeed(self, value=None):
        """Set speed value - expects RPM input"""
        if value is None:
            value = self.getSpeed()
        # Format RPM with one decimal place
        self.speedLineEdit.setText(f"{value:.1f}")
        # Emit RPM directly without conversion
        self.speedRPMChanged.emit(value) 

    def getSpeed(self):
        """Get speed value - returns RPM"""
        return float(self.speedLineEdit.text())

    def updateSpeedFromLinear(self, linear_speed):
        """Update display from linear speed (mm/s)"""
        rpm_speed = self.linear_to_rpm(linear_speed)
        self.setSpeed(rpm_speed)
        # Make sure label shows RPM
        self.speedLabel.setText(f"Speed (RPM)")

    def set_configuration(self, configuration):
        
        # Set radius for speed conversion
        radius = self.controlConfiguration["settings"].get("radius", 10.0)
        self.jog.set_radius(radius)
        
        # Set initial speed
        initial_speed = self.controlConfiguration["settings"].get("secondarySetPoint", 0.0)
        self.jog.updateSpeedFromLinear(initial_speed)

    def set_unit(self, unit):
        """Override to always use RPM"""
        # Ignore incoming unit and always use RPM
        self.unit = "RPM"
        self.speedLabel.setText(f"Speed ({self.unit})")
        self.speedUnitChanged.emit()

    def handlePositiveJog(self, checked):
        """Handle positive direction jog button toggle"""
        if checked:
            self.jogMinusButton.setEnabled(False)
            rpm_speed = self.getSpeed()
            self.positiveJogRPMEnabled.emit(rpm_speed)
            self.dialValueLabel.setStyleSheet(get_dial_label_style(is_active=True, rpm=rpm_speed))
        else:
            self.jogMinusButton.setEnabled(True)
            self.positiveJogRPMDisabled.emit()
            self.dialValueLabel.setStyleSheet(get_dial_label_style(is_active=False))

    def handleNegativeJog(self, checked):
        """Handle negative direction jog button toggle"""
        if checked:
            self.jogPlusButton.setEnabled(False)
            rpm_speed = self.getSpeed()
            self.negativeJogRPMEnabled.emit(-rpm_speed)
            self.dialValueLabel.setStyleSheet(get_dial_label_style(is_active=True, rpm=rpm_speed))
        else:
            self.jogPlusButton.setEnabled(True)
            self.negativeJogRPMDisabled.emit()
            self.dialValueLabel.setStyleSheet(get_dial_label_style(is_active=False))

    def handleDialChange(self, value):
        """Handle dial value changes"""
        rpm = float(value)
        # Update line edit
        self.speedLineEdit.setText(f"{rpm:.1f}")
        # Update label
        self.dialValueLabel.setText(f"{rpm:.1f} RPM")
        
        # Update color based on current state and RPM
        if self.jogPlusButton.isChecked() or self.jogMinusButton.isChecked():
            self.dialValueLabel.setStyleSheet(get_dial_label_style(is_active=True, rpm=rpm))
        
        # Emit signal for real-time updates
        self.speedDialChanged.emit(rpm)
        
        # If jogging, update speed immediately
        if self.jogPlusButton.isChecked():
            self.positiveJogRPMEnabled.emit(rpm)
        elif self.jogMinusButton.isChecked():
            self.negativeJogRPMEnabled.emit(-rpm)

    def updateDialFromInput(self):
        """Update dial when line edit value changes"""
        try:
            rpm = float(self.speedLineEdit.text())
            self.speedDial.setValue(int(rpm))
        except ValueError:
            pass  # Invalid input

    def setMaxRPM(self, max_rpm):
        """Update the maximum RPM value for the dial"""
        self.speedDial.setMaximum(max_rpm)
        # Also update the validator for the speed line edit
        self.doubleValidator.setTop(float(max_rpm))