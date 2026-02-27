# EMIOT Labs

> GitHub: [Chenya7008/EMIOT_Labs](https://github.com/Chenya7008/EMIOT_Labs/tree/main)

Lab assignments for the **Energy Management in IoT** course at Politecnico di Torino.

> Each lab subfolder contains its own **README** with detailed instructions and a lab report PDF.
> See: [lab1/README.md](lab1/README.md) · [lab2/README.md](lab2/README.md) · [lab3/readme.md](lab3/readme.md)

## Structure

| Directory | Topic |
|-----------|-------|
| [lab1/](lab1/) | Dynamic Power Management (DPM) — simulator & workload analysis |
| [lab2/](lab2/) | Battery modelling & image processing with energy constraints |
| [lab3/](lab3/) | Energy harvesting simulation& solar converter |

## Lab 1 — DPM Simulator quick reference

```bash
# Run simulator with a workload (from lab1/dpm-simulator/)
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_1.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_2.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_hover.txt
./dpm_simulator -h 0 0 0 0 0 0 0 -psm example/psm.txt -wl ../../workloads/workloads/workload_ramp.txt
```

