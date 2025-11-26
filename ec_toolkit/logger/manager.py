"""
manager.py

This module defines the `LoggerManager` class, which is responsible for
coordinating the start and stop of multiple metric loggers.

It also provides a `from_config` class method that instantiates a list
of loggers based on a configuration dictionary. This enables flexible
composition of logging workflows based on external YAML/JSON configs.

Supported logger types:
- Execution time logger
- RAPL-based energy logger
- Total CPU usage logger
- Per-core CPU usage logger
- Per-core frequency logger
"""

from .execution_time_logger import ExecutionTimeLogger
from .rapl_logger import RAPLLogger
from .cpu_logger import CPULogger
from .cpu_per_core_logger import PerCoreCPULogger
from .freq_logger import PerCoreFreqLogger

from ec_toolkit.db.writer import DBWriter
from pathlib import Path

class LoggerManager:
    def __init__(self, loggers, use_db: bool = False,
        db_writer: DBWriter | None = None, config: dict | None = None): 
        self.loggers = loggers
        self.use_db = use_db
        self.db_writer = db_writer
        self.config = config or {}
        self.run_id = None

    def start_all(self):
        # Start DB run if needed
        if self.use_db and self.db_writer is not None:
            self.run_id = self.db_writer.create_run(self.config)

        # Start all loggers    
        for logger in self.loggers:
            logger.start()

    def stop_all(self):
        # Stop all loggers
        for logger in self.loggers:
            logger.stop()
        
        # If using DB, insert collected data
        if self.use_db and self.db_writer is not None and self.run_id is not None:
            for logger in self.loggers:
                # Use an explicit name, falling back to class name if missing
                logger_name = getattr(logger, "logger_name", logger.__class__.__name__)

                # Raw samples from interval mode
                data = getattr(logger, "data", None)
                if data:
                    self.db_writer.insert_samples(self.run_id, logger_name, data)

                # Summary metrics (e.g., diffs, edge metrics)
                summary = getattr(logger, "summary", None)
                if summary:
                    self.db_writer.insert_summary_metrics(self.run_id, logger_name, summary)

            self.db_writer.finalize_run(self.run_id)
            # Optional: close connection here
            self.db_writer.close()
            self.run_id = None

    @classmethod
    def from_config(cls, logging_cfg, rep_dir, use_db: bool = False, db_path: str | None = None):
        """
        Factory method to create a LoggerManager instance from a configuration dictionary.

        Args:
            logging_cfg (dict): Dictionary containing logger configurations. Example:
                {
                    "interval": 1.0,
                    "loggers": {
                        "rapl": [{"enabled": True, "mode": "interval"}],
                        "cpu_total": [{"enabled": True}],
                        ...
                    }
                }

            rep_dir (Path): Path to the directory where CSV logs should be saved.
            use_db (bool): If True, log into SQLite instead of CSV (or in addition).
            db_path (str): Optional path to SQLite database file.

        Returns:
            LoggerManager: An initialized LoggerManager with configured loggers.
        """
        rep_dir = Path(rep_dir)
        rep_dir.mkdir(parents=True, exist_ok=True)

        interval = logging_cfg.get("interval", 1.0)
        config = logging_cfg.get("loggers", {})
        loggers = []

        logger_classes = {
            "execution_time": ExecutionTimeLogger,
            "rapl": RAPLLogger,
            "cpu_total": CPULogger,
            "cpu_per_core": PerCoreCPULogger,
            "freq_per_core": PerCoreFreqLogger
        }

        # Decide on DB writer if needed
        db_writer = None
        if use_db:
            db_path = db_path or (rep_dir / "ec_logs.sqlite") # type: ignore
            db_writer = DBWriter(db_path)

        for name, logger_configs in config.items():
            logger_class = logger_classes.get(name)
            if not logger_class:
                continue

            for i, cfg in enumerate(logger_configs):
                if not cfg.get("enabled", False):
                    continue

                mode = cfg.get("mode", "interval")
                suffix = f"_{mode}"
                file_path = rep_dir / f"{name}{suffix}.csv"

                # Build kwargs based on logger init signature
                init_params = logger_class.__init__.__code__.co_varnames
                kwargs = {"mode": mode}

                if "interval" in init_params:
                    kwargs["interval"] = cfg.get("interval", interval)
                
                if "save_to_csv" in init_params:
                    kwargs["save_to_csv"] = not use_db  # Disable CSV if using DB

                logger = logger_class(file_path, **kwargs)
                logger.logger_name = name
                loggers.append(logger)

        # We pass the whole logging_cfg as "config" to store in DB
        return cls(
            loggers=loggers,
            use_db=use_db,
            db_writer=db_writer,
            config=logging_cfg,
        )