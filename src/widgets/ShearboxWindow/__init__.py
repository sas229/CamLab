import os
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QRadioButton
from PySide6.QtGui import QScreen
from PySide6.QtCore import Signal, Slot, Qt
from local_qt_material import QtStyleTools
from widgets.ShearboxWindow._TabUtilities import TabUtilities
from widgets.ShearboxWindow._PlotUtilities import PlotUtilities
from widgets.ShearboxWindow.Tabs import TabInterface
from widgets.ShearboxWindow.ToolBar import ToolBar
from widgets.ShearboxWindow.PlotWidget import PlotWidget
import logging
from datetime import timedelta
from pathlib import Path

log = logging.getLogger(__name__)

def num_to_str(num):
    if num != None:
        return str(num)
    else:
        return ""
    
def secs_to_time(s):
    if s == None or s >= 86400 or s <= 0:
        return None
    
    string = ""
    if s < 10*60*60:
        string = string + "0"
    string = string + str(timedelta(seconds=s))

    while len(string.split(".")) > 1 and string[-1] == "0":
        string = string[:-1]
        
    return string
    
class ShearboxWindow(QMainWindow, TabUtilities, PlotUtilities, QtStyleTools):

    def __init__(self, configuration):
        """Main window containing shear box setup

        Arguments:
            configuration -- configuration for initial setup
        """
        super().__init__()
        self.setWindowTitle("Shear Box")
        self.setMinimumSize(1000, 1048)
        self.screenSize = QScreen.availableGeometry(QApplication.primaryScreen())

        self.configuration = configuration
        self.running = False

        self.Layout = QVBoxLayout()
        self.toolbar = ToolBar()

        self.specimens_label = QLabel("Number of Specimens")
        self.specimens = QSpinBox()
        self.specimens.setMinimum(1)
        self.specimens.setMaximum(4)
        self.specimens.lineEdit().setReadOnly(True)

        self.direct_shear = QRadioButton("Direct Shear")
        self.residual_shear = QRadioButton("Residual Shear")
        self.radiobuttons = QWidget()
        self.radiobuttons_layout = QVBoxLayout()
        self.radiobuttons_layout.addWidget(self.direct_shear, 0)
        self.radiobuttons_layout.addWidget(self.residual_shear, 0)
        self.radiobuttons.setLayout(self.radiobuttons_layout)

        self.cycles = QSpinBox()
        self.cycles.setMinimum(1)
        self.cycles.setMaximum(10)
        self.cycles.lineEdit().setReadOnly(True)
        self.cycles_layout = QHBoxLayout()
        self.cycles_label = QLabel("Number of Cycles")

        self.topbar = QWidget()
        self.topbarlayout = QHBoxLayout()
        self.topbarlayout.addWidget(self.specimens_label, 0)
        self.topbarlayout.addWidget(self.specimens, 0)
        self.topbarlayout.addStretch(1)
        self.topbarlayout.addWidget(self.radiobuttons, 0)
        self.topbarlayout.addLayout(self.cycles_layout)
        self.topbarlayout.addStretch(3)
        self.topbarlayout.addWidget(self.toolbar, 0)
        self.topbar.setLayout(self.topbarlayout)

        self.toolbar.runButton.triggered.connect(self.run_shear, Qt.UniqueConnection)
        self.toolbar.setupButton.triggered.connect(self.change_setup, Qt.UniqueConnection)
        self.toolbar.pauseButton.triggered.connect(self.pause_shear, Qt.UniqueConnection)
        self.toolbar.stopButton.triggered.connect(self.stop_shear, Qt.UniqueConnection)

        self.tabs = TabInterface()

        self.plotWidget = PlotWidget()

        self.Layout.addWidget(self.topbar, 0)
        self.Layout.addWidget(self.tabs, 2)

        # Set the central widget of the main window.
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.Layout)
        self.setCentralWidget(self.centralWidget)

        self.set_theme()

        self.apply_configuration()

    def moveEvent(self, event):
        self.configuration["shearbox"]["x"] = self.pos().x()
        self.configuration["shearbox"]["y"] = self.pos().y()
        return super(ShearboxWindow, self).moveEvent(event)

    def resizeEvent(self, event):
        self.configuration["shearbox"]["width"] = self.size().width()
        self.configuration["shearbox"]["height"] = self.size().height()
        return super(ShearboxWindow, self).resizeEvent(event)

    def set_theme(self):
        """Method to set the theme and apply the qt-material stylesheet."""
        self.darkMode = self.configuration["global"]["darkMode"]
        # Set the darkmode. 
        if self.darkMode == True:
            self.apply_stylesheet(self, theme='dark_blue.xml')
        else:
            self.apply_stylesheet(self, theme='light_blue.xml')
        stylesheet = self.styleSheet()
        
        # Get css directory.
        bundle_dir = Path(__file__).parents[2]
        path_to_css = os.path.abspath(os.path.join(bundle_dir,"CamLab.css"))
        with open(path_to_css) as file:
            self.setStyleSheet(stylesheet + file.read().format(**os.environ))

    @Slot(int)    
    def specimens_number(self, num):
        """Change number of specimens

        Arguments:
            num -- new number of specimens
        """
        index = self.tabs.currentIndex()
        if num == 1:
            self.tabs.specimen.setParent(None)
            for i in range(self.tabs.specimen.count()):
                self.tabs.specimen.specimens[f"Specimen {i+1}"]["tabs"].setParent(None)
            self.tabs.insert_persistent_tab(1, self.tabs.specimen.specimens["Specimen 1"]["tabs"], "Specimen")
            self.tabs.setCurrentIndex(index)
        elif self.tabs.specimen.count() == 0 and num > 1:
            self.tabs.specimen.specimens["Specimen 1"]["tabs"].setParent(None)
            self.tabs.insert_persistent_tab(1, self.tabs.specimen, "Specimen")
            self.tabs.setCurrentIndex(index)
            for i in range(num):
                self.tabs.specimen.add_persistent_tab(self.tabs.specimen.specimens[f"Specimen {i+1}"]["tabs"], f"Specimen {i+1}")
        elif num < self.tabs.specimen.count():
            for i in range(self.tabs.specimen.count(), num, -1):
                self.tabs.specimen.close_tab(i-1)
        elif num > self.tabs.specimen.count():
            for i in range(self.tabs.specimen.count(), num):
                self.tabs.specimen.add_persistent_tab(self.tabs.specimen.specimens[f"Specimen {i+1}"]["tabs"], f"Specimen {i+1}")
        self.configuration["shearbox"]["Number of Specimens"] = num

    @Slot(dict)
    def set_configuration(self):
        """Set the configuration"""

        self.set_theme()

        try:
            self.move(self.configuration["shearbox"]["x"], self.configuration["shearbox"]["y"])
            self.resize(self.configuration["shearbox"]["width"], self.configuration["shearbox"]["height"])
        except:
            pass
    
    @Slot()
    def shear_type(self):
        """switch between direct and residual shear.
        """
        index = self.tabs.currentIndex()
        if self.direct_shear.isChecked():
            self.configuration["shearbox"]["Mode"] = "direct"

            self.cycles_label.setParent(None)
            self.cycles.setParent(None)

            if self.configuration["shearbox"]["Residual Cycles"] > 1:
                self.tabs.shear.setParent(None)
                self.tabs.shear.cycles["Cycle 1"]["widget"].setParent(None)
                self.tabs.insert_persistent_tab(3, self.tabs.shear.cycles["Cycle 1"]["widget"], "Shear setup")
                self.tabs.setCurrentIndex(index)

            self.tabs.shear.cycles["Cycle 1"]["reverse_wait_label"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_wait"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_wait_unit"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_disp_label"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_disp"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_disp_unit"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_stress_label"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_stress"].setParent(None)
            self.tabs.shear.cycles["Cycle 1"]["reverse_stress_unit"].setParent(None)
        else:
            self.configuration["shearbox"]["Mode"] = "residual"

            self.cycles_layout.addWidget(self.cycles_label)
            self.cycles_layout.addWidget(self.cycles)

            if self.configuration["shearbox"]["Residual Cycles"] > 1:
                self.tabs.shear.cycles["Cycle 1"]["widget"].setParent(None)
                self.tabs.insert_persistent_tab(3, self.tabs.shear, "Shear setup")
                self.tabs.setCurrentIndex(index)
                self.tabs.shear.insert_persistent_tab(0, self.tabs.shear.cycles["Cycle 1"]["widget"], "Cycle 1")
                self.tabs.shear.setCurrentIndex(0)

            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_wait_label"], 2, 0)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_wait"], 2, 1)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_wait_unit"], 2, 2)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_disp_label"], 3, 0)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_disp"], 3, 1)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_disp_unit"], 3, 2)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_stress_label"], 4, 0)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_stress"], 4, 1)
            self.tabs.shear.cycles["Cycle 1"]["reverse_layout"].addWidget(self.tabs.shear.cycles["Cycle 1"]["reverse_stress_unit"], 4, 2)

        log.info(f'Shear mode set to "{self.configuration["shearbox"]["Mode"]}".')

    @Slot(int)    
    def residuals_number(self, num):
        """Change number of residual shear stages by one

        Arguments:
            num -- new number of residuals
        """
        index = self.tabs.currentIndex()
        if num == 1:
            self.tabs.shear.setParent(None)
            for i in range(self.tabs.shear.count()):
                self.tabs.shear.cycles[f"Cycle {i+1}"]["widget"].setParent(None)
            self.tabs.insert_persistent_tab(3, self.tabs.shear.cycles["Cycle 1"]["widget"], "Shear setup")
            self.tabs.setCurrentIndex(index)
        elif self.tabs.shear.count() == 0 and num > 1:
            self.tabs.shear.cycles["Cycle 1"]["widget"].setParent(None)
            self.tabs.insert_persistent_tab(3, self.tabs.shear, "Shear setup")
            self.tabs.setCurrentIndex(index)
            for i in range(num):
                self.tabs.shear.add_persistent_tab(self.tabs.shear.cycles[f"Cycle {i+1}"]["widget"], f"Cycle {i+1}")
        elif num < self.tabs.shear.count():
            for i in range(self.tabs.shear.count(), num, -1):
                self.tabs.shear.close_tab(i-1)
        elif num > self.tabs.shear.count():
            for i in range(self.tabs.shear.count(), num): 
                self.tabs.shear.add_persistent_tab(self.tabs.shear.cycles[f"Cycle {i+1}"]["widget"], f"Cycle {i+1}")
        self.configuration["shearbox"]["Residual Cycles"] = num

    def apply_configuration(self):
        """Apply configuration values to widgets"""

        self.get_devices_and_channels()
        self.addItemstoInstrumentComboboxes()

        self.specimens.setValue(self.configuration["shearbox"]["Number of Specimens"])
        self.specimens_number(self.configuration["shearbox"]["Number of Specimens"])

        if self.configuration["shearbox"]["Mode"] == "direct":
            self.direct_shear.setChecked(True)
        else:
            self.residual_shear.setChecked(True)
        self.shear_type()

        self.cycles.setValue(self.configuration["shearbox"]["Residual Cycles"])
        self.residuals_number(self.configuration["shearbox"]["Residual Cycles"])

        self.tabs.horiz_load_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Load Instrument"])
        if self.tabs.horiz_load_ins.currentText() != "":
            self.set_horiz_load_ins(self.tabs.horiz_load_ins.currentText(), apply_config=True)
            self.tabs.horiz_load_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Load Channel"])
            if self.tabs.horiz_load_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Horizontal Load Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Horizontal Load Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Horizontal Load Channel"] = None

        self.tabs.horiz_disp_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Instrument"])
        if self.tabs.horiz_disp_ins.currentText() != "":
            self.set_horiz_disp_ins(self.tabs.horiz_disp_ins.currentText(), apply_config=True)
            self.tabs.horiz_disp_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Channel"])
            if self.tabs.horiz_disp_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Horizontal Displacement Channel"] = None

        self.tabs.vert_load_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Load Instrument"])
        if self.tabs.vert_load_ins.currentText() != "":
            self.set_vert_load_ins(self.tabs.vert_load_ins.currentText(), apply_config=True)
            self.tabs.vert_load_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Load Channel"])
            if self.tabs.vert_load_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Vertical Load Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Vertical Load Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Vertical Load Channel"] = None

        self.tabs.vert_disp_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Displacement Instrument"])
        if self.tabs.vert_disp_ins.currentText() != "":
            self.set_vert_disp_ins(self.tabs.vert_disp_ins.currentText(), apply_config=True)
            self.tabs.vert_disp_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Displacement Channel"])
            if self.tabs.vert_disp_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Vertical Displacement Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Vertical Displacement Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Vertical Displacement Channel"] = None

        self.tabs.horiz_cont_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Control Instrument"])
        if self.tabs.horiz_cont_ins.currentText() != "":
            self.set_horiz_cont_ins(self.tabs.horiz_cont_ins.currentText(), apply_config=True)
            self.tabs.horiz_cont_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Horizontal Control Channel"])
            if self.tabs.horiz_cont_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Horizontal Control Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Horizontal Control Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Horizontal Control Channel"] = None

        self.tabs.vert_cont_ins.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Control Instrument"])
        if self.tabs.vert_cont_ins.currentText() != "":
            self.set_vert_cont_ins(self.tabs.vert_cont_ins.currentText(), apply_config=True)
            self.tabs.vert_cont_chan.setCurrentText(self.configuration["shearbox"]["Hardware"]["Vertical Control Channel"])
            if self.tabs.vert_cont_chan.currentText() == "":
                self.configuration["shearbox"]["Hardware"]["Vertical Control Channel"] = None
        else:
            self.configuration["shearbox"]["Hardware"]["Vertical Control Instrument"] = None
            self.configuration["shearbox"]["Hardware"]["Vertical Control Channel"] = None

        self.tabs.specimen.apply_configuration(self.configuration)
        self.specimen_selections()

        self.tabs.consolidation_start_stress.setText(num_to_str(self.configuration["shearbox"]["Consolidation"]["Initial Stress"]))
        self.tabs.consolidation_trigger_stress_select.setChecked(self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Stress"])
        self.tabs.consolidation_trigger_stress.setText(num_to_str(self.configuration["shearbox"]["Consolidation"]["Trigger Stress"]))
        self.tabs.consolidation_trigger_disp_select.setChecked(self.configuration["shearbox"]["Consolidation"]["Trigger Logging at Displacement"])
        self.tabs.consolidation_trigger_disp.setText(num_to_str(self.configuration["shearbox"]["Consolidation"]["Trigger Displacement"]))
        self.tabs.consolidation_in_water.setChecked(self.configuration["shearbox"]["Consolidation"]["Sample in Water"])

        self.tabs.consolidation_log_rate_radio.setChecked(self.configuration["shearbox"]["Consolidation"]["Logging Method"]=="rate")
        self.tabs.consolidation_log_rate_val.setText(secs_to_time(self.configuration["shearbox"]["Consolidation"]["Logging Rate"]))
        self.tabs.consolidation_log_timetable_radio.setChecked(self.configuration["shearbox"]["Consolidation"]["Logging Method"]=="timetable")
        self.tabs.consolidation_log_timetable_opt.setCurrentText(self.configuration["shearbox"]["Consolidation"]["Logging Timetable"])
        self.tabs.consolidation_log_change_radio.setChecked(self.configuration["shearbox"]["Consolidation"]["Logging Method"]=="change")
        self.tabs.consolidation_log_change_val.setText(num_to_str(self.configuration["shearbox"]["Consolidation"]["Logging Channel Change"]))

        self.tabs.consolidation_stop_rate_select.setChecked(self.configuration["shearbox"]["Consolidation"]["Stop on Rate of Change"])
        self.tabs.consolidation_stop_rate_disp.setText(num_to_str(self.configuration["shearbox"]["Consolidation"]["Stopping Displacement Change"]))
        self.tabs.consolidation_stop_rate_time.setText(secs_to_time(self.configuration["shearbox"]["Consolidation"]["Stopping Time Change"]))
        self.tabs.consolidation_stop_time_select.setChecked(self.configuration["shearbox"]["Consolidation"]["Stop after Time"])
        self.tabs.consolidation_stop_time_opt.setText(secs_to_time(self.configuration["shearbox"]["Consolidation"]["Stop Time"]))
        self.tabs.consolidation_stop_buzz.setChecked(self.configuration["shearbox"]["Consolidation"]["Buzz on Finish"])

        self.consolidation_selections()

        self.tabs.shear.apply_configuration(self.configuration)
        self.shear_selections()

        log.info("Configuration applied.")

    def block_signals(self, block):
        """Block/Unblock all signals from emitting

        Arguments:
            block -- bool (Block if True/Unblock if False)
        """
        self.blockSignals(block)
        self.tabs.blockSignals(block)
        self.tabs.horiz_load_ins.blockSignals(block)
        self.tabs.horiz_load_chan.blockSignals(block)
        self.tabs.horiz_disp_ins.blockSignals(block)
        self.tabs.horiz_disp_chan.blockSignals(block)
        self.tabs.vert_load_ins.blockSignals(block)
        self.tabs.vert_load_chan.blockSignals(block)
        self.tabs.vert_disp_ins.blockSignals(block)
        self.tabs.vert_disp_chan.blockSignals(block)
        self.tabs.horiz_cont_ins.blockSignals(block)
        self.tabs.horiz_cont_chan.blockSignals(block)
        self.tabs.vert_cont_ins.blockSignals(block)
        self.tabs.vert_cont_chan.blockSignals(block)

        for i in range(1,5):
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].rectangular.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_weight.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_height.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_width.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_depth.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].initial_radius.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["dimensions"].particle_density.blockSignals(block)
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_wet_weight.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].initial_dry_weight.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["moisture"].tin_initial_weight.blockSignals(block)
            
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_weight.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].platen_corr.blockSignals(block)
            self.tabs.specimen.specimens[f"Specimen {i}"]["additional"].est_strain_at_fail.blockSignals(block)

        self.tabs.consolidation_start_stress.blockSignals(block)
        self.tabs.consolidation_trigger_stress_select.blockSignals(block)
        self.tabs.consolidation_trigger_stress.blockSignals(block)
        self.tabs.consolidation_trigger_disp_select.blockSignals(block)
        self.tabs.consolidation_trigger_disp.blockSignals(block)
        self.tabs.consolidation_in_water.blockSignals(block)

        self.tabs.consolidation_log_rate_radio.blockSignals(block)
        self.tabs.consolidation_log_rate_val.blockSignals(block)
        self.tabs.consolidation_log_timetable_opt.blockSignals(block)
        self.tabs.consolidation_log_change_val.blockSignals(block)

        self.tabs.consolidation_stop_rate_select.blockSignals(block)
        self.tabs.consolidation_stop_rate_disp.blockSignals(block)
        self.tabs.consolidation_stop_rate_time.blockSignals(block)
        self.tabs.consolidation_stop_time_select.blockSignals(block)
        self.tabs.consolidation_stop_time_opt.blockSignals(block)
        self.tabs.consolidation_stop_buzz.blockSignals(block)

        for i in range(1,11): 
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed_select"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_speed"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_select"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_calc_opt"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_select"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["trigger_load_change"].blockSignals(block)

            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_radio"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["store_rate_val"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_radio"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["store_strain_val"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_radio"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["store_disp_val"].blockSignals(block)

            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop_select"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_drop"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain_select"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["stop_strain"].blockSignals(block)

            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_radio"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_rate_val"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_same"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_wait"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_disp"].blockSignals(block)
            self.tabs.shear.cycles[f"Cycle {i}"]["reverse_stress"].blockSignals(block)

    def closeEvent(self, event):

        if "shearbox" in self.configuration.keys():
            self.configuration["shearbox"]["x"] = self.frameGeometry().x()
            self.configuration["shearbox"]["y"] = self.frameGeometry().y()
            self.configuration["shearbox"]["width"] = self.frameGeometry().width()
            self.configuration["shearbox"]["height"] = self.frameGeometry().height()
            self.configuration["shearbox"]["active"] = False


        log.info("Closing ShearBox")
        return super().closeEvent(event)