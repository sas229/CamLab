from PySide6.QtCore import QObject, Signal
from labjack import ljm
from time import time
import logging

log = logging.getLogger(__name__)

class Timing(QObject):
    controlDevices = Signal()
    actualRate = Signal(float)

    def __init__(self):
        super().__init__()

    def start(self, rate):
        log.info("Starting device timer.")
        self.running = True
        self.cycles = 0
        self.rate = rate
        interval = int(1000000*(1/self.rate))
        err = ljm.startInterval(1, interval)
        startTime = time()
        while self.running:
            self.cycles += 1
            self.controlDevices.emit()
            if self.cycles%rate == 0:
                endTime = time()
                elapsed = endTime - startTime
                actualRate = self.rate/elapsed
                self.actualRate.emit(actualRate)
                startTime = time()
            skippedIntervals = ljm.waitForNextInterval(1)

    def stop(self):
        self.running = False
        log.info("Stopped device timer.")



