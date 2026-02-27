# EMIOT Labs

> GitHub: [Chenya7008/EMIOT_Labs](https://github.com/Chenya7008/EMIOT_Labs/tree/main)

Lab assignments for the **Energy Management in IoT** course at Politecnico di Torino.

Please read the README file in each subfolder — the corresponding reports are contained within.

## Structure

| Directory | Topic |
|-----------|-------|
| [lab1/](lab1/) | Dynamic Power Management (DPM) — simulator & workload analysis |
| [lab2/](lab2/) | Battery modelling & image processing with energy constraints |
| [lab3/](lab3/) | Energy harvesting simulation (EM4IoT) & solar converter |

## Commit conventions

| Prefix | Meaning |
|--------|---------|
| `updated` | new or improved content |
| `fixed` | bug fix or correction to existing files |
| `test` | experimental / work-in-progress |
| `delete` | removed unused files |

## Lab 1 — DPM Simulator quick reference

```bash
# Run simulator with a workload (from lab1/dpm-simulator/)
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_1.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_2.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_hover.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_ramp.txt
```

Policy rule logic is implemented in `utilities.c`.
