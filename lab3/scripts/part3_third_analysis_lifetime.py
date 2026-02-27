import pandas as pd
import matplotlib.pyplot as plt


FILENAME = 'sim_trace.txt'
OUTPUT_IMG = 'lifetime_analysis.png'


def plot_lifetime_optimized():
    print(f"[-] 正在使用 C 引擎读取文件 {FILENAME} ...")
    
    try:
       
        df = pd.read_csv(FILENAME, delim_whitespace=True, engine='c')
    except FileNotFoundError:
        print(f"错误: 找不到 {FILENAME}")
        return

    
    df.rename(columns={'%time': 'time'}, inplace=True)

    
    
    df.drop(df[df['time'] < 10].index, inplace=True)
    
    
    df.reset_index(drop=True, inplace=True)

    if df.empty:
        print("错误：数据为空 (可能被全部过滤)")
        return

    
    last_row = df.iloc[-1]
    lifetime_days = last_row['time'] / 86400.0
    final_soc = last_row['soc']
    
    
    
    if final_soc <= 0.015: 
        status = "DEAD (Depleted)"
        color_status = "red"
        
        dead_rows = df[df['soc'] <= 0.0101]
        if not dead_rows.empty:
            lifetime_days = dead_rows.iloc[0]['time'] / 86400.0
    else:
        status = "ALIVE (Running)"
        color_status = "green"

    print(f"[-] 分析结果: 状态={status}, 寿命={lifetime_days:.2f} 天")

    
    print("[-] 正在绘图...")
    
    
    step = 1000
    df_plot = df.iloc[::step].copy()
    
    
    df_plot['days'] = df_plot['time'] / 86400.0

    fig, ax = plt.subplots(figsize=(10, 6))
    
    
    ax.plot(df_plot['days'], df_plot['soc'], color='green', linewidth=1.5, label='Battery SOC')
    
    
    ax.axhline(y=0.01, color='red', linestyle=':', alpha=0.5, label='Death Threshold (1%)')

    
    info_text = (f"Status: {status}\n"
                 f"Lifetime: {lifetime_days:.2f} Days\n"
                 f"Final SOC: {final_soc*100:.1f}%")
    
    ax.text(0.97, 0.97, info_text, transform=ax.transAxes,
            fontsize=12, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor=color_status))

    
    ax.set_xlabel('Time (Days)')
    ax.set_ylabel('SOC (0.0 - 1.0)')
    ax.set_title(f'Third Analysis: Lifetime Check (Sampled 1/{step})')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=200)
    print(f"[-] 图表已保存为: {OUTPUT_IMG}")
    

if __name__ == "__main__":
    plot_lifetime_optimized()
