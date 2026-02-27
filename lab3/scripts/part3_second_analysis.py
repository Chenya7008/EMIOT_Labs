import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_simulation_data(filepath):
    # sep='\s+' 表示匹配任意数量的空格，engine='python' 更加稳定
    df = pd.read_csv(filepath, sep='\s+', engine='python')
    
    # 去掉表头中可能存在的 '%' 符号 (例如 %time -> time)
    df.columns = df.columns.str.replace('%', '')
    
    # 将时间转换为 '天' 或 '小时' 以便宏观观察
    df['day'] = df['time'] / 86400  # 86400秒 = 1天
    df['hour'] = df['time'] / 3600
    
    return df

df_serial = load_simulation_data('se_sim_trace.txt')
df_parallel = load_simulation_data('sim_trace.txt')
# 假设 df_serial 和 df_parallel 已经加载完毕
# 截取前 200 秒的数据
limit_sec = 120

# 注意：使用 <= 还是 < 取决于你是否想包含第200秒那个点，通常差异极小
# 这里的 copy() 是为了防止 SettingWithCopy 警告
subset_serial = df_serial[df_serial['time'] <= limit_sec].copy()
subset_parallel = df_parallel[df_parallel['time'] <= limit_sec].copy()

# 【核心修复】：使用 np.trapezoid 替代 np.trapz
try:
    # 尝试使用新版 NumPy 2.0+ 的函数
    charge_serial = np.trapezoid(subset_serial['i_tot'], subset_serial['time'])
    charge_parallel = np.trapezoid(subset_parallel['i_tot'], subset_parallel['time'])
except AttributeError:
    # 如果是为了兼容旧版 NumPy (1.x)，使用旧函数
    charge_serial = np.trapz(subset_serial['i_tot'], subset_serial['time'])
    charge_parallel = np.trapz(subset_parallel['i_tot'], subset_parallel['time'])

# 转换为 mAh
charge_serial_mah = charge_serial / 3600
charge_parallel_mah = charge_parallel / 3600

print(f"Serial Scheduling Total Charge:   {charge_serial:.4f} mAs ({charge_serial_mah:.4f} mAh)")
print(f"Parallel Scheduling Total Charge: {charge_parallel:.4f} mAs ({charge_parallel_mah:.4f} mAh)")

# 计算差异百分比
diff_percent = abs(charge_serial - charge_parallel) / ((charge_serial + charge_parallel) / 2) * 100
print(f"Difference: {diff_percent:.4f}%")

# ==========================================
# 2. 绘图
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, sharey=True)

# 1. 串行电流图
ax1.plot(subset_serial['time'], subset_serial['i_tot'], color='blue', label='Current')
ax1.fill_between(subset_serial['time'], 0, subset_serial['i_tot'], color='blue', alpha=0.1)
ax1.text(0.02, 0.9, f'Area = {charge_serial:.2f} mAs', transform=ax1.transAxes, color='blue', fontsize=12, fontweight='bold')

ax1.set_title(f'Serial Scheduling (0-{limit_sec}s): Total Load Current', fontsize=14)
ax1.set_ylabel('Current (mA)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend(loc='upper right')

# 2. 并行电流图
ax2.plot(subset_parallel['time'], subset_parallel['i_tot'], color='orange', label='Current')
ax2.fill_between(subset_parallel['time'], 0, subset_parallel['i_tot'], color='orange', alpha=0.1)
ax2.text(0.02, 0.9, f'Area = {charge_parallel:.2f} mAs', transform=ax2.transAxes, color='orange', fontsize=12, fontweight='bold')

ax2.set_title(f'Parallel Scheduling (0-{limit_sec}s): Total Load Current', fontsize=14)
ax2.set_xlabel('Time (s)', fontsize=12)
ax2.set_ylabel('Current (mA)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()


# ==========================================
# 3. 电池电压对比 (Battery Voltage Comparison - IR Drop Visualization)
# ==========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# 设置统一的 Y 轴范围，以便直观对比 "坑" 的深度
# 根据你的 sim_trace 数据，电压大约在 4.0V - 4.1V 之间
# 我们动态获取数据的最大最小值来设定范围，或者手动设定一个窄范围
v_min = min(subset_serial['v_batt'].min(), subset_parallel['v_batt'].min()) - 0.02
v_max = max(subset_serial['v_batt'].max(), subset_parallel['v_batt'].max()) + 0.01

# --- 1. 串行电压图 ---
ax1.plot(subset_serial['time'], subset_serial['v_batt'], color='blue', label='Serial Voltage')

# 标注最低电压点
min_v_serial = subset_serial['v_batt'].min()
min_t_serial = subset_serial.loc[subset_serial['v_batt'].idxmin(), 'time']
ax1.scatter(min_t_serial, min_v_serial, color='red', zorder=5)
ax1.text(min_t_serial + 5, min_v_serial, f'Min: {min_v_serial:.4f} V', color='blue', fontweight='bold', verticalalignment='center')

ax1.set_title(f'Serial Scheduling (0-{limit_sec}s): Battery Voltage', fontsize=14)
ax1.set_ylabel('Voltage (V)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.set_ylim(v_min, v_max)  # 统一量程

# --- 2. 并行电压图 ---
ax2.plot(subset_parallel['time'], subset_parallel['v_batt'], color='orange', label='Parallel Voltage')

# 标注最低电压点
min_v_parallel = subset_parallel['v_batt'].min()
min_t_parallel = subset_parallel.loc[subset_parallel['v_batt'].idxmin(), 'time']
ax2.scatter(min_t_parallel, min_v_parallel, color='red', zorder=5)
ax2.text(min_t_parallel + 5, min_v_parallel, f'Min: {min_v_parallel:.4f} V', color='orange', fontweight='bold', verticalalignment='center')

ax2.set_title(f'Parallel Scheduling (0-{limit_sec}s): Battery Voltage (Deep Sag)', fontsize=14)
ax2.set_xlabel('Time (s)', fontsize=12)
ax2.set_ylabel('Voltage (V)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.set_ylim(v_min, v_max)  # 统一量程

plt.tight_layout()
plt.show()

# --- 打印数值分析供报告使用 ---
print("="*40)
print("      IR Drop (Voltage Sag) Analysis      ")
print("="*40)
print(f"Serial Lowest Voltage:   {min_v_serial:.5f} V")
print(f"Parallel Lowest Voltage: {min_v_parallel:.5f} V")
print(f"Difference (Sag Depth):  {min_v_serial - min_v_parallel:.5f} V")
print("-" * 40)
print("Conclusion: Parallel scheduling causes a deeper voltage drop.")
print("Lower Voltage -> Higher Current required by DC-DC Converter -> Faster Depletion.")
print("="*40)