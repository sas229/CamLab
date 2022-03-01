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
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionModels[name].acquisitionChannelToggled.connect(self.updateFeedbackComboBox)

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

        # Add the tab but hidden.
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        index = self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(self.deviceConfigurationWidget[name])
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, False)

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

        # # Clear the acquisition table TabWidget.
        # self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

        # # Get a list of enabled devices and current status.
        # enabledDevices = self.manager.deviceTableModel.enabledDevices()

        # # If enabled and status is True, add the TabWidget for this device.
        # for device in enabledDevices:
        #     connect = device["connect"]
        #     name = device["name"]
        #     status = device["status"]
        #     if status == True and connect == True and name in self.acquisitionTableViews:
        #         self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        # # # Update control tabs to remove any deselected devices.
        # # self.updateControlTabs()

    @Slot()
    def clearDeviceConfigurationTabs(self):
        self.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

    # @Slot(str)
    # def updateFeedbackChannelList(self, name):
    #     print(name)
    #     # feedbackChannel    # @Slot(str, list)
    # # def addControlTable(self, name, defaultFeedbackChannel):
    # #     # Add acquisition table to dict, update the TabWidget and connect to control widget generation method.
    # #     self.controlTableViews[name] = ControlTableView(self.manager.controlModeList, self.manager.controlActuatorList, defaultFeedbackChannel)
    # #     print("Test")
    # #     self.controlTableViews[name].setModel(self.manager.controlTableModels[name])
    # #     self.controlTableViews[name].setFixedHeight(89)
    # #     self.deviceConfigurationLayout[name].addWidget(self.controlTableViews[name])
    # #     self.manager.controlTableModels[name].controlChannelToggled.connect(self.toggleControlChannel)List = self.manager.setFeedBackChannelList(name)
    #     print(feedbackChannelList)
    #     # self.controlTableViews[name].updateFeedbackChannelList(feedbackChannelList)

    @Slot(int, bool)
    def toggleControlChannel(self, index, state):
        print(str(index) + str(state))  
        # self.controlTableViews[name].updateFeedbackChannelList()

    @Slot(str)
    def removeControlTable(self, name):
        self.controlTableViews[name].setParent(None)

    