from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from src.views import AcquisitionTableView, ControlTableView

class ConfigurationUtilities:

    @Slot(str)
    def addDeviceConfigurationTab(self, name):
        # Create layout.
        self.deviceConfigurationLayout[name] = QVBoxLayout()

        # Add acquisition table label.
        acquisitionLabel = QLabel('Acquisition')
        self.deviceConfigurationLayout[name].addWidget(acquisitionLabel)

        # Add acquisition table to the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionTableModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionTableModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionTableModels[name].acquisitionChannelToggled.connect(self.updateFeedbackComboBox)

        # Add control table label.
        controlLabel = QLabel('Control')
        self.deviceConfigurationLayout[name].addWidget(controlLabel)

        # Add acquisition table to dict, update the TabWidget and connect to control widget generation method.
        self.controlTableViews[name] = ControlTableView(
            self.manager.controlModeList,
            self.manager.controlActuatorList, 
            self.manager.feedbackChannelLists[name]
            )
        self.controlTableViews[name].setModel(self.manager.controlTableModels[name])
        self.controlTableViews[name].setFixedHeight(89)
        self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])

        # Connections for control table.
        self.manager.controlTableModels[name].controlChannelToggled.connect(self.toggleControlChannel)
        self.manager.controlTableModels[name].controlChannelNameChanged.connect(self.manager.updatePlotWindowChannelsData)

        # Set layout within widget.
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

        # Add the tab and show if device connected boolean is true.
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        index = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(self.deviceConfigurationWidget[name])
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        for device in enabledDevices:
            if device["name"] == name:
                self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, True)
            else:
                self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, False)
        
        # Instantiate the control widgets and add tabs if enabled boolean is true.
        for channel in range(self.manager.controlTableModels[name].rowCount()):
            self.addControlTab(name, channel)

    @Slot(str, int, int, bool)
    def updateDeviceConfigurationTabs(self, name, id, connection, connect):
        widget = self.deviceConfigurationWidget[name]
        index = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(widget)
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, connect)

    @Slot()
    def updateFeedbackComboBox(self):
        # Get the name of the device.
        tabIndex = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)

        # Create an updated feedback channel list for this device.
        feedbackChannelList = self.manager.setFeedbackChannelList(name)

        # Get current feedback channels selected for each control channel.
        selectedFeedbackChannels = []
        numChannels = self.manager.controlTableModels[name].rowCount()
        for index in range(numChannels):
            channel = self.configuration["devices"][name]["control"][index]["feedback"]
            if channel not in feedbackChannelList:
                channel = "N/A"
            selectedFeedbackChannels.append(channel)

        # Update feedback channel selector ComboBox.
        self.controlTableViews[name].updateFeedbackChannelList(feedbackChannelList, selectedFeedbackChannels)

    @Slot()
    def clearDeviceConfigurationTabs(self):
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

    