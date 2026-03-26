# utils/freq.py
"""
Helper functions for setting CPU frequency / governor.

All stdout / stderr from privileged commands is suppressed so benchmark
output stays tidy. Requires sudo privileges for setter calls.
"""
import glob
import os
from subprocess import DEVNULL, run


_POLICY_GLOB = "/sys/devices/system/cpu/cpufreq/policy*"
_CPUFREQ_CUR_GLOB = "/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq"


def _sudo_cpupower(*args: str) -> None:
    """Run `cpupower` with sudo and silence its output."""
    run(
        ["sudo", "cpupower", *args],
        check=True,
        stdout=DEVNULL,
        stderr=DEVNULL,
    )


def _sudo_write_sysfs(path: str, value: int | str) -> None:
    """Write a value to a sysfs file with sudo."""
    run(
        ["sudo", "tee", path],
        input=f"{value}\n",
        text=True,
        check=True,
        stdout=DEVNULL,
        stderr=DEVNULL,
    )


def _read_sysfs(path: str) -> str | None:
    """Read a sysfs file, returning None when it does not exist."""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def _policy_dirs() -> list[str]:
    """Return CPU frequency policy directories."""
    return sorted(
        path for path in glob.glob(_POLICY_GLOB) if os.path.basename(path).startswith("policy")
    )


def _supports_userspace(policy_dir: str) -> bool:
    """Check whether a policy can be pinned via userspace governor."""
    governors = _read_sysfs(f"{policy_dir}/scaling_available_governors") or ""
    return "userspace" in governors.split() and os.path.exists(f"{policy_dir}/scaling_setspeed")


def set_governor(governor: str) -> None:
    """Set governor only (`schedutil`, `performance`, `powersave`, ...)."""
    _sudo_cpupower("frequency-set", "-g", governor)


def set_fixed_freq(khz: int) -> None:
    """
    Pin all policies to a fixed frequency in kHz.

    Uses the userspace governor and `scaling_setspeed` when available on every
    policy for tighter pinning. Otherwise falls back to `cpupower` with the
    performance governor plus matching min/max bounds.
    """
    freq = str(int(khz))
    policies = _policy_dirs()

    if policies and all(_supports_userspace(policy) for policy in policies):
        for policy in policies:
            _sudo_write_sysfs(f"{policy}/scaling_governor", "userspace")
            _sudo_write_sysfs(f"{policy}/scaling_min_freq", freq)
            _sudo_write_sysfs(f"{policy}/scaling_max_freq", freq)
            _sudo_write_sysfs(f"{policy}/scaling_setspeed", freq)
        return

    _sudo_cpupower("frequency-set", "-g", "performance")
    _sudo_cpupower("frequency-set", "-d", freq)
    _sudo_cpupower("frequency-set", "-u", freq)


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
    for path in sorted(glob.glob(_CPUFREQ_CUR_GLOB)):
        try:
            with open(path, encoding="utf-8") as file:
                freqs.append(int(file.read().strip()))
        except FileNotFoundError:
            freqs.append(None)
    return freqs  # list of frequencies in kHz
