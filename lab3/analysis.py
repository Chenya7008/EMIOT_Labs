import pandas as pd
import matplotlib.pyplot as plt

# 1. 定义加载函数，处理空格分隔和表头
def load_simulation_data(filepath):
    # sep='\s+' 表示匹配任意数量的空格，engine='python' 更加稳定
    df = pd.read_csv(filepath, sep='\s+', engine='python')
    
    # 去掉表头中可能存在的 '%' 符号 (例如 %time -> time)
    df.columns = df.columns.str.replace('%', '')
    
    # 将时间转换为 '天' 或 '小时' 以便宏观观察
    df['day'] = df['time'] / 86400  # 86400秒 = 1天
    df['hour'] = df['time'] / 3600
    
    return df

# 2. 加载两个文件
# 请确保文件名与你实际生成的一致
df_serial = load_simulation_data('se_sim_trace.txt')
df_parallel = load_simulation_data('sim_trace.txt')

print("数据加载完成！")
print(f"串行数据时长: {df_serial['day'].max():.2f} 天")
print(f"并行数据时长: {df_parallel['day'].max():.2f} 天")