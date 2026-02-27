import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load simulation log data
# Ensure column names match sim_trace.txt headers exactly
columns = [
    'time', 'soc', 'i_tot', 'i_mcu', 'i_rf', 'i_pv', 'v_pv', 'real_i_pv', 
    'i_batt', 'v_batt', 'i_air_quality_sensor', 'i_methane_sensor', 
    'i_temperature_sensor', 'i_mic_click_sensor'
]

# Read data, skip comment lines starting with '%'
# Ensure 'sim_trace(1).txt' is in the same directory as this script
df = pd.read_csv('sim_trace(1).txt', sep=r'\s+', comment='%', names=columns)

# 2. Filter battery charging phase
# During charging, bus current i_tot is negative (PV produces more than load needs)
df_charge = df[df['i_tot'] < 0].copy()

# 3. Compute charging efficiency
V_BUS = 3.3  # bus reference voltage

# Input power from 3.3V bus, output power goes into battery
df_charge['P_bus_in'] = abs(df_charge['i_tot']) * V_BUS
df_charge['P_batt_out'] = abs(df_charge['i_batt']) * df_charge['v_batt']

# [Fix 1]: filter out cases where denominator (P_batt_out) is 0 or very small to avoid division by zero
df_charge = df_charge[df_charge['P_batt_out'] > 1e-6]

# [Fix 2]: invert formula to recover real lookup efficiency (P_bus_in / P_batt_out)
df_charge['eff_charge'] = (df_charge['P_bus_in'] / df_charge['P_batt_out']) * 100

# Remove outliers caused by precision issues (most data naturally falls within 0-100)
df_charge = df_charge[(df_charge['eff_charge'] >= 0) & (df_charge['eff_charge'] <= 100)]

# 4. Plot distribution
plt.figure(figsize=(10, 6))
plt.hist(df_charge['eff_charge'], bins=50, color='mediumseagreen', edgecolor='black', alpha=0.8)
plt.title('Point 2: Battery Converter Charging Efficiency Distribution')
plt.xlabel('Efficiency (%)')
plt.ylabel('Frequency (Seconds)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 5. Print statistics for report
print("=== Battery Converter Charging Efficiency Statistics ===")
print(f"Total charging duration: {len(df_charge):,} s")
if len(df_charge) > 0:
    print(f"Avg charging efficiency: {df_charge['eff_charge'].mean():.2f}%")
    print(f"Max charging efficiency: {df_charge['eff_charge'].max():.2f}%")
    print(f"Min charging efficiency: {df_charge['eff_charge'].min():.2f}%")
    
    # Compute time fraction spent in low-efficiency zone (<40%)
    low_eff_charge = len(df_charge[df_charge['eff_charge'] < 40])
    ratio_low_eff = (low_eff_charge / len(df_charge)) * 100
    print(f"Low-efficiency time (<40%): {low_eff_charge:,} s ({ratio_low_eff:.2f}%)")
else:
    print("No charging phase data found in trace log.")
