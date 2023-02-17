from PySide6.QtCore import Slot
import logging

log = logging.getLogger(__name__)

class TabUtilities:

    def get_devices_and_channels(self):
        """Get devices and channels of each device and store in self.devices
        """
        self.devices = dict()
        for device in self.configuration["devices"].keys():
            key = f'{self.configuration["devices"][device]["model"]} ({self.configuration["devices"][device]["id"]})'
            channels = [channel_info["name"] for channel_info in self.configuration["devices"][device]["acquisition"]]
            self.devices[key] = [device, channels]
    
    def addItemstoComboboxes(self):
        """Fill comboboxes in hardware tab with device names
        """
        self.get_devices_and_channels()
            
        self.tabs.horiz_load_ins.clear()
        self.tabs.horiz_load_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.horiz_load_chan.clear()
        self.tabs.horiz_disp_ins.clear()
        self.tabs.horiz_disp_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.horiz_disp_chan.clear()
        self.tabs.vert_load_ins.clear()
        self.tabs.vert_load_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_load_chan.clear()
        self.tabs.vert_disp_ins.clear()
        self.tabs.vert_disp_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_disp_chan.clear()
        self.tabs.horiz_cont_ins.clear()
        self.tabs.horiz_cont_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.horiz_cont_chan.clear()
        self.tabs.vert_cont_ins.clear()
        self.tabs.vert_cont_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_cont_chan.clear()
    
    def make_hardware_tab_connections(self):
        """Connect hardware tab combobox signals to slots 
        """
        self.tabs.horiz_load_ins.currentTextChanged.connect(self.set_horiz_load_ins)
        self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        self.tabs.horiz_disp_ins.currentTextChanged.connect(self.set_horiz_disp_ins)
        self.tabs.horiz_disp_chan.currentTextChanged.connect(self.set_horiz_disp_chan)
        self.tabs.vert_load_ins.currentTextChanged.connect(self.set_vert_load_ins)
        self.tabs.vert_load_chan.currentTextChanged.connect(self.set_vert_load_chan)
        self.tabs.vert_disp_ins.currentTextChanged.connect(self.set_vert_disp_ins)
        self.tabs.vert_disp_chan.currentTextChanged.connect(self.set_vert_disp_chan)
        self.tabs.horiz_cont_ins.currentTextChanged.connect(self.set_horiz_cont_ins)
        self.tabs.horiz_cont_chan.currentTextChanged.connect(self.set_horiz_cont_chan)
        self.tabs.vert_cont_ins.currentTextChanged.connect(self.set_vert_cont_ins)
        self.tabs.vert_cont_chan.currentTextChanged.connect(self.set_vert_cont_chan)

    @Slot(str)
    def set_horiz_load_ins(self, device):
        """Set device to use for horizontal load measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["horiz_load_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_ins"] = None
            self.tabs.horiz_load_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_horiz_load_chan(self, channel):
        """Set channel to use for horizontal load measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    @Slot(str)
    def set_horiz_disp_ins(self, device):
        """Set device to use for horizontal displacement measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["horiz_disp_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_disp_chan.clear()
            self.tabs.horiz_disp_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_disp_ins"] = None
            self.tabs.horiz_disp_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_horiz_disp_chan(self, channel):
        """Set channel to use for horizontal displacement measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    @Slot(str)
    def set_vert_load_ins(self, device):
        """Set device to use for vertical load measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["vert_load_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_load_chan.clear()
            self.tabs.vert_load_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["vert_load_ins"] = None
            self.tabs.vert_load_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_vert_load_chan(self, channel):
        """Set channel to use for vertical load measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    @Slot(str)
    def set_vert_disp_ins(self, device):
        """Set device to use for vertical displacement measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["vert_disp_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_disp_chan.clear()
            self.tabs.vert_disp_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["vert_disp_ins"] = None
            self.tabs.vert_disp_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_vert_disp_chan(self, channel):
        """Set channel to use for vertical displacement measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    @Slot(str)
    def set_horiz_cont_ins(self, device):
        """Set device to use for horizontal control

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["horiz_cont_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_cont_chan.clear()
            self.tabs.horiz_cont_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_cont_ins"] = None
            self.tabs.horiz_cont_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_horiz_cont_chan(self, channel):
        """Set channel to use for horizontal control

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    @Slot(str)
    def set_vert_cont_ins(self, device):
        """Set device to use for vertical control

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["vert_cont_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_cont_chan.clear()
            self.tabs.vert_cont_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["vert_cont_ins"] = None
            self.tabs.vert_cont_chan.clear()
        self.update_configuration()

    @Slot(str)
    def set_vert_cont_chan(self, channel):
        """Set channel to use for vertical control

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()