import numpy as np
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
        self.specimens.valueChanged.disconnect()
        self.residual_shear.toggled.disconnect()
        self.cycles.valueChanged.disconnect()
        self.remove_hardware_tab_connections()
        self.remove_specimen_tab_connections()

    def get_devices_and_channels(self):
        """Get devices and channels of each device and store in self.devices
        """
        self.devices = dict()
        if "devices" in self.configuration.keys():
            for device in self.configuration["devices"].keys():
                key = f'{self.configuration["devices"][device]["model"]} ({self.configuration["devices"][device]["id"]})'
                channels = [channel_info["name"] for channel_info in self.configuration["devices"][device]["acquisition"]]
                self.devices[key] = [device, channels]
    
    def addItemstoInstrumentComboboxes(self):
        """Fill instrument comboboxes in hardware tab with device names
        """
            
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
        self.tabs.horiz_disp_ins.currentTextChanged.connect(self.set_horiz_disp_ins)
        self.tabs.vert_load_ins.currentTextChanged.connect(self.set_vert_load_ins)
        self.tabs.vert_disp_ins.currentTextChanged.connect(self.set_vert_disp_ins)
        self.tabs.horiz_cont_ins.currentTextChanged.connect(self.set_horiz_cont_ins)
        self.tabs.vert_cont_ins.currentTextChanged.connect(self.set_vert_cont_ins)
    
    def remove_hardware_tab_connections(self):
        """Disconnect hardware tab combobox signals to slots 
        """
        self.tabs.horiz_load_ins.currentTextChanged.disconnect()
        self.tabs.horiz_disp_ins.currentTextChanged.disconnect()
        self.tabs.vert_load_ins.currentTextChanged.disconnect()
        self.tabs.vert_disp_ins.currentTextChanged.disconnect()
        self.tabs.horiz_cont_ins.currentTextChanged.disconnect()
        self.tabs.vert_cont_ins.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Horizontal Load Instrument"] != None:
            self.tabs.horiz_load_chan.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Instrument"] != None:
            self.tabs.horiz_disp_chan.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Vertical Load Instrument"] != None:
            self.tabs.vert_load_chan.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Vertical Displacement Instrument"] != None:
            self.tabs.vert_disp_chan.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Horizontal Control Instrument"] != None:
            self.tabs.horiz_cont_chan.currentTextChanged.disconnect()
        if self.configuration["shearbox"]["Hardware"]["Vertical Control Instrument"] != None:
            self.tabs.vert_cont_chan.currentTextChanged.disconnect()
    
    def make_specimen_tab_connections(self):
        """Connect specimen tab signals to slots 
        """
        for i in range(1,5):
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].rectangular.toggled.connect(partial(self.shape_switch, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_weight.returnPressed.connect(partial(self.set_weight, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_height.returnPressed.connect(partial(self.set_height, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_width.returnPressed.connect(partial(self.set_width, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_depth.returnPressed.connect(partial(self.set_depth, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_radius.returnPressed.connect(partial(self.set_radius, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].particle_density.returnPressed.connect(partial(self.set_density, f"Specimen {i}"))
    
    def remove_specimen_tab_connections(self):
        """Connect specimen tab signals to slots 
        """
        for i in range(1,5):
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].rectangular.toggled.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_weight.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_height.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_width.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_depth.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_radius.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].particle_density.returnPressed.disconnect()

    @Slot(str)
    def set_horiz_load_ins(self, device, apply_config=False):
        """Set device to use for horizontal load measurement

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Load Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_load_chan.clear()
                self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
            else:
                self.configuration["shearbox"]["Horizontal Load Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_load_chan.currentTextChanged.disconnect(self.set_horiz_load_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Horizontal Load Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_disp_ins(self, device, apply_config=False):
        """Set device to use for horizontal displacement measurement

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Displacement Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_disp_chan.clear()
                self.tabs.horiz_disp_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_disp_chan.currentTextChanged.connect(self.set_horiz_disp_chan)
            else:
                self.configuration["shearbox"]["Horizontal Displacement Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_disp_chan.currentTextChanged.disconnect(self.set_horiz_disp_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Horizontal Displacement Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_load_ins(self, device, apply_config=False):
        """Set device to use for vertical load measurement

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Load Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_load_chan.clear()
                self.tabs.vert_load_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_load_chan.currentTextChanged.connect(self.set_vert_load_chan)
            else:
                self.configuration["shearbox"]["Vertical Load Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_load_chan.currentTextChanged.disconnect(self.set_vert_load_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Vertical Load Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_disp_ins(self, device, apply_config=False):
        """Set device to use for vertical displacement measurement

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Displacement Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_disp_chan.clear()
                self.tabs.vert_disp_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_disp_chan.currentTextChanged.connect(self.set_vert_disp_chan)
            else:
                self.configuration["shearbox"]["Vertical Displacement Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_disp_chan.currentTextChanged.disconnect(self.set_vert_disp_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Vertical Displacement Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_horiz_cont_ins(self, device, apply_config=False):
        """Set device to use for horizontal control

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Control Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_cont_chan.clear()
                self.tabs.horiz_cont_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_cont_chan.currentTextChanged.connect(self.set_horiz_cont_chan)
            else:
                self.configuration["shearbox"]["Horizontal Control Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_cont_chan.currentTextChanged.disconnect(self.set_horiz_cont_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Horizontal Control Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def set_vert_cont_ins(self, device, apply_config=False):
        """Set device to use for vertical control

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Control Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_cont_chan.clear()
                self.tabs.vert_cont_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_cont_chan.currentTextChanged.connect(self.set_vert_cont_chan)
            else:
                self.configuration["shearbox"]["Vertical Control Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_cont_chan.currentTextChanged.disconnect(self.set_vert_cont_chan)
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
            log.info("Channel deselected / No channel selected")
            self.configuration["shearbox"]["Vertical Control Channel"] = None
        self.configurationChanged.emit(self.configuration)

    @Slot(str)
    def shape_switch(self, specimen, _=None):
        if self.tabs.specimen.specimens[specimen]["dimensions"].rectangular.isChecked():
            self.configuration["shearbox"]["Specimens"][specimen]["Shape"] = "rectangular"

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

            weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
            height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
            width = self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"]
            depth = self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"]

            if not (None in [width, depth]):
                area = width * depth / 100
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))
            else:
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText("")
            if not (None in [height, width, depth]):
                volume = height * width * depth / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            else:
                volume = None
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText("")

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
        else:
            self.configuration["shearbox"]["Specimens"][specimen]["Shape"] = "circular"

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

            weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
            height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
            radius = self.configuration["shearbox"]["Specimens"][specimen]["Initial Radius"]

            if radius != None:
                area = np.pi * radius**2 / 100
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))
            else:
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText("")
            if not (None in [height, radius]):
                volume = height * np.pi * radius**2 / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            else:
                volume = None
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText("")

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))

            
    @Slot(str)
    def set_weight(self, specimen):
        weight = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_weight.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"] = weight

        log.info(f'Set {specimen} initial weight to {weight}.')        

        volume = self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"]

        if not (None in [weight, volume]):
            bulk_density = weight / volume
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
        
            log.info(f'Set {specimen} initial bulk density to {bulk_density}.')

            
    @Slot(str)
    def set_height(self, specimen):
        height = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_height.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"] = height

        log.info(f'Set {specimen} initial height to {height}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        width = self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"]
        depth = self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"]
        radius = self.configuration["shearbox"]["Specimens"][specimen]["Initial Radius"]
        rect = (self.configuration["shearbox"]["Specimens"][specimen]["Shape"] == "rectangular")

        if (not (None in [height, width, depth]) and rect) or (not (None in [height, radius]) and not rect):
            if not (None in [height, width, depth]) and rect:
                volume = height * width * depth / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            else:
                volume = height * np.pi * radius**2 / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            
            log.info(f'Set {specimen} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen} initial bulk density to {bulk_density}.')
            
    @Slot(str)
    def set_width(self, specimen):
        width = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_width.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"] = width

        log.info(f'Set {specimen} initial width to {width}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
        depth = self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"]

        if not (None in [width, depth]):
            area = width * depth / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen} initial area to {area}.')
        if not (None in [height, width, depth]):
            volume = height * width * depth / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen} initial bulk density to {bulk_density}.')
            
    @Slot(str)
    def set_depth(self, specimen):
        depth = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_depth.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"] = depth

        log.info(f'Set {specimen} initial depth to {depth}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
        width = self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"]

        if not (None in [width, depth]):
            area = width * depth / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen} initial area to {area}.')
        if not (None in [height, width, depth]):
            volume = height * width * depth / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen} initial bulk density to {bulk_density}.')
            
    @Slot(str)
    def set_radius(self, specimen):
        radius = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_radius.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Radius"] = radius

        log.info(f'Set {specimen} initial radius to {radius}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]

        if radius != None:
            area = np.pi * radius**2 / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen} initial area to {area}.')
        if not (None in [height, radius]):
            volume = height * np.pi * radius**2 / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen} initial bulk density to {bulk_density}.')
            
    @Slot(str)
    def set_density(self, specimen):
        particle_density = float(self.tabs.specimen.specimens[specimen]["dimensions"].particle_density.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Particle Density"] = particle_density

        log.info(f'Set {specimen} particle density to {particle_density}.')