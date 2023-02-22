from PySide6.QtCore import Slot
from functools import partial
import logging

log = logging.getLogger(__name__)

class TabUtilities:

    def make_connections(self):
        self.specimens.valueChanged.connect(self.specimens_number)
        self.residual_shear.toggled.connect(self.shear_type)
        self.cycles.valueChanged.connect(self.residuals_number)
        self.make_hardware_tab_connections()
        self.make_specimen_tab_connections()

    def remove_connections(self):
        self.specimens.valueChanged.disconnect(self.specimens_number)
        self.residual_shear.toggled.disconnect(self.shear_type)
        self.cycles.valueChanged.disconnect(self.residuals_number)
        self.remove_hardware_tab_connections()

    def get_devices_and_channels(self):
        """Get devices and channels of each device and store in self.devices
        """
        self.devices = dict()
        if "devices" in self.configuration.keys():
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
    
    def remove_hardware_tab_connections(self):
        """Disconnect hardware tab combobox signals to slots 
        """
        self.tabs.horiz_load_ins.currentTextChanged.disconnect(self.set_horiz_load_ins)
        self.tabs.horiz_load_chan.currentTextChanged.disconnect(self.set_horiz_load_chan)
        self.tabs.horiz_disp_ins.currentTextChanged.disconnect(self.set_horiz_disp_ins)
        self.tabs.horiz_disp_chan.currentTextChanged.disconnect(self.set_horiz_disp_chan)
        self.tabs.vert_load_ins.currentTextChanged.disconnect(self.set_vert_load_ins)
        self.tabs.vert_load_chan.currentTextChanged.disconnect(self.set_vert_load_chan)
        self.tabs.vert_disp_ins.currentTextChanged.disconnect(self.set_vert_disp_ins)
        self.tabs.vert_disp_chan.currentTextChanged.disconnect(self.set_vert_disp_chan)
        self.tabs.horiz_cont_ins.currentTextChanged.disconnect(self.set_horiz_cont_ins)
        self.tabs.horiz_cont_chan.currentTextChanged.disconnect(self.set_horiz_cont_chan)
        self.tabs.vert_cont_ins.currentTextChanged.disconnect(self.set_vert_cont_ins)
        self.tabs.vert_cont_chan.currentTextChanged.disconnect(self.set_vert_cont_chan)
    
    def make_specimen_tab_connections(self):
        """Connect specimen tab signals to slots 
        """
        for i in range(1,5):
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].rectangular.toggled.connect(partial(self.shape_switch, f"Specimen {i}"))
            # self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].circular.toggled.connect(partial(self.shape_switch, f"Specimen {i}"))

    @Slot(str)
    def set_horiz_load_ins(self, device):
        """Set device to use for horizontal load measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Horizontal Load Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Load Instrument"] = None
            self.tabs.horiz_load_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_load_chan(self, channel):
        """Set channel to use for horizontal load measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Horizontal Load Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Load Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_disp_ins(self, device):
        """Set device to use for horizontal displacement measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Horizontal Displacement Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_disp_chan.clear()
            self.tabs.horiz_disp_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Displacement Instrument"] = None
            self.tabs.horiz_disp_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_disp_chan(self, channel):
        """Set channel to use for horizontal displacement measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Horizontal Displacement Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Displacement Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_load_ins(self, device):
        """Set device to use for vertical load measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Vertical Load Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_load_chan.clear()
            self.tabs.vert_load_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Load Instrument"] = None
            self.tabs.vert_load_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_load_chan(self, channel):
        """Set channel to use for vertical load measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Vertical Load Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Load Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_disp_ins(self, device):
        """Set device to use for vertical displacement measurement

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Vertical Displacement Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_disp_chan.clear()
            self.tabs.vert_disp_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Displacement Instrument"] = None
            self.tabs.vert_disp_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_disp_chan(self, channel):
        """Set channel to use for vertical displacement measurement

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Vertical Displacement Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Displacement Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_cont_ins(self, device):
        """Set device to use for horizontal control

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Horizontal Control Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_cont_chan.clear()
            self.tabs.horiz_cont_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Control Instrument"] = None
            self.tabs.horiz_cont_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_cont_chan(self, channel):
        """Set channel to use for horizontal control

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Horizontal Control Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Horizontal Control Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_cont_ins(self, device):
        """Set device to use for vertical control

        Arguments:
            device -- self.devices key
        """
        if device != "":
            self.configuration["shearbox"]["Vertical Control Instrument"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.vert_cont_chan.clear()
            self.tabs.vert_cont_chan.addItems([None] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Control Instrument"] = None
            self.tabs.vert_cont_chan.clear()
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_cont_chan(self, channel):
        """Set channel to use for vertical control

        Arguments:
            channel -- channel to use
        """
        if channel != "":
            self.configuration["shearbox"]["Vertical Control Channel"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["Vertical Control Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def shape_switch(self, specimen, _):
        if self.tabs.specimen.specimens[specimen]["dimensions"].rectangular.isChecked():
            self.configuration["shearbox"][specimen]["Shape"] = "rect"

            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].width_label1, 3, 0)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].width_label2, 3, 1)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].initial_width, 3, 2)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].width_label3, 3, 3)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].depth_label1, 4, 0)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].depth_label2, 4, 1)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].initial_depth, 4, 2)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].depth_label3, 4, 3)
            self.tabs.specimen.specimens[specimen]["dimensions"].radius_label1.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].radius_label2.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_radius.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].radius_label3.setParent(None)
        else:
            self.configuration["shearbox"][specimen]["Shape"] = "circ"

            self.tabs.specimen.specimens[specimen]["dimensions"].width_label1.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].width_label2.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_width.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].width_label3.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].depth_label1.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].depth_label2.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_depth.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].depth_label3.setParent(None)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].radius_label1, 3, 0, 2, 1)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].radius_label2, 3, 1, 2, 1)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].initial_radius, 3, 2, 2, 1)
            self.tabs.specimen.specimens[specimen]["dimensions"].Layout.addWidget(self.tabs.specimen.specimens[specimen]["dimensions"].radius_label3, 3, 3, 2, 1)