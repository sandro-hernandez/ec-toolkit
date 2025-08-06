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

class LoggerManager:
    def __init__(self, loggers):
        self.loggers = loggers

    def start_all(self):
        for logger in self.loggers:
            logger.start()

    def stop_all(self):
        for logger in self.loggers:
            logger.stop()

    @classmethod
    def from_config(cls, logging_cfg, rep_dir):
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

        Returns:
            LoggerManager: An initialized LoggerManager with configured loggers.
        """
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

                kwargs = {"mode": mode}
                if "interval" in logger_class.__init__.__code__.co_varnames:
                    kwargs["interval"] = cfg.get("interval", interval)

                loggers.append(logger_class(file_path, **kwargs))

        return cls(loggers)
