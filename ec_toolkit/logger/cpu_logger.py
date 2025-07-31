# logger/cpu_logger.py

from .base_logger import BaseLogger
from ..utils.cpu import read_cpu_times_total, compute_cpu_usage_percent_total

class CPULogger(BaseLogger):
    def collect(self):
        current = read_cpu_times_total()
        return current

    def compute_metrics(self):
        if len(self.data) >= 2:
            previous = self.data[-2][1]
            current = self.data[-1][1]
            diff = compute_cpu_usage_percent_total(previous, current)
            self.summary.append((self.data[-1][0], diff))