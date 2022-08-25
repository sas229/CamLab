from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QCheckBox, QLineEdit, QComboBox
from views import AcquisitionTableView, ControlTableView
from widgets.CameraSettings import CameraSettings
from widgets.PressSettings import PressSettings
import logging
from time import sleep

log = logging.getLogger(__name__)

class ConfigurationUtilities:

    @Slot(str)
    def add_device_configuration_tab(self, name, deviceType):
        if deviceType == "Hub":
            self.add_LabJackT7_configuration_tab(name)
        elif deviceType == "Camera":
            self.add_camera_configuration_tab(name)
        elif deviceType == "Press":
            self.add_press_configuration_tab(name)

    def add_press_configuration_tab(self, name):
        # Instantiate widget.
        self.deviceConfigurationWidget[name] = PressSettings(name)
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        self.deviceConfigurationWidget[name].set_device_list(enabledDevices)

        # Add the tab and show if device connected boolean is true.
        self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        index = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(self.deviceConfigurationWidget[name])
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        for device in enabledDevices:
            if device["name"] == name:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, True)
            else:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, False)
        
        # Connections.
        self.manager.deviceTableModel.deviceConnectStatusUpdated.connect(self.update_press_feedback_device_ComboBox)

        # self.deviceConfigurationWidget[name].setImageMode.connect(self.manager.devices[name].set_image_mode)
        # self.deviceConfigurationWidget[name].setAutoWhiteBalanceMode.connect(self.manager.devices[name].set_auto_white_balance_mode)
        # self.deviceConfigurationWidget[name].setAutoExposureMode.connect(self.manager.devices[name].set_auto_exposure_mode)
        # self.deviceConfigurationWidget[name].setExposureTime.connect(self.manager.devices[name].set_exposure_time)
        # self.deviceConfigurationWidget[name].setGain.connect(self.manager.devices[name].set_gain)
        # self.deviceConfigurationWidget[name].setAutoGain.connect(self.manager.devices[name].set_auto_gain)
        # self.deviceConfigurationWidget[name].setBinningMode.connect(self.manager.devices[name].set_binning_mode)
        # self.deviceConfigurationWidget[name].setBinning.connect(self.manager.devices[name].set_binning)
        # self.deviceConfigurationWidget[name].setAcquisitionMode.connect(self.manager.devices[name].set_acquisition_mode)
        # self.deviceConfigurationWidget[name].setAcquisitionRate.connect(self.manager.devices[name].set_acquisition_rate)

        # self.deviceConfigurationWidget[name].calibrateButton.clicked.connect(self.manager.devices[name].calibrate)

        # self.manager.devices[name].previewImage.connect(self.previews[name].set_image)

        # # self.manager.devices[name].updateImageMode.connect(self.deviceConfigurationWidget[name].update_image_mode)
        # self.manager.devices[name].updateExposureTime.connect(self.deviceConfigurationWidget[name].update_exposure_time)
        # self.manager.devices[name].updateGain.connect(self.deviceConfigurationWidget[name].update_gain)
        # self.manager.devices[name].updateImageMode.connect(self.deviceConfigurationWidget[name].update_mode)
        # self.manager.devices[name].updateAcquisitionRate.connect(self.deviceConfigurationWidget[name].update_acquisition_rate)

        # # Initialise settings.
        # self.deviceConfigurationWidget[name].set_configuration(self.manager.configuration)
        # sleep(1.0)

        # # Start stream.
        # self.manager.devices[name].capture_image()

        # log.info("Device configuration tab added for {device}.".format(device=name))

    @Slot()
    def update_press_feedback_device_ComboBox(self):
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        inputDevices = []
        for device in enabledDevices:
            if device["type"] == "Hub":
                inputDevices.append(device["name"])
        self.deviceConfigurationWidget["VJT"].set_device_list(inputDevices)
        self.update_press_feedback_channel_ComboBox()
    
    def update_press_feedback_channel_ComboBox(self):
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        feedback_channel_lists = {}
        for device in enabledDevices:
            if device["type"] == "Hub":
                name = device["name"]
                enabledChannels = self.manager.acquisitionTableModels[name].enabledChannels()
                feedback_channel_lists[name] = enabledChannels
        if "VJT" in self.deviceConfigurationWidget:
            self.deviceConfigurationWidget["VJT"].set_channel_lists(feedback_channel_lists)

    def add_camera_configuration_tab(self, name):
        # Instantiate widget.
        self.deviceConfigurationWidget[name] = CameraSettings(name)

        # Add the tab and show if device connected boolean is true.
        self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        index = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(self.deviceConfigurationWidget[name])
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        for device in enabledDevices:
            if device["name"] == name:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, True)
            else:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, False)
        
        # Instantiate the camera widget and add tab if enabled boolean is true.
        self.add_camera_tab(name)

        # Connections.
        self.previews[name].getImage.connect(self.manager.devices[name].capture_image)

        self.deviceConfigurationWidget[name].setImageMode.connect(self.manager.devices[name].set_image_mode)
        self.deviceConfigurationWidget[name].setAutoWhiteBalanceMode.connect(self.manager.devices[name].set_auto_white_balance_mode)
        self.deviceConfigurationWidget[name].setAutoExposureMode.connect(self.manager.devices[name].set_auto_exposure_mode)
        self.deviceConfigurationWidget[name].setExposureTime.connect(self.manager.devices[name].set_exposure_time)
        self.deviceConfigurationWidget[name].setGain.connect(self.manager.devices[name].set_gain)
        self.deviceConfigurationWidget[name].setAutoGain.connect(self.manager.devices[name].set_auto_gain)
        self.deviceConfigurationWidget[name].setBinningMode.connect(self.manager.devices[name].set_binning_mode)
        self.deviceConfigurationWidget[name].setBinning.connect(self.manager.devices[name].set_binning)
        self.deviceConfigurationWidget[name].setAcquisitionMode.connect(self.manager.devices[name].set_acquisition_mode)
        self.deviceConfigurationWidget[name].setAcquisitionRate.connect(self.manager.devices[name].set_acquisition_rate)

        self.deviceConfigurationWidget[name].calibrateButton.clicked.connect(self.manager.devices[name].calibrate)

        self.manager.devices[name].previewImage.connect(self.previews[name].set_image)

        # self.manager.devices[name].updateImageMode.connect(self.deviceConfigurationWidget[name].update_image_mode)
        self.manager.devices[name].updateExposureTime.connect(self.deviceConfigurationWidget[name].update_exposure_time)
        self.manager.devices[name].updateGain.connect(self.deviceConfigurationWidget[name].update_gain)
        self.manager.devices[name].updateImageMode.connect(self.deviceConfigurationWidget[name].update_mode)
        self.manager.devices[name].updateAcquisitionRate.connect(self.deviceConfigurationWidget[name].update_acquisition_rate)

        # Initialise settings.
        self.deviceConfigurationWidget[name].set_configuration(self.manager.configuration)
        sleep(1.0)

        # Start stream.
        self.manager.devices[name].capture_image()

        log.info("Device configuration tab added for {device}.".format(device=name))
        
    def add_LabJackT7_configuration_tab(self, name):
        # Create layout.
        self.deviceConfigurationLayout[name] = QVBoxLayout()

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
        self.manager.controlTableModels[name].controlChannelToggled.connect(self.toggle_control_channel)
        self.manager.controlTableModels[name].controlChannelToggled.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.controlTableModels[name].controlChannelNameChanged.connect(self.update_control_name)
        self.manager.controlTableModels[name].controlWidgetChanged.connect(self.change_control_widget)
        self.manager.controlTableModels[name].controlFeedbackChannelChanged.connect(self.change_control_feedback_channel)

        # Add acquisition table label.
        self.acquisitionLabel = QLabel('Acquisition')
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionLabel)

        # Add acquisition table to the TabWidget.
        self.acquisitionTableViews[name] = AcquisitionTableView()
        self.acquisitionTableViews[name].setModel(self.manager.acquisitionTableModels[name])
        self.deviceConfigurationLayout[name].addWidget(self.acquisitionTableViews[name])

        # Connections for acquisition table.
        self.manager.acquisitionTableModels[name].acquisitionChannelTableUpdated.connect(self.manager.updatePlotWindowChannelsData)
        self.manager.acquisitionTableModels[name].acquisitionChannelToggled.connect(self.update_feedback_ComboBox)
        self.manager.acquisitionTableModels[name].acquisitionChannelToggled.connect(self.update_press_feedback_channel_ComboBox)

        # Set layout within widget.
        self.deviceConfigurationWidget[name] = QWidget()
        self.deviceConfigurationWidget[name].setLayout(self.deviceConfigurationLayout[name])

        # Add the tab and show if device connected boolean is true.
        self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.addTab(self.deviceConfigurationWidget[name], name)
        index = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(self.deviceConfigurationWidget[name])
        enabledDevices = self.manager.deviceTableModel.enabledDevices()
        for device in enabledDevices:
            if device["name"] == name:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, True)
            else:
                self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, False)
        
        # Instantiate the control widgets and add tabs.
        for channel in range(self.manager.controlTableModels[name].rowCount()):
            self.add_control_tab(name, channel)

        log.info("Device configuration tab added for {device}.".format(device=name))
        
    @Slot(str, str)
    def update_control_name(self, currentName, newName):
        # Update tab names.
        for index in range(self.tabs.count()):
            if self.tabs.tabText(index) == currentName:
                self.tabs.setTabText(index, newName)

    @Slot(str, bool)
    def update_device_configuration_tab(self, name, connect):
        if name in self.deviceConfigurationWidget:
            widget = self.deviceConfigurationWidget[name]
            index = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.indexOf(widget)
            self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.setTabVisible(index, connect)

    @Slot()
    def update_feedback_ComboBox(self):
        # Get the name of the device.
        tabIndex = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.currentIndex()
        name = self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.tabText(tabIndex)

        # Create an updated feedback channel list for this device.
        feedbackChannelList = self.manager.setFeedbackChannelList(name)

        # Update feedback channel selector ComboBox.
        self.controlTableViews[name].updateFeedbackChannelList(feedbackChannelList)

    @Slot()
    def clear_device_configuration_tabs(self):
        self.configurationTab.deviceConfigurationGroupBox.deviceConfigurationTabWidget.clear()

    