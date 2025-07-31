# CI‑Energy‑Experiments

Measure **wall‑clock time**, **package energy** (via Intel RAPL) and **CPU utilisation** for synthetic workloads at different CPU frequencies/governors.  Results are stored as CSV for post‑analysis in the accompanying Jupyter notebook.

---

## 1  Folder Glossary

| Path                           | What lives here                                                                                |
| ------------------------------ | ---------------------------------------------------------------------------------------------- |
| `benchmarks/micro_benchmarks/` | Small, self‑contained stress scripts (`cpu_stress.py`, `mixed_stress.py`, …).                  |
| `utils/`                       | Reusable helpers – `rapl.py` (energy), `freq.py` (cpupower wrapper), `cpu.py` (tick parsing).  |
| `scripts/`                     | Entry points you *run*. `runner.py` executes all workloads & writes `results/energy_runs.csv`. |
| `configs/`                     | (optional) YAML files for future batch sweeps.                                                 |
| `results/`                     | Lightweight artefacts under 100 kB – CSVs and figures.                                         |
| `notebooks/`                   | Exploratory analysis notebook.                                                                 |

Large raw logs **never** enter Git history – they belong in `data/` (ignored).



---

## 2  Prerequisites

- Linux with Intel RAPL (tested on Ubuntu 24.04)
- `cpupower` (`sudo apt install linux-tools-common linux-tools-generic`)
- Python ≥ 3.11
- Ability to run `sudo cpupower …` (the script will prompt for your password)

---

## 3  Quick Start

```bash
# 1  Clone and enter the repo
$ git clone https://github.com/your‑fork/ci-energy-experiments.git
$ cd ci-energy-experiments

# 2  Create & activate an isolated environment
$ python3 -m venv venv
$ source venv/bin/activate

# 3  Install runtime deps (only psutil & numpy)
(venv) $ pip install --upgrade pip
(venv) $ pip install numpy psutil

# 4  Run all benchmarks (2 runs × 3 freqs × 2 workloads)
(venv) $ sudo -E venv/bin/python scripts/run_micro.py
# Adds `-E` so the venv Python is preserved while `cpupower` still runs with sudo.

# 5  Open results
(venv) $ python - <<'PY'
import pandas as pd; print(pd.read_csv('results/energy_runs.csv').head())
PY
```

### What the script does

1. Loops over `benchmarks/micro_benchmarks/*_stress.py` listed in `WORKLOADS`.
2. For each frequency in `FREQS_KHZ` it pins all cores via `cpupower`.
3. Measures before/after RAPL energy and `/proc/stat` ticks.
4. Appends one row per run to `results/energy_runs.csv` with:
   - `timestamp_iso` – UTC timestamp
   - `workload`, `freq_khz`, `run_id`
   - `elapsed_s`, `energy_uJ`
   - `cpu_user_pct`, `cpu_sys_pct` (per‑core %)

---

## 4  Adding a New Workload

1. Drop a `foo_stress.py` in `benchmarks/micro_benchmarks/`.\
   Script must be executable standalone: `python foo_stress.py`.
2. Append its module path to `WORKLOADS` in `scripts/runner.py`.

That’s it – next run is automatically swept and logged.

---

## 5  Troubleshooting

| Symptom                                 | Fix                                                                                      |
| --------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Script exits with NumPy ImportError** | Make sure the venv is active and `pip install numpy` was run inside it.                  |
| ``                                      | `sudo apt install linux-tools-common linux-tools-$(uname -r)`                            |
| ``                                      | Run the whole script as root *or* give your user read access to `/sys/class/powercap/…`. |
| **Push rejected (>100 MB)**             | Large artefacts belong in `data/` and are git‑ignored.                                   |

---

## 6  Road‑map

- YAML‑driven sweeps with `governors:` and `workloads:` lists.
- GitHub Actions smoke test (< 5 s benchmark).
- Automatic plots in `notebooks/results_analysis.ipynb`.

---

## 7  License & Citation

MIT License – see `LICENSE` file.\
If you use this code or dataset in academic work, please cite:\
*Hernández S. 2025. Energy–Performance Sweet‑Spots in CI/CD Pipelines.*

