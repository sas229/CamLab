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
        self.make_consolidation_tab_connections()
        self.make_shear_tab_connections()

    def remove_connections(self):
        self.specimens.valueChanged.disconnect()
        self.residual_shear.toggled.disconnect()
        self.cycles.valueChanged.disconnect()
        self.remove_hardware_tab_connections()
        self.remove_specimen_tab_connections()
        self.remove_consolidation_tab_connections()
        self.remove_shear_tab_connections()
    
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
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].rectangular.toggled.connect(partial(self.set_rectangular_shape, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].circular.toggled.connect(partial(self.set_circular_shape, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_weight.returnPressed.connect(partial(self.set_weight, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_height.returnPressed.connect(partial(self.set_height, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_width.returnPressed.connect(partial(self.set_width, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_depth.returnPressed.connect(partial(self.set_depth, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_radius.returnPressed.connect(partial(self.set_radius, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].particle_density.returnPressed.connect(partial(self.set_density, f"Specimen {i}"))
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_wet_weight.returnPressed.connect(partial(self.set_wet_weight, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_dry_weight.returnPressed.connect(partial(self.set_dry_weight, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].tin_initial_weight.returnPressed.connect(partial(self.set_tin_weight, f"Specimen {i}"))
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_weight.returnPressed.connect(partial(self.set_platen_weight, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_corr.returnPressed.connect(partial(self.set_platen_corr, f"Specimen {i}"))
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].est_strain_at_fail.returnPressed.connect(partial(self.set_est_strain_at_fail, f"Specimen {i}"))
    
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
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_wet_weight.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_dry_weight.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].tin_initial_weight.returnPressed.disconnect()
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_weight.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_corr.returnPressed.disconnect()
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].est_strain_at_fail.returnPressed.disconnect()

    def make_consolidation_tab_connections(self):
        """Connect consolidation tab signals to slots 
        """
        self.tabs.consolidation_start_stress.returnPressed.connect(self.set_consolidation_start_stress)
        self.tabs.consolidation_trigger_stress_select.toggled.connect(self.set_consolidation_trigger_stress_select)
        self.tabs.consolidation_trigger_stress.returnPressed.connect(self.set_consolidation_trigger_stress)
        self.tabs.consolidation_trigger_disp_select.toggled.connect(self.set_consolidation_trigger_disp_select)
        self.tabs.consolidation_trigger_disp.returnPressed.connect(self.set_consolidation_trigger_disp)
        self.tabs.consolidation_in_water.toggled.connect(self.set_consolidation_in_water)

        self.tabs.consolidation_log_rate_radio.toggled.connect(self.set_consolidation_log_rate_radio)
        self.tabs.consolidation_log_rate_val.returnPressed.connect(self.set_consolidation_log_rate_val)
        self.tabs.consolidation_log_timetable_radio.toggled.connect(self.set_consolidation_log_timetable_radio)
        self.tabs.consolidation_log_timetable_opt.currentTextChanged.connect(self.set_consolidation_log_timetable_opt)
        self.tabs.consolidation_log_change_radio.toggled.connect(self.set_consolidation_log_change_radio)
        self.tabs.consolidation_log_change_val.returnPressed.connect(self.set_consolidation_log_change_val)

        self.tabs.consolidation_stop_rate_select.toggled.connect(self.set_consolidation_stop_rate_select)
        self.tabs.consolidation_stop_rate_disp.returnPressed.connect(self.set_consolidation_stop_rate_disp)
        self.tabs.consolidation_stop_rate_time.returnPressed.connect(self.set_consolidation_stop_rate_time)
        self.tabs.consolidation_stop_time_select.toggled.connect(self.set_consolidation_stop_time_select)
        self.tabs.consolidation_stop_time_opt.returnPressed.connect(self.set_consolidation_stop_time_opt)
        self.tabs.consolidation_stop_buzz.toggled.connect(self.set_consolidation_stop_buzz)

    def remove_consolidation_tab_connections(self):
        """Disconnect consolidation tab signals to slots 
        """
        self.tabs.consolidation_start_stress.returnPressed.disconnect()
        self.tabs.consolidation_trigger_stress_select.toggled.disconnect()
        self.tabs.consolidation_trigger_stress.returnPressed.disconnect()
        self.tabs.consolidation_trigger_disp_select.toggled.disconnect()
        self.tabs.consolidation_trigger_disp.returnPressed.disconnect()
        self.tabs.consolidation_in_water.toggled.disconnect()

        self.tabs.consolidation_log_rate_radio.toggled.disconnect()
        self.tabs.consolidation_log_rate_val.returnPressed.disconnect()
        self.tabs.consolidation_log_timetable_opt.currentTextChanged.disconnect()
        self.tabs.consolidation_log_change_val.returnPressed.disconnect()

        self.tabs.consolidation_stop_rate_select.toggled.disconnect()
        self.tabs.consolidation_stop_rate_disp.returnPressed.disconnect()
        self.tabs.consolidation_stop_rate_time.returnPressed.disconnect()
        self.tabs.consolidation_stop_time_select.toggled.disconnect()
        self.tabs.consolidation_stop_time_opt.returnPressed.disconnect()
        self.tabs.consolidation_stop_buzz.toggled.disconnect()
    
    def make_shear_tab_connections(self):
        """Connect shear tab signals to slots 
        """
        for i in range(1,11): 
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed_select"].toggled.connect(partial(self.set_shear_trigger_speed_select, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed"].returnPressed.connect(partial(self.set_shear_trigger_speed, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_select"].toggled.connect(partial(self.set_shear_trigger_calc_select, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_opt"].currentTextChanged.connect(partial(self.set_shear_trigger_calc_opt, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_select"].toggled.connect(partial(self.set_shear_trigger_load_select, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_change"].returnPressed.connect(partial(self.set_shear_trigger_load_change, f"Cycle {i}"))

            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_radio"].toggled.connect(partial(self.set_shear_store_rate_radio, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_val"].returnPressed.connect(partial(self.set_shear_store_rate_val, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_radio"].toggled.connect(partial(self.set_shear_store_strain_radio, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_val"].returnPressed.connect(partial(self.set_shear_store_strain_val, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_radio"].toggled.connect(partial(self.set_shear_store_disp_radio, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_val"].returnPressed.connect(partial(self.set_shear_store_disp_val, f"Cycle {i}"))

            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop_select"].toggled.connect(partial(self.set_shear_stop_drop_select, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop"].valueChanged.connect(partial(self.set_shear_stop_drop, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain_select"].toggled.connect(partial(self.set_shear_stop_strain_select, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain"].returnPressed.connect(partial(self.set_shear_stop_strain, f"Cycle {i}"))

            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_radio"].toggled.connect(partial(self.set_shear_reverse_rate_radio, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_val"].returnPressed.connect(partial(self.set_shear_reverse_rate_val, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_same"].toggled.connect(partial(self.set_shear_reverse_same, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_wait"].returnPressed.connect(partial(self.set_shear_reverse_wait, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_disp"].returnPressed.connect(partial(self.set_shear_reverse_disp, f"Cycle {i}"))
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_stress"].returnPressed.connect(partial(self.set_shear_reverse_stress, f"Cycle {i}"))
    
    def remove_shear_tab_connections(self):
        """Disconnect shear tab signals to slots 
        """
        for i in range(1,11): 
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed_select"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_select"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_opt"].currentTextChanged.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_select"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_change"].returnPressed.disconnect()

            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_radio"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_val"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_radio"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_val"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_radio"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_val"].returnPressed.disconnect()

            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop_select"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop"].valueChanged.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain_select"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain"].returnPressed.disconnect()

            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_radio"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_val"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_same"].toggled.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_wait"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_disp"].returnPressed.disconnect()
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_stress"].returnPressed.disconnect()
            
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
        self.tabs.horiz_load_chan.setEnabled(False)
        self.tabs.horiz_disp_ins.clear()
        self.tabs.horiz_disp_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.horiz_disp_chan.clear()
        self.tabs.horiz_disp_chan.setEnabled(False)
        self.tabs.vert_load_ins.clear()
        self.tabs.vert_load_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_load_chan.clear()
        self.tabs.vert_load_chan.setEnabled(False)
        self.tabs.vert_disp_ins.clear()
        self.tabs.vert_disp_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_disp_chan.clear()
        self.tabs.vert_disp_chan.setEnabled(False)
        self.tabs.horiz_cont_ins.clear()
        self.tabs.horiz_cont_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.horiz_cont_chan.clear()
        self.tabs.horiz_cont_chan.setEnabled(False)
        self.tabs.vert_cont_ins.clear()
        self.tabs.vert_cont_ins.addItems([None] + list(self.devices.keys()))
        self.tabs.vert_cont_chan.clear()
        self.tabs.vert_cont_chan.setEnabled(False)

    @Slot(str)
    def set_horiz_load_ins(self, device, apply_config=False):
        """Set device to use for horizontal load measurement

        Arguments:
            device -- self.devices key
        """
        if apply_config:
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.setEnabled(True)
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Load Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_load_chan.setEnabled(True)
                self.tabs.horiz_load_chan.clear()
                self.tabs.horiz_load_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
            else:
                self.configuration["shearbox"]["Horizontal Load Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_load_chan.currentTextChanged.disconnect()
                self.tabs.horiz_load_chan.clear()
                self.tabs.horiz_load_chan.setEnabled(False)
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
            self.tabs.horiz_disp_chan.setEnabled(True)
            self.tabs.horiz_disp_chan.clear()
            self.tabs.horiz_disp_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_disp_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Displacement Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_disp_chan.setEnabled(True)
                self.tabs.horiz_disp_chan.clear()
                self.tabs.horiz_disp_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_disp_chan.currentTextChanged.connect(self.set_horiz_disp_chan)
            else:
                self.configuration["shearbox"]["Horizontal Displacement Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_disp_chan.currentTextChanged.disconnect()
                self.tabs.horiz_disp_chan.clear()
                self.tabs.horiz_disp_chan.setEnabled(False)
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
            self.tabs.vert_load_chan.setEnabled(True)
            self.tabs.vert_load_chan.clear()
            self.tabs.vert_load_chan.addItems([None] + self.devices[device][1])
            self.tabs.vert_load_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Load Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_load_chan.setEnabled(True)
                self.tabs.vert_load_chan.clear()
                self.tabs.vert_load_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_load_chan.currentTextChanged.connect(self.set_vert_load_chan)
            else:
                self.configuration["shearbox"]["Vertical Load Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_load_chan.currentTextChanged.disconnect()
                self.tabs.vert_load_chan.clear()
                self.tabs.vert_load_chan.setEnabled(False)
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
            self.tabs.vert_disp_chan.setEnabled(True)
            self.tabs.vert_disp_chan.clear()
            self.tabs.vert_disp_chan.addItems([None] + self.devices[device][1])
            self.tabs.vert_disp_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Displacement Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_disp_chan.setEnabled(True)
                self.tabs.vert_disp_chan.clear()
                self.tabs.vert_disp_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_disp_chan.currentTextChanged.connect(self.set_vert_disp_chan)
            else:
                self.configuration["shearbox"]["Vertical Displacement Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_disp_chan.currentTextChanged.disconnect()
                self.tabs.vert_disp_chan.clear()
                self.tabs.vert_disp_chan.setEnabled(False)
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
            self.tabs.horiz_cont_chan.setEnabled(True)
            self.tabs.horiz_cont_chan.clear()
            self.tabs.horiz_cont_chan.addItems([None] + self.devices[device][1])
            self.tabs.horiz_cont_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Horizontal Control Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.horiz_cont_chan.setEnabled(True)
                self.tabs.horiz_cont_chan.clear()
                self.tabs.horiz_cont_chan.addItems([None] + self.devices[device][1])
                self.tabs.horiz_cont_chan.currentTextChanged.connect(self.set_horiz_cont_chan)
            else:
                self.configuration["shearbox"]["Horizontal Control Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.horiz_cont_chan.currentTextChanged.disconnect()
                self.tabs.horiz_cont_chan.clear()
                self.tabs.horiz_cont_chan.setEnabled(False)
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
            self.tabs.vert_cont_chan.setEnabled(True)
            self.tabs.vert_cont_chan.clear()
            self.tabs.vert_cont_chan.addItems([None] + self.devices[device][1])
            self.tabs.vert_cont_chan.currentTextChanged.connect(self.set_horiz_load_chan)
        else:
            if device != "":
                self.configuration["shearbox"]["Vertical Control Instrument"] = self.devices[device][0]
                log.info(f"Device selected: {device}")
                self.tabs.vert_cont_chan.setEnabled(True)
                self.tabs.vert_cont_chan.clear()
                self.tabs.vert_cont_chan.addItems([None] + self.devices[device][1])
                self.tabs.vert_cont_chan.currentTextChanged.connect(self.set_vert_cont_chan)
            else:
                self.configuration["shearbox"]["Vertical Control Instrument"] = None
                log.info("Device deselected / No device selected")
                self.tabs.vert_cont_chan.currentTextChanged.disconnect()
                self.tabs.vert_cont_chan.clear()
                self.tabs.vert_cont_chan.setEnabled(False)
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

    def shape_switch(self, specimen):
        self.set_rectangular_shape(specimen, self.tabs.specimen.specimens[specimen]["dimensions"].rectangular.isChecked())
        self.set_circular_shape(specimen, self.tabs.specimen.specimens[specimen]["dimensions"].circular.isChecked())

    @Slot(str)
    def set_rectangular_shape(self, specimen, checked):
        if checked:
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

    @Slot(str)
    def set_circular_shape(self, specimen, checked):
        if checked:
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

        log.info(f'Set {specimen.lower()} initial weight to {weight}.')        

        volume = self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"]
        moisture = self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"]

        if not (None in [weight, volume]):
            bulk_density = weight / volume
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
        
            log.info(f'Set {specimen.lower()} initial bulk density to {bulk_density}.')
        
            if not (None in [moisture, bulk_density]):
                dry_density = bulk_density / (1 + moisture/100)
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
            else:
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")

            
    @Slot(str)
    def set_height(self, specimen):
        height = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_height.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"] = height

        log.info(f'Set {specimen.lower()} initial height to {height}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        width = self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"]
        depth = self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"]
        radius = self.configuration["shearbox"]["Specimens"][specimen]["Initial Radius"]
        rect = (self.configuration["shearbox"]["Specimens"][specimen]["Shape"] == "rectangular")
        moisture = self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"]

        if (not (None in [height, width, depth]) and rect) or (not (None in [height, radius]) and not rect):
            if not (None in [height, width, depth]) and rect:
                volume = height * width * depth / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            else:
                volume = height * np.pi * radius**2 / 1000
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))
            
            log.info(f'Set {specimen.lower()} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial bulk density to {bulk_density}.')
        
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
                else:
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
    @Slot(str)
    def set_width(self, specimen):
        width = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_width.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"] = width

        log.info(f'Set {specimen.lower()} initial width to {width}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
        depth = self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"]
        moisture = self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"]

        if not (None in [width, depth]):
            area = width * depth / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen.lower()} initial area to {area}.')
        if not (None in [height, width, depth]):
            volume = height * width * depth / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen.lower()} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial bulk density to {bulk_density}.')
        
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
                else:
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
    @Slot(str)
    def set_depth(self, specimen):
        depth = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_depth.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Depth"] = depth

        log.info(f'Set {specimen.lower()} initial depth to {depth}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
        width = self.configuration["shearbox"]["Specimens"][specimen]["Initial Width"]
        moisture = self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"]

        if not (None in [width, depth]):
            area = width * depth / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen.lower()} initial area to {area}.')
        if not (None in [height, width, depth]):
            volume = height * width * depth / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen.lower()} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial bulk density to {bulk_density}.')
        
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
                else:
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
    @Slot(str)
    def set_radius(self, specimen):
        radius = float(self.tabs.specimen.specimens[specimen]["dimensions"].initial_radius.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Radius"] = radius

        log.info(f'Set {specimen.lower()} initial radius to {radius}.')

        weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Weight"]
        height = self.configuration["shearbox"]["Specimens"][specimen]["Initial Height"]
        moisture = self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"]

        if radius != None:
            area = np.pi * radius**2 / 100
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Area"] = area
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_area.setText(str(round(area, 3)))

            log.info(f'Set {specimen.lower()} initial area to {area}.')

        if not (None in [height, radius]):
            volume = height * np.pi * radius**2 / 1000
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Volume"] = volume
            self.tabs.specimen.specimens[specimen]["dimensions"].initial_volume.setText(str(round(volume, 3)))

            log.info(f'Set {specimen.lower()} initial volume to {volume}.')

            if not (None in [weight, volume]):
                bulk_density = weight / volume
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"] = bulk_density
                self.tabs.specimen.specimens[specimen]["dimensions"].initial_bulk_density.setText(str(round(bulk_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial bulk density to {bulk_density}.')
        
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
                else:
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")

    @Slot(str)
    def set_density(self, specimen):
        particle_density = float(self.tabs.specimen.specimens[specimen]["dimensions"].particle_density.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Particle Density"] = particle_density

        log.info(f'Set {specimen.lower()} particle density to {particle_density}.')
            
    @Slot(str)
    def set_wet_weight(self, specimen):
        wet_weight = float(self.tabs.specimen.specimens[specimen]["moisture"].initial_wet_weight.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Wet Weight"] = wet_weight

        log.info(f'Set {specimen.lower()} initial wet weight to {wet_weight}.')

        bulk_density = self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"]
        dry_weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Weight"]
        tin_weight = self.configuration["shearbox"]["Specimens"][specimen]["Tin (initial) Weight"]

        try:
            moisture = ((wet_weight - tin_weight) / (dry_weight - tin_weight) - 1) * 100
            assert (moisture >= 0 and moisture <= 100)
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"] = moisture
            self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText(str(round(moisture, 1)))
        
            log.info(f'Set {specimen.lower()} initial moisture to {moisture}.')
        
            if not (None in [moisture, bulk_density]):
                dry_density = bulk_density / (1 + moisture/100)
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
            
                log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
            else:
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("") 
        except:
            moisture = None
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"] = None
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = None
            self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText("")
            self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
        if not (None in [moisture, bulk_density]):
            voids_ratio = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Voids Ratio"] = voids_ratio
            self.tabs.specimen.specimens[specimen]["moisture"].initial_voids_ratio.setText(str(round(voids_ratio, 3)))
        
            log.info(f'Set {specimen.lower()} initial voids ratio to {voids_ratio}.')
            
        if not (None in [moisture, bulk_density]):
            deg_of_sat = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Degree of Saturation"] = deg_of_sat
            self.tabs.specimen.specimens[specimen]["moisture"].initial_deg_of_sat.setText(str(round(deg_of_sat, 1)))
        
            log.info(f'Set {specimen.lower()} initial degree of saturation to {deg_of_sat}.')
            
    @Slot(str)
    def set_dry_weight(self, specimen):
        dry_weight = float(self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_weight.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Weight"] = dry_weight

        log.info(f'Set {specimen.lower()} initial dry weight to {dry_weight}.')

        bulk_density = self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"]
        wet_weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Wet Weight"]
        tin_weight = self.configuration["shearbox"]["Specimens"][specimen]["Tin (initial) Weight"]

        if not (None in [dry_weight, tin_weight]):
            moisture = ((wet_weight - tin_weight) / (dry_weight - tin_weight) - 1) * 100
            if moisture >= 0 and moisture <= 100:
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"] = moisture
                self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText(str(round(moisture, 1)))
            
                log.info(f'Set {specimen.lower()} initial moisture to {moisture}.')
            
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
            else:
                moisture = None
                self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText("")
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
        else:
            moisture = None
            self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText("")
            self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
        if not (None in [moisture, bulk_density]):
            voids_ratio = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Voids Ratio"] = voids_ratio
            self.tabs.specimen.specimens[specimen]["moisture"].initial_voids_ratio.setText(str(round(voids_ratio, 3)))
        
            log.info(f'Set {specimen.lower()} initial voids ratio to {voids_ratio}.')
            
        if not (None in [moisture, bulk_density]):
            deg_of_sat = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Degree of Saturation"] = deg_of_sat
            self.tabs.specimen.specimens[specimen]["moisture"].initial_deg_of_sat.setText(str(round(deg_of_sat, 1)))
        
            log.info(f'Set {specimen.lower()} initial degree of saturation to {deg_of_sat}.')
            
    @Slot(str)
    def set_tin_weight(self, specimen):
        tin_weight = float(self.tabs.specimen.specimens[specimen]["moisture"].tin_initial_weight.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Tin (initial) Weight"] = tin_weight

        log.info(f'Set {specimen.lower()} tin (initial) weight to {tin_weight}.')

        bulk_density = self.configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"]
        wet_weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Wet Weight"]
        dry_weight = self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Weight"]

        if not (None in [dry_weight, tin_weight]):
            moisture = ((wet_weight - tin_weight) / (dry_weight - tin_weight) - 1) * 100
            if moisture >= 0 and moisture <= 100:
                self.configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"] = moisture
                self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText(str(round(moisture, 1)))
            
                log.info(f'Set {specimen.lower()} initial moisture to {moisture}.')
            
                if not (None in [moisture, bulk_density]):
                    dry_density = bulk_density / (1 + moisture/100)
                    self.configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"] = dry_density
                    self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText(str(round(dry_density, 3)))
                
                    log.info(f'Set {specimen.lower()} initial dry density to {dry_density}.')
            else:
                moisture = None
                self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText("")
                self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
        else:
            moisture = None
            self.tabs.specimen.specimens[specimen]["moisture"].initial_moisture.setText("")
            self.tabs.specimen.specimens[specimen]["moisture"].initial_dry_density.setText("")
            
        if not (None in [moisture, bulk_density]):
            voids_ratio = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Voids Ratio"] = voids_ratio
            self.tabs.specimen.specimens[specimen]["moisture"].initial_voids_ratio.setText(str(round(voids_ratio, 3)))
        
            log.info(f'Set {specimen.lower()} initial voids ratio to {voids_ratio}.')
            
        if not (None in [moisture, bulk_density]):
            deg_of_sat = 2
            self.configuration["shearbox"]["Specimens"][specimen]["Initial Degree of Saturation"] = deg_of_sat
            self.tabs.specimen.specimens[specimen]["moisture"].initial_deg_of_sat.setText(str(round(deg_of_sat, 1)))
        
            log.info(f'Set {specimen.lower()} initial degree of saturation to {deg_of_sat}.')

    @Slot(str)
    def set_platen_weight(self, specimen):
        platen_weight = float(self.tabs.specimen.specimens[specimen]["additional"].platen_weight.text())
        self.configuration["shearbox"]["Specimens"][specimen]["platen_weight"] = platen_weight

        log.info(f'Set {specimen.lower()} platen weight to {platen_weight}.')

    @Slot(str)
    def set_platen_corr(self, specimen):
        platen_corr = float(self.tabs.specimen.specimens[specimen]["additional"].platen_corr.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Platen Correction"] = platen_corr

        log.info(f'Set {specimen.lower()} platen correction to {platen_corr}.')

    @Slot(str)
    def set_est_strain_at_fail(self, specimen):
        est_strain_at_fail = float(self.tabs.specimen.specimens[specimen]["additional"].est_strain_at_fail.text())
        self.configuration["shearbox"]["Specimens"][specimen]["Estimated Strain at Shear Failure"] = est_strain_at_fail

        log.info(f'Set {specimen.lower()} estimated strain at shear failure to {est_strain_at_fail}.')

    def consolidation_selections(self):
        self.set_consolidation_trigger_stress_select(self.tabs.consolidation_trigger_stress_select.isChecked())
        self.set_consolidation_trigger_disp_select(self.tabs.consolidation_trigger_disp_select.isChecked())
        self.set_consolidation_log_rate_radio(self.tabs.consolidation_log_rate_radio.isChecked())
        self.set_consolidation_log_timetable_radio(self.tabs.consolidation_log_timetable_radio.isChecked())
        self.set_consolidation_log_change_radio(self.tabs.consolidation_log_change_radio.isChecked())
        self.set_consolidation_stop_rate_select(self.tabs.consolidation_stop_rate_select.isChecked())
        self.set_consolidation_stop_time_select(self.tabs.consolidation_stop_time_select.isChecked())

    @Slot()
    def set_consolidation_start_stress(self):
        stress = float(self.tabs.consolidation_start_stress.text())
        self.configuration["shearbox"]["Consolidation"]["Initial Stress"] = stress

        log.info(f'Set consolidation stage initial stress to {stress}.')

    @Slot(bool)
    def set_consolidation_trigger_stress_select(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Stress"] = checked

        self.tabs.consolidation_trigger_stress.setEnabled(checked)

        if not (checked or self.tabs.consolidation_trigger_disp_select.isChecked()):
            self.tabs.consolidation_trigger_disp.setEnabled(True)
            self.tabs.consolidation_trigger_disp_select.setChecked(True)
            self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Displacement"] = True

        log.info(f'Set consolidation stage trigger logging at stress to {checked}.')
    
    @Slot()
    def set_consolidation_trigger_stress(self):
        stress = float(self.tabs.consolidation_trigger_stress.text())
        self.configuration["shearbox"]["Consolidation"]["Trigger Stress"] = stress

        log.info(f'Set consolidation stage trigger stress to {stress}.')

    @Slot(bool)
    def set_consolidation_trigger_disp_select(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Displacement"] = checked

        self.tabs.consolidation_trigger_disp.setEnabled(checked)

        if not (checked or self.tabs.consolidation_trigger_stress_select.isChecked()):
            self.tabs.consolidation_trigger_stress.setEnabled(True)
            self.tabs.consolidation_trigger_stress_select.setChecked(True)
            self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Stress"] = True

        log.info(f'Set consolidation stage trigger logging at displacement to {checked}.')

    @Slot()
    def set_consolidation_trigger_disp(self):
        disp = float(self.tabs.consolidation_trigger_disp.text())
        self.configuration["shearbox"]["Consolidation"]["Trigger Displacement"] = disp

        log.info(f'Set consolidation stage trigger displacement to {disp}.')

    @Slot(bool)
    def set_consolidation_in_water(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Sample in Water"] = checked

        log.info(f'Set consolidation stage sample in water to {checked}.')


    @Slot(bool)
    def set_consolidation_log_rate_radio(self, checked):
        self.tabs.consolidation_log_rate_val.setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Consolidation"]["Logging Method"] = "rate"

            log.info('Set consolidation stage logging method to "rate".')
        
    @Slot(bool)
    def set_consolidation_log_timetable_radio(self, checked):
        self.tabs.consolidation_log_timetable_opt.setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Consolidation"]["Logging Method"] = "timetable"

            log.info('Set consolidation stage logging method to "timetable".')

    @Slot(bool)
    def set_consolidation_log_change_radio(self, checked):
        self.tabs.consolidation_log_change_val.setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Consolidation"]["Logging Method"] = "change"

            log.info('Set consolidation stage logging method to "change".')

    @Slot()
    def set_consolidation_log_rate_val(self):
        time = 0
        split_time = self.tabs.consolidation_log_rate_val.text().split(":")
        for i in range(len(split_time)):
            time = time*60 + int(split_time[i])
        self.configuration["shearbox"]["Consolidation"]["Logging Rate"] = time

        log.info(f'Set consolidation stage logging rate to "{self.tabs.consolidation_log_rate_val.text()}".')

    @Slot()
    def set_consolidation_log_timetable_opt(self, text):
        self.configuration["shearbox"]["Consolidation"]["Logging Timetable"] = text

        log.info(f'Set consolidation stage logging timetable to {text}.')

    @Slot()
    def set_consolidation_log_change_val(self):
        val = float(self.tabs.consolidation_log_change_val.text())
        self.configuration["shearbox"]["Consolidation"]["Logging Channel Change"] = val

        log.info(f'Set consolidation stage logging channel change to {val}.')


    @Slot(bool)
    def set_consolidation_stop_rate_select(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Stop on Rate of Change"] = checked

        self.tabs.consolidation_stop_rate_disp.setEnabled(checked)
        self.tabs.consolidation_stop_rate_time.setEnabled(checked)

        if not (checked or self.tabs.consolidation_stop_time_select.isChecked()):
            self.tabs.consolidation_stop_time_opt.setEnabled(True)
            self.tabs.consolidation_stop_time_select.setChecked(True)
            self.configuration["shearbox"]["Consolidation"]["Stop after Time"] = True

        log.info(f'Set consolidation stage stop on rate of change to {checked}.')

    @Slot()
    def set_consolidation_stop_rate_disp(self):
        disp = float(self.tabs.consolidation_stop_rate_disp.text())
        self.configuration["shearbox"]["Consolidation"]["Stopping Displacement Change"] = disp

        log.info(f'Set consolidation stage stopping displacement change to {disp}.')

    @Slot()
    def set_consolidation_stop_rate_time(self):
        time = 0
        split_time = self.tabs.consolidation_stop_rate_time.text().split(":")
        for i in range(len(split_time)):
            time = time*60 + int(split_time[i])
        self.configuration["shearbox"]["Consolidation"]["Stopping Time Change"] = time

        log.info(f'Set consolidation stage stopping time change to "{self.tabs.consolidation_stop_rate_time.text()}".')

    @Slot(bool)
    def set_consolidation_stop_time_select(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Stop after Time"] = checked

        self.tabs.consolidation_stop_time_opt.setEnabled(checked)

        if not (checked or self.tabs.consolidation_stop_rate_select.isChecked()):
            self.tabs.consolidation_stop_rate_disp.setEnabled(True)
            self.tabs.consolidation_stop_rate_time.setEnabled(True)
            self.tabs.consolidation_stop_rate_select.setChecked(True)
            self.configuration["shearbox"]["Consolidation"]["Stop on Rate of Change"] = True

        log.info(f'Set consolidation stage stop after time to {checked}.')

    @Slot()
    def set_consolidation_stop_time_opt(self):
        time = 0
        split_time = self.tabs.consolidation_stop_time_opt.text().split(":")
        for i in range(len(split_time)):
            time = time*60 + int(split_time[i])
        self.configuration["shearbox"]["Consolidation"]["Stop Time"] = time

        log.info(f'Set consolidation stage stop time to "{self.tabs.consolidation_stop_time_opt.text()}".')

    @Slot(bool)
    def set_consolidation_stop_buzz(self, checked):
        self.configuration["shearbox"]["Consolidation"]["Buzz on Finish"] = checked

        log.info(f'Set consolidation stage buzz on finish to {checked}.')


    def shear_selections(self):
        for i in range(1,11):
            cycle = f"Cycle {i}"

            self.set_shear_trigger_speed_select(cycle, self.tabs.shear.cycles[cycle]["trigger_speed_select"].isChecked())
            self.set_shear_trigger_calc_select(cycle, self.tabs.shear.cycles[cycle]["trigger_calc_select"].isChecked())
            self.set_shear_trigger_load_select(cycle, self.tabs.shear.cycles[cycle]["trigger_load_select"].isChecked())

            self.set_shear_store_rate_radio(cycle, self.tabs.shear.cycles[cycle]["store_rate_radio"].isChecked())
            self.set_shear_store_strain_radio(cycle, self.tabs.shear.cycles[cycle]["store_strain_radio"].isChecked())
            self.set_shear_store_disp_radio(cycle, self.tabs.shear.cycles[cycle]["store_disp_radio"].isChecked())

            self.set_shear_stop_drop_select(cycle, self.tabs.shear.cycles[cycle]["stop_drop_select"].isChecked())
            self.set_shear_stop_strain_select(cycle, self.tabs.shear.cycles[cycle]["stop_strain_select"].isChecked())

            self.set_shear_reverse_rate_radio(cycle, self.tabs.shear.cycles[cycle]["reverse_rate_radio"].isChecked())
            self.set_shear_reverse_same(cycle, self.tabs.shear.cycles[cycle]["reverse_same"].isChecked())
    
    @Slot(str, bool)
    def set_shear_trigger_speed_select(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["trigger_speed"].setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Shear Speed Selection"] = "manual"

            log.info(f'Set shear {cycle.lower()} shear speed selection to "manual".')

    @Slot(str)
    def set_shear_trigger_speed(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["trigger_speed"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Shear Speed"] = val

        log.info(f'Set shear {cycle.lower()} shear speed to {val}.')

    @Slot(str, bool)
    def set_shear_trigger_calc_select(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["trigger_calc_opt"].setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Shear Speed Selection"] = "calculated"

            log.info(f'Set shear {cycle.lower()} shear speed selection to "calculated".')

    @Slot(str)
    def set_shear_trigger_calc_opt(self, cycle, opt):
        self.configuration["shearbox"]["Shear"][cycle]["Speed Calculation"] = opt

        log.info(f'Set shear {cycle.lower()} speed calculation to "{opt}".')

    @Slot(str, bool)
    def set_shear_trigger_load_select(self, cycle, checked):
        self.configuration["shearbox"]["Shear"][cycle]["Trigger on Load Change"] = checked
        self.tabs.shear.cycles[cycle]["trigger_load_change"].setEnabled(checked)

        log.info(f'Set shear {cycle.lower()} trigger on load change to {checked}.')

    @Slot(str)
    def set_shear_trigger_load_change(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["trigger_load_change"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Load Change Rate"] = val

        log.info(f'Set shear {cycle.lower()} load change rate to {val}.')

    
    @Slot(str, bool)
    def set_shear_store_rate_radio(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["store_rate_val"].setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Logging Method"] = "rate"

            log.info(f'Set shear {cycle.lower()} logging method to "rate".')

    @Slot(str)
    def set_shear_store_rate_val(self, cycle):
        time = 0
        split_time = self.tabs.shear.cycles[cycle]["store_rate_val"].text().split(":")
        for i in range(len(split_time)):
            time = time*60 + int(split_time[i])
        self.configuration["shearbox"]["Shear"][cycle]["Logging rate"] = time

        log.info(f'Set shear {cycle.lower()} logging rate to "{self.tabs.shear.cycles[cycle]["store_rate_val"].text()}".')

    @Slot(str, bool)
    def set_shear_store_strain_radio(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["store_strain_val"].setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Logging Method"] = "strain"

            log.info(f'Set shear {cycle.lower()} logging method to "strain".')

    @Slot(str)
    def set_shear_store_strain_val(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["store_strain_val"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Logging Strain"] = val

        log.info(f'Set shear {cycle.lower()} logging strain to {val}.')

    @Slot(str, bool)
    def set_shear_store_disp_radio(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["store_disp_val"].setEnabled(checked)

        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Logging Method"] = "displacement"

            log.info(f'Set shear {cycle.lower()} logging method to "displacement".')

    @Slot(str)
    def set_shear_store_disp_val(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["store_disp_val"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Logging Displacement"] = val

        log.info(f'Set shear {cycle.lower()} logging displacement to {val}.')

    
    @Slot(str, bool)
    def set_shear_stop_drop_select(self, cycle, checked):
        self.configuration["shearbox"]["Shear"][cycle]["Stop after Repeated Falls"] = checked
        self.tabs.shear.cycles[cycle]["stop_drop"].setEnabled(checked)

        if not (checked or self.tabs.shear.cycles[cycle]["stop_strain_select"].isChecked()):
            self.configuration["shearbox"]["Shear"][cycle]["Stop on Maximum Strain"] = True
            self.tabs.shear.cycles[cycle]["stop_strain_select"].setChecked(True)
            self.tabs.shear.cycles[cycle]["stop_strain"].setEnabled(True)

        log.info(f'Set shear {cycle.lower()} stop after repeated falls to {checked}.')

    @Slot(str, int)
    def set_shear_stop_drop(self, cycle, repeats):
        self.configuration["shearbox"]["Shear"][cycle]["Number of Falls"] = repeats

        log.info(f'Set shear {cycle.lower()} number of falls to {repeats}.')

    @Slot(str, bool)
    def set_shear_stop_strain_select(self, cycle, checked):
        self.configuration["shearbox"]["Shear"][cycle]["Stop on Maximum Strain"] = True
        self.tabs.shear.cycles[cycle]["stop_strain"].setEnabled(checked)

        if not (checked or self.tabs.shear.cycles[cycle]["stop_drop_select"].isChecked()):
            self.configuration["shearbox"]["Shear"][cycle]["Stop after Repeated Falls"] = True
            self.tabs.shear.cycles[cycle]["stop_drop_select"].setChecked(True)
            self.tabs.shear.cycles[cycle]["stop_drop"].setEnabled(True)

        log.info(f'Set shear {cycle.lower()} stop on maximum strain to {checked}.')

    @Slot(str)
    def set_shear_stop_strain(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["stop_strain"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Maximum Strain"] = val

        log.info(f'Set shear {cycle.lower()} maximum strain to {val}.')

    
    @Slot(str, bool)
    def set_shear_reverse_rate_radio(self, cycle, checked):
        self.tabs.shear.cycles[cycle]["reverse_rate_val"].setEnabled(checked)
        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Reverse Method"] = "rate"

            log.info(f'Set shear {cycle.lower()} reverse method to "rate".')

    @Slot(str)
    def set_shear_reverse_rate_val(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["reverse_rate_val"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Reverse Speed"] = val

        log.info(f'Set shear {cycle.lower()} reverse speed to {val}.')

    @Slot(str, bool)
    def set_shear_reverse_same(self, cycle, checked):
        if checked:
            self.configuration["shearbox"]["Shear"][cycle]["Reverse Method"] = "same"

            log.info(f'Set shear {cycle.lower()} reverse method to "same".')

    @Slot(str)
    def set_shear_reverse_wait(self, cycle):
        time = 0
        split_time = self.tabs.shear.cycles[cycle]["reverse_wait"].text().split(":")
        for i in range(len(split_time)):
            time = time*60 + int(split_time[i])
        self.configuration["shearbox"]["Shear"][cycle]["Wait before Reversing"] = time

        log.info(f'Set shear {cycle.lower()} wait before reversing to "{self.tabs.shear.cycles[cycle]["reverse_wait"].text()}".')

    @Slot(str)
    def set_shear_reverse_disp(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["reverse_disp"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Shear until Displacement"] = val

        log.info(f'Set shear {cycle.lower()} shear until displacement to {val}.')

    @Slot(str)
    def set_shear_reverse_stress(self, cycle):
        val = float(self.tabs.shear.cycles[cycle]["reverse_stress"].text())
        self.configuration["shearbox"]["Shear"][cycle]["Repeat until Stress"] = val

        log.info(f'Set shear {cycle.lower()} repeat until stress to {val}.')
