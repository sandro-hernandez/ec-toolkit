from .base_logger import BaseLogger
from ..utils.rapl import read_energy_uj

class RAPLLogger(BaseLogger):
    def collect(self):
        return read_energy_uj() 