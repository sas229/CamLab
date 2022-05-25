from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Signal, Slot
import local_pyqtgraph.pyqtgraph as pg
import numpy as np
import logging
import os

log = logging.getLogger(__name__)

class CameraTab(QWidget):
    previewWindowClosed = Signal(QWidget)
    getImage = Signal()

    def __init__(self, name):
        """CameraTab init."""
        super().__init__()
        self.setWhatsThis("camera")
        self.name = name

        # Image item.
        self.preview = pg.GraphicsLayoutWidget()
        self.preview.setBackground(None)
        self.viewBox = self.preview.addViewBox()
        self.viewBox.setAspectLocked(True)
        self.imageItem = pg.ImageItem(axisOrder="row-major")
        self.viewBox.addItem(self.imageItem)

        self.label = QLabel("Live Preview")

        self.layout = QGridLayout()
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.preview, 1, 0)

        self.setLayout(self.layout)

    @Slot(np.ndarray)
    def set_image(self, image):
        """Set image in ImageItem."""
        image = np.flipud(image)
        self.imageItem.setImage(image=image)
        self.preview.setBackground(None)
        self.getImage.emit()

    def set_window(self):
        """Method to set widget as window."""
        x = int(self.cameraConfiguration["preview"]["x"])
        y = int(self.cameraConfiguration["preview"]["y"])
        w = int(self.cameraConfiguration["preview"]["width"])
        h = int(self.cameraConfiguration["preview"]["height"])
        self.setGeometry(x, y, w, h)
        self.cameraConfiguration["preview"]["mode"] = "window"

    def set_tab(self):
        """Method to set widget as tab."""
        self.cameraConfiguration["preview"]["mode"] = "tab"

    @Slot(str, str)
    def setTitle(self, currentTitle, newTitle):
        """Method to set widget title."""
        if self.windowTitle() == currentTitle:
            self.setWindowTitle(newTitle)
                
    def set_configuration(self, configuration):
        """Method to set configuration for widget."""
        # Set the configuration.
        self.cameraConfiguration = configuration["devices"][self.name]

    def resizeEvent(self, event):
        """Override of Qt resizeEvent method."""
        if self.cameraConfiguration["preview"]["mode"] == "window":
            self.cameraConfiguration["preview"]["width"] = int(self.width())
            self.cameraConfiguration["preview"]["height"] = int(self.height())

    def moveEvent(self, event):
        """Override of Qt moveEvent method."""
        if self.cameraConfiguration["preview"]["mode"] == "window":
            position = self.geometry()
            self.cameraConfiguration["preview"]["x"] = int(position.x())
            self.cameraConfiguration["preview"]["y"] = int(position.y())

    def closeEvent(self, event):
        """Override of Qt closeEvent method."""
        self.previewWindowClosed.emit(self)