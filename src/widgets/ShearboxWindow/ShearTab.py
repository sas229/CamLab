from PySide6.QtWidgets import QTabWidget, QTabBar, QGridLayout, QLineEdit, QLabel, QRadioButton, QGroupBox, QCheckBox, QComboBox, QSpinBox, QVBoxLayout, QWidget
from PySide6.QtGui import QDoubleValidator, QRegularExpressionValidator
import logging 

log = logging.getLogger(__name__)

def num_to_str(num):
    if num != None:
        return str(num)
    else:
        return ""

class ShearTabs(QTabWidget):

    def __init__(self, configuration):
        super().__init__()
        """Shear stage defining tabs"""

        self.cycles = dict()

        for i in range(1,11):
            cycle = f"Cycle {i}"
            self.cycles[cycle] = dict()
            self.build_tab(cycle, configuration)
            if configuration["shearbox"]["Residual Cycles"] > 1 and i <= configuration["shearbox"]["Residual Cycles"] and (configuration["shearbox"]["Mode"] == "residual" or i != 1):
                self.add_persistent_tab(self.cycles[cycle]["widget"], cycle)

    def build_tab(self, cycle, configuration):
        """Build one of the shear tabs

        Arguments:
            cycle -- Tab name
        """
        self.cycles[cycle]["widget"] = QWidget()
        self.cycles[cycle]["layout"] = QVBoxLayout()

        self.cycles[cycle]["trigger"] = QGroupBox("Trigger conditions")
        self.cycles[cycle]["trigger_layout"] = QGridLayout()
        self.cycles[cycle]["store"] = QGroupBox("Storage Conditions")
        self.cycles[cycle]["store_layout"] = QGridLayout()
        self.cycles[cycle]["stop"] = QGroupBox("Stopping Conditions")
        self.cycles[cycle]["stop_layout"] = QGridLayout()
        self.cycles[cycle]["reverse"] = QGroupBox("Reversing")
        self.cycles[cycle]["reverse_layout"] = QGridLayout()

        self.cycles[cycle]["trigger_speed_select"] = QRadioButton("Enter shearing speed")
        self.cycles[cycle]["trigger_speed"] = QLineEdit()
        self.cycles[cycle]["trigger_calc_select"] = QRadioButton("Use the rate calculated during consolidation")
        self.cycles[cycle]["trigger_calc_opt"] = QComboBox()
        self.cycles[cycle]["trigger_load_select"] = QCheckBox("Start when the shear load changes by")
        self.cycles[cycle]["trigger_load_change"] = QLineEdit()

        self.cycles[cycle]["store_rate_radio"] = QRadioButton("Log data at this rate")
        self.cycles[cycle]["store_rate_val"] = QLineEdit()
        self.cycles[cycle]["store_strain_radio"] = QRadioButton("When Horizontal Strain changes by")
        self.cycles[cycle]["store_strain_val"] = QLineEdit()
        self.cycles[cycle]["store_disp_radio"] = QRadioButton("When Horizontal Displacement changes by")
        self.cycles[cycle]["store_disp_val"] = QLineEdit()

        self.cycles[cycle]["stop_drop_select"] = QCheckBox("After the Shear Stress reaches a peak\nand repeatedly falls this number of times")
        self.cycles[cycle]["stop_drop"] = QSpinBox()
        self.cycles[cycle]["stop_strain_select"] = QCheckBox("When the Shear Strain reaches this level")
        self.cycles[cycle]["stop_strain"] = QLineEdit()

        self.cycles[cycle]["reverse_rate_radio"] = QRadioButton("Reverse at this speed")
        self.cycles[cycle]["reverse_rate_val"] = QLineEdit()
        self.cycles[cycle]["reverse_same"] = QRadioButton("Use the same speed as the initial shear")
        self.cycles[cycle]["reverse_wait_label"] = QLabel("Wait time for pore pressure to equalise")
        self.cycles[cycle]["reverse_wait"] = QLineEdit()
        self.cycles[cycle]["reverse_wait_unit"] = QLabel("(hh:mm:ss)")
        self.cycles[cycle]["reverse_disp_label"] = QLabel("Then re-shear until the shear displacement is:")
        self.cycles[cycle]["reverse_disp"] = QLineEdit()
        self.cycles[cycle]["reverse_disp_unit"] = QLabel("mm")
        self.cycles[cycle]["reverse_stress_label"] = QLabel("Repeat the procedure until the change in\nShear Stress between passes is less than:")
        self.cycles[cycle]["reverse_stress"] = QLineEdit()
        self.cycles[cycle]["reverse_stress_unit"] = QLabel("kPa")

        time_validator = QRegularExpressionValidator("^(2[0-3]|[01]?[0-9]):([0-5][0-9]):([0-5][0-9])$")
        num_validator = QDoubleValidator(bottom=0)

        self.cycles[cycle]["trigger_speed"].setValidator(num_validator)
        self.cycles[cycle]["trigger_load_change"].setValidator(num_validator)
        self.cycles[cycle]["store_rate_val"].setValidator(time_validator)
        self.cycles[cycle]["store_strain_val"].setValidator(num_validator)
        self.cycles[cycle]["stop_strain"].setValidator(num_validator)
        self.cycles[cycle]["reverse_rate_val"].setValidator(num_validator)
        self.cycles[cycle]["reverse_wait"].setValidator(time_validator)
        self.cycles[cycle]["reverse_disp"].setValidator(num_validator)
        self.cycles[cycle]["reverse_stress"].setValidator(num_validator)

        self.cycles[cycle]["trigger_calc_opt"].addItem("Use the largest vertical stress")
        self.cycles[cycle]["trigger_calc_opt"].addItem("Use the last applied vertical stress")
        self.cycles[cycle]["trigger_calc_opt"].addItem("Use the average of all vertical stresses")

        self.cycles[cycle]["stop_drop"].setMinimum(2)
        self.cycles[cycle]["stop_drop"].setMaximum(15)
        self.cycles[cycle]["stop_drop"].setValue(2)

        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_speed_select"], 0, 0)
        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_speed"], 0, 1)
        self.cycles[cycle]["trigger_layout"].addWidget(QLabel("mm/min"), 0, 2)
        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_calc_select"], 1, 0)
        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_calc_opt"], 1, 1)
        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_load_select"], 2, 0)
        self.cycles[cycle]["trigger_layout"].addWidget(self.cycles[cycle]["trigger_load_change"], 2, 1)
        self.cycles[cycle]["trigger_layout"].addWidget(QLabel("N/s"), 2, 2)

        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_rate_radio"], 0, 0)
        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_rate_val"], 0, 1)
        self.cycles[cycle]["store_layout"].addWidget(QLabel("(hh:mm:ss)"), 0, 2)
        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_strain_radio"], 1, 0)
        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_strain_val"], 1, 1)
        self.cycles[cycle]["store_layout"].addWidget(QLabel("%"), 1, 2)
        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_disp_radio"], 2, 0)
        self.cycles[cycle]["store_layout"].addWidget(self.cycles[cycle]["store_disp_val"], 2, 1)
        self.cycles[cycle]["store_layout"].addWidget(QLabel("%"), 2, 2)

        self.cycles[cycle]["stop_layout"].addWidget(self.cycles[cycle]["stop_drop_select"], 0, 0)
        self.cycles[cycle]["stop_layout"].addWidget(self.cycles[cycle]["stop_drop"], 0, 1)
        self.cycles[cycle]["stop_layout"].addWidget(self.cycles[cycle]["stop_strain_select"], 1, 0)
        self.cycles[cycle]["stop_layout"].addWidget(self.cycles[cycle]["stop_strain"], 1, 1)
        self.cycles[cycle]["stop_layout"].addWidget(QLabel("%"), 1, 2)

        self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_rate_radio"], 0, 0)
        self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_rate_val"], 0, 1)
        self.cycles[cycle]["reverse_layout"].addWidget(QLabel("mm/min"), 0, 2)
        self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_same"], 1, 0, 1, 3)

        if configuration["shearbox"]["Mode"] == "residual" or cycle != "Cycle 1":
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_wait_label"], 2, 0)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_wait"], 2, 1)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_wait_unit"], 2, 2)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_disp_label"], 3, 0)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_disp"], 3, 1)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_disp_unit"], 3, 2)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_stress_label"], 4, 0)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_stress"], 4, 1)
            self.cycles[cycle]["reverse_layout"].addWidget(self.cycles[cycle]["reverse_stress_unit"], 4, 2)

        self.cycles[cycle]["trigger"].setLayout(self.cycles[cycle]["trigger_layout"])
        self.cycles[cycle]["store"].setLayout(self.cycles[cycle]["store_layout"])
        self.cycles[cycle]["stop"].setLayout(self.cycles[cycle]["stop_layout"])
        self.cycles[cycle]["reverse"].setLayout(self.cycles[cycle]["reverse_layout"])

        self.cycles[cycle]["layout"].addWidget(self.cycles[cycle]["trigger"], 0)
        self.cycles[cycle]["layout"].addWidget(self.cycles[cycle]["store"], 0)
        self.cycles[cycle]["layout"].addWidget(self.cycles[cycle]["stop"], 0)
        self.cycles[cycle]["layout"].addWidget(self.cycles[cycle]["reverse"], 0)

        self.cycles[cycle]["widget"].setLayout(self.cycles[cycle]["layout"])

        self.cycles[cycle]["trigger_layout"].setColumnStretch(0,8)
        self.cycles[cycle]["trigger_layout"].setColumnStretch(1,4)
        self.cycles[cycle]["trigger_layout"].setColumnStretch(2,1)
        self.cycles[cycle]["store_layout"].setColumnStretch(0,8)
        self.cycles[cycle]["store_layout"].setColumnStretch(1,4)
        self.cycles[cycle]["store_layout"].setColumnStretch(2,1)
        self.cycles[cycle]["stop_layout"].setColumnStretch(0,8)
        self.cycles[cycle]["stop_layout"].setColumnStretch(1,4)
        self.cycles[cycle]["stop_layout"].setColumnStretch(2,1)
        self.cycles[cycle]["reverse_layout"].setColumnStretch(0,8)
        self.cycles[cycle]["reverse_layout"].setColumnStretch(1,4)
        self.cycles[cycle]["reverse_layout"].setColumnStretch(2,1)

    def apply_configuration(self, configuration):
        """Apply configuration values to widgets

        Arguments:
            configuration -- configuration to apply
        """
        for i in range(1,11):
            cycle = f"Cycle {i}"
            self.cycles[cycle]["trigger_speed_select"].setChecked(configuration["shearbox"]["Shear"][cycle]["Shear Speed Selection"]=="manual")
            self.cycles[cycle]["trigger_speed"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Shear Speed"]))
            self.cycles[cycle]["trigger_calc_select"].setChecked(configuration["shearbox"]["Shear"][cycle]["Shear Speed Selection"]=="calculated")
            self.cycles[cycle]["trigger_calc_opt"].setCurrentText(configuration["shearbox"]["Shear"][cycle]["Speed Calculation"])
            self.cycles[cycle]["trigger_load_select"].setChecked(configuration["shearbox"]["Shear"][cycle]["Trigger on Load Change"])
            self.cycles[cycle]["trigger_load_change"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Load Change Rate"]))

            self.cycles[cycle]["store_rate_radio"].setChecked(configuration["shearbox"]["Shear"][cycle]["Logging Method"]=="rate")
            self.cycles[cycle]["store_rate_val"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Logging Rate"]))
            self.cycles[cycle]["store_strain_radio"].setChecked(configuration["shearbox"]["Shear"][cycle]["Logging Method"]=="strain")
            self.cycles[cycle]["store_strain_val"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Logging Strain"]))
            self.cycles[cycle]["store_disp_radio"].setChecked(configuration["shearbox"]["Shear"][cycle]["Logging Method"]=="displacement")
            self.cycles[cycle]["store_disp_val"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Logging Displacement"]))

            self.cycles[cycle]["stop_drop_select"].setChecked(configuration["shearbox"]["Shear"][cycle]["Stop after Repeated Falls"])
            self.cycles[cycle]["stop_drop"].setValue(configuration["shearbox"]["Shear"][cycle]["Number of Falls"])
            self.cycles[cycle]["stop_strain_select"].setChecked(configuration["shearbox"]["Shear"][cycle]["Stop on Maximum Strain"])
            self.cycles[cycle]["stop_strain"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Maximum Strain"]))

            self.cycles[cycle]["reverse_rate_radio"].setChecked(configuration["shearbox"]["Shear"][cycle]["Reverse Method"]=="rate")
            self.cycles[cycle]["reverse_rate_val"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Reverse Speed"]))
            self.cycles[cycle]["reverse_same"].setChecked(configuration["shearbox"]["Shear"][cycle]["Reverse Method"]=="same")
            self.cycles[cycle]["reverse_wait"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Wait before Reversing"]))
            self.cycles[cycle]["reverse_disp"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Shear until Displacement"]))
            self.cycles[cycle]["reverse_stress"].setText(num_to_str(configuration["shearbox"]["Shear"][cycle]["Repeat until Stress"]))

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
        log.info(f'"{name}" tab added.')
    
    def insert_persistent_tab(self, index, widget, name):
        """Method to insert a persistent tab at the given index."""
        self.insertTab(index, widget, name)
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
        log.info(f'"{name}" tab inserted.')

    def close_tab(self, index):
        """Method to close tab."""
        name = self.tabText(index)
        self.removeTab(index)
        log.info(f'"{name}" tab removed.')
    