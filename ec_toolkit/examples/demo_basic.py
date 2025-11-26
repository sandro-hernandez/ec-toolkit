from pathlib import Path
from ec_toolkit.logger.manager import LoggerManager

logging_cfg = {
    "interval": 1.0,
    "loggers": {
        "execution_time": [
            {"enabled": True, "mode": "edge"}
        ],
        "rapl": [
            {"enabled": True, "mode": "interval"},
            {"enabled": True, "mode": "edge"}
        ],
        "cpu_total": [
            {"enabled": True, "mode": "interval"}
        ],
        "cpu_per_core": [
            {"enabled": False}
        ],
        "freq_per_core": [
            {"enabled": True, "mode": "interval"}
        ],
    }
}

rep_dir = Path("./ec_toolkit/examples/demo_logs")

if __name__ == "__main__":
    manager = LoggerManager.from_config(logging_cfg, rep_dir)
    manager.start_all()

    print("Running dummy workload...")
    for _ in range(5_000_000):
        pass  # dummy CPU loop

    manager.stop_all()
    print("Done! Logs written to:", rep_dir)
