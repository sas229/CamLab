from PySide6.QtWidgets import QGroupBox, QLabel, QGridLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QDate, Slot
import logging
from datetime import datetime

log = logging.getLogger(__name__)

class StatusGroupBox(QGroupBox):

    def __init__(self):
        super().__init__() 
        self.setTitle("Status")
        self.setVisible(False)
        self.count = 0

        # Set layout.
        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 5)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        # Acquire time and date.
        self.initialTime = datetime.now()
        self.currentTime = datetime.now()
        date = QDate.currentDate()
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)

        # Create UI objects.
        self.dateLabel = QLabel()
        self.dateLabel.setText("Date:")
        self.timeLabel = QLabel()
        self.timeLabel.setText("Current time:")
        self.elapsedLabel = QLabel()
        self.elapsedLabel.setText("Elapsed time:")
        self.date = QLabel()
        self.date.setFont(QFont("Arial", 25))
        self.date.setText(date.toString(Qt.ISODate))
        self.clock = QLabel()
        self.clock.setFont(QFont("Arial", 25))
        self.clock.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )
        self.outputLabel = QLabel()
        self.outputLabel.setText("Output:")
        self.output = QLabel()
        self.output.setFont(QFont("Arial", 15))
        self.output.setText(
            "{path}/{date}_{hours:02}:{minutes:02}:{seconds:02}.txt".format(path="/home/data", date=date.toString(Qt.ISODate), hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )
        self.elapsed = QLabel()
        self.elapsed.setFont(QFont("Arial", 25))
        self.elapsed.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second)
        )
        self.samplesLabel = QLabel()
        self.samplesLabel.setText("Samples:")
        self.samples = QLabel()
        self.samples.setFont(QFont("Arial", 25))
        self.samples.setText(str(self.count))

        # Assemble layout.
        self.layout.addWidget(self.dateLabel, 0, 0)
        self.layout.addWidget(self.timeLabel, 0, 1)
        self.layout.addWidget(self.elapsedLabel, 0, 2)
        self.layout.addWidget(self.date, 1, 0)
        self.layout.addWidget(self.clock, 1, 1)
        self.layout.addWidget(self.outputLabel, 2, 0, 1, 3)
        self.layout.addWidget(self.output, 3, 0, 1, 3)
        self.layout.addWidget(self.elapsed, 1, 2)
        self.layout.addWidget(self.samplesLabel, 0, 3)
        self.layout.addWidget(self.samples, 1, 3)
        self.setLayout(self.layout)

    @Slot()
    def setInitialTime(self):
        # Method to set initial time.
        self.initialTime = datetime.now()

    @Slot()
    def updateTimes(self):
        # Method to update times being displayed.
        self.currentTime = datetime.now()
        nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)
        elapsed =  nullRef + (self.currentTime - self.initialTime)
        self.clock.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )
        self.elapsed.setText("{hours:02}:{minutes:02}:{seconds:02}".format(hours=elapsed.hour, minutes=elapsed.minute, seconds=elapsed.second))

    @Slot(int)
    def updateSamplesCount(self, count):
        # Method to update the number of samples. If less than 1e4 samples present as an integer, otherwise present in scientific notation.
        self.count = count
        if self.count < 1e4:
            self.samples.setText("{count}".format(count=self.count))
        else:
            self.samples.setText("{count:.3E}".format(count=self.count))
