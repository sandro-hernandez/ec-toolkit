# utils/cpu.py
import psutil

def read_cpu_times_per_core():
    times = psutil.cpu_times(percpu=True)
    result = []
    for i, t in enumerate(times):
        result.append({
            "core": i,  # ← Add this!
            "user": t.user,
            "system": t.system,
            "idle": t.idle,
            "nice": getattr(t, "nice", 0.0),
            "iowait": getattr(t, "iowait", 0.0),
            "irq": getattr(t, "irq", 0.0),
            "softirq": getattr(t, "softirq", 0.0),
            "steal": getattr(t, "steal", 0.0),
        })
    return result

def compute_cpu_usage_percent_per_core(start, end):
    """
    Computes per-core usage percentages between two snapshots.
    Both `start` and `end` must be lists returned by `read_cpu_times_per_core`.
    """
    result = []
    for core_index, (s, e) in enumerate(zip(start, end)):
        delta = {k: e[k] - s[k] for k in s}
        total = sum(delta.values())
        if total == 0:
            usage = {k: 0.0 for k in delta}
        else:
            usage = {k: 100 * v / total for k, v in delta.items()}
        usage["core"] = core_index
        result.append(usage)
    return result



def read_cpu_times_total():
    """Returns a dict of system-wide CPU times (in seconds) for each mode."""
    t = psutil.cpu_times()
    return {
        "user": t.user,
        "system": t.system,
        "idle": t.idle,
        "nice": getattr(t, "nice", 0.0),
        "iowait": getattr(t, "iowait", 0.0),
        "irq": getattr(t, "irq", 0.0),
        "softirq": getattr(t, "softirq", 0.0),
        "steal": getattr(t, "steal", 0.0),
    }

def compute_cpu_usage_percent_total(start, end):
    """Returns system-wide CPU usage breakdown in percentage over the interval."""
    delta = {k: end[k] - start[k] for k in start}
    total = sum(delta.values())
    if total == 0:
        return {k: 0.0 for k in delta}
    return {k: 100 * v / total for k, v in delta.items()}

