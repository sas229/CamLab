from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal
import math

class JogGroupBox(QGroupBox):
    speedLineEditChanged = Signal(float)
    speedUnitChanged = Signal()
    speedRPMChanged = Signal(float)  # For direct RPM control
    positiveJogRPMEnabled = Signal(float)  # Sends current RPM value
    negativeJogRPMEnabled = Signal(float)
    positiveJogRPMDisabled = Signal()
    negativeJogRPMDisabled = Signal()
    
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
        self.doubleValidator = QDoubleValidator(decimals=1, bottom=0.0, top=5000.0)
        
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

    def create_layouts(self):
        """Set up the widget layouts"""
        # Button layout
        self.jogButtonsLayout = QHBoxLayout()
        self.jogButtonsLayout.addWidget(self.jogMinusButton)
        self.jogButtonsLayout.addWidget(self.jogPlusButton)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.speedLabel)
        self.layout.addWidget(self.speedLineEdit)
        self.layout.addWidget(self.jogDirectionLabel)
        self.layout.addLayout(self.jogButtonsLayout)
        self.setLayout(self.layout)

    def set_geometry(self):
        """Set widget geometry"""
        self.setFixedHeight(200)
        self.setFixedWidth(150)

    def create_connections(self):
        """Set up signal connections"""
        self.speedLineEdit.returnPressed.connect(self.setSpeed)
        # Use toggled instead of clicked for checkable buttons
        self.jogPlusButton.toggled.connect(self.handlePositiveJog)
        self.jogMinusButton.toggled.connect(self.handleNegativeJog)

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
            # Button is pressed down - start continuous rotation
            self.jogMinusButton.setEnabled(False)  # Disable other button
            rpm_speed = self.getSpeed()
            self.positiveJogRPMEnabled.emit(rpm_speed)
        else:
            # Button is released - stop rotation
            self.jogMinusButton.setEnabled(True)  # Enable other button
            self.positiveJogRPMDisabled.emit()

    def handleNegativeJog(self, checked):
        """Handle negative direction jog button toggle"""
        if checked:
            # Button is pressed down - start continuous rotation
            self.jogPlusButton.setEnabled(False)  # Disable other button  
            rpm_speed = -self.getSpeed()
            self.negativeJogRPMEnabled.emit(rpm_speed)
        else:
            # Button is released - stop rotation
            self.jogPlusButton.setEnabled(True)  # Enable other button
            self.negativeJogRPMDisabled.emit()