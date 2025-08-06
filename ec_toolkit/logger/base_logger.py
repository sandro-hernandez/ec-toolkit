"""
base_logger.py

This module defines an abstract base class `BaseLogger` for collecting
time-series data at fixed intervals or on demand. Subclasses should
implement the `collect()` method to gather specific metrics.

Supports two modes:
- 'interval': collect data periodically.
- 'edge': collect data only at start/stop.

Output is saved as a CSV file containing timestamped metric values.
"""

from abc import ABC, abstractmethod
import time
import csv
from threading import Thread

class BaseLogger(ABC):
    """
    Abstract base logger class.

    Args:
        output_path (str): Path to save the output CSV file.
        interval (int): Time interval (in seconds) between samples in 'interval' mode.
        mode (str): Logging mode - either 'interval' or 'edge'.

    Attributes:
        data (list): Raw data collected as (timestamp, value) tuples.
        summary (list): Post-processed metrics, e.g., deltas between values.
    """

    def __init__(self, output_path, interval=1, mode='interval'):
        self.output_path = output_path
        self.interval = interval
        self.mode = mode
        self.running = False
        self.data = []
        self.summary = []

    @abstractmethod
    def collect(self):
        """
        Collect a single metric sample.
        Must be implemented by subclasses.

        Returns:
            Any: A numeric or structured metric value.
        """
        pass

    def start(self):
        if self.mode == 'interval':
            self.running = True
            def loop():
                while self.running:
                    self.data.append((time.time(), self.collect()))
                    self.compute_metrics()  # Compute metrics after collecting
                    time.sleep(self.interval)
            self.thread = Thread(target=loop)
            self.thread.start()
        elif self.mode == 'edge':
            self.data.append((time.time(), self.collect()))

    def stop(self):
        if self.mode == 'interval':
            self.running = False
            self.thread.join()
        elif self.mode == 'edge':
            self.data.append((time.time(), self.collect()))
            self.compute_metrics() 
        self.save() 

    def compute_metrics(self):
        """Override in subclass if needed."""
        if len(self.data) >= 2:
            prev = self.data[-2][1]
            curr = self.data[-1][1]
            diff = curr - prev
            self.summary.append((self.data[-1][0], diff))  # (timestamp, diff)
            
    def save(self):
        with open(self.output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "metric"])
            for timestamp, metric in self.summary:
                writer.writerow([timestamp, metric])
