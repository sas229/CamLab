from PySide6.QtWidgets import QTabWidget, QTabBar, QGridLayout
from widgets.ShearboxWindow.DimensionTab import DimensionTab
from widgets.ShearboxWindow.MoistureTab import MoistureTab
from widgets.ShearboxWindow.AdditionalTab import AdditionalTab
import logging 

log = logging.getLogger(__name__)

class SpecimenTabs(QTabWidget):

    def __init__(self, configuration):
        super().__init__()
        """TabInterface init."""

        self.specimens = dict()

        for i in range(1,5):
            specimen = f"Specimen {i}"
            self.specimens[specimen] = dict()
            self.build_specimen(specimen, configuration)
            if i > 1 and i <= configuration["shearbox"]["Number of Specimens"]:
                self.add_persistent_tab(self.specimens[specimen]["tabs"], specimen)

    def build_specimen(self, specimen, configuration):
        """Build one of the specimen tabs

        Arguments:
            specimen -- Tab name
        """
        self.specimens[specimen]["tabs"] = QTabWidget()
        self.specimens[specimen]["dimensions"] = DimensionTab(specimen, configuration)
        self.specimens[specimen]["moisture"] = MoistureTab()
        self.specimens[specimen]["additional"] = AdditionalTab()

        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["dimensions"], "Dimensions")
        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["moisture"], "Moisture")
        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["additional"], "Additional Data")

        self.apply_configuration(specimen, configuration)

    def apply_configuration(self, specimen, configuration):
        """Apply configuration values to widgets

        Arguments:
            specimen -- Tab name
            configuration -- Configuration to apply
        """
        self.specimens[specimen]["dimensions"].initial_weight.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Weight"])
        self.specimens[specimen]["dimensions"].initial_height.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Height"])
        self.specimens[specimen]["dimensions"].rectangular.setChecked(configuration["shearbox"]["Specimens"][specimen]["Shape"]=="rectangular")
        self.specimens[specimen]["dimensions"].circular.setChecked(configuration["shearbox"]["Specimens"][specimen]["Shape"]=="circular")
        self.specimens[specimen]["dimensions"].initial_width.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Width"])
        self.specimens[specimen]["dimensions"].initial_depth.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Depth"])
        self.specimens[specimen]["dimensions"].initial_radius.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Radius"])
        self.specimens[specimen]["dimensions"].particle_density.setText(configuration["shearbox"]["Specimens"][specimen]["Particle Density"])
        self.specimens[specimen]["dimensions"].initial_area.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Area"])
        self.specimens[specimen]["dimensions"].initial_volume.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Volume"])
        self.specimens[specimen]["dimensions"].initial_bulk_density.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Bulk Density"])
        
        self.specimens[specimen]["moisture"].initial_wet_weight.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Wet Weight"])
        self.specimens[specimen]["moisture"].initial_dry_weight.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Dry Weight"])
        self.specimens[specimen]["moisture"].tin_initial_weight.setText(configuration["shearbox"]["Specimens"][specimen]["Tin (initial) Weight"])
        self.specimens[specimen]["moisture"].initial_moisture.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Moisture"])
        self.specimens[specimen]["moisture"].initial_dry_density.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Dry Density"])
        self.specimens[specimen]["moisture"].initial_voids_ratio.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Voids Ratio"])
        self.specimens[specimen]["moisture"].initial_deg_of_sat.setText(configuration["shearbox"]["Specimens"][specimen]["Initial Degree of Saturation"])

        self.specimens[specimen]["additional"].platen_weight.setText(configuration["shearbox"]["Specimens"][specimen]["Platen Weight"])
        self.specimens[specimen]["additional"].platen_corr.setText(configuration["shearbox"]["Specimens"][specimen]["Platen Correction"])
        self.specimens[specimen]["additional"].est_strain_at_fail.setText(configuration["shearbox"]["Specimens"][specimen]["Estimated Strain at Shear Failure"])

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
        log.info(f'"{name}" tab added.')

    def close_tab(self, index):
        """Method to close tab."""
        name = self.tabText(index)
        self.removeTab(index)
        log.info(f'"{name}" tab removed.')
    