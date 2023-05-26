from PySide6.QtCore import QObject, Signal
import time
import numpy as np
import pandas as pd

class Simulation(QObject):
    emitData = Signal(np.ndarray)

    def __init__(self, data):
        super().__init__()
        self.index = 0
        self.data = data

        try:
            self.data["Timedelta"] = pd.to_timedelta(self.data["Time"], unit="S")-pd.to_timedelta(self.data["Time"][0], unit="S")
        except:
            self.data["Timedelta"] = pd.to_timedelta(self.data["Time"])-pd.to_timedelta(self.data["Time"][0])
        self.data["Time"] = self.data["Timedelta"].dt.total_seconds()

    def start(self, initial_index=0):
        self.stopped = False
        start_time = time.time_ns() - self.data["Timedelta"].iloc[initial_index].total_seconds()*(10**9)

        for index in range(initial_index, self.data.shape[0]):
        # for index in range(10):
            self.index = index
            self.emitData.emit(self.data.values[: index+1, :5])
            self.elapsed_time = time.time_ns() - start_time
            if index != self.data.shape[0]-1:
                time.sleep(max(0, (self.data["Timedelta"].iloc[index+1]-pd.Timedelta(nanoseconds=time.time_ns()-start_time)).total_seconds()))
            else:
                self.index = 0
            if self.stopped:
                break
