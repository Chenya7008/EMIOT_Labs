# -*- coding: utf-8 -*-
import os

def generate_file(filename, pattern_data):
    """
    模拟 Jumper 的输出格式：
    Active_Start Active_Duration
    """
    current_time = 2000 # 模拟 Jumper 启动后的初始时间
    
    with open(filename, 'w') as f:
        for active_dur, idle_dur in pattern_data:
            # 写入当前任务的开始时间和持续时长
            f.write("{} {}\n".format(int(current_time), int(active_dur)))
            
            # 时间推进：工作时间 + 休息时间
            current_time += active_dur + idle_dur
            
    print("Generate SUCCESS: " + filename)

# ==========================================
# 1. 生成 Workload A: Boundary Hover (临界徘徊)
#    Active 10ms <-> Idle 80ms
#    Active 10ms <-> Idle 4ms
# ==========================================
hover_data = []
# 生成 50 个周期，足够测试了
for _ in range(50):
    hover_data.append((10, 120000)) # 长空闲 (应睡)
    hover_data.append((10, 4))  # 短空闲 (不应睡)

generate_file("workload_hover.txt", hover_data)

# ==========================================
# 2. 生成 Workload B: Ramp-up Noise (阶梯上升)
#    Active 10ms <-> Idle 1, 2, 5, 10, 50 ms
# ==========================================
#ramp_data = []
#delays = [6, 6, 6, 100000, 6, 6, 6, 100000]
# 重复 10 轮
#for _ in range(10):
 #   for d in delays:
 #       ramp_data.append((10, d))
#generate_file("workload_ramp.txt", ramp_data)