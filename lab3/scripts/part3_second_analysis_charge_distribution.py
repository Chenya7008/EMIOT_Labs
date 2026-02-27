import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. 加载仿真日志数据
# 确保列名与你的 sim_trace.txt 的表头严格对应
columns = [
    'time', 'soc', 'i_tot', 'i_mcu', 'i_rf', 'i_pv', 'v_pv', 'real_i_pv', 
    'i_batt', 'v_batt', 'i_air_quality_sensor', 'i_methane_sensor', 
    'i_temperature_sensor', 'i_mic_click_sensor'
]

# 读取数据，跳过以 '%' 开头的注释行
# 确保 'sim_trace(1).txt' 放在与此代码相同的目录下
df = pd.read_csv('sim_trace(1).txt', sep=r'\s+', comment='%', names=columns)

# 2. 筛选电池充电阶段
# 充电发生时，总线请求的电流 i_tot 为负（PV 产生的电流多于负载所需）
df_charge = df[df['i_tot'] < 0].copy()

# 3. 计算充电效率
V_BUS = 3.3  # 总线参考电压

# 输入功率来自 3.3V 总线，输出功率进入电池
df_charge['P_bus_in'] = abs(df_charge['i_tot']) * V_BUS
df_charge['P_batt_out'] = abs(df_charge['i_batt']) * df_charge['v_batt']

# 【修改点 1】：过滤掉分母（P_batt_out）为 0 或极小的情况，防止除以零错误
df_charge = df_charge[df_charge['P_batt_out'] > 1e-6]

# 【修改点 2】：反转公式还原真实的查表效率 (P_bus_in / P_batt_out)
df_charge['eff_charge'] = (df_charge['P_bus_in'] / df_charge['P_batt_out']) * 100

# 清除可能因为精度问题导致的异常值（此时绝大多数数据都会自然落在 0-100 之间）
df_charge = df_charge[(df_charge['eff_charge'] >= 0) & (df_charge['eff_charge'] <= 100)]

# 4. 绘制分布图
plt.figure(figsize=(10, 6))
plt.hist(df_charge['eff_charge'], bins=50, color='mediumseagreen', edgecolor='black', alpha=0.8)
plt.title('Point 2: Battery Converter Charging Efficiency Distribution')
plt.xlabel('Efficiency (%)')
plt.ylabel('Frequency (Seconds)')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# 5. 打印统计数据供报告分析使用
print("=== 电池转换器充电效率统计 (Battery Converter Charging Efficiency Statistics) ===")
print(f"总充电时长: {len(df_charge):,} 秒")
if len(df_charge) > 0:
    print(f"平均充电效率: {df_charge['eff_charge'].mean():.2f}%")
    print(f"最高充电效率: {df_charge['eff_charge'].max():.2f}%")
    print(f"最低充电效率: {df_charge['eff_charge'].min():.2f}%")
    
    # 计算在低效率区间 (<40%) 花费的时间比例
    low_eff_charge = len(df_charge[df_charge['eff_charge'] < 40])
    ratio_low_eff = (low_eff_charge / len(df_charge)) * 100
    print(f"低效率运行时间 (<40%): {low_eff_charge:,} 秒 ({ratio_low_eff:.2f}%)")
else:
    print("追踪日志中未找到充电阶段数据。")
