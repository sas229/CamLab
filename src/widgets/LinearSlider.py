from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, QRectF, Property, QPoint, Signal
from PySide6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QPolygon

class LinearSlider(QWidget):
    leftLimitChanged = Signal(float)
    rightLimitChanged = Signal(float)
    setPointChanged = Signal(float)
    
    def __init__(self, minimumRange = 0, maximumRange = 100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(450, 100)
        self.minimumRange = minimumRange
        self.maximumRange = maximumRange
        self.span = self.maximumRange - self.minimumRange
        self.offset = self.minimumRange
        self.leftLimit = self.minimumRange
        self.rightLimit = self.maximumRange
        self.setPoint = 0.5*self.span
        self.processVariable = 0.0

        self.positionsUpdated = False
        self.pressedControl = 0
        self.precision = 2

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self.background = QColor("white")
        self.colourSetPoint = QColor("black")
        self.colourProcessVariable = QColor("black")
        self.groove = QColor("black")
        self.limitText = QColor("black")
        self.rangeText = QColor("black")
        self.text = QColor("black")
        
        self.limitRadius = 10
        self.limitWidth = 20
        self.limitHeight = 20
        self.padding = 30
        self.grooveHeight = 4
    
    def setMinRange(self, value):
        self.minimumRange = min(value, self.processVariable)
        self.leftLimit = max(self.leftLimit, self.minimumRange)
        self.span = self.maximumRange - self.minimumRange
        self.offset = self.minimumRange
        self.update()

    def getMinRange(self):
        return self.minimumRange

    def setMaxRange(self, value):
        self.maximumRange = max(value, self.processVariable)
        self.rightLimit = min(self.rightLimit, self.maximumRange)
        self.span = self.maximumRange - self.minimumRange
        self.offset = self.minimumRange
        self.update()

    def getMaxRange(self):
        return self.minimumRange
    
    def setLeftLimit(self, value):
        self.leftLimit = min(max(value, self.minimumRange), self.setPoint)
        self.update()

    def getLeftLimit(self):
        return self.leftLimit
    
    def setRightLimit(self, value):
        self.rightLimit = max(min(value, self.maximumRange), self.setPoint)
        self.update()

    def getRightLimit(self):
        return self.rightLimit

    def setSetPoint(self, value):
        self.setPoint = min(max(value, self.leftLimit), self.rightLimit)
        self.update()

    def getSetPoint(self):
        return self.setPoint

    def setProcessVariable(self, value):
        self.processVariable = value
        self.update()

    def getProcessVariable(self):
        return self.processVariable

    def setLimitRadius(self, value):
        self.limitRadius = value

    def getLimitRadius(self):
        return self.limitRadius

    def setLimitWidth(self, value):
        self.limitWidth = value

    def getLimitWidth(self):
        return self.limitWidth
    
    def setLimitHeight(self, value):
        self.limitHeight = value

    def getLimitHeight(self):
        return self.limitHeight

    def setGrooveHeight(self, value):
        self.grooveHeight = value

    def getGrooveHeight(self):
        return self.grooveHeight
    
    def setPadding(self, value):
        self.padding = value

    def getPadding(self):
        return self.padding
    
    def setBackgroundColour(self, colour):
        self.background = colour
    
    def getBackgroundColour(self):
        return self.background

    def setTextColour(self, colour):
        self.text = colour
    
    def getTextColour(self):
        return self.text

    def setLimitColour(self, colour):
        self.limitText = colour
    
    def getLimitColour(self):
        return self.limitText
    
    def setRangeColour(self, colour):
        self.rangeText = colour
    
    def getRangeColour(self):
        return self.rangeText

    def setProcessVariableColour(self, colour):
        self.colourProcessVariable = colour
    
    def getProcessVariableColour(self):
        return self.processVariable

    def setSetPointColour(self, colour):
        self.colourSetPoint = colour
    
    def getSetPointColour(self):
        return self.colourSetPoint

    def setGrooveColour(self, colour):
        self.groove = colour
    
    def getGrooveColour(self):
        return self.groove

    def paintEvent(self, event):
        self.span = self.maximumRange - self.minimumRange
        self.offset = self.minimumRange
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the size of the canvas .
        self.d_height = painter.device().height() - (self.padding * 2)
        self.d_width = painter.device().width() - (self.padding * 2)

        # Groove.
        brush = QBrush()
        brush.setColor(self.background)
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(self.groove)
        x = self.rangeValueToPixel(self.leftLimit)
        rect = QRect(self.padding + 1.5*self.limitWidth, self.d_height/2 - self.grooveHeight/2 + self.padding, self.d_width - (2*self.limitWidth) - self.padding, self.grooveHeight)
        painter.fillRect(rect, brush)

        # Left limit.
        self.xLeft = self.rangeValueToPixel(self.leftLimit) - self.limitWidth/2
        self.yLeft = self.d_height/2 - self.limitHeight/2 + self.padding
        painter.setPen(QPen(QBrush(self.limitText), 2))
        painter.setBrush(QBrush(self.limitText))
        self.leftLimitRect = QRectF(self.xLeft, self.yLeft, self.limitWidth, self.limitHeight)
        painter.drawRoundedRect(self.leftLimitRect, self.limitRadius, self.limitRadius)

        # Right limit.
        self.xRight = self.rangeValueToPixel(self.rightLimit) - self.limitWidth/2
        self.yRight = self.d_height/2 - self.limitHeight/2 + self.padding
        painter.setPen(QPen(QBrush(self.limitText), 2))
        painter.setBrush(QBrush(self.limitText))
        self.rightLimitRect = QRectF(self.xRight, self.yRight, self.limitWidth, self.limitHeight)
        painter.drawRoundedRect(self.rightLimitRect, self.limitRadius, self.limitRadius)

        # Active range.
        brush.setColor(self.limitText)
        rect = QRect(self.xLeft + self.limitWidth/2, self.d_height/2 - self.grooveHeight/2 + self.padding, self.xRight-self.xLeft, self.grooveHeight)
        painter.fillRect(rect, brush)

        # Set point indicator.
        painter.setPen(self.colourSetPoint)
        painter.setBrush(QBrush(self.colourSetPoint, Qt.SolidPattern))
        self.setPointX = self.rangeValueToPixel(self.setPoint)
        points = [
            QPoint(self.setPointX - 10, self.d_height/2 - 20 - self.grooveHeight/2 + self.padding),
            QPoint(self.setPointX + 10, self.d_height/2 - 20 - self.grooveHeight/2 + self.padding),
            QPoint(self.setPointX, self.d_height/2 - self.grooveHeight/2 + self.padding)
            ]
        self.setPointPolygon = QPolygon(points)
        painter.drawPolygon(self.setPointPolygon)

        # Process variable indicator.
        painter.setPen(self.colourProcessVariable)
        painter.setBrush(QBrush(self.colourProcessVariable, Qt.SolidPattern))
        self.processVariableX = self.rangeValueToPixel(self.processVariable)
        points = [
            QPoint(self.processVariableX - 10, self.d_height/2 + 20 + self.grooveHeight/2 + self.padding),
            QPoint(self.processVariableX + 10, self.d_height/2 + 20 + self.grooveHeight/2 + self.padding),
            QPoint(self.processVariableX, self.d_height/2 + self.grooveHeight/2 + self.padding)
            ]
        self.processVariablePolygon = QPolygon(points)
        painter.drawPolygon(self.processVariablePolygon)

        # Left limit label.
        rect = QRect(self.xLeft + self.limitRadius - 30, self.d_height/2  + self.padding - 62, 60, 60)
        painter.setPen(self.limitText)
        painter.setFont(QFont('monoespace', 10))
        if self.precision == 0:
            painter.drawText(rect, Qt.AlignCenter, "{position:.0f}".format(position=self.leftLimit))
        elif self.precision == 1:
            painter.drawText(rect, Qt.AlignCenter, "{position:.1f}".format(position=self.leftLimit))
        elif self.precision == 2:
            painter.drawText(rect, Qt.AlignCenter, "{position:.2f}".format(position=self.leftLimit))
        elif self.precision == 3:
            painter.drawText(rect, Qt.AlignCenter, "{position:.3f}".format(position=self.leftLimit))

        # Right limit label.
        rect = QRect(self.xRight + self.limitRadius - 30, self.d_height/2 + self.padding - 62, 60, 60)
        painter.setPen(self.limitText)
        painter.setFont(QFont('monoespace', 10))
        if self.precision == 0:
            painter.drawText(rect, Qt.AlignCenter, "{position:.0f}".format(position=self.rightLimit))
        elif self.precision == 1:
            painter.drawText(rect, Qt.AlignCenter, "{position:.1f}".format(position=self.rightLimit))
        elif self.precision == 2:
            painter.drawText(rect, Qt.AlignCenter, "{position:.2f}".format(position=self.rightLimit))
        elif self.precision == 3:
            painter.drawText(rect, Qt.AlignCenter, "{position:.3f}".format(position=self.rightLimit))

        # Minimum range label.
        x = 0
        rect = QRect(x, self.d_height/2 + self.padding - 10, 60, 60)
        painter.setPen(self.rangeText)
        painter.setFont(QFont('monoespace', 10))
        if self.precision == 0:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.0f}".format(position=self.minimumRange))
        elif self.precision == 1:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.1f}".format(position=self.minimumRange))
        elif self.precision == 2:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.2f}".format(position=self.minimumRange))
        elif self.precision == 3:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.3f}".format(position=self.minimumRange))

        # Maximum range label.
        x = self.d_width + self.padding - 30
        rect = QRect(x, self.d_height/2 + self.padding - 10, 60, 60)
        painter.setPen(self.rangeText)
        painter.setFont(QFont('monoespace', 10))
        if self.precision == 0:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.0f}".format(position=self.maximumRange))
        elif self.precision == 1:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.1f}".format(position=self.maximumRange))
        elif self.precision == 2:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.2f}".format(position=self.maximumRange))
        elif self.precision == 3:
            painter.drawText(rect, Qt.AlignHCenter, "{position:.3f}".format(position=self.maximumRange))

        # Set point label.
        rect = QRect(self.setPointX - 30, self.d_height/2 + self.padding - 75, 60, 60)
        painter.setPen(self.text)
        painter.setFont(QFont('monoespace', 10))
        painter.drawText(rect, Qt.AlignCenter, "{position:.2f}".format(position=self.setPoint))

        # Process variable label.
        rect = QRect(self.processVariableX - 30, self.d_height/2 + self.padding + 15, 60, 60)
        painter.setPen(self.colourProcessVariable)
        painter.setFont(QFont('monoespace', 10))
        painter.drawText(rect, Qt.AlignCenter, "{position:.2f}".format(position=self.processVariable))

        painter.end()

    def mousePressEvent(self, event):
        # Left limit press.
        if self.leftLimitRect.contains(event.pos()):
            self.pressedControl = 1
            self.clickOffset = event.x()
            self.update()
            return
        
        # Right limit press.
        if self.rightLimitRect.contains(event.pos()):
            self.pressedControl = 2
            self.clickOffset = event.x()
            self.update()
            return

        # Set point press.
        if self.setPointPolygon.containsPoint(event.pos(), Qt.OddEvenFill):
            self.pressedControl = 3
            self.clickOffset = event.x()
            self.update()
            return

        self.pressedControl = 0

    def mouseMoveEvent(self, event):
        # Erroneous move.
        if self.pressedControl == 0:
            event.ignore()
            self.positionsUpdated = False
            return
        event.accept()
        disp = event.x() - self.clickOffset

        # Left limit move.
        if self.pressedControl == 1:
            newPosition = self.pixelToRangeValue(self.clickOffset + disp)
            self.leftLimit = max(self.minimumRange, newPosition)
            self.leftLimit = min(self.setPoint, self.leftLimit)
            self.leftLimit = round(self.leftLimit, self.precision)
            self.clickOffset = self.clickOffset + disp
        
        # Right limit move.
        if self.pressedControl == 2:
            newPosition = self.pixelToRangeValue(self.clickOffset + disp)
            self.rightLimit = min(self.maximumRange, newPosition)
            self.rightLimit = max(self.setPoint, self.rightLimit)
            self.rightLimit = round(self.rightLimit, self.precision)
            self.clickOffset = self.clickOffset + disp
        
        # Set point move.
        if self.pressedControl == 3:
            newPosition = self.pixelToRangeValue(self.clickOffset + disp)
            self.setPoint = max(self.leftLimit, newPosition)
            self.setPoint = min(self.rightLimit, self.setPoint)
            self.setPoint = round(self.setPoint, self.precision)
            self.clickOffset = self.clickOffset + disp

        self.positionsUpdated = True
        self.update()  

    def mouseReleaseEvent(self, event):
        # If the position of any handle has changed.
        if self.positionsUpdated == True:
            if self.pressedControl == 1: 
                # Emit the left limit changed signal.
                self.leftLimitChanged.emit(self.leftLimit)
            elif self.pressedControl == 2: 
                # Emit the right limit changed signal.
                self.rightLimitChanged.emit(self.rightLimit)
            elif self.pressedControl == 3: 
                # Emit the set point changed signal.
                self.setPointChanged.emit(self.setPoint)
            self.positionsUpdated = False
        self.pressedControl = 0
        self.update()

    def pixelToRangeValue(self, pixel): 
        pos = ((pixel - (2*self.padding))/(self.d_width - (2*self.limitWidth) - self.padding)*self.span) + self.offset
        return pos

    def rangeValueToPixel(self, pos):
        pixel = ((pos - self.offset)*(self.d_width - (2*self.limitWidth) - self.padding)/self.span) + (2*self.padding)
        return pixel

    # Properties to expose.
    backgroundColour = Property(QColor, getBackgroundColour, setBackgroundColour)
    setPointColour = Property(QColor, getSetPointColour, setSetPointColour)
    processVariableColour = Property(QColor, getProcessVariableColour, setProcessVariableColour)
    grooveColour = Property(QColor, getGrooveColour, setGrooveColour)
    textColour = Property(QColor, getTextColour, setTextColour)
    limitColour = Property(QColor, getLimitColour, setLimitColour)
    rangeColour = Property(QColor, getRangeColour, setRangeColour)