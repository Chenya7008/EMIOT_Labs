# Lab 1 — Dynamic Power Management (DPM) Simulator

## Directory Structure

```
lab1/
├── Lab1.pdf                        # Lab manual
├── dpm-simulator/dpm-simulator/    # Simulator source and executables
│   ├── dpm_simulator               # Compiled binary
│   ├── dpm_simulator.c             # Main simulator entry point
│   ├── Makefile
│   ├── run_all.py                  # Batch runner for timeout policy sweep
│   ├── example/                    # PSM definition files
│   │   ├── origin_psm.txt          # Original PSM provided by the lab
│   │   ├── psm.txt                 # Our custom PSM
│   │   └── wl.txt                  # Example workload
│   ├── inc/                        # Header files
│   └── src/
│       └── dpm_policies.c          # DPM policy implementations (edit here)
├── workloads/workloads/            # Workload files
│   ├── workload_1.txt
│   ├── workload_2.txt
│   ├── workload_hover.txt
│   ├── workload_ramp.txt
│   └── get_workload.py             # Script to generate custom workloads
└── results/                        # Report figures and log results
    ├── *.png                       # Result plots
    └── log_results/                # Raw simulator output logs
```

## Running the Simulator

### Non-timeout policies (simple / predictive)

Run directly from the `dpm-simulator/dpm-simulator/` directory:

```bash
cd lab1/dpm-simulator/dpm-simulator

./dpm_simulator -psm example/origin_psm.txt \
                -wl ../../workloads/workloads/workload_ramp.txt \
                -h 0 0 0 0 1 0 0
```

The `-h` flag selects the policy variant. Adjust the values as needed for your experiment.

### Timeout policy (batch sweep)

Use `run_all.py` to sweep a range of timeout values and automatically plot energy vs. transitions:

```bash
cd lab1/dpm-simulator/dpm-simulator
python3 run_all.py
```

Edit the top of `run_all.py` to configure your experiment:

```python
WORKLOAD_FILE = '../../workloads/workloads/workload_1.txt'  # choose workload
PSM_FILE      = 'example/psm.txt'                           # choose PSM
TIMEOUT_RANGE = range(0, 101, 1)                            # timeout sweep range (ms)
```

## Modifying Policies

DPM policy logic lives in [src/dpm_policies.c](dpm-simulator/dpm-simulator/src/dpm_policies.c), starting at **line 135** inside `dpm_decide_state()`.

- **Timeout policy**: transition to sleep after a fixed idle period.
- **Predictive policy**: use historical idle-time data to decide when to sleep.

After editing, rebuild with:

```bash
cd lab1/dpm-simulator/dpm-simulator
make
```

## PSM Files

Custom Power State Machine (PSM) definitions are stored in the `example/` folder:

| File | Description |
|------|-------------|
| `origin_psm.txt` | Original PSM from the lab handout |
| `psm.txt` | Our modified PSM for experiments |

## Workloads

All workload files are in `workloads/workloads/`:

| File | Description |
|------|-------------|
| `workload_1.txt` | Lab-provided workload 1 |
| `workload_2.txt` | Lab-provided workload 2 |
| `workload_hover.txt` | Custom hover workload |
| `workload_ramp.txt` | Custom ramp workload |

`get_workload.py` is our script to generate new synthetic workloads.

## Results

The `results/` directory contains all plots and logs used in the lab report:

- `*.png` — energy and transition plots for each experiment
- `log_results/` — raw simulator output for timeout sweeps and PSM variants
