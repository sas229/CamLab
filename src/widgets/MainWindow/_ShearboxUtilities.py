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
        width = max(1200, self.screenSize.width()/2)
        height = max(1060, self.screenSize.height()/2)
        x = self.screenSize.width()/2 - width/2
        y = self.screenSize.height()/2 - height/2
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
        for key, value in defaultProperties.items():
            if key not in self.manager.configuration["shearbox"].keys():
                self.manager.configuration["shearbox"][key] = value

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
        if not external:
            self.shearbox.make_connections()
        
        self.manager.configurationChanged.emit(self.manager.configuration)

    @Slot()
    def disconnect_shearbox(self):
        log.info("Disconnecting ShearBox")
        self.manager.clear_shearbox_configuration.disconnect(self.disconnect_shearbox)
        self.manager.configurationChanged.disconnect(self.shearbox.set_configuration) 
        self.shearbox.close()