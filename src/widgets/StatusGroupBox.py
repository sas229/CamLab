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

        # Acquire initial time and calculate a nullref.
        self.setInitialTimeDate()
        self.nullRef = datetime(self.initialTime.year, self.initialTime.month, self.initialTime.day, 0, 0, 0)

        # Set layout.
        self.layout = QGridLayout()
        self.layout.setColumnStretch(0, 5)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 4)

        # Create UI objects.
        self.dateLabel = QLabel()
        self.dateLabel.setText("Date:")
        self.timeLabel = QLabel()
        self.timeLabel.setText("Current time:")
        self.elapsedLabel = QLabel()
        self.elapsedLabel.setText("Elapsed time:")
        self.date = QLabel()
        self.date.setFont(QFont("Arial", 25))
        self.date.setText(self.initialDate.toString(Qt.ISODate))
        self.clock = QLabel()
        self.clock.setFont(QFont("Arial", 25))
        self.outputLabel = QLabel()
        self.outputLabel.setText("Output:")
        self.output = QLabel()
        self.output.setFont(QFont("Arial", 15))
        
        self.elapsed = QLabel()
        self.elapsed.setFont(QFont("Arial", 25))
        
        self.rateLabel = QLabel()
        self.rateLabel.setText("Rate (Hz):")
        self.rate = QLabel()
        self.rate.setFont(QFont("Arial", 25))
        self.rate.setText("-")

        # Assemble layout.
        self.layout.addWidget(self.dateLabel, 0, 0)
        self.layout.addWidget(self.timeLabel, 0, 1)
        self.layout.addWidget(self.elapsedLabel, 0, 2)
        self.layout.addWidget(self.date, 1, 0)
        self.layout.addWidget(self.clock, 1, 1)
        self.layout.addWidget(self.outputLabel, 2, 0, 1, 3)
        self.layout.addWidget(self.output, 3, 0, 1, 3)
        self.layout.addWidget(self.elapsed, 1, 2)
        self.layout.addWidget(self.rateLabel, 0, 3)
        self.layout.addWidget(self.rate, 1, 3)
        self.setLayout(self.layout)

        # Output text.
        self.output.setText(
            "{path}/{date}_{hours:02}:{minutes:02}:{seconds:02}.txt".format(path="/home/data", date=self.initialDate.toString(Qt.ISODate), hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )
    
    def update(self, actualRate):
        # Store actual rate.
        self.actualRate = actualRate

        # Acquire time now and calculate time elapsed.
        self.currentTime = datetime.now()
        self.elapsedTime =  self.nullRef + (self.currentTime - self.initialTime)
        
        # Update clock text.
        self.clock.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )

        # Update elapsed time text.
        self.elapsed.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.elapsedTime.hour, minutes=self.elapsedTime.minute, seconds=self.elapsedTime.second)
        )

        # Update rate text.
        self.rate.setText("{actualRate:.2f}".format(actualRate=self.actualRate))

    @Slot()
    def reset(self):
        # Reset initial time and date.
        self.setInitialTimeDate()

        # Reset output text.
        self.output.setText(
            "{path}/{date}_{hours:02}:{minutes:02}:{seconds:02}.txt".format(path="/home/data", date=self.initialDate.toString(Qt.ISODate), hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )

        # Reset clock text.
        self.clock.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.initialTime.hour, minutes=self.initialTime.minute, seconds=self.initialTime.second)
        )

        # Reset elapsed time text.
        self.elapsed.setText(
            "{hours:02}:{minutes:02}:{seconds:02}".format(hours=self.elapsedTime.hour, minutes=self.elapsedTime.minute, seconds=self.elapsedTime.second)
        )

        # Reset rate text.
        self.rate.setText("-")

    @Slot()
    def setInitialTimeDate(self):
        # Method to set initial time and date.
        self.initialTime = datetime.now()
        self.initialDate = QDate.currentDate()
        
        
