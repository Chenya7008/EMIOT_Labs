import subprocess
import re
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. Configuration - modify according to your experiment
# ==============================================================================
# Path to the C simulator executable
SIMULATOR_EXEC = './dpm_simulator'


#WORKLOAD_FILE = '../../workloads/workloads/workload_2.txt'
#WORKLOAD_FILE = '../../workloads/workloads/workload_1.txt'

PSM_FILE = 'example/psm.txt'

# Timeout range to test
# e.g. range(1, 101, 2) means 1 to 100, step 2 (1, 3, 5...)
TIMEOUT_RANGE = range(0,101, 1)

# ==============================================================================
# 2. Core script functions - no modification needed
# ==============================================================================

def run_simulation(timeout, workload_path, psm_path):
    """Build command, run simulator and return output"""
    command = [
        SIMULATOR_EXEC,
        '-t', str(timeout),
        '-wl', workload_path,
        '-psm', psm_path
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def parse_output(output_text):
    """Parse all key data from output text using regex"""
    patterns = {
        'active_time': r"\[sim\] Active time in profile = ([\d.]+)s",
        'inactive_time': r"\[sim\] Inactive time in profile = ([\d.]+)s",
        'time_no_dpm': r"\[sim\] Tot\. Time w/o DPM = ([\d.]+)s",
        'time_dpm': r"\[sim\] Tot\. Time w DPM = .*?, Tot\. Time w DPM = ([\d.]+)s",
        'time_run': r"\[sim\] Total time in state Run = ([\d.]+)s",
        'time_idle': r"\[sim\] Total time in state Idle = ([\d.]+)s",
        'time_sleep': r"\[sim\] Total time in state Sleep = ([\d.]+)s",
        'time_waiting': r"\[sim\] Timeout waiting time = ([\d.]+)s",
        'time_transitions': r"\[sim\] Transitions time = ([\d.]+)s",
        'transitions': r"\[sim\] N\. of transitions = (\d+)",
        'energy_transitions': r"\[sim\] Energy for transitions = ([\d.]+)J",
        'energy_no_dpm': r"\[sim\] Tot\. Energy w/o DPM = ([\d.]+)J",
        'energy_dpm': r"\[sim\] Tot\. Energy w/o DPM = .*?, Tot\. Energy w DPM = ([\d.]+)J"
    }

    parsed_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, output_text)
        if match:
            value_str = match.group(1)
            parsed_data[key] = float(value_str) if '.' in value_str else int(value_str)
        else:
            parsed_data[key] = None

    return parsed_data



def analyze_workload_distribution(filepath):
    """
    Read workload file and compute idle time distribution.
    Helps explain why transitions drop sharply at certain timeout values.
    """
    try:
        # Read workload file (space-separated)
        # Format: start_time duration
        df = pd.read_csv(filepath, sep=r'\s+', header=None, names=['start', 'duration'])

        # Compute idle time
        # Idle = current task start - (previous task start + previous task duration)
        df['prev_end'] = df['start'].shift(1) + df['duration'].shift(1)
        df['idle_time'] = df['start'] - df['prev_end']

        # Drop first row (NaN) and non-positive values
        df = df.dropna()
        df = df[df['idle_time'] > 0]

        # Count occurrences of each idle time value
        distribution = df['idle_time'].value_counts().sort_index()

        print("\n" + "="*50)
        print(f"WORKLOAD ANALYSIS: {filepath}")
        print("="*50)
        print(f"{'Idle Time (ms)':<20} | {'Count':<15} | {'Timeout threshold to suppress transition'}")
        print("-" * 65)

        for idle_val, count in distribution.items():
            # A transition is suppressed only when Timeout > idle_val
            threshold = int(idle_val)
            print(f"{idle_val:<20} | {count:<15} | Timeout > {threshold} ms")

        print("-" * 65)
        print("Tip: each time your Timeout crosses one of the idle time values above,")
        print("     the transition count drops by a step.")
        print("="*50 + "\n")

    except Exception as e:
        print(f"Failed to analyze workload file: {e}")

# ==========================================
# Call before the main loop
# ==========================================
# ... your code ...

# Insert call here:
analyze_workload_distribution(WORKLOAD_FILE)


# --- Main program ---
all_results = []
print(f"Starting batch test for {WORKLOAD_FILE}...")
print(f"Timeout range: {TIMEOUT_RANGE.start}ms to {TIMEOUT_RANGE.stop - 1}ms")

for t in TIMEOUT_RANGE:
    try:
        print(f"Running t = {t}ms...", end='', flush=True)
        output = run_simulation(t, WORKLOAD_FILE, PSM_FILE)
        data = parse_output(output)
        data['timeout'] = t
        all_results.append(data)
        print(" done")
    except subprocess.CalledProcessError as e:
        print(f"\nError: simulator failed (t={t}ms).")
        print(e.stderr)
        break
    except Exception as e:
        print(f"\nError: unexpected error (t={t}ms): {e}")
        break

df_results = pd.DataFrame(all_results)
print("\n" + "="*50)
print("Results summary")
print("="*50)
print(df_results)

# ==============================================================================
# Save results to text file
# ==============================================================================
# Create output filename
output_txt_filename = f'results_{WORKLOAD_FILE.split("/")[-1].split(".")[0]}.txt'

# Save DataFrame to text file
df_results.to_csv(output_txt_filename, sep='\t', index=False, float_format='%.6f')
print(f"\nResults saved to: {output_txt_filename}")

# ==============================================================================
# 3. Visualization
# ==============================================================================
if not df_results.empty and 'energy_dpm' in df_results.columns and df_results['energy_dpm'].notna().any():
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(14, 7))

    color = 'tab:blue'
    ax1.set_xlabel('Timeout (ms)', fontsize=14)
    ax1.set_ylabel('Total Energy (J)', color=color, fontsize=14)
    ax1.plot(df_results['timeout'], df_results['energy_dpm'], color=color, marker='o', label='Total Energy w/ DPM')
    ax1.tick_params(axis='y', labelcolor=color)

    min_energy_point = df_results.loc[df_results['energy_dpm'].idxmin()]
    optimal_t = min_energy_point['timeout']
    min_energy = min_energy_point['energy_dpm']
    ax1.scatter(optimal_t, min_energy, color='red', s=150, zorder=5,
                label=f'Optimal Point\nt={int(optimal_t)}ms, E={min_energy:.4f}J')

    ax2 = ax1.twinx()
    color = 'tab:green'
    ax2.set_ylabel('Number of Transitions', color=color, fontsize=14)
    ax2.plot(df_results['timeout'], df_results['transitions'], color=color, linestyle='--', marker='x', label='Transitions')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title(f'Analysis for {WORKLOAD_FILE}', fontsize=16, fontweight='bold')
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

    output_filename = f'analysis_{WORKLOAD_FILE.split("/")[-1].split(".")[0]}.png'
    plt.savefig(output_filename)
    print(f"\nPlot saved as: {output_filename}")
    plt.show()
