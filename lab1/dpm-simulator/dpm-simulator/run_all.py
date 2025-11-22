import subprocess
import re
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# 1. 配置区 - 请根据你的实验任务修改
# ==============================================================================
# C语言模拟器的可执行文件路径
SIMULATOR_EXEC = './dpm_simulator'


WORKLOAD_FILE = '../../workloads/workloads/workload_1.txt'
# 任务2: 分析 workload2.txt (使用时请取消下面的注释，并注释掉上面一行)

#WORKLOAD_FILE = '../../workloads/workloads/workload_2.txt'
# PSM 文件的路径 (通常保持不变，与您的命令一致)

PSM_FILE = 'example/psm.txt'

# 你想要测试的超时值范围
# 例如 range(1, 101, 2) 表示从1到100，每隔2测试一次 (1, 3, 5...)
TIMEOUT_RANGE = range(0, 8, 1)

# ==============================================================================
# 2. 脚本核心功能区 - 无需修改
# ==============================================================================

def run_simulation(timeout, workload_path, psm_path):
    """构建命令、运行模拟器并返回输出结果"""
    command = [
        SIMULATOR_EXEC,
        '-t', str(timeout),
        '-wl', workload_path,
        '-psm', psm_path
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return result.stdout

def parse_output(output_text):
    """使用正则表达式从输出文本中解析所有关键数据"""
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

# --- 主程序开始 ---
all_results = []
print(f"开始批量测试 {WORKLOAD_FILE}...")
print(f"测试超时范围: {TIMEOUT_RANGE.start}ms to {TIMEOUT_RANGE.stop - 1}ms")

for t in TIMEOUT_RANGE:
    try:
        print(f"正在运行 t = {t}ms...", end='', flush=True)
        output = run_simulation(t, WORKLOAD_FILE, PSM_FILE)
        data = parse_output(output)
        data['timeout'] = t
        all_results.append(data)
        print(" 完成")
    except subprocess.CalledProcessError as e:
        print(f"\n错误：运行模拟器失败 (t={t}ms)。")
        print(e.stderr)
        break
    except Exception as e:
        print(f"\n错误：处理数据时发生未知错误 (t={t}ms): {e}")
        break

df_results = pd.DataFrame(all_results)
print("\n" + "="*50)
print("实验结果汇总 (已包含所有字段)")
print("="*50)
print(df_results)

# ==============================================================================
# 添加最简单的文本输出功能
# ==============================================================================
# 创建文本文件
output_txt_filename = f'results_{WORKLOAD_FILE.split("/")[-1].split(".")[0]}.txt'

# 直接将DataFrame保存为文本文件
df_results.to_csv(output_txt_filename, sep='\t', index=False, float_format='%.6f')
print(f"\n测试结果已保存到文本文件: {output_txt_filename}")

# ==============================================================================
# 3. 结果可视化区 (保持不变)
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
    print(f"\n图表已保存为: {output_filename}")
    plt.show()