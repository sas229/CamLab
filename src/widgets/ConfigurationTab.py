from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal
from widgets.GlobalSettingsGroupBox import GlobalSettingsGroupBox
from widgets.DevicesGroupBox import DevicesGroupBox
from widgets.DeviceConfigurationGroupBox import DeviceConfigurationGroupBox

class ConfigurationTab(QWidget):
    configurationWindowClosed = Signal(QWidget)

    def __init__(self, configuration):
        super().__init__()
        self.setWhatsThis("configuration")
        self.configuration = configuration
        self.configurationMainWindow = configuration["mainWindow"]

        # Global settings GroupBox.
        self.globalSettingsGroupBox = GlobalSettingsGroupBox(self.configuration)
        
        # Device table GroupBox.
        self.devicesGroupBox = DevicesGroupBox(self.configuration)

        # Device configuration Groupbox.
        self.deviceConfigurationGroupBox = DeviceConfigurationGroupBox()

        # Define layout.
        self.layout = QGridLayout()
        self.layout.addWidget(self.globalSettingsGroupBox, 1, 0, 1, 1)
        self.layout.addWidget(self.devicesGroupBox, 2, 0, 1, 1)
        self.layout.addWidget(self.deviceConfigurationGroupBox, 1, 1, 2, 1)
        self.layout.setRowStretch(self.layout.rowCount(), 1)
        self.setLayout(self.layout)

    def setWindow(self):
        x = int(self.configuration["x"])
        y = int(self.configuration["y"])
        w = int(self.configuration["width"])
        h = int(self.configuration["height"])
        self.setGeometry(x, y, w, h)
        self.configuration["mode"] = "window"

    def setTab(self):
        self.configuration["mode"] = "tab"

    def closeEvent(self, event):
        self.configurationWindowClosed.emit(self)