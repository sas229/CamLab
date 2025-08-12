from PySide6.QtWidgets import QDial
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt
import math

class CustomDial(QDial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background: transparent;")
        # Set notches and ranges
        self.setNotchesVisible(True)
        self.setPageStep(10)
        # Enable mouse tracking for smooth movement
        self.setTracking(True)

    def paintEvent(self, event):
        # First paint the base dial
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate center and radius
        center = self.rect().center()
        radius = min(self.width(), self.height()) / 2 - 10

        # Start at 206 degrees and rotate clockwise for 304 degrees
        start_angle = 206
        angle = start_angle + ((self.value() - self.minimum()) * 304.0 / (self.maximum() - self.minimum()))
        
        # Draw needle
        painter.save()
        painter.translate(center)
        painter.rotate(angle)
        
        # Create red pen for needle
        pen = QPen(QColor("#FF0000"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw the needle line
        painter.drawLine(0, 0, 0, -radius)
        
        # Draw the needle base circle
        painter.setBrush(QColor("#FF0000"))
        painter.drawEllipse(-4, -4, 8, 8)
        
        painter.restore()