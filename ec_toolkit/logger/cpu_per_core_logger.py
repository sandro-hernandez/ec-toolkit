# logger/cpu_per_core_logger.py
from .base_logger import BaseLogger
from ..utils.cpu import read_cpu_times_per_core, compute_cpu_usage_percent_per_core

class PerCoreCPULogger(BaseLogger):
    def collect(self):
        current = read_cpu_times_per_core()
        return current
    
    def compute_metrics(self):
        if len(self.data) >= 2:
            previous = self.data[-2][1]
            current = self.data[-1][1]
            diff = compute_cpu_usage_percent_per_core(previous, current)
            self.summary.append((self.data[-1][0], diff))  # (timestamp, diff)
