from pathlib import Path
import json
from PySide6.QtCore import Slot
from widgets.ShearboxWindow import ShearboxWindow
import logging

log = logging.getLogger(__name__)

class ShearboxUtilities:

    @Slot()
    def initialise_shearbox(self):
        # Defaults.
        width = max(1200, self.screenSize.width()//2)
        height = max(1048, self.screenSize.height()//2)
        x = self.screenSize.width()//2 - width//2
        y = self.screenSize.height()//2 - height//2
        defaultDimensions = {
            "height": height,
            "width": width,
            "x": x,
            "y": y,
        }      
        with open(Path(__file__).parents[1].joinpath("ShearboxWindow","defaults.json"), "r") as file:
            defaultProperties = json.load(file)
            defaultProperties.update(defaultDimensions)

        if "shearbox" not in self.manager.configuration.keys() or type(self.manager.configuration["shearbox"]) is not dict:
            self.manager.configuration["shearbox"] = dict()
        self.manager.configuration["shearbox"] = add_defaults_if_missing(self.manager.configuration["shearbox"], defaultProperties)

        self.manager.configuration["shearbox"]["active"] = True
        
        try:
            self.shearbox.activateWindow()
            self.shearbox.set_configuration(self.manager.configuration)
            self.shearbox.addItemstoComboboxes()
            self.connect_shearbox()
        except:
            self.shearbox = ShearboxWindow(self.manager.configuration)
            self.connect_shearbox()

        self.shearbox.show()
        
        log.info("ShearBox opened.")

    def connect_shearbox(self, external=False):
        log.info("Connecting ShearBox")
        self.manager.clear_shearbox_configuration.connect(self.disconnect_shearbox)
        self.manager.configurationChanged.connect(self.shearbox.set_configuration)
        self.shearbox.configurationChanged.connect(self.set_configuration)
        self.shearbox.toolbar.saveConfiguration.connect(self.manager.saveConfiguration)
        self.shearbox.toolbar.loadConfiguration.connect(self.manager.loadConfiguration)
        if not external:
            self.shearbox.make_connections()
        
        self.manager.configurationChanged.emit(self.manager.configuration)

    @Slot()
    def disconnect_shearbox(self):
        log.info("Disconnecting ShearBox")
        self.manager.clear_shearbox_configuration.disconnect(self.disconnect_shearbox)
        self.manager.configurationChanged.disconnect(self.shearbox.set_configuration)
        self.shearbox.close()

def add_defaults_if_missing(configuration, defaults):
    for key, value in defaults.items():
        if key not in configuration.keys():
            configuration[key] = value
        elif type(defaults[key]) is dict:
            for key2, value2 in defaults[key].items():
                if key2 not in configuration[key].keys():
                    configuration[key][key2] = value2
                elif type(defaults[key][key2]) is dict:
                    for key3, value3 in defaults[key][key2].items():
                        if key3 not in configuration[key][key2].keys():
                            configuration[key][key2][key3] = value3
    return configuration