from PySide6.QtWidgets import QTabWidget, QWidget, QTabBar, QGridLayout, QLineEdit, QLabel
from PySide6.QtGui import QDoubleValidator
from widgets.ShearboxWindow.DimensionTab import DimensionTab
from widgets.ShearboxWindow.MoistureTab import MoistureTab
from widgets.ShearboxWindow.AdditionalTab import AdditionalTab
import logging 

log = logging.getLogger(__name__)

class SpecimenTabs(QTabWidget):

    def __init__(self):
        super().__init__()
        """TabInterface init."""

        self.specimens = dict()

        for i in range(1,5):
            specimen = f"Specimen {i}"
            self.specimens[specimen] = dict()
            self.build_specimen(specimen)
            if i == 1:
                self.add_persistent_tab(self.specimens[specimen]["tabs"], specimen)

    def build_specimen(self, specimen):
        """Build one of the specimen tabs

        Arguments:
            specimen -- Tab name
        """
        self.specimens[specimen]["tabs"] = QTabWidget()
        self.specimens[specimen]["layout"] = QGridLayout()
        self.specimens[specimen]["dimensions"] = DimensionTab()
        self.specimens[specimen]["moisture"] = MoistureTab()
        self.specimens[specimen]["additional"] = AdditionalTab()

        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["dimensions"], "Dimensions")
        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["moisture"], "Moisture")
        self.specimens[specimen]["tabs"].addTab(self.specimens[specimen]["additional"], "Additional Data")

    def add_persistent_tab(self, widget, name):
        """Method to add persistent tab."""
        self.addTab(widget, name)
        index = self.tabBar().count()-1
        self.tabBar().setTabButton(index, QTabBar.RightSide, None)
        log.info("Specimen tab added.")

    def close_tab(self, index):
        """Method to close tab."""
        self.removeTab(index)
        log.info("Specimen tab removed.")
    