import re
import os
import pandas as pd
import matplotlib.pyplot as plt

# 1. 配置文件路径
data_dir = "./" 
file_names = {
    "1.0% Limit": "experiment_report_1%_distortion.txt",
    "2.0% Limit": "experiment_report_2%_distortion.txt",
    "3.0% Limit": "experiment_report_3%_distortion.txt"
}

def parse_report(file_path, constraint):
    """解析文本文件并提取数据"""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 正则表达式匹配核心数据
    pattern = r"Voltage:\s+(\d+\.\d+) V\n\s+Strategy:\s+(\w+)\n\s+Power Saving:\s+(\d+\.\d+)%\n\s+Distortion:\s+(\d+\.\d+)%"
    matches = re.findall(pattern, content)
    
    data = []
    for m in matches:
        data.append({
            "Constraint": constraint,
            "Voltage": float(m[0]),
            "Strategy": m[1],
            "Power_Saving": float(m[2]),
            "Distortion": float(m[3])
        })
    return pd.DataFrame(data)

# 2. 读取并合并数据
all_dfs = []
for constraint, fname in file_names.items():
    df = parse_report(os.path.join(data_dir, fname), constraint)
    if not df.empty:
        all_dfs.append(df)

full_df = pd.concat(all_dfs, ignore_index=True)

# --- 分析维度 1：平均值对比 (简单直观) ---
summary = full_df.groupby('Constraint')[['Power_Saving', 'Distortion']].mean()
print("=== 维度 1: 各约束下的平均表现 ===")
print(summary)

# --- 分析维度 2：电压选择占比 (展示系统如何降压) ---
# 统计在不同约束下，15V, 14V, 13V 等电压出现的次数 [cite: 373, 406]
voltage_counts = full_df.groupby(['Constraint', 'Voltage']).size().unstack(fill_value=0)
print("\n=== 维度 2: 电压选择分布 (次数) ===")
print(voltage_counts)

# --- 分析维度 3：可视化柱状图 (替代箱线图) ---
# 绘制平均省电百分比柱状图 [cite: 339, 340]
plt.figure(figsize=(10, 6))
summary['Power_Saving'].plot(kind='bar', color=['#3498db', '#9b59b6', '#e74c3c'])
plt.title("Average Power Saving by Distortion Limit", fontsize=14)
plt.ylabel("Average Power Saving (%)", fontsize=12)
plt.xlabel("Constraint", fontsize=12)
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('average_power_saving.png')
print("\n[图像已保存: average_power_saving.png]")

# --- 分析维度 4：策略偏好统计 ---
# 统计哪种补偿策略最常被用到
plt.figure(figsize=(10, 6))
strategy_dist = full_df.groupby(['Constraint', 'Strategy']).size().unstack(fill_value=0)
strategy_dist.plot(kind='bar', stacked=True, colormap='viridis', figsize=(10,6))
plt.title("Compensation Strategy Distribution", fontsize=14)
plt.ylabel("Number of Images", fontsize=12)
plt.legend(title="Strategy")
plt.savefig('strategy_distribution.png')
print("[图像已保存: strategy_distribution.png]")

print("\n分析完成！您可以将打印出的表格和生成的图片直接放入报告。")