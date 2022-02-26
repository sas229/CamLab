from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.views import AcquisitionTableView, ControlTableView

class ConfigurationUtilities:

    @Slot(str, list)
    def addDeviceConfigurationTab(self, name, defaultFeedbackChannel):
        # Create layout.
        self.deviceConfigurationLayout[name] = QVBoxLayout()

        # Add acquisition table label.
        acquisitionLabel = QLabel('Acquisition')
        self.deviceConfigurationLayout[name].addWidget(acquisitionLabel)

        # Add acquisition table to the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.setListFeedbackCombobox)
        self.manager.acquisitionModels[name].acquisitionChannelToggled.connect(self.resetControlFeedbackComboBox)

        # Add control table label.
        controlLabel = QLabel('Control')
        self.deviceConfigurationLayout[name].addWidget(controlLabel)

        # Add control table to the TabWidget.
        self.addControlTable(name, defaultFeedbackChannel)
        self.manager.controlTableModels[name].controlChannelNameChanged.connect(self.manager.updatePlotWindowChannelsData)

        # Set layout within widget.
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

    @Slot()
    def updateDeviceConfigurationTabs(self):
        # Clear the acquisition table TabWidget.
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

        # Get a list of enabled devices and current status.
        enabledDevices = self.manager.deviceTableModel.enabledDevices()

        # If enabled and status is True, add the TabWidget for this device.
        for device in enabledDevices:
            connect = device["connect"]
            name = device["name"]
            status = device["status"]
            if status == True and connect == True and name in self.acquisitionTableViews:
                self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        self.updateControlTabs()

    @Slot()
    def clearDeviceConfigurationTabs(self):
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

    @Slot(str, list)
    def addControlTable(self, name, defaultFeedbackChannel):
        # Add acquisition table to dict, update the TabWidget and connect to control widget generation method.
        self.controlTableViews[name] = ControlTableView(self.manager.controlModeList, self.manager.controlActuatorList, defaultFeedbackChannel)
        self.controlTableViews[name].setModel(self.manager.controlTableModels[name])
        self.controlTableViews[name].setFixedHeight(89)
        self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
        self.manager.controlTableModels[name].controlChannelToggled.connect(self.updateControlTabs)
        self.updateControlTabs()

    @Slot(str)
    def removeControlTable(self, name):
        self.controlTableViews[name].setParent(None)

    @Slot(int)
    def resetControlFeedbackComboBox(self, row):
        # Method receives the row of the acquisition channel toggled and then gets the name of the channel and sends it to manager.
        tabIndex = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)
        self.manager.resetIndexFeedbackComboBox(row, name)