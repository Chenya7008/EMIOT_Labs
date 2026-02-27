import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Define data loading and processing function
# ==========================================
def load_simulation_data(filepath):
    # Read data and clean column headers
    df = pd.read_csv(filepath, sep='\s+', engine='python')
    df.columns = df.columns.str.replace('%', '')
    df['day'] = df['time'] / 86400 
    
    # --- Basic power calculation (Point 1 & basic analysis) ---
    # Real load current = i_tot + real_i_pv
    df['i_load_true'] = df['i_tot'] + df['real_i_pv']
    # Compute power (mW)
    df['P_load'] = df['i_load_true'] * 3.3          
    df['P_pv_out'] = df['real_i_pv'] * 3.3          
    df['P_batt'] = df['i_batt'] * df['v_batt']      
    
    # --- Added: compute converter efficiency (for Point 2) ---
    # 1. PV converter efficiency (%)
    df['P_pv_in'] = df['i_pv'] * df['v_pv']         
    df['pv_efficiency'] = np.where(df['P_pv_in'] > 0, (df['P_pv_out'] / df['P_pv_in']) * 100, np.nan)
    
    # 2. Battery discharge converter efficiency (%)
    # When i_tot > 0, PV is insufficient and battery is discharging.
    # Power delivered to bus: P_out = i_tot * 3.3
    # Power consumed by battery: P_in = i_batt * v_batt
    df['batt_discharge_eff'] = np.where(
        (df['i_tot'] > 0) & (df['i_batt'] > 0),
        (df['i_tot'] * 3.3) / (df['i_batt'] * df['v_batt']) * 100,
        np.nan # NaN when charging or idle, filtered out in plots
    )
    
    return df

# Load data (ensure filename 'sim_trace.txt' is correct)
df_parallel = load_simulation_data('sim_trace.txt')


# ==========================================
# Plot 1: macro trend (7-day global view)
# ==========================================
df_macro = df_parallel[df_parallel['day'] <= 7]

fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
axs[0].plot(df_macro['day'], df_macro['P_load'], label='True Load Power (mW)', color='red', alpha=0.8)
axs[0].plot(df_macro['day'], df_macro['P_pv_out'], label='PV Power Supplied (mW)', color='blue', alpha=0.6)
axs[0].set_ylabel('Power (mW)')
axs[0].set_title('Macro View (7 Days): Global Trend')
axs[0].legend(loc='upper right')
axs[0].grid(True)

axs[1].plot(df_macro['day'], df_macro['P_batt'], label='Battery Power (mW)', color='orange')
axs[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
axs[1].set_ylabel('Power (mW)')
axs[1].set_title('Battery Behavior (>0 Discharging, <0 Charging)')
axs[1].legend(loc='upper right')
axs[1].grid(True)

axs[2].plot(df_macro['day'], df_macro['soc'], label='Battery SOC', color='green')
axs[2].set_ylabel('SOC (0-1)')
axs[2].set_xlabel('Time (Days)')
axs[2].set_title('Battery State of Charge')
axs[2].legend(loc='lower right')
axs[2].grid(True)

plt.tight_layout()
plt.show()


# ==========================================
# Plot 2: zoomed-in view (2-hour fine view)
# ==========================================
start_time = 3 * 3600
end_time = 5 * 3600
df_micro = df_parallel[(df_parallel['time'] >= start_time) & (df_parallel['time'] <= end_time)]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

ax1.step(df_micro['time'] / 3600, df_micro['P_load'], label='True Load Power (mW)', color='red', where='post', linewidth=1.5)
ax1.plot(df_micro['time'] / 3600, df_micro['P_pv_out'], label='PV Power Supplied (mW)', color='blue', alpha=0.8, linewidth=2)
ax1.set_ylabel('Power (mW)')
ax1.set_title('Zoomed-in View (Hours 3-5): Load Pulses vs PV Generation')
ax1.legend(loc='upper right')
ax1.grid(True, which='both', linestyle='--', alpha=0.7)

ax2.plot(df_micro['time'] / 3600, df_micro['P_batt'], label='Battery Power (mW)', color='orange', linewidth=1.5)
ax2.axhline(0, color='black', linewidth=1, linestyle='-')
ax2.fill_between(df_micro['time'] / 3600, 0, df_micro['P_batt'], where=(df_micro['P_batt'] > 0), color='red', alpha=0.3, label='Discharging (Battery -> Load)')
ax2.fill_between(df_micro['time'] / 3600, 0, df_micro['P_batt'], where=(df_micro['P_batt'] < 0), color='green', alpha=0.3, label='Charging (PV -> Battery)')

ax2.set_ylabel('Power (mW)')
ax2.set_xlabel('Time (Hours)')
ax2.set_title('Zoomed-in View (Hours 3-5): Battery Rapid Charge/Discharge Cycles')
ax2.legend(loc='upper right')
ax2.grid(True, which='both', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()


# ==========================================
# Plot 3: Point 2 analysis - converter efficiency histogram 
# (Efficiency of the converters)
# ==========================================
# 1. Extract valid efficiency data and drop NaN
pv_eff_raw = df_parallel['pv_efficiency'].dropna()
batt_eff_raw = df_parallel['batt_discharge_eff'].dropna()

# 2. [Key fix]: Data Cleaning
# Filter out math artifacts (>100%) caused by simulator 1-second calculation delay
pv_eff_cleaned = pv_eff_raw[pv_eff_raw <= 100]
batt_eff_cleaned = batt_eff_raw[batt_eff_raw <= 100]

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# 1. PV converter efficiency distribution
ax[0].hist(pv_eff_cleaned, bins=50, color='blue', alpha=0.7, edgecolor='black')
ax[0].set_title('Point 2: PV Converter Efficiency Distribution')
ax[0].set_xlabel('Efficiency (%)')
ax[0].set_ylabel('Frequency (Seconds)')
ax[0].grid(axis='y', alpha=0.75)

# 2. Battery converter discharge efficiency distribution (x-axis max is 100%)
ax[1].hist(batt_eff_cleaned, bins=50, color='orange', alpha=0.7, edgecolor='black')
ax[1].set_title('Point 2: Battery Converter Discharge Efficiency Distribution')
ax[1].set_xlabel('Efficiency (%)')
ax[1].set_ylabel('Frequency (Seconds)')
ax[1].grid(axis='y', alpha=0.75)

plt.tight_layout()
plt.show()

# Print real average efficiency for report
print(f"PV Converter Average Efficiency: {pv_eff_cleaned.mean():.2f}%")
print(f"Battery Converter Average Discharge Efficiency: {batt_eff_cleaned.mean():.2f}%")


# ==========================================
# Plot 4: Point 3 analysis - battery usage frequency pie chart 
# (How often the battery has to be used)
# ==========================================
total_time = len(df_parallel)
# Discharging: PV insufficient, battery needed (i_tot > 0)
discharging_time = len(df_parallel[df_parallel['i_tot'] > 0])
# Charging/self-sufficient: PV covers load or charges battery (i_tot <= 0)
charging_idle_time = total_time - discharging_time

plt.figure(figsize=(7, 7))
labels = ['Battery Discharging\n(PV Not Enough)', 'PV Sufficient\n(Battery Charging or Idle)']
sizes = [discharging_time, charging_idle_time]
colors = ['#ff9999', '#66b3ff']
explode = (0.1, 0)  # highlight discharge slice (core issue in report)

plt.pie(sizes, explode=explode, labels=labels, colors=colors, 
        autopct='%1.1f%%', shadow=True, startangle=140, textprops={'fontsize': 12})
plt.title('Point 3: How Often is the Battery Used to Supply Power?', fontsize=14)
plt.show()

print(f"Battery Discharging Time Ratio: {(discharging_time/total_time)*100:.2f}%")