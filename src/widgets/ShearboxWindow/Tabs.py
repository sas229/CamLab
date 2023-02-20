from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QGridLayout, QVBoxLayout, QComboBox, QLabel, QGroupBox, QRadioButton, QCheckBox, QLineEdit
from PySide6.QtGui import QDoubleValidator, QRegularExpressionValidator
from PySide6.QtCore import Slot, Qt
from widgets.PlotWindow import PlotWindow
from widgets.ShearboxWindow.SpecimenTab import SpecimenTabs
import logging 

log = logging.getLogger(__name__)

class TabInterface(QTabWidget):

    def __init__(self):
        super().__init__()
        """TabInterface init."""

        # Settings.
        self.hardware = QWidget()
        self.specimen = QWidget()
        self.consolidation = QWidget()
        self.shear = QWidget()

        self.add_persistent_tab(self.hardware, "Hardware")
        self.add_persistent_tab(self.specimen, "Specimen")
        self.add_persistent_tab(self.consolidation, "Consolidation setup")
        self.add_persistent_tab(self.shear, "Shear setup")

        self.build_hardware_tab()
        self.build_specimen_tab()
        self.build_consolidation_tab()
        self.build_shear_tab()

    def build_hardware_tab(self):
        self.hardwareLayout = QGridLayout()

        self.hardwareLayout.addWidget(QLabel("Controllers & Transducer Inputs"), 0, 0, 1, 2, Qt.AlignCenter)
        self.hardwareLayout.addWidget(QLabel("Instrument"), 0, 2, Qt.AlignCenter)
        self.hardwareLayout.addWidget(QLabel("Channel"), 0, 3, Qt.AlignCenter)

        self.horiz_load_ins = QComboBox()
        self.horiz_load_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal load input"), 1, 0)
        self.hardwareLayout.addWidget(QLabel("N"), 1, 1)
        self.hardwareLayout.addWidget(self.horiz_load_ins, 1, 2)
        self.hardwareLayout.addWidget(self.horiz_load_chan, 1, 3)
        
        self.horiz_disp_ins = QComboBox()
        self.horiz_disp_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal displacement input"), 2, 0)
        self.hardwareLayout.addWidget(QLabel("mm"), 2, 1)
        self.hardwareLayout.addWidget(self.horiz_disp_ins, 2, 2)
        self.hardwareLayout.addWidget(self.horiz_disp_chan, 2, 3)
        
        self.vert_load_ins = QComboBox()
        self.vert_load_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical load input"), 3, 0)
        self.hardwareLayout.addWidget(QLabel("N"), 3, 1)
        self.hardwareLayout.addWidget(self.vert_load_ins, 3, 2)
        self.hardwareLayout.addWidget(self.vert_load_chan, 3, 3)
        
        self.vert_disp_ins = QComboBox()
        self.vert_disp_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical displacement input"), 4, 0)
        self.hardwareLayout.addWidget(QLabel("mm"), 4, 1)
        self.hardwareLayout.addWidget(self.vert_disp_ins, 4, 2)
        self.hardwareLayout.addWidget(self.vert_disp_chan, 4, 3)
        
        self.horiz_cont_ins = QComboBox()
        self.horiz_cont_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Horizontal Control Machine"), 5, 0)
        self.hardwareLayout.addWidget(self.horiz_cont_ins, 5, 2)
        self.hardwareLayout.addWidget(self.horiz_cont_chan, 5, 3)
        
        self.vert_cont_ins = QComboBox()
        self.vert_cont_chan = QComboBox()
        self.hardwareLayout.addWidget(QLabel("Vertical Control Machine"), 6, 0)
        self.hardwareLayout.addWidget(self.vert_cont_ins, 6, 2)
        self.hardwareLayout.addWidget(self.vert_cont_chan, 6, 3)

        self.hardwareLayout.addWidget(QWidget(),7,0,1,4)

        self.hardwareLayout.setRowStretch(0,0)
        self.hardwareLayout.setRowStretch(1,1)
        self.hardwareLayout.setRowStretch(2,1)
        self.hardwareLayout.setRowStretch(3,1)
        self.hardwareLayout.setRowStretch(4,1)
        self.hardwareLayout.setRowStretch(5,1)
        self.hardwareLayout.setRowStretch(6,1)
        self.hardwareLayout.setRowStretch(7,1)
        self.hardwareLayout.setColumnStretch(0,0)
        self.hardwareLayout.setColumnStretch(1,0)
        self.hardwareLayout.setColumnStretch(2,1)
        self.hardwareLayout.setColumnStretch(3,1)
        self.hardwareLayout.setHorizontalSpacing(15)
        self.hardwareLayout.setVerticalSpacing(15)

        self.hardware.setLayout(self.hardwareLayout)
        
    def build_specimen_tab(self):
        self.specimenLayout = QVBoxLayout()
        self.specimen.tabs = SpecimenTabs()
        self.specimenLayout.addWidget(self.specimen.tabs)
        self.specimen.setLayout(self.specimenLayout)
        
    def build_consolidation_tab(self):
        self.consolidationLayout = QVBoxLayout()
        self.consolidation_start = QGroupBox("Starting conditions")
        self.consolidation_start_layout = QGridLayout()
        self.consolidation_log = QGroupBox("Data Logging")
        self.consolidation_log_layout = QGridLayout()
        self.consolidation_stop = QGroupBox("Stop Criteria")
        self.consolidation_stop_layout = QGridLayout()

        self.consolidation_start_stress = QLineEdit()
        self.consolidation_trigger_stress_select = QCheckBox("Trigger data logging as soon as the\nnormal stress exceeds this level:")
        self.consolidation_trigger_stress = QLineEdit()
        self.consolidation_trigger_disp_select = QCheckBox("Or whenever the normal settlement\nchanges by this amount")
        self.consolidation_trigger_disp = QLineEdit()
        self.consolidation_in_water = QCheckBox("Specimen is submersed in water")

        self.consolidation_log_rate_radio = QRadioButton("Log data at this rate")
        self.consolidation_log_rate_val = QLineEdit()
        self.consolidation_log_timetable_radio = QRadioButton("Use the following timetable for data logging")
        self.consolidation_log_timetable_opt = QComboBox()
        self.consolidation_log_change_radio = QRadioButton("Every time the settlement input channel\nchanges by the given amount")
        self.consolidation_log_change_val = QLineEdit()

        self.consolidation_stop_rate_select = QCheckBox("When the settlement does not change by\nmore than the value entered here within the specified time")
        self.consolidation_stop_rate_disp = QLineEdit()
        self.consolidation_stop_rate_time = QLineEdit()
        self.consolidation_stop_time_select = QCheckBox("When the maximum time entered here is exceeded")
        self.consolidation_stop_time_opt = QLineEdit()
        self.consolidation_stop_buzz = QCheckBox("Buzz to inform when the consolidation stage is completed")

        time_validator = QRegularExpressionValidator("^(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])$")
        num_validator = QDoubleValidator(bottom=0)

        self.consolidation_start_stress.setValidator(num_validator)
        self.consolidation_trigger_stress.setValidator(num_validator)
        self.consolidation_trigger_disp.setValidator(num_validator)
        self.consolidation_log_rate_val.setValidator(time_validator)
        self.consolidation_log_change_val.setValidator(num_validator)
        self.consolidation_stop_rate_disp.setValidator(num_validator)
        self.consolidation_stop_rate_time.setValidator(time_validator)
        self.consolidation_stop_time_opt.setValidator(num_validator)

        self.consolidation_trigger_stress_select.setChecked(True)
        self.consolidation_log_rate_radio.setChecked(True)
        self.consolidation_stop_rate_select.setChecked(True)

        self.consolidation_start_layout.addWidget(QLabel("Apply the following vertical stress"), 0, 0)
        self.consolidation_start_layout.addWidget(self.consolidation_start_stress, 0, 1)
        self.consolidation_start_layout.addWidget(QLabel("kPa"), 0, 2)
        self.consolidation_start_layout.addWidget(self.consolidation_trigger_stress_select, 1, 0)
        self.consolidation_start_layout.addWidget(self.consolidation_trigger_stress, 1, 1)
        self.consolidation_start_layout.addWidget(QLabel("kPa"), 1, 2)
        self.consolidation_start_layout.addWidget(self.consolidation_trigger_disp_select, 2, 0)
        self.consolidation_start_layout.addWidget(self.consolidation_trigger_disp, 2, 1)
        self.consolidation_start_layout.addWidget(QLabel("mm"), 2, 2)
        self.consolidation_start_layout.addWidget(self.consolidation_in_water, 3, 0, 1, 3)

        self.consolidation_log_layout.addWidget(self.consolidation_log_rate_radio, 0, 0)
        self.consolidation_log_layout.addWidget(self.consolidation_log_rate_val, 0, 1)
        # self.consolidation_log_layout.addWidget(QLabel("kPa"), 0, 2)
        self.consolidation_log_layout.addWidget(self.consolidation_log_timetable_radio, 1, 0)
        self.consolidation_log_layout.addWidget(self.consolidation_log_timetable_opt, 1, 1)
        # self.consolidation_log_layout.addWidget(QLabel("Edit"), 1, 2)
        self.consolidation_log_layout.addWidget(self.consolidation_log_change_radio, 2, 0)
        self.consolidation_log_layout.addWidget(self.consolidation_log_change_val, 2, 1)
        # self.consolidation_log_layout.addWidget(QLabel("kPa"), 2, 2)

        self.consolidation_stop_layout.addWidget(self.consolidation_stop_rate_select, 0, 0, 2, 1)
        self.consolidation_stop_layout.addWidget(self.consolidation_stop_rate_disp, 0, 1)
        self.consolidation_stop_layout.addWidget(QLabel("mm"), 0, 2)
        self.consolidation_stop_layout.addWidget(self.consolidation_stop_rate_time, 1, 1)
        self.consolidation_stop_layout.addWidget(self.consolidation_stop_time_select, 2, 0)
        self.consolidation_stop_layout.addWidget(self.consolidation_stop_time_opt, 2, 1)
        # self.consolidation_stop_layout.addWidget(QLabel("kPa"), 2, 2)
        self.consolidation_stop_layout.addWidget(self.consolidation_stop_buzz, 3, 0, 1, 3)

        self.consolidation_start.setLayout(self.consolidation_start_layout)
        self.consolidation_log.setLayout(self.consolidation_log_layout)
        self.consolidation_stop.setLayout(self.consolidation_stop_layout)

        self.consolidationLayout.addWidget(self.consolidation_start, 0)
        self.consolidationLayout.addWidget(self.consolidation_log, 0)
        self.consolidationLayout.addWidget(self.consolidation_stop, 0)

        self.consolidation.setLayout(self.consolidationLayout)
        
    def build_shear_tab(self):
        self.shearLayout = QGridLayout()
        self.shear.setLayout(self.shearLayout)

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)

    @Slot(int)
    def close_tab(self, index):
        """Method to close tab."""
        widget = self.widget(index)
        # Delete if a plot widget.
        if isinstance(widget, PlotWindow):
            plotNumber = widget.plotNumber
            self.remove_plot.emit(plotNumber)
        self.removeTab(index)
        log.info("Tab removed.")
    