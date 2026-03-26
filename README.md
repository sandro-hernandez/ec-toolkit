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
from pathlib import Path

from ec_toolkit.logger.manager import LoggerManager

logging_cfg = {
    "interval": 0.1,
    "loggers": {
      "execution_time": [
        {
          "enabled": True,
          "mode": "edge"
        }
      ],
      "rapl": [
        {
          "enabled": True,
          "mode": "edge"
        },
        {
          "enabled": True,
          "mode": "interval"
        }
      ],
      "cpu_total": [
        {
          "enabled": True,
          "mode": "edge"
        },
        {
          "enabled": True,
          "mode": "interval"
        }
      ],
      "cpu_per_core": [
        {
          "enabled": True,
          "mode": "edge"
        },
        {
          "enabled": True,
          "mode": "interval"
        }
      ],
      "freq_per_core": [
        {
          "enabled": True,
          "mode": "interval"
        }
      ]
    }
}
rep_dir = Path("./logs")
manager = LoggerManager.from_config(logging_cfg, rep_dir)
manager.start_all()
# ... run your workload ...
manager.stop_all()
```

## Smoke Test Demo

If you want a quick end-to-end check that the toolkit is collecting data correctly, run the demo script in `examples/smoke_test_demo.py`.

It starts a representative set of loggers, runs a small CPU-bound synthetic workload, and writes the resulting CSV files to a timestamped directory.

```bash
source venv/bin/activate
python3 examples/smoke_test_demo.py --duration 5 --interval 0.5
```

Optional arguments:

- `--output-dir demo_logs` to choose where the CSV files are saved
- `--upper-bound 20000` to make the synthetic workload heavier
- `--duration 10` to collect a longer run
- `--fixed-freq-khz 2500000` to pin the CPU to a target frequency before the workload
- `--restore-default-after` to switch back to the default governor after a fixed-frequency run

What the demo does:

- enables `execution_time`, `cpu_total`, and `cpu_per_core`
- enables `freq_per_core` only if CPU frequency sysfs entries are available
- enables `rapl` only if Intel RAPL energy counters are available on the machine
- runs a pure-Python prime-counting loop for the requested duration

Expected result:

- a new directory such as `demo_logs/smoke-test-20260326-120000`
- one CSV file per enabled logger
- non-empty CSV files with timestamped metric values

This is meant as a smoke test, not a benchmark. Different servers may expose different metrics, so it is normal for one machine to generate `rapl_interval.csv` while another does not.

If you also want to exercise the frequency-setting path, run the demo in fixed-frequency mode:

```bash
source venv/bin/activate
python3 examples/smoke_test_demo.py --duration 5 --interval 0.5 --fixed-freq-khz 2500000 --restore-default-after
```

This uses `set_fixed_freq()` before the workload starts. It may require `sudo` depending on your environment.

## Loggers

- `CPULogger`: Logs system-wide CPU usage
- `PerCoreCPULogger`: Logs per-core CPU usage
- `PerCoreFreqLogger`: Logs per-core CPU frequency
- `RAPLLogger`: Logs energy consumption via RAPL
- `ExecutionTimeLogger`: Logs execution time

## License

MIT License
