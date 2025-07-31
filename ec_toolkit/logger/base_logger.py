from abc import ABC, abstractmethod
import time
import csv
from threading import Thread

class BaseLogger(ABC):
    def __init__(self, output_path, interval=1, mode='interval'):
        self.output_path = output_path
        self.interval = interval
        self.mode = mode
        self.running = False
        self.data = []
        self.summary = []

    @abstractmethod
    def collect(self):
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
