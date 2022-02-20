from PySide6.QtWidgets import QGroupBox, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Slot, Qt, Signal
from src.widgets.LinearSlider import LinearSlider

class SliderGroupBox(QGroupBox):
    leftLimitChanged = Signal(float)
    rightLimitChanged = Signal(float)
    setPointChanged = Signal(float)
    processVariableChanged = Signal(float)
    minimumRangeChanged = Signal(float)
    maximumRangeChanged = Signal(float)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validator.
        self.doubleValidator = QDoubleValidator(decimals=2)

        # Minimum range.
        self.minimumRangeLabel = QLabel("Minimum")
        self.minimumRangeLineEdit = QLineEdit()
        self.minimumRangeLineEdit.setValidator(self.doubleValidator)
        self.minimumRangeLineEdit.setProperty("class", "range")
        
        # Left limit.
        self.leftLimitLabel = QLabel("Limit")
        self.leftLimitLineEdit = QLineEdit()
        self.leftLimitLineEdit.setValidator(self.doubleValidator)
        self.leftLimitLineEdit.setProperty("class", "limit")

        # Right limit.
        self.rightLimitLabel = QLabel("Limit")
        self.rightLimitLineEdit = QLineEdit()
        self.rightLimitLineEdit.setValidator(self.doubleValidator)
        self.rightLimitLineEdit.setProperty("class", "limit")
        
        # Maximum range.
        self.maximumRangeLabel = QLabel("Maximum")
        self.maximumRangeLineEdit = QLineEdit()
        self.maximumRangeLineEdit.setValidator(self.doubleValidator)
        self.maximumRangeLineEdit.setProperty("class", "range")

        # Axis slider.
        self.axisSlider = LinearSlider()

        # Left controls layout.
        self.leftControlsLayout = QVBoxLayout()
        self.leftControlsLayout.addWidget(self.leftLimitLabel)
        self.leftControlsLayout.addWidget(self.leftLimitLineEdit)
        self.leftControlsLayout.addWidget(self.minimumRangeLabel)
        self.leftControlsLayout.addWidget(self.minimumRangeLineEdit)

        # Riight controls layout.
        self.rightControlsLayout = QVBoxLayout()
        self.rightControlsLayout.addWidget(self.rightLimitLabel)
        self.rightControlsLayout.addWidget(self.rightLimitLineEdit)
        self.rightControlsLayout.addWidget(self.maximumRangeLabel)
        self.rightControlsLayout.addWidget(self.maximumRangeLineEdit)

        #  Axis slider layout.
        self.axisSliderLayout = QVBoxLayout()
        self.axisSliderLayout.addSpacing(25)
        self.axisSliderLayout.addWidget(self.axisSlider)

        # Main layout.
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.leftControlsLayout)
        self.layout.addLayout(self.axisSliderLayout)
        self.layout.addLayout(self.rightControlsLayout)
        self.setLayout(self.layout)

        # Sizings.
        self.setFixedHeight(200)
        self.minimumRangeLineEdit.setFixedWidth(100)
        self.leftLimitLineEdit.setFixedWidth(100)
        self.rightLimitLineEdit.setFixedWidth(100)
        self.maximumRangeLineEdit.setFixedWidth(100)

        # Connections.
        self.axisSlider.leftLimitSliderMoved.connect(self.updateLeftLimit)
        self.axisSlider.rightLimitSliderMoved.connect(self.updateRightLimit)
        self.axisSlider.setPointSliderMoved.connect(self.emitSetPointChanged)
        self.leftLimitLineEdit.returnPressed.connect(self.setLeftLimit)
        self.rightLimitLineEdit.returnPressed.connect(self.setRightLimit)
        self.minimumRangeLineEdit.returnPressed.connect(self.setMinimumRange)
        self.maximumRangeLineEdit.returnPressed.connect(self.setMaximumRange)

    @Slot()
    def emitSetPointChanged(self, value):
        self.setPointChanged.emit(value)

    @Slot(float)
    def updateLeftLimit(self, value):
        self.leftLimitLineEdit.setText("{value:.2f}".format(value=value))
        self.leftLimitChanged.emit(value)

    @Slot(float)
    def updateRightLimit(self, value):
        self.rightLimitLineEdit.setText("{value:.2f}".format(value=value))
        self.rightLimitChanged.emit(value)

    @Slot()
    def setLeftLimit(self, value=None):
        # Limit values to range between minimum range and set point.
        if value == None:
            value = float(self.leftLimitLineEdit.text())
        value = min(value, self.axisSlider.setPoint)
        value = max(value, self.axisSlider.minimumRange)
        self.axisSlider.setLeftLimit(value)
        self.axisSlider.update()
        self.leftLimitLineEdit.setText("{value:.2f}".format(value=value))
        self.leftLimitChanged.emit(value)

    def getLeftLimit(self):
        return self.axisSlider.getLeftLimit()

    @Slot(float)
    def setRightLimit(self, value=None):
        # Limit values to range between maximum range and set point.
        if value == None:
            value = float(self.rightLimitLineEdit.text())
        value = max(value, self.axisSlider.setPoint)
        value = min(value, self.axisSlider.maximumRange)
        self.axisSlider.setRightLimit(value)
        self.axisSlider.update()
        self.rightLimitLineEdit.setText("{value:.2f}".format(value=value))
        self.rightLimitChanged.emit(value)

    def getRightLimit(self):
        return self.axisSlider.rightLimit

    @Slot()
    def setSetPoint(self, value=None):
        # Set point values to range between left and right limits.
        if value == None:
            value = float(self.setPointLineEdit.text())
        value = max(value, self.getLeftLimit())
        value = min(value, self.getRightLimit())
        self.axisSlider.setPoint = value
        self.axisSlider.update()
        # self.setPointChanged.emit(value)

    def getSetPoint(self):
        return self.axisSlider.setPoint

    @Slot()
    def setProcessVariable(self, value=None):
        # Process variable values.
        if value == None:
            value = float(self.processVariableLineEdit.text())
        self.axisSlider.processVariable = value
        self.axisSlider.update()
        self.processVariableChanged.emit(value)

    def getProcessVariable(self):
        return self.axisSlider.processVariable

    # @Slot()
    # def setSetPoint(self, value):
    #     # Set set point.
    #     self.axisSlider.setPoint = value
    #     self.axisSlider.update()

    # def getSetPoint(self):
    #     return self.axisSlider.setPoint

    @Slot()
    def setMinimumRange(self, value=None):
        # Limit values to less than the set point and adjust left limit if required.
        if value == None:
            value = float(self.minimumRangeLineEdit.text())
        if value <= self.axisSlider.leftLimit and value <= self.axisSlider.setPoint:
            self.axisSlider.minimumRange = value
            self.minimumRangeLineEdit.setText("{value:.2f}".format(value=value))
        elif value >= self.axisSlider.leftLimit and value <= self.axisSlider.setPoint:
            self.axisSlider.leftLimit = value
            self.axisSlider.minimumRange = value
            self.leftLimitLineEdit.setText("{value:.2f}".format(value=value))
            self.minimumRangeLineEdit.setText("{value:.2f}".format(value=value))
        elif value >= self.axisSlider.setPoint:
            value = self.axisSlider.setPoint
            self.axisSlider.leftLimit = value
            self.axisSlider.minimumRange = value
            self.leftLimitLineEdit.setText("{value:.2f}".format(value=value))
            self.minimumRangeLineEdit.setText("{value:.2f}".format(value=value))
        self.axisSlider.update()
        self.minimumRangeChanged.emit(value)

    def getMinimumRange(self):
        return self.axisSlider.minimumRange
        
    @Slot()
    def setMaximumRange(self, value=None):
        # Limit values to greater than the set point and adjust right limit if required.
        if value == None:
            value = float(self.maximumRangeLineEdit.text())
        if value >= self.axisSlider.rightLimit and value >= self.axisSlider.setPoint:
            self.axisSlider.maximumRange = value
            self.maximumRangeLineEdit.setText("{value:.2f}".format(value=value))
        elif value <= self.axisSlider.rightLimit and value >= self.axisSlider.setPoint:
            self.axisSlider.rightLimit = value
            self.axisSlider.maximumRange = value
            self.rightLimitLineEdit.setText("{value:.2f}".format(value=value))
            self.maximumRangeLineEdit.setText("{value:.2f}".format(value=value))
        elif value <= self.axisSlider.setPoint:
            value = self.axisSlider.setPoint
            self.axisSlider.rightLimit = value
            self.axisSlider.maximumRange = value
            self.rightLimitLineEdit.setText("{value:.2f}".format(value=value))
            self.maximumRangeLineEdit.setText("{value:.2f}".format(value=value))
        self.axisSlider.update()
        self.maximumRangeChanged.emit(value)

    def getMaximumRange(self):
        return self.axisSlider.maximumRange
    
    def setUnit(self, unit):
        # Set units for labels.
        self.unit = unit
        self.leftLimitLabel.setText("Limit " + self.unit)
        self.rightLimitLabel.setText("Limit " + self.unit)
        self.minimumRangeLabel.setText("Minimum " + self.unit)
        self.maximumRangeLabel.setText("Maximum " + self.unit)