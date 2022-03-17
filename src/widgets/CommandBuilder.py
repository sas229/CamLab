from PySide6.QtWidgets import QPushButton, QGridLayout, QLineEdit, QGroupBox, QLabel, QComboBox, QSpinBox
from PySide6.QtGui import QIcon, QDoubleValidator
from PySide6.QtCore import Slot, Signal, QSize

class CommandBuilder(QGroupBox):
    commandPreview = Signal(dict)
    clearPreview = Signal()
    addCommandToSequence = Signal(dict)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dT = 0.01
        self.darkMode = True
        self.timeUnit = "s"
        self.positionUnit = "mm"
        self.positionRateUnit = "mm/s"
        self.feedbackUnit = "N"
        self.feedbackRateUnit = "N/s" 
        self.speedUnit = "mm/s"
        self.speedRateUnit = "mm/s<sup>2</sup>" 

        self.nameLabel = QLabel("Name")
        self.nameLabel.setVisible(True)
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setVisible(True)
        self.nameLineEdit.setFixedWidth(100)
        self.nameLineEdit.setWhatsThis("name")
        
        self.deviceLabel = QLabel("Device")
        self.deviceLabel.setVisible(False)
        self.deviceComboBox = QComboBox()
        self.deviceComboBox.setVisible(False)
        self.deviceComboBox.setFixedWidth(120)
        self.deviceComboBox.setWhatsThis("device")

        self.channelLabel = QLabel("Channel")
        self.channelLabel.setVisible(False)
        self.channelComboBox = QComboBox()
        self.channelComboBox.setVisible(False)
        self.channelComboBox.setFixedWidth(120)
        self.channelComboBox.setWhatsThis("channel")

        self.variableLabel = QLabel("Variable")
        self.variableLabel.setVisible(False)
        self.variableComboBox = QComboBox()
        self.variableComboBox.setVisible(False)
        self.variableComboBox.setFixedWidth(120)
        self.variableComboBox.setWhatsThis("variable")

        self.commandLabel = QLabel("Command")
        self.commandLabel.setVisible(False)
        self.commandComboBox = QComboBox()
        self.commandComboBox.setVisible(False)
        self.commandComboBox.setFixedWidth(120)
        self.commandComboBox.setWhatsThis("command")

        self.offsetLabel = QLabel("Offset")
        self.offsetLabel.setVisible(False)
        self.offsetLineEdit = QLineEdit()
        self.offsetLineEdit.setValidator(QDoubleValidator())
        self.offsetLineEdit.setVisible(False)
        self.offsetLineEdit.setFixedWidth(100)
        self.offsetLineEdit.setWhatsThis("offset")

        self.amplitudeLabel = QLabel("Value")
        self.amplitudeLabel.setVisible(False)
        self.amplitudeLineEdit = QLineEdit()
        self.amplitudeLineEdit.setValidator(QDoubleValidator())
        self.amplitudeLineEdit.setVisible(False)
        self.amplitudeLineEdit.setFixedWidth(100)
        self.amplitudeLineEdit.setWhatsThis("amplitude")

        self.rateLabel = QLabel("Rate")
        self.rateLabel.setVisible(False)
        self.rateLineEdit = QLineEdit()
        self.rateLineEdit.setValidator(QDoubleValidator())
        self.rateLineEdit.setVisible(False)
        self.rateLineEdit.setFixedWidth(100)
        self.rateLineEdit.setWhatsThis("rate")

        self.fileLoadLabel = QLabel("Input")
        self.fileLoadLabel.setVisible(False)
        self.fileLoadButton = QPushButton()
        self.fileLoadButton.setIconSize(QSize(25, 25))
        self.fileLoadButton.setVisible(False)

        self.filePathLabel = QLabel("Path")
        self.filePathLabel.setVisible(False)
        self.filePathLineEdit = QLineEdit()
        self.filePathLineEdit.setVisible(False)
        self.filePathLineEdit.setFixedWidth(250)
        self.filePathLineEdit.setWhatsThis("filePath")
        self.filePathLineEdit.setReadOnly(True)

        self.triggerLabel = QLabel("Trigger")
        self.triggerLabel.setVisible(False)
        self.triggerComboBox = QComboBox()
        self.triggerComboBox.setVisible(False)
        self.triggerComboBox.setFixedWidth(120)
        self.triggerComboBox.setWhatsThis("trigger")

        self.triggerValueLabel = QLabel("Trigger Value")
        self.triggerValueLabel.setVisible(False)
        self.triggerValueLineEdit = QLineEdit("0.0")
        self.triggerValueLineEdit.setVisible(False)
        self.triggerValueLineEdit.setFixedWidth(100)
        self.triggerValueLineEdit.setWhatsThis("triggerValue")

        self.repeatLabel = QLabel("Repeat")
        self.repeatLabel.setVisible(False)
        self.repeatSpinBox = QSpinBox()
        self.repeatSpinBox.setMinimum(1)
        self.repeatSpinBox.setSingleStep(1)
        self.repeatSpinBox.setVisible(False)
        self.repeatSpinBox.setFixedWidth(60)
        self.repeatSpinBox.setWhatsThis("repeat")

        self.finaliseLabel = QLabel("Finalise")
        self.finaliseLabel.setVisible(False)

        self.clearButton = QPushButton()
        self.clearButton.setIconSize(QSize(25, 25))
        self.clearButton.setVisible(False)
        self.clearButton.setToolTip("Clear command.")

        self.addButton = QPushButton()
        self.addButton.setIconSize(QSize(25, 25))
        self.addButton.setVisible(False)
        self.addButton.setToolTip("Add command to sequence.")

        deviceList = ["Select", "AMY", "BEN"]
        self.deviceComboBox.addItems(deviceList)

        channelList = ["Select", "C1", "C2"]
        self.channelComboBox.addItems(channelList)

        variableList = ["Select", "Position", "Speed", "Feedback"]
        self.variableComboBox.addItems(variableList)

        commandList = ["Select", "Demand", "Ramp", "Triangle", "Sine", "File"]
        self.commandComboBox.addItems(commandList)

        eventList = ["Select", "Completion", "Immediate", "Time", "Feedback", "Position"]
        self.triggerComboBox.addItems(eventList)

        self.commandLayout = QGridLayout()
        n = 0
        self.commandLayout.addWidget(self.nameLabel, 0, n)
        self.commandLayout.addWidget(self.nameLineEdit, 1, n)
        n += 1
        self.commandLayout.addWidget(self.deviceLabel, 0, n)
        self.commandLayout.addWidget(self.deviceComboBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.channelLabel, 0, n)
        self.commandLayout.addWidget(self.channelComboBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.variableLabel, 0, n)
        self.commandLayout.addWidget(self.variableComboBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.commandLabel, 0, n)
        self.commandLayout.addWidget(self.commandComboBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.rateLabel, 0, n)
        self.commandLayout.addWidget(self.rateLineEdit, 1, n)
        n += 1
        self.commandLayout.addWidget(self.amplitudeLabel, 0, n)
        self.commandLayout.addWidget(self.amplitudeLineEdit , 1, n)
        n += 1
        self.commandLayout.addWidget(self.offsetLabel, 0, n)
        self.commandLayout.addWidget(self.offsetLineEdit, 1, n)
        n += 1
        self.commandLayout.addWidget(self.repeatLabel, 0, n)
        self.commandLayout.addWidget(self.repeatSpinBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.fileLoadLabel, 0, n)
        self.commandLayout.addWidget(self.fileLoadButton, 1, n)
        n += 1
        self.commandLayout.addWidget(self.filePathLabel, 0, n)
        self.commandLayout.addWidget(self.filePathLineEdit, 1, n)
        n += 1
        self.commandLayout.addWidget(self.triggerLabel, 0, n)
        self.commandLayout.addWidget(self.triggerComboBox, 1, n)
        n += 1
        self.commandLayout.addWidget(self.triggerValueLabel, 0, n)
        self.commandLayout.addWidget(self.triggerValueLineEdit, 1, n)
        n += 1
        self.commandLayout.addWidget(self.finaliseLabel, 0, n)
        self.commandLayout.addWidget(self.clearButton, 1, n)
        n += 1
        self.commandLayout.addWidget(self.addButton, 1, n)
        n += 1
    
        self.commandLayout.setHorizontalSpacing(10)
        self.commandLayout.setColumnStretch(n, 1)

        self.setLayout(self.commandLayout)
        
        # Connections.
        self.nameLineEdit.returnPressed.connect(self.nameSelected)
        self.deviceComboBox.currentTextChanged.connect(self.deviceSelected)
        self.channelComboBox.currentTextChanged.connect(self.channelSelected)
        self.variableComboBox.currentTextChanged.connect(self.variableSelected)
        self.commandComboBox.currentTextChanged.connect(self.commandSelected)
        self.rateLineEdit.returnPressed.connect(self.enableAmplitudeInput)
        self.amplitudeLineEdit.returnPressed.connect(self.amplitudeSelected)
        self.repeatSpinBox.valueChanged.connect(self.repeatSelected)
        self.offsetLineEdit.returnPressed.connect(self.offsetSelected)
        self.triggerComboBox.currentTextChanged.connect(self.triggerSelected)
        self.triggerValueLineEdit.returnPressed.connect(self.showOptions)
        self.clearButton.clicked.connect(self.clearCommand)
        self.addButton.clicked.connect(self.addCommand)

    def updateIcons(self):
        # Change appearance between light and dark modes.
        self.fileLoadButton.setIcon(QIcon("icon:/secondaryText/input.svg"))
        self.clearButton.setIcon(QIcon("icon:/secondaryText/clear.svg"))
        self.addButton.setIcon(QIcon("icon:/secondaryText/add.svg"))

    def previewCommand(self):
        if self.finaliseLabel.isVisible() == True:
            self.createCommand()
            self.commandPreview.emit(self.command)
        else:
            self.clearPreview.emit()

    def addCommand(self):
        self.createCommand()
        self.addCommandToSequence.emit(self.command)

    @Slot()
    def showOptions(self):
        self.createCommand()
        self.finaliseLabel.setVisible(True)
        self.clearButton.setVisible(True)
        self.addButton.setVisible(True)
    
    @Slot()
    def repeatSelected(self):
        if self.finaliseLabel.isVisible() == True:
            self.createCommand()
            self.commandPreview.emit(self.command)
        else:
            self.clearPreview.emit()

    @Slot()
    def amplitudeSelected(self):
        if self.commandComboBox.currentText() == "Triangle":
            self.offsetLabel.setVisible(True)
            self.offsetLineEdit.setVisible(True)
        elif self.commandComboBox.currentText() == "Sine":
            self.offsetLabel.setVisible(True)
            self.offsetLineEdit.setVisible(True)
        else:
            self.triggerLabel.setVisible(True)
            self.triggerComboBox.setVisible(True)
        self.previewCommand()

    def resetBuilder(self, currentIndex):
        # Hide all other widgets, reset ComboBoxes and re-initialise defaults in LineEdits. 
        for index in range(self.commandLayout.count()):
            if index > currentIndex:
                widget = self.commandLayout.itemAt(index).widget()
                widget.setVisible(False)   
                if isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)
                if isinstance(widget, QLineEdit):
                    widget.setText("")
                if isinstance(widget, QSpinBox):
                    widget.setValue(1)
        self.previewCommand()

    @Slot()
    def nameSelected(self):
        # Show device ComboBox.
        text = self.nameLineEdit.text()
        if text != "":
            self.deviceLabel.setVisible(True)
            self.deviceComboBox.setVisible(True)
        else:
            currentIndex = self.commandLayout.indexOf(self.nameLineEdit)
            self.resetBuilder(currentIndex)
        self.previewCommand()

    @Slot(str)
    def deviceSelected(self, text):
        # Show channel ComboBox.
        if text != "Select":
            self.channelLabel.setVisible(True)
            self.channelComboBox.setVisible(True)
        else:
            currentIndex = self.commandLayout.indexOf(self.deviceComboBox)
            self.resetBuilder(currentIndex)
        self.previewCommand()

    @Slot(str)
    def channelSelected(self, text):
        # Show variable ComboBox.
        if text != "Select":
            self.variableLabel.setVisible(True)
            self.variableComboBox.setVisible(True)
        else:
            currentIndex = self.commandLayout.indexOf(self.channelComboBox)
            self.resetBuilder(currentIndex)
        self.previewCommand()

    def setUnits(self):
        # Set units.
        if self.variableComboBox.currentText() == "Position":
            text = "Rate " + "(" +self.positionRateUnit + ")"
        elif self.variableComboBox.currentText() == "Feedback":
            text = "Rate " + "(" +self.feedbackRateUnit + ")"
        elif self.variableComboBox.currentText() == "Speed":
            text = "Rate " + "(" +self.speedRateUnit + ")"
        else:
            text = "Rate"
        self.rateLabel.setText(text)
        if self.variableComboBox.currentText() == "Position":
            text = "Offset " + "(" +self.positionUnit + ")"
        elif self.variableComboBox.currentText() == "Feedback":
            text = "Offset " + "(" +self.feedbackUnit + ")"
        elif self.variableComboBox.currentText() == "Speed":
            text = "Offset " + "(" +self.speedUnit + ")"
        else:
            text = "Offset"
        self.offsetLabel.setText(text)
        if self.variableComboBox.currentText() == "Position":
            text = "Amplitude " + "(" +self.positionUnit + ")"
        elif self.variableComboBox.currentText() == "Feedback":
            text = "Amplitude " + "(" +self.feedbackUnit + ")"
        elif self.variableComboBox.currentText() == "Speed":
            text = "Amplitude " + "(" +self.speedUnit + ")"
        else:
            text = "Amplitude"
        self.amplitudeLabel.setText(text)
        if self.triggerComboBox.currentText() == "Position":
            unit = "Value " + "(" + self.positionUnit + ")"
        elif self.triggerComboBox.currentText() == "Feedback":
            unit = "Value " + "(" + self.feedbackUnit + ")"
        elif self.triggerComboBox.currentText() == "Time":
            unit = "Value " + "(" + self.timeUnit + ")"
        else:
            unit = "Value"
        self.triggerValueLabel.setText(unit)

    @Slot(str)
    def variableSelected(self, text):
        # Show command ComboBox.
        if text != "Select":
            self.commandLabel.setVisible(True)
            self.commandComboBox.setVisible(True)
        else:
            currentIndex = self.commandLayout.indexOf(self.variableComboBox)
            self.resetBuilder(currentIndex)

        # Update preview or clear it.
        self.previewCommand()

        self.setUnits()

    @Slot(str)
    def commandSelected(self, text):
        currentIndex = self.commandLayout.indexOf(self.commandComboBox)
        self.resetBuilder(currentIndex)
        if text == "Ramp":
            self.enableRateInput()
        elif text == "Demand":
            self.enableAmplitudeInput()
        elif text == "Triangle":
            self.enableRateInput()
        elif text == "Sine":
            self.enableRateInput()
        elif text == "File":
            self.fileLoadLabel.setVisible(True)
            self.fileLoadButton.setVisible(True)
            self.filePathLabel.setVisible(True)
            self.filePathLineEdit.setVisible(True)
    
    @Slot(str)
    def offsetSelected(self):
        self.offset = float(self.offsetLineEdit.text())
        self.enableRepeatInput()
        self.showOptions()

        # Update preview or clear it.
        self.previewCommand()

    @Slot(str)
    def triggerSelected(self, text):
        if text == "Select":
            self.triggerValueLabel.setVisible(False)
            self.triggerValueLineEdit.setVisible(False)
            self.finaliseLabel.setVisible(False)
            self.clearButton.setVisible(False)
            self.addButton.setVisible(False)
        elif text == "Completion":
            self.createCommand()
            self.triggerValueLabel.setVisible(False)
            self.triggerValueLineEdit.setVisible(False)
            self.finaliseLabel.setVisible(True)
            self.clearButton.setVisible(True)
            self.addButton.setVisible(True)
        elif text == "Immediate":
            self.createCommand()
            self.triggerValueLabel.setVisible(False)
            self.triggerValueLineEdit.setVisible(False)
            self.finaliseLabel.setVisible(True)
            self.clearButton.setVisible(True)
            self.addButton.setVisible(True)
        else:
            self.triggerValueLabel.setVisible(True)
            self.triggerValueLineEdit.setVisible(True)
            self.finaliseLabel.setVisible(False)
            self.clearButton.setVisible(False)
            self.addButton.setVisible(False)
        self.previewCommand()
        self.setUnits() 

    @Slot()
    def enableRepeatInput(self):
        self.repeatLabel.setVisible(True)
        self.repeatSpinBox.setVisible(True)
        self.previewCommand()

    @Slot()
    def enablePhaseInput(self):
        self.offsetLabel.setVisible(True)
        self.offsetLineEdit.setVisible(True)
        self.previewCommand()

    @Slot()
    def enableRateInput(self):
        self.rateLabel.setVisible(True)
        self.rateLineEdit.setVisible(True)
        self.previewCommand()

    @Slot()
    def enableAmplitudeInput(self):
        self.amplitudeLabel.setVisible(True)
        self.amplitudeLineEdit.setVisible(True)
        self.previewCommand()

    @Slot()
    def createCommand(self):
        self.command = {}
        for index in range(self.commandLayout.count()):
            widget = self.commandLayout.itemAt(index).widget()
            if widget.isVisible() == True and index % 2 != 0:  
                name = widget.whatsThis() 
                if isinstance(widget, QComboBox):
                    self.command[name] = str(widget.currentText())
                if isinstance(widget, QLineEdit):
                    if name == "name":
                        self.command[name] = widget.text()
                    else:
                        self.command[name] = float(widget.text())
                if isinstance(widget, QSpinBox):
                    self.command[name] = int(widget.value())

    @Slot()
    def clearCommand(self):
        self.resetBuilder(1)
        self.nameLineEdit.setText("")
        self.clearPreview.emit()