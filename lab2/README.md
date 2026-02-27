# Lab 2 — Display Power Management

## Directory Structure

```
lab2/
├── Lab2.pdf                # Lab manual
├── lab2_part1.ipynb        # Part 1 notebook
├── lab2_part2.ipynb        # Part 2 notebook
├── myscreen/               # 5 computer screenshots captured for experiments
│   ├── myscreen1.png
│   ├── myscreen2.png
│   ├── myscreen3.png
│   ├── myscreen4.png
│   └── myscreen5.png
├── test_images/            # 50 natural images from the BSDS500 dataset
├── part1_results/          # Result plots for Part 1
└── part2_results/          # Result plots and logs for Part 2
    ├── lab2_final_analysis/
    ├── lab2_results_output_limit_1.0/
    ├── lab2_results_output_limit_2.0/
    ├── lab2_results_output_limit_3.0/
    └── experiment_report_*.txt
```

## Lab Overview

This lab is split into two parts, each with its own notebook.

### Part 1 — `lab2_part1.ipynb`

Explores display power saving techniques on a mixed image set (natural images + screenshots):

- Brightness Scaling (BS): uniformly scale pixel brightness
- Histogram Equalization (HE): redistribute luminance histogram
- Gamma correction: non-linear tone mapping
- Pareto analysis: trade-off between power saving and image distortion across strategies and parameters

Results are saved in `part1_results/`.

### Part 2 — `lab2_part2.ipynb`

Applies a per-image optimization pipeline over the 50 BSDS500 natural images under distortion constraints:

- Sweeps voltage / backlight levels and enhancement strategies (brightness, contrast, both)
- For each distortion limit (1%, 2%, 3%), finds the best power-saving configuration per image
- Outputs best-result images and simulation records per constraint level

Results are organized in `part2_results/`:

| Folder / File | Description |
|---|---|
| `lab2_results_output_limit_1.0/` | Best configs and records under 1% distortion limit |
| `lab2_results_output_limit_2.0/` | Best configs and records under 2% distortion limit |
| `lab2_results_output_limit_3.0/` | Best configs and records under 3% distortion limit |
| `best_images_output/` | Visual comparison of best-optimized images |
| `lab2_final_analysis/` | Summary plots and decision tables across all constraints |
| `experiment_report_*%_distortion.txt` | Per-run textual report |

## Image Datasets

| Folder | Content |
|---|---|
| `myscreen/` | 5 screenshots captured from our own computers |
| `test_images/` | 50 natural images from the [BSDS500](https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html) dataset |
