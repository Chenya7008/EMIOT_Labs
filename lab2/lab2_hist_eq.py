import os
import glob
import numpy as np
from PIL import Image
from skimage import color, exposure
import matplotlib.pyplot as plt

# ================= 配置区域 =================
# 请确保这里指向你存放图片的文件夹
IMG_DIR = "./test_images" 
# ===========================================

def estimate_power(image_array):
    """ 
    计算功耗 (Part 1 Model) 
    返回单位通常是 Watts (取决于系数定义的单位)
    """
    img = image_array.astype(np.float32)
    R, G, B = img[:,:,0], img[:,:,1], img[:,:,2]
    
    # 参数来自 Slide 23
    gamma = 0.7755
    w0 = 1.48169521e-6
    wr = 2.13636845e-7
    wg = 1.77746705e-7
    wb = 2.14348309e-7
    
    # 计算每个像素的动态功耗
    p_pixel = wr * np.power(R, gamma) + wg * np.power(G, gamma) + wb * np.power(B, gamma)
    
    # 总功耗
    return w0 + np.sum(p_pixel)

def compute_distortion(img_orig, img_mod):
    """ 计算失真度 (LAB Space Euclidean Distance) """
    # 归一化并转 LAB
    img_orig_norm = img_orig.astype(np.float32) / 255.0
    img_mod_norm = img_mod.astype(np.float32) / 255.0
    
    lab_orig = color.rgb2lab(img_orig_norm)
    lab_mod = color.rgb2lab(img_mod_norm)
    
    # 计算差异
    diff_sq = np.sum((lab_orig - lab_mod) ** 2, axis=2)
    dist_pixel = np.sqrt(diff_sq)
    epsilon = np.sum(dist_pixel)
    
    H, W, _ = img_orig.shape
    # Slide 28 的分母常数
    max_dist_const = np.sqrt(100**2 + 255**2 + 255**2)
    
    return (epsilon / (W * H * max_dist_const)) * 100

def apply_histogram_equalization(image_rgb):
    """ 
    标准直方图均衡化 (无参数) 
    过程: RGB -> HSV -> Equalize V -> RGB
    """
    img_float = image_rgb.astype(np.float32) / 255.0
    img_hsv = color.rgb2hsv(img_float)
    
    # 对 V 通道 (亮度) 进行均衡化
    img_hsv[:, :, 2] = exposure.equalize_hist(img_hsv[:, :, 2])
    
    img_rgb_eq = color.hsv2rgb(img_hsv)
    # 还原回 0-255 整数
    return (img_rgb_eq * 255).clip(0, 255).astype(np.uint8)

def main():
    # 1. 寻找图片
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.bmp']
    image_files = []
    
    if os.path.exists(IMG_DIR):
        for ext in extensions:
            image_files.extend(glob.glob(os.path.join(IMG_DIR, ext)))
    
    if not image_files:
        print(f"No images found in '{IMG_DIR}'. Creating a dummy image for testing.")
        dummy = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        Image.fromarray(dummy).save("dummy_test.png")
        image_files = ["dummy_test.png"]

    print(f"Processing {len(image_files)} images with Standard Histogram Equalization...\n")
    
    # --- 修改点：增加了 Orig Power 和 New Power 列 ---
    header = f"{'Image Name':<20} | {'Orig Power':<12} | {'New Power':<12} | {'Saving %':<10} | {'Distortion %':<12}"
    print(header)
    print("-" * len(header))

    savings = []
    dists = []

    # 2. 循环处理
    for img_path in image_files:
        try:
            filename = os.path.basename(img_path)
            
            # 读取图片
            pil_img = Image.open(img_path).convert('RGB')
            img_arr = np.array(pil_img)
            
            # 原始功耗
            p_orig = estimate_power(img_arr)
            
            # 应用 HE
            img_mod = apply_histogram_equalization(img_arr)
            
            # 新功耗
            p_new = estimate_power(img_mod)
            
            # 计算指标
            s = (p_orig - p_new) / p_orig * 100
            d = compute_distortion(img_arr, img_mod)
            
            savings.append(s)
            dists.append(d)
            
            # --- 修改点：打印具体的功耗数值 ---
            print(f"{filename[:18]:<20} | {p_orig:<12.4f} | {p_new:<12.4f} | {s:6.2f}%    | {d:6.2f}%")

        except Exception as e:
            print(f"Error on {os.path.basename(img_path)}: {e}")

    # 3. 统计结果 (Summary Table)
    if len(savings) > 0:
        avg_save = np.mean(savings)
        avg_dist = np.mean(dists)
        
        print("\n" + "=" * 60)
        print("SUMMARY TABLE (Average, Min, Max)")
        print("=" * 60)
        print(f"{'Metric':<15} | {'Average':<10} | {'Min':<10} | {'Max':<10}")
        print("-" * 60)
        print(f"{'Power Saving':<15} | {avg_save:9.2f}% | {np.min(savings):9.2f}% | {np.max(savings):9.2f}%")
        print(f"{'Distortion':<15} | {avg_dist:9.2f}% | {np.min(dists):9.2f}% | {np.max(dists):9.2f}%")

        # 4. 绘制散点图
        plt.figure(figsize=(8, 6))
        
        # 每一张图片的点
        plt.scatter(dists, savings, alpha=0.6, color='blue', label='Individual Images')
        
        # 平均值点 (红星)
        plt.scatter(avg_dist, avg_save, color='red', s=150, marker='*', label='Average')
        
        plt.title("Standard Histogram Equalization: Performance Distribution")
        plt.xlabel("Distortion (%)")
        plt.ylabel("Power Saving (%)")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.show()
        print("\nPlot generated.")

if __name__ == "__main__":
    main()
