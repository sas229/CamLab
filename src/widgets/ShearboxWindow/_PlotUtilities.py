from PySide6.QtCore import Signal, Slot, QModelIndex
from widgets.ShearboxWindow.PlotWidget import PlotWidget
import copy
import logging

log = logging.getLogger(__name__)

class PlotUtilities:
    GenericChannelsData = Signal()

    @Slot(list)
    def open_plot(self):
        # Define a default configuration in the same format as we want it to be stored in self.configuration["shearbox"]["plot"].
        self.plotWidget = PlotWidget()

        # Defaults.
        width = 1200
        height = 800
        x = self.screenSize.width()/2 - width/2
        y = self.screenSize.height()/2 - height/2
        defaultProperties = {
            "alpha": 50,
            "auto": True,
            "autoCommonAxis": True,
            "autoSelectedAxis": True,
            "height": height,
            "width": width,
            "invertCommonAxis": False,
            "invertSelectedAxis": False,
            "lock": False,
            "lockCommonAxis": False,
            "lockSelectedAxis": False,
            "logCommonAxis": False,
            "logSelectedAxis": False,          
            "manualCommonAxis": False,
            "manualSelectedAxis": False,
            "minCommonAxisRange": 0,
            "minCommonAxisRangeLock": 0,
            "minSelectedAxisRange": 0,
            "minSelectedAxisRangeLock": 0,
            "maxCommonAxisRange": 1,
            "maxCommonAxisRangeLock": 1,
            "maxSelectedAxisRange": 1,
            "maxSelectedAxisRangeLock": 1,
            "mode": "tab",
            "opacity": 50,
            "setGrid": False,
            "swap": False,
            "x": x,
            "y": y,
        }

        # Add the plot and set the colour for the new plot window.        
        self.configuration["shearbox"]["plot"] = copy.deepcopy(defaultProperties)
        self.getGenericChannelsData()
# NEED TO CHANGE         self.manager.setColourNewPlot(plotNumber)

        # Show the plot.
        self.plotWidget.set_configuration(self.configuration)
        self.tabs.setParent(None)
        self.Layout.addWidget(self.plotWidget, 2)

        # Connections.
        self.configurationChanged.connect(self.plotWidget.set_configuration)
# NEED TO CHANGE        self.manager.assembly.plotDataChanged.connect(self.plotWidget.update_output_data)
# NEED TO CHANGE        self.plotWidget.plotWidgetClosed.connect(self.window_to_tab)
        self.plotWidget.colourUpdated.connect(self.update_channel_colours)

        # Update all plot windows to reset configuration.
        self.update_plots()

    @Slot()
    def create_existing_plots(self):
        # Create plot widget object
        plotWidget = PlotWidget()

        # Show the plot.
        plotWidget.set_configuration(self.configuration)
        self.tabs.setParent(None)
        self.Layout.addWidget(self.plotWidget, 2)

        # Connections.
        self.configurationChanged.connect(self.plotWidget.set_configuration)
# NEED TO CHANGE        self.manager.assembly.plotDataChanged.connect(self.plotWidget.update_output_data)
# NEED TO CHANGE        self.plotWidget.plotWidgetClosed.connect(self.window_to_tab)
        self.plotWidget.colourUpdated.connect(self.update_channel_colours)

        # Convert tab to window if required by configuration.
        if self.configuration["shearbox"]["plot"]["mode"] == "window":
            self.tab_to_window(self.plotWidget)    
        
        # Update all plot windows to reset configuration.
        self.update_plots()
         
    @Slot()
    def update_plots(self):
        # If plots exist update the configuration.
        if "plot" in self.configuration["shearbox"]:
            self.plotWidget.set_configuration(self.configuration)
                 
# NEED TO CHANGE     @Slot(str)
# NEED TO CHANGE     def remove_plot(self, plotNumber):
# NEED TO CHANGE         # Pop plot from if "plots" key in dict.
# NEED TO CHANGE         if plotNumber in self.plots:
# NEED TO CHANGE             self.plotWidget.setParent(None)
# NEED TO CHANGE             self.plots.pop(plotNumber)
# NEED TO CHANGE         if "plots" in self.configuration:
# NEED TO CHANGE             self.configuration["shearbox"]["plots"].pop(plotNumber)
# NEED TO CHANGE             # If plots dict in manager is empty delete the plots key.
# NEED TO CHANGE             if self.configuration["shearbox"]["plots"] == {}:
# NEED TO CHANGE                 del self.configuration["shearbox"]["plots"]
# NEED TO CHANGE     
    def close_plot(self):
        self.configurationChanged.disconnect(self.plotWidget.set_configuration)
        self.plotWidget.setParent(None)
        self.plotWidget.close()
        self.Layout.addWidget(self.tabs, 2)

    @Slot(QModelIndex, str)
    def update_channel_colours(self, index, colour):
        # Update colours of channels in plot.
        self.plotWidget.setColour(index, colour)
        self.update_plots()

    def getGenericChannelsData(self):
        self.configurationChanged.emit(self.configuration)
        self.GenericChannelsData.emit()