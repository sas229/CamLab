from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Signal, Slot, QModelIndex, Qt
from widgets.ShearboxWindow.Simulation import Simulation
import numpy as np
import pandas as pd
from pathlib import Path
import copy
import logging
import threading

log = logging.getLogger(__name__)

class PlotUtilities:
    GenericChannelsData = Signal()

    @Slot()
    def run(self):
        if self.simulating:
            self.resume_simulation()
        elif self.running:
            self.start_shear()
        elif self.check_settings():
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Calibration reminder")
            dlg.setText("This is a reminder to calibrate the machine.\nWould you like to continue?")
            dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dlg.setIcon(QMessageBox.Information)
            button = dlg.exec()

            if button == QMessageBox.Yes:
                self.running = True
                self.show_plot()

                # Change the topbar buttons
                self.toolbar.setParent(None)
                self.topbar.setParent(None)
                self.Layout.insertWidget(0, self.toolbar, 0)
                self.toolbar.pauseButton.setVisible(True)
                self.toolbar.stopButton.setVisible(True)
                self.toolbar.runButton.setVisible(False)
                self.toolbar.setupButton.setVisible(True)
                self.toolbar.setupButton.setEnabled(False)
                self.toolbar.saveButton.setVisible(True)
                self.toolbar.loadButton.setVisible(False)
                self.toolbar.saveResultsButton.setVisible(True)
                self.toolbar.spacer.setVisible(True)

                self.start_shear()
    
    def start_shear(self):
        pass

    def resume_simulation(self):
        self.simulationThread = threading.Thread(target=self.simulation.start, args=[self.simulation.index])
        self.simulationThread.start()
        self.toolbar.pauseButton.setVisible(True)
        self.toolbar.runButton.setVisible(False)

    @Slot()
    def pause(self):
        if self.simulating:
            self.pause_simulation()
        elif self.running:
            self.pause_shear()

    def pause_simulation(self):
        self.simulation.stopped=True
        self.toolbar.pauseButton.setVisible(False)
        self.toolbar.runButton.setVisible(True)

    def pause_shear(self):
        self.toolbar.pauseButton.setVisible(False)
        self.toolbar.stopButton.setVisible(True)
        self.toolbar.runButton.setVisible(True)

    @Slot()
    def stop_shear(self):
        self.running = False
        self.toolbar.setupButton.setEnabled(True)
        self.toolbar.pauseButton.setVisible(False)
        self.toolbar.stopButton.setVisible(False)
        self.toolbar.runButton.setVisible(True)
    
    def check_settings(self):
        log.info("Checking setup is acceptable.")
        try:
            assert True
        except AssertionError:
            log.error("Setting ... not set to an acceptable value! Please ensure it is in the range ...")
            return False
        
        try:
            assert True
        except AssertionError:
            log.error("Setting ... not set to an acceptable value! Please ensure it is in the range ...")
            return False
        
        log.info("Setup accepted.")
        return True
        
    def show_plot(self):
        # Define a default configuration in the same format as we want it to be stored in self.configuration["shearbox"]["plot"].

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
        self.plotWidget.set_configuration()
        self.tabs.setParent(None)
        self.Layout.addWidget(self.plotWidget, 2)

        # Connections.
        self.plotWidget.colourUpdated.connect(self.update_channel_colours, Qt.UniqueConnection)

        # Update all plot windows to reset configuration.
        self.update_plots()

    def change_setup(self):
        self.simulating = False
        self.running = False
        self.pause_simulation()

        self.plotWidget.setParent(None)
        self.Layout.addWidget(self.tabs, 2)

        # Change the top buttons
        self.toolbar.setParent(None)
        self.topbar.setParent(None)
        self.Layout.insertWidget(0, self.topbar, 0)
        self.toolbar.pauseButton.setVisible(False)
        self.toolbar.stopButton.setVisible(False)
        self.toolbar.runButton.setVisible(True)
        self.toolbar.setupButton.setVisible(False)
        self.toolbar.saveButton.setVisible(True)
        self.toolbar.loadButton.setVisible(True)
        self.toolbar.saveResultsButton.setVisible(False)
        self.toolbar.spacer.setVisible(False)
        self.topbarlayout.addWidget(self.toolbar)

    @Slot()
    def simulate(self):
        """Open the plots from a previous test
        """
        self.simulating = True
        camlab_folder = Path(__file__).parents[3]
        if camlab_folder.joinpath("results").is_dir():
            filename, _ = QFileDialog.getOpenFileName(self, "Open results file", str(camlab_folder.joinpath("results")), "CSV files (*.csv);;Text files (*.txt);;Excel files (*.xlsx *.xls);;Pickle files (*.pkl);;JSON files (*.json)")
        else:
            filename, _ = QFileDialog.getOpenFileName(self, "Open results file", str(camlab_folder), "CSV files (*.csv);;Text files (*.txt);;Excel files (*.xlsx *.xls);;Pickle files (*.pkl);;JSON files (*.json)")
        
        if filename != "":
            log.info("File " + filename + " selected.")
            filetype = Path(filename).suffix[1:]
            if filetype == "csv":
                df = pd.read_csv(filename)
            elif filetype == "txt":
                df = pd.read_csv(filename, sep="\t")
            elif filetype in ["xlsx", "xls"]:
                df = pd.read_excel(filename)
            elif filetype == "pkl":
                df = pd.read_pickle(open(filename, 'rb'))
            elif filetype == "json":
                df = pd.read_json(filename)

            df["Horizontal Displacement"] = df["Horizontal Displacement"]/1000
            df["Vertical Displacement"] = df["Vertical Displacement"]/1000
                
            if not self.plotWidget.isVisible():
                self.show_plot()

            # Change the topbar buttons
            self.toolbar.setParent(None)
            self.topbar.setParent(None)
            self.Layout.insertWidget(0, self.toolbar, 0)
            self.toolbar.pauseButton.setVisible(True)
            self.toolbar.stopButton.setVisible(False)
            self.toolbar.runButton.setVisible(False)
            self.toolbar.setupButton.setVisible(True)
            self.toolbar.setupButton.setEnabled(True)
            self.toolbar.saveButton.setVisible(False)
            self.toolbar.loadButton.setVisible(False)
            self.toolbar.saveResultsButton.setVisible(True)
            self.toolbar.spacer.setVisible(True)
            
            
            self.plotWidget.setChannelsModel(self.plotWidget.defaultChannelsData)
            self.plotWidget.selectedChannelsTableView.setModel(self.plotWidget.channelsModel)

            self.plotWidget.commonChannelComboBox.blockSignals(True)
            self.plotWidget.fillCommonChannelComboBox()
            self.plotWidget.commonChannelComboBox.blockSignals(False)

            self.simulation = Simulation(df)
            self.simulation.emitData.connect(self.plotWidget.update_output_data, Qt.UniqueConnection)
            self.simulationThread = threading.Thread(target=self.simulation.start)
            self.simulationThread.start()
            
        else:
            log.info("File loading cancelled")

    def save_results(self):
        """Save results data to file
        """
        df = pd.DataFrame(data = self.plotWidget.plotData, columns = ["Time", "Horizontal Load", "Horizontal Displacement", "Vertical Load", "Vertical Displacement"])

        df["Time"] = pd.to_timedelta(df["Time"], unit="S").astype("string")
        df["Time"] = df["Time"].str.removeprefix("0 days ")

        df["Horizontal Displacement"] = df["Horizontal Displacement"]*1000
        df["Vertical Displacement"] = df["Vertical Displacement"]*1000

        camlab_folder = Path(__file__).parents[3]
        if camlab_folder.joinpath("results").is_dir():
            filename, _ = QFileDialog.getSaveFileName(self, "Save results file", str(camlab_folder.joinpath("results")), "CSV files (*.csv);;Text files (*.txt);;Excel files (*.xlsx *.xls);;Pickle files (*.pkl);;JSON files (*.json)")
        else:
            filename, _ = QFileDialog.getSaveFileName(self, "Save results file", str(camlab_folder), "CSV files (*.csv);;Text files (*.txt);;Excel files (*.xlsx *.xls);;Pickle files (*.pkl);;JSON files (*.json)")

        if filename != "":
            filetype = Path(filename).suffix[1:]
            try:
                if filetype == "csv":
                    df.to_csv(filename, index=False)
                elif filetype == "txt":
                    df.to_csv(filename, index=False, sep="\t")
                elif filetype in ["xlsx", "xls"]:
                    df.to_excel(filename, index=False)
                elif filetype == "pkl":
                    df.to_pickle(open(filename, 'wb'), index=False)
                elif filetype == "json":
                    df.to_json(filename, index=False, orient='records')
            except PermissionError:
                log.error("File could not save due to permission error.")
                dlg = QMessageBox(self)
                dlg.setWindowTitle("Save error")
                dlg.setText("File could not save due to permission error. (Are you overwriting an open file?)")
                dlg.setStandardButtons(QMessageBox.Ok)
                dlg.setIcon(QMessageBox.Critical)
                button = dlg.exec()

    # def save_test_results(self):
    #     """Save results data to file
    #     """
    #     data = {
    #         'Horizontal Load': np.sort(np.random.rand(200)),
    #         'Horizontal Displacement': np.sort(np.random.rand(200)),
    #         'Vertical Load': np.sort(np.random.rand(200)),
    #         'Vertical Displacement': np.sort(np.random.rand(200)),
    #         'Horizontal Control': np.sort(np.random.rand(200)),
    #         'Vertical Control': np.sort(np.random.rand(200))
    #     }
    #     df = pd.DataFrame(data)

    #     df.index.name = 'Time'
    #     print(df.head())

    #     camlab_folder = Path(__file__).parents[3]
    #     filename = camlab_folder.joinpath("results", "test.")

    #     for filetype in ["csv", "txt", "xlsx", "pkl", "json"]:
    #         if filetype == "csv":
    #             df.to_csv(str(filename) + filetype)
    #         elif filetype == "txt":
    #             df.to_csv(str(filename) + filetype, sep="\t")
    #         elif filetype in ["xlsx", "xls"]:
    #             df.to_excel(str(filename) + filetype)
    #         elif filetype == "pkl":
    #             df.to_pickle(open(str(filename) + filetype, 'wb'))
    #         elif filetype == "json":
    #             df.to_json(str(filename) + filetype, orient='records')
        
         
    @Slot()
    def update_plots(self):
        # If plots exist update the configuration.
        if "plot" in self.configuration["shearbox"]:
            self.plotWidget.set_configuration()
                 
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
        self.plotWidget.setParent(None)
        self.plotWidget.close()
        self.Layout.addWidget(self.tabs, 2)

    @Slot(QModelIndex, str)
    def update_channel_colours(self, index, colour):
        # Update colours of channels in plot.
        self.plotWidget.setColour(index, colour)
        self.update_plots()

    def getGenericChannelsData(self):
        self.GenericChannelsData.emit()