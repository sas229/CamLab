import os
from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox, QTabWidget, QLabel, QLineEdit, QGridLayout, QFrame, QFileDialog, QComboBox, QSlider
from PySide6.QtGui import QIcon, QAction, QCursor, QDoubleValidator, QIntValidator, QFont
from PySide6.QtCore import Signal, Slot, Qt, QTime, QDate
import logging
from datetime import datetime

log = logging.getLogger(__name__)

class StatusGroupBox(QGroupBox):

    def __init__(self):
        super().__init__() 
        self.setTitle("Status")
        self.setVisible(False)

        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 5)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        self.initialTime = datetime.now()
        self.currentTime = datetime.now()
        date = QDate.currentDate()

        self.dateLabel = QLabel()
        self.dateLabel.setText("Date:")
        self.layout.addWidget(self.dateLabel, 0, 0)

        self.timeLabel = QLabel()
        self.timeLabel.setText("Current time:")
        self.layout.addWidget(self.timeLabel, 0, 1)

        self.elapsedLabel = QLabel()
        self.elapsedLabel.setText("Elapsed time:")
        self.layout.addWidget(self.elapsedLabel, 0, 2)

        self.date = QLabel()
        self.date.setFont(QFont("Arial", 25))
        self.date.setText(date.toString(Qt.ISODate))
        self.layout.addWidget(self.date, 1, 0)
        
        self.clock = QLabel()
        self.clock.setFont(QFont("Arial", 25))
        self.clock.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        self.layout.addWidget(self.clock, 1, 1)

        self.outputLabel = QLabel()
        self.outputLabel.setText("Output:")
        self.layout.addWidget(self.outputLabel, 2, 0, 1, 3)

        self.output = QLabel()
        self.output.setFont(QFont("Arial", 15))
        self.output.setText("{path}/{date}_{hours:02}:{minutes:02}:{seconds:02}.txt".format(path="/home/data", date=date.toString(Qt.ISODate), hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        self.layout.addWidget(self.output, 3, 0, 1, 3)
        
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)
        self.elapsed = QLabel()
        self.elapsed.setFont(QFont("Arial", 25))
        self.elapsed.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second))
        self.layout.addWidget(self.elapsed, 1, 2)
        self.setLayout(self.layout)

    def setInitialTime(self):
        self.initialTime = datetime.now()

    def updateTimes(self):
        self.currentTime = datetime.now()
        self.clock.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second))
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)
        self.elapsed.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second))