from __future__ import annotations

import argparse
import glob
import math
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ec_toolkit.logger.manager import LoggerManager
from ec_toolkit.utils.freq import _policy_dirs, _read_sysfs, restore_default, set_fixed_freq, set_freq_or_default


RAPL_FILE = Path("/sys/class/powercap/intel-rapl:0/energy_uj")
CPUFREQ_GLOB = "/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq"


def _can_read(path: Path) -> bool:
    try:
        path.read_text(encoding="utf-8")
        return True
    except OSError:
        return False


def _available_logger_config(interval: float) -> tuple[dict, list[str]]:
    loggers = {
        "execution_time": [{"enabled": True, "mode": "edge"}],
        "cpu_total": [{"enabled": True, "mode": "interval", "interval": interval}],
        "cpu_per_core": [{"enabled": True, "mode": "interval", "interval": interval}],
    }
    enabled = ["execution_time", "cpu_total", "cpu_per_core"]

    # if _can_read(RAPL_FILE):
    if RAPL_FILE.exists():
        loggers["rapl"] = [{"enabled": True, "mode": "interval", "interval": interval}]
        enabled.append("rapl")
        # rapl logger edge mode
        loggers["rapl"].append({"enabled": True, "mode": "edge"})


    if any(glob.glob(CPUFREQ_GLOB)):
        loggers["freq_per_core"] = [{"enabled": True, "mode": "interval", "interval": interval}]
        enabled.append("freq_per_core")

    return {"interval": interval, "loggers": loggers}, enabled


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False

    limit = math.isqrt(value)
    for candidate in range(3, limit + 1, 2):
        if value % candidate == 0:
            return False
    return True


def run_synthetic_workload(duration_s: float, upper_bound: int) -> dict[str, int | float]:
    deadline = time.perf_counter() + duration_s
    iterations = 0
    primes_found = 0

    while time.perf_counter() < deadline:
        primes_found += sum(1 for value in range(2, upper_bound) if _is_prime(value))
        iterations += 1

    return {
        "iterations": iterations,
        "primes_found": primes_found,
        "upper_bound": upper_bound,
        "duration_s": duration_s,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a simple EC Toolkit smoke test and save CSV logs."
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=5.0,
        help="How long to run the synthetic workload in seconds.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Sampling interval for interval-based loggers in seconds.",
    )
    parser.add_argument(
        "--upper-bound",
        type=int,
        default=100_000,
        help="Upper bound used by the prime-counting workload.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("demo_logs"),
        help="Directory where CSV logs will be written.",
    )
    parser.add_argument(
        "--fixed-freq-khz",
        type=int,
        default=None,
        help="Optional fixed CPU frequency in kHz to apply before the workload starts.",
    )
    parser.add_argument(
        "--governor",
        type=str,
        default=None,
        help="Optional CPU governor to apply before the workload starts.",
    )
    parser.add_argument(
        "--restore-default-after",
        action="store_true",
        help="Restore the default governor after the demo when fixed frequency mode is used.",
    )
    args = parser.parse_args()

    timestamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    run_dir = args.output_dir / f"smoke-test-{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    config, enabled_loggers = _available_logger_config(args.interval)
    manager = LoggerManager.from_config(config, run_dir)

    print(f"[INFO] Writing demo logs to {run_dir}")
    print(f"[INFO] Enabled loggers: {', '.join(enabled_loggers)}")
    if args.fixed_freq_khz is not None:
        print(f"[INFO] Applying fixed CPU frequency: {args.fixed_freq_khz} kHz")
        set_freq_or_default(args.fixed_freq_khz)
    if args.governor is not None:
        print(f"[INFO] Applying CPU governor: {args.governor}")
        set_freq_or_default(args.governor)
    print(
        "[INFO] Running synthetic workload: "
        f"prime counting up to {args.upper_bound} for {args.duration:.1f}s"
    )
    print("[INFO] Current CPU governor is set to: ")
    for policy in _policy_dirs():
        governor = _read_sysfs(f"{policy}/scaling_governor")
        if governor:
            print(f"  - {policy}: {governor}")

    manager.start_all()
    workload_stats = None
    try:
        workload_stats = run_synthetic_workload(args.duration, args.upper_bound)
    finally:
        manager.stop_all()
        if (args.fixed_freq_khz is not None or args.governor is not None) and args.restore_default_after:
            print("[INFO] Restoring default CPU governor")
            restore_default()

    print(f"[INFO] Workload summary: {workload_stats}")
    print("[INFO] Generated files:")
    for csv_file in sorted(run_dir.glob("*.csv")):
        print(f"  - {csv_file.name}")


if __name__ == "__main__":
    main()
