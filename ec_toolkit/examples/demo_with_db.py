# ec_toolkit/examples/demo_with_db.py

from pathlib import Path
from ec_toolkit.logger.manager import LoggerManager

logging_cfg = {
    "interval": 1.0,
    "loggers": {
        "rapl": [{"enabled": True, "mode": "interval"}],
        "cpu_total": [{"enabled": True, "mode": "interval"}],
        "execution_time": [{"enabled": True, "mode": "edge"}]
    }
}

if __name__ == "__main__":
    rep_dir = Path("./ec_toolkit/examples/demo_logs")

    manager = LoggerManager.from_config(
        logging_cfg,
        rep_dir,
        use_db=True,                 # <--- DB mode
        db_path=rep_dir / "demo.sqlite" # type: ignore
    )

    manager.start_all()

    # Dummy workload
    for _ in range(50_000_000):
        pass

    manager.stop_all()

    print("SQLite DB created at:", rep_dir / "demo.sqlite")
