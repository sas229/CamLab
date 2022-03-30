from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Signal, Slot
import src.local_pyqtgraph.pyqtgraph as pg
from PIL import Image
import numpy as np
import logging

logging.getLogger("PIL").setLevel(logging.WARNING)

class CameraTab(QWidget):
    previewWindowClosed = Signal(QWidget)

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
        self.imageItem.setAutoDownsample(active=True)
        self.viewBox.addItem(self.imageItem)

        self.label = QLabel("Live Preview")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.preview)

        self.setLayout(self.layout)

        # Test image.
        image = Image.open("Test.png")
        image = image.transpose(Image.TRANSVERSE)
        numpy_image = np.asarray(image)
        self.set_image(numpy_image)

    @Slot(np.ndarray)
    def set_image(self, image):
        """Set image in ImageItem."""
        image = np.flipud(image)
        self.imageItem.setImage(image=image)
        self.update_background()

    def update_background(self):
        """Update background."""
        self.preview.setBackground(None)

    def setWindow(self):
        x = int(self.configuration["preview"]["x"])
        y = int(self.configuration["preview"]["y"])
        w = int(self.configuration["preview"]["width"])
        h = int(self.configuration["preview"]["height"])
        self.setGeometry(x, y, w, h)
        self.configuration["preview"]["mode"] = "window"

    def setTab(self):
        self.configuration["preview"]["mode"] = "tab"
        
    def resizeEvent(self, event):
        # Save updated size in configuration.
        self.configuration["preview"]["width"] = int(self.width())
        self.configuration["preview"]["height"] = int(self.height())

    def moveEvent(self, event):
        # Save updated position in configuration.
        position = self.geometry()
        self.configuration["preview"]["x"] = int(position.x())
        self.configuration["preview"]["y"] = int(position.y())
        
    def setConfiguration(self, configuration):
        # Set the configuration.
        self.configuration = configuration["devices"][self.name]

    def closeEvent(self, event):
        self.previewWindowClosed.emit(self)