from PySide6.QtCore import Slot
from widgets.ShearboxWindow import ShearboxWindow

class ShearboxUtilities:

    @Slot()
    def initialise_shearbox(self):
        try:
            self.shearbox.activateWindow()
            self.shearbox.show()
        except:
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

            self.create_shearbox_window()

    @Slot()
    def create_shearbox_window(self):
        self.shearbox = ShearboxWindow(self.manager.configuration)

        # Connections.
        self.manager.clear_shearbox_configuration.connect(self.disconnect_shearbox)
        self.manager.configurationChanged.connect(self.shearbox.set_configuration)
        self.shearbox.configurationChanged.connect(self.set_configuration)
        
        self.manager.configurationChanged.emit(self.manager.configuration)

        self.shearbox.show()

    @Slot()
    def disconnect_shearbox(self):
        self.manager.clear_shearbox_configuration.disconnect(self.disconnect_shearbox)
        self.manager.configurationChanged.disconnect(self.shearbox.set_configuration)
        self.shearbox.close()