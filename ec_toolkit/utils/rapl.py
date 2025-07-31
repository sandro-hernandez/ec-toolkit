# utils/rapl.py
RAPL_FILE = "/sys/class/powercap/intel-rapl:0/energy_uj"

def read_energy_uj():
    with open(RAPL_FILE, "r") as fh:
        return int(fh.read().strip())
