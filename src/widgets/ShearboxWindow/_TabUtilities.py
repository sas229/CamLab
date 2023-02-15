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
        self.tabs.horiz_load_ins.addItems([""] + list(self.devices.keys()))
        self.tabs.horiz_load_chan.clear()

    def set_horiz_load_ins(self, device):
        if device != "":
            self.configuration["shearbox"]["horiz_load_ins"] = self.devices[device][0]
            log.info(f"Device selected: {device}")
            self.tabs.horiz_load_chan.clear()
            self.tabs.horiz_load_chan.addItems([""] + self.devices[device][1])
        else:
            log.info("No device selected")
            self.configuration["shearbox"]["horiz_load_ins"] = None
            self.tabs.horiz_load_chan.clear()
        self.update_configuration()

    def set_horiz_load_chan(self, channel):
        pass

    def set_horiz_disp_ins(self, device):
        pass

    def set_horiz_disp_chan(self, channel):
        pass

    def set_vert_load_ins(self, device):
        pass

    def set_vert_load_chan(self, channel):
        pass

    def set_vert_disp_ins(self, device):
        pass

    def set_vert_disp_chan(self, channel):
        pass

    def set_horiz_cont_ins(self, device):
        pass

    def set_horiz_cont_chan(self, channel):
        pass

    def set_vert_cont_ins(self, device):
        pass

    def set_vert_cont_chan(self, channel):
        pass