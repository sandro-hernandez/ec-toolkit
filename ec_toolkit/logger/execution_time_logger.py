# logger/execution_time_logger.py

from .base_logger import BaseLogger
import time

class ExecutionTimeLogger(BaseLogger):

    def start(self):
        self.mode = 'edge'
        super().start() # Start in edge mode

    def collect(self):
        return time.time()