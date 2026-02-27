# -*- coding: utf-8 -*-
import os

def generate_file(filename, pattern_data):
    """
    Simulates Jumper output format:
    Active_Start Active_Duration
    """
    current_time = 2000 # initial time after Jumper starts

    with open(filename, 'w') as f:
        for active_dur, idle_dur in pattern_data:
            # write start time and duration of current task
            f.write("{} {}\n".format(int(current_time), int(active_dur)))

            # advance time: active duration + idle duration
            current_time += active_dur + idle_dur

    print("Generate SUCCESS: " + filename)

# ==========================================
# 1. Generate Workload A: Boundary Hover
#    Active 10ms <-> Idle 80ms
#    Active 10ms <-> Idle 4ms
# ==========================================
hover_data = []
# generate 50 cycles
for _ in range(50):
    hover_data.append((10, 120000)) # long idle (should sleep)
    hover_data.append((10, 4))  # short idle (should not sleep)

generate_file("workload_hover.txt", hover_data)

# ==========================================
# 2. Generate Workload B: Ramp-up Noise
#    Active 10ms <-> Idle 1, 2, 5, 10, 50 ms
# ==========================================
#ramp_data = []
#delays = [6, 6, 6, 100000, 6, 6, 6, 100000]
# repeat 10 rounds
#for _ in range(10):
 #   for d in delays:
 #       ramp_data.append((10, d))
#generate_file("workload_ramp.txt", ramp_data)
