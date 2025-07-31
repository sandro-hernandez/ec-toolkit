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
