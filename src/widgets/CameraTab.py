from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from PySide6.QtCore import Signal, Slot
import src.local_pyqtgraph.pyqtgraph as pg
import numpy as np
import logging
import os

log = logging.getLogger(__name__)

class CameraTab(QWidget):
    previewWindowClosed = Signal(QWidget)
    getImage = Signal()

    def __init__(self, name):
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

    def setWindow(self):
        x = int(self.cameraConfiguration["preview"]["x"])
        y = int(self.cameraConfiguration["preview"]["y"])
        w = int(self.cameraConfiguration["preview"]["width"])
        h = int(self.cameraConfiguration["preview"]["height"])
        self.setGeometry(x, y, w, h)
        self.cameraConfiguration["preview"]["mode"] = "window"

    def setTab(self):
        self.cameraConfiguration["preview"]["mode"] = "tab"

    @Slot(str, str)
    def setTitle(self, currentTitle, newTitle):
        if self.windowTitle() == currentTitle:
            self.setWindowTitle(newTitle)
        
    def resizeEvent(self, event):
        # Save updated size in configuration.
        if self.cameraConfiguration["preview"]["mode"] == "window":
            self.cameraConfiguration["preview"]["width"] = int(self.width())
            self.cameraConfiguration["preview"]["height"] = int(self.height())

    def moveEvent(self, event):
        # Save updated position in configuration.
        if self.cameraConfiguration["preview"]["mode"] == "window":
            position = self.geometry()
            self.cameraConfiguration["preview"]["x"] = int(position.x())
            self.cameraConfiguration["preview"]["y"] = int(position.y())
        
    def setConfiguration(self, configuration):
        # Set the configuration.
        self.cameraConfiguration = configuration["devices"][self.name]

    def closeEvent(self, event):
        self.previewWindowClosed.emit(self)