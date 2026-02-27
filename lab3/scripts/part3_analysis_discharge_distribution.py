import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Data loading and preprocessing
# ==========================================
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath, sep='\s+', engine='python')
    df.columns = df.columns.str.replace('%', '')
    df['day'] = df['time'] / 86400 
    
    # Basic physical quantity calculation
    df['i_load_true'] = df['i_tot'] + df['real_i_pv']
    df['P_load'] = df['i_load_true'] * 3.3
    df['P_pv_out'] = df['real_i_pv'] * 3.3
    df['P_batt'] = df['i_batt'] * df['v_batt']
    
    # --- Key fix: distinguish "day" and "night" ---
    # Define night: when PV output is nearly 0 (use small threshold to avoid occasional cloud cover)
    df['is_night'] = df['real_i_pv'] < 0.001 

    # --- Compute battery discharge efficiency ---
    # Condition: 1. Bus is drawing from battery (i_tot > 0)
    #           2. Battery is actually outputting current (i_batt > 0)
    df['batt_eff_raw'] = np.where(
        (df['i_tot'] > 0) & (df['i_batt'] > 0),
        (df['i_tot'] * 3.3) / (df['i_batt'] * df['v_batt']) * 100,
        np.nan 
    )
    
    # Data cleaning: remove math artifacts from simulator delay (>100%)
    # Note: keep low-efficiency points, only remove physically impossible ones
    df['batt_eff_clean'] = df['batt_eff_raw'].mask(df['batt_eff_raw'] > 100)
    
    return df

df = load_and_clean_data('sim_trace.txt')

# ==========================================
# Chart A: efficiency vs load current (Scatter Plot)
# This is the most standard engineering analysis method, avoids false rejection
# ==========================================
# Extract valid discharge data
discharge_data = df.dropna(subset=['batt_eff_clean'])


# ==========================================
# Chart B: efficiency distribution histogram (day vs night)
# ==========================================
night_eff = discharge_data[discharge_data['is_night'] == True]['batt_eff_clean']
day_eff = discharge_data[discharge_data['is_night'] == False]['batt_eff_clean']

plt.figure(figsize=(12, 5))

# Stacked histogram shows low-efficiency data mainly at night
plt.hist([day_eff, night_eff], bins=50, stacked=True, 
         color=['blue', 'red'], label=['Daytime Discharge', 'Nighttime Discharge'],
         edgecolor='black', alpha=0.7)

plt.title('Point 2: Efficiency Distribution (Day vs Night Breakdown)', fontsize=14)
plt.xlabel('Efficiency (%)', fontsize=12)
plt.ylabel('Frequency (Seconds)', fontsize=12)
plt.legend()
plt.grid(axis='y', alpha=0.5)

plt.tight_layout()
plt.show()

# ==========================================
# Console data analysis output
# ==========================================
print("--- In-depth efficiency analysis ---")
print(f"Total discharge duration: {len(discharge_data)} s")
print(f"  - Night discharge: {len(night_eff)} s (mainly low-efficiency zone)")
print(f"  - Day discharge: {len(day_eff)} s (mainly high-efficiency zone)")
print("-" * 30)
print(f"Night avg discharge efficiency: {night_eff.mean():.2f}% (Bad Area!")
print(f"Day avg discharge efficiency: {day_eff.mean():.2f}% (Good Area)")
print("-" * 30)
# Compute fraction of truly low-efficiency time
low_eff_count = len(discharge_data[discharge_data['batt_eff_clean'] < 40])
print(f"Total time in low-efficiency zone (<40%): {low_eff_count} s")
print(f"Low-efficiency time fraction: {(low_eff_count / len(discharge_data)) * 100:.2f}%")