import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. 数据加载与预处理
# ==========================================
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath, sep='\s+', engine='python')
    df.columns = df.columns.str.replace('%', '')
    df['day'] = df['time'] / 86400 
    
    # 基础物理量计算
    df['i_load_true'] = df['i_tot'] + df['real_i_pv']
    df['P_load'] = df['i_load_true'] * 3.3
    df['P_pv_out'] = df['real_i_pv'] * 3.3
    df['P_batt'] = df['i_batt'] * df['v_batt']
    
    # --- 关键修正：区分“白天”和“黑夜” ---
    # 定义黑夜：光伏输出几乎为0的时候 (防止白天偶尔的云遮挡，取极小阈值)
    df['is_night'] = df['real_i_pv'] < 0.001 

    # --- 计算电池放电效率 ---
    # 条件：1. 总线在向电池要电 (i_tot > 0)
    #       2. 电池确实在输出电流 (i_batt > 0)
    df['batt_eff_raw'] = np.where(
        (df['i_tot'] > 0) & (df['i_batt'] > 0),
        (df['i_tot'] * 3.3) / (df['i_batt'] * df['v_batt']) * 100,
        np.nan 
    )
    
    # 数据清洗：去除仿真器延迟导致的数学伪影 (>100%)
    # 注意：我们保留低效点，只去除物理上不可能的点
    df['batt_eff_clean'] = df['batt_eff_raw'].mask(df['batt_eff_raw'] > 100)
    
    return df

df = load_and_clean_data('sim_trace.txt')

# ==========================================
# 图表 A: 效率 vs 负载电流 (Scatter Plot)
# 这是工程上最标准的分析方法，完美避免“误丢弃”
# ==========================================
# 提取有效放电数据
discharge_data = df.dropna(subset=['batt_eff_clean'])


# ==========================================
# 图表 B: 效率分布直方图 (对比日夜)
# ==========================================
night_eff = discharge_data[discharge_data['is_night'] == True]['batt_eff_clean']
day_eff = discharge_data[discharge_data['is_night'] == False]['batt_eff_clean']

plt.figure(figsize=(12, 5))

# 绘制堆叠直方图，清楚看到低效数据主要来自晚上
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
# 控制台数据分析输出
# ==========================================
print("--- 深度效率分析 ---")
print(f"总放电时长: {len(discharge_data)} 秒")
print(f"  - 夜间放电时长: {len(night_eff)} 秒 (主要处于低效区)")
print(f"  - 白天放电时长: {len(day_eff)} 秒 (主要处于高效区)")
print("-" * 30)
print(f"夜间平均放电效率: {night_eff.mean():.2f}% (Bad Area!)")
print(f"白天平均放电效率: {day_eff.mean():.2f}% (Good Area)")
print("-" * 30)
# 统计真正的“低效时间”占比
low_eff_count = len(discharge_data[discharge_data['batt_eff_clean'] < 40])
print(f"处于低效率区间 (<40%) 的总时长: {low_eff_count} 秒")
print(f"低效率时间占比: {(low_eff_count / len(discharge_data)) * 100:.2f}%")