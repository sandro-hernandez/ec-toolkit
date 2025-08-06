# EC Toolkit

**EC Toolkit** is a modular Python library for logging and analyzing energy consumption (EC) metrics during software and system experiments. It provides flexible logger components to track CPU usage, frequency, per-core stats, and RAPL-based energy consumption measurements.

---

## Features

- Modular logger architecture for CPU, per-core CPU, frequency, RAPL, and execution time
- Interval and edge-based logging modes
- CSV output for easy analysis
- Utility functions for reading system metrics

---

## 📁 Project Structure

```
ec_toolkit/
├── logger/           # Logging components for different metrics
│   ├── base_logger.py
│   ├── cpu_logger.py
│   ├── cpu_per_core_logger.py
│   ├── execution_time_logger.py
│   ├── freq_logger.py
│   ├── rapl_logger.py
│   └── manager.py
├── utils/            # Utility functions for reading system metrics
│   ├── cpu.py
│   ├── freq.py
│   └── rapl.py
setup.py              # Installation script
requirements.txt      # Dependencies
README.md             # Project documentation
```

---

## 🚀 Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/sandro-hernandez/ec-toolkit.git
cd ec-toolkit
python -m venv venv
source venv/bin/activate
pip install -e .
```

---
## Usage

Example usage to log CPU and energy metrics:

```python
from ec_toolkit.logger.manager import LoggerManager

logging_cfg = {
 "logging": {
    "interval": 0.1,
    "loggers": {
      "execution_time": [
        {
          "enabled": true,
          "mode": "edge"
        }
      ],
      "rapl": [
        {
          "enabled": true,
          "mode": "edge"
        },
        {
          "enabled": true,
          "mode": "interval"
        }
      ],
      "cpu_total": [
        {
          "enabled": true,
          "mode": "edge"
        },
        {
          "enabled": true,
          "mode": "interval"
        }
      ],
      "cpu_per_core": [
        {
          "enabled": true,
          "mode": "edge"
        },
        {
          "enabled": true,
          "mode": "interval"
        }
      ],
      "freq_per_core": [
        {
          "enabled": true,
          "mode": "interval"
        }
      ]
    }
  }
}
rep_dir = Path("./logs")
manager = LoggerManager.from_config(logging_cfg, rep_dir)
manager.start_all()
# ... run your workload ...
manager.stop_all()
```

## Loggers

- `CPULogger`: Logs system-wide CPU usage
- `PerCoreCPULogger`: Logs per-core CPU usage
- `PerCoreFreqLogger`: Logs per-core CPU frequency
- `RAPLLogger`: Logs energy consumption via RAPL
- `ExecutionTimeLogger`: Logs execution time

## License

MIT License


