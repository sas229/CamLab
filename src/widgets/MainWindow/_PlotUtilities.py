from PySide6.QtCore import Slot, QModelIndex
from widgets.PlotWindow import PlotWindow
import copy

class PlotUtilities:

    @Slot(list)
    def add_plot(self):
        # Define a default configuration in the same format as we want it to be stored in self.manager.configuration["plots"][plotNumber].
        plotWindow = PlotWindow()
        plotNumber = str(id(plotWindow))
        plotWindow.setPlotNumber(plotNumber)

        # Store the plot windwow.
        self.plots.update({plotNumber: plotWindow})

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
            "channels": self.manager.getGenericChannelsData()
        }

        # If the "plots" key doesn't exist in the configuration, it means no plots have been made before, so we add the key.
        # Otherwise we add the plot and set the colour for the new plot window.        
        if "plots" not in self.manager.configuration:
            self.manager.configuration["plots"] = {plotNumber: copy.deepcopy(defaultProperties)}
        else:
            self.manager.configuration["plots"][plotNumber] = copy.deepcopy(defaultProperties)
        self.manager.setColourNewPlot(plotNumber)

        # Show the plot.
        plotWindow.set_configuration(self.manager.configuration)
        self.tabs.addTab(self.plots[plotNumber], "Plot")

        # Connections.
        self.manager.configurationChanged.connect(self.plots[plotNumber].set_configuration)
        self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].update_output_data)
        self.plots[plotNumber].plotWindowClosed.connect(self.window_to_tab)
        self.plots[plotNumber].colourUpdated.connect(self.update_channel_colours)

        # Update all plot windows to reset configuration.
        self.update_plots()

    @Slot()
    def create_existing_plots(self):
        # For all plots in self.manager.configuration["plots"][plotNumber], create a plot window.
        for plotNumber in self.manager.configuration["plots"].keys():
            # Create plot window object and set the plot number.
            plotWindow = PlotWindow()
            plotWindow.setPlotNumber(plotNumber)

            # Store plot window object in plots dict.
            self.plots.update({plotNumber: plotWindow})

            # Show the plot.
            plotWindow.set_configuration(self.manager.configuration)
            self.tabs.addTab(self.plots[plotNumber], "Plot")

            # Connections.
            self.manager.configurationChanged.connect(self.plots[plotNumber].set_configuration)
            self.manager.assembly.plotDataChanged.connect(self.plots[plotNumber].update_output_data)
            self.plots[plotNumber].plotWindowClosed.connect(self.window_to_tab)
            self.plots[plotNumber].colourUpdated.connect(self.update_channel_colours)

            # Convert tab to window if required by configuration.
            if self.manager.configuration["plots"][plotNumber]["mode"] == "window":
                index = self.tabs.indexOf(self.plots[plotNumber])
                self.tab_to_window(self.plots[plotNumber], index)    
        
        # Update all plot windows to reset configuration.
        self.update_plots()
        
    @Slot()
    def update_plots(self):
        # If plots exist update the configuration.
        if "plots" in self.manager.configuration:
            for plotNumber in self.manager.configuration["plots"].keys():
                plotWindow = self.plots[plotNumber]
                plotWindow.setPlotNumber(plotNumber)
                plotWindow.set_configuration(self.manager.configuration)
                
    @Slot(str)
    def remove_plot(self, plotNumber):
        # Pop plot from if "plots" key in dict.
        if plotNumber in self.plots:
            self.plots[plotNumber].setParent(None)
            self.plots.pop(plotNumber)
        if "plots" in self.manager.configuration:
            self.manager.configuration["plots"].pop(plotNumber)
            # If plots dict in manager is empty delete the plots key.
            if self.manager.configuration["plots"] == {}:
                del self.manager.configuration["plots"]
    
    def close_plots(self):
        # Close windows into tabs.
        for plotNumber in self.plots:
            self.plots[plotNumber].close()
        # Remove plot tabs.
        tabs = self.tabs.count()
        for index in reversed(range(tabs)):
            widget = self.tabs.widget(index)
            if isinstance(widget, PlotWindow):
                self.tabs.removeTab(index)
                widget.deleteLater()
        self.plots = {}

    @Slot(QModelIndex, str)
    def update_channel_colours(self, index, colour):
        # Update colours of channels in all plots.
        for plotNumber in self.manager.configuration["plots"].keys():
            self.plots[plotNumber].setColour(index, colour)
        self.update_plots()