# utils/freq.py
"""
Helper functions for setting CPU frequency / governor.

All stdout / stderr from `cpupower` is suppressed so benchmark
output stays tidy.  Requires sudo privileges for each call.
"""
from subprocess import run, DEVNULL, CalledProcessError
import glob

def _sudo_cpupower(*args: str) -> None:
    """Run `cpupower` with sudo and silence its output."""
    run(["sudo", "cpupower", *args],
        check=True, stdout=DEVNULL, stderr=DEVNULL)

def set_governor(governor: str) -> None:
    """Set governor only (`schedutil`, `performance`, `powersave`, …)."""
    _sudo_cpupower("frequency-set", "-g", governor)

def set_fixed_freq(khz: int) -> None:
    """
    Pin all cores to a fixed frequency (kHz) via userspace governor.
    Example: 1700000 → 1.7 GHz
    """
    ghz = f"{khz/1e6:.1f}GHz"
    _sudo_cpupower("frequency-set", "-g", "userspace")
    _sudo_cpupower("frequency-set", "-f", ghz)

def set_freq_or_default(khz_or_gov: int | str) -> None:
    """
    Set CPU frequency or governor.
    - If 'default', sets 'schedutil'.
    - If a known governor name, sets that governor.
    - If an int, sets fixed frequency.
    """
    governors = {"conservative", "ondemand", "userspace", "powersave", "performance", "schedutil"}
    if khz_or_gov == "default":
        set_governor("schedutil")
    elif isinstance(khz_or_gov, str) and khz_or_gov in governors:
        set_governor(khz_or_gov)
    else:
        set_fixed_freq(int(khz_or_gov))

def restore_default() -> None:
    """Convenience wrapper to go back to schedutil governor."""
    set_governor("schedutil")

def read_cpu_freq_per_core():
    """
    Read current CPU frequency for each core.
    Returns a list of dicts with 'core' and 'frequency' in kHz.
    """
    freqs = []
    for path in sorted(glob.glob("/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq")):
        try:
            with open(path) as f:
                freqs.append(int(f.read().strip()))
        except FileNotFoundError:
            freqs.append(None)
    return freqs  # list of frequencies in kHz