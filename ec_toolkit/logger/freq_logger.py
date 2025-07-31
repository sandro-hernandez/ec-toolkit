# logger/freq_logger.py

from .base_logger import BaseLogger
from ..utils.freq import read_cpu_freq_per_core

class PerCoreFreqLogger(BaseLogger):
    def collect(self):
        return read_cpu_freq_per_core()
    
    def compute_metrics(self):
        self.summary.append((self.data[-1][0], self.data[-1][1]))