from PySide6.QtCore import Slot
import logging

log = logging.getLogger(__name__)

class TabUtilities:
    
    def addItemstoComboboxes(self):
        # print(self.configuration["devices"])
        self.devices = dict()
        for device in self.configuration["devices"].keys():
            # print(f"Device: {device}")
            key = f'{self.configuration["devices"][device]["model"]} ({self.configuration["devices"][device]["id"]})'
            channels = [channel_info["name"] for channel_info in self.configuration["devices"][device]["acquisition"]]
            self.devices[key] = [device, channels]
        # print(self.devices.keys())
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

    def set_horiz_load_ins(self, device):
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

    def set_horiz_load_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    def set_horiz_disp_ins(self, device):
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

    def set_horiz_disp_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    def set_vert_load_ins(self, device):
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

    def set_vert_load_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    def set_vert_disp_ins(self, device):
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

    def set_vert_disp_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    def set_horiz_cont_ins(self, device):
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

    def set_horiz_cont_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()

    def set_vert_cont_ins(self, device):
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

    def set_vert_cont_chan(self, channel):
        if channel != "":
            self.configuration["shearbox"]["horiz_load_chan"] = channel
            log.info(f"Channel selected: {channel}")
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_chan"] = None
        self.update_configuration()