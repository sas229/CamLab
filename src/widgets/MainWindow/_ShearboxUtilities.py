from PySide6.QtCore import Slot, QModelIndex
from widgets.ShearboxWindow import ShearboxWindow
import copy

class ShearboxUtilities:

    @Slot()
    def initialise_shearbox(self):
        # If the "shearbox" key doesn't exist in the configuration, it means no shearbox Window has been made before, so we add the key.
        if "shearbox" not in self.manager.configuration.keys():
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
                "Number of specimens": 1,

            }      
            self.manager.configuration["shearbox"] = copy.deepcopy(defaultProperties)

        self.create_shearbox_window()

    @Slot()
    def create_shearbox_window(self):
        # For all plots in self.manager.configuration["plots"][plotNumber], create a plot window.
        # Create plot window object and set the plot number.
        self.shearbox = ShearboxWindow(self.manager.configuration)

        # Connections.
        self.manager.configurationChanged.connect(self.shearbox.set_configuration)
        self.shearbox.configurationChanged.connect(self.set_configuration)

        self.shearbox.show()
        
    # @Slot()
    # def update_plots(self):
    #     # If plots exist update the configuration.
    #     if "plots" in self.manager.configuration:
    #         for plotNumber in self.manager.configuration["plots"].keys():
    #             plotWindow = self.plots[plotNumber]
    #             plotWindow.setPlotNumber(plotNumber)
    #             plotWindow.set_configuration(self.manager.configuration)
                
    # @Slot(str)
    # def remove_plot(self, plotNumber):
    #     # Pop plot from if "plots" key in dict.
    #     if plotNumber in self.plots:
    #         self.plots[plotNumber].setParent(None)
    #         self.plots.pop(plotNumber)
    #     if "plots" in self.manager.configuration:
    #         self.manager.configuration["plots"].pop(plotNumber)
    #         # If plots dict in manager is empty delete the plots key.
    #         if self.manager.configuration["plots"] == {}:
    #             del self.manager.configuration["plots"]
    
    # def close_plots(self):
    #     # Close windows into tabs.
    #     for plotNumber in self.plots:
    #         self.plots[plotNumber].close()
    #     # Remove plot tabs.
    #     tabs = self.tabs.count()
    #     for index in reversed(range(tabs)):
    #         widget = self.tabs.widget(index)
    #         text = self.tabs.tabText(index)
    #         if isinstance(widget, PlotWindow):
    #             self.tabs.removeTab(index)
    #             widget.setParent(None)
    #             widget.deleteLater()
    #     self.plots = {}

    # @Slot(QModelIndex, str)
    # def update_channel_colours(self, index, colour):
    #     # Update colours of channels in all plots.
    #     for plotNumber in self.manager.configuration["plots"].keys():
    #         self.plots[plotNumber].setColour(index, colour)
    #     self.update_plots()