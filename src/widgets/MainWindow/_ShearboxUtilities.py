from PySide6.QtCore import Slot
from widgets.ShearboxWindow import ShearboxWindow

class ShearboxUtilities:

    @Slot()
    def initialise_shearbox(self):
        # Defaults.
        width = 1200
        height = 800
        x = self.screenSize.width()/2 - width/2
        y = self.screenSize.height()/2 - height/2
        defaultProperties = {
            "height": height,
            "width": width,
            "x": x,
            "y": y,
            "Number of Specimens": 1,
            "horiz_load_ins": None
        }      

        if "shearbox" not in self.manager.configuration.keys():
            self.manager.configuration["shearbox"] = dict()
        for key, value in defaultProperties.items():
            if key not in self.manager.configuration["shearbox"].keys():
                self.manager.configuration["shearbox"][key] = value

        try:
            self.shearbox.activateWindow()
            self.connect_shearbox()
            self.shearbox.addItemstoComboboxes()
        except:
            self.shearbox = ShearboxWindow(self.manager.configuration)
            self.connect_shearbox()

        self.shearbox.show()

    @Slot()
    def connect_shearbox(self):
        # Connections.
        self.manager.clear_shearbox_configuration.connect(self.disconnect_shearbox)
        self.manager.configurationChanged.connect(self.shearbox.set_configuration)
        self.shearbox.configurationChanged.connect(self.set_configuration)
        
        self.manager.configurationChanged.emit(self.manager.configuration)

    @Slot()
    def disconnect_shearbox(self):
        self.manager.clear_shearbox_configuration.disconnect(self.disconnect_shearbox)
        self.manager.configurationChanged.disconnect(self.shearbox.set_configuration)
        self.shearbox.close()