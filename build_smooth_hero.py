import os
import math
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

def create_smooth_cinematic_hero():
    repo_dir = r'C:\Users\Puzzz\.gemini\antigravity\scratch\Dopevibe-profile'
    assets_dir = os.path.join(repo_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    src_path = r'C:\Users\Puzzz\.gemini\antigravity\brain\a652c583-ed1f-4213-966a-c7803255cc3e\.user_uploaded\media_1791409275162.png'
    raw_img = Image.open(src_path).convert('RGB')
    w, h = raw_img.size
    arr = np.array(raw_img).astype(np.float32)
    
    clean_arr = arr.copy()
    
    # 1. Seamless inpaint of the lower decorative lines & trident
    for y in range(258, 276):
        alpha = (y - 254) / (280 - 254)
        for x in range(320, 704):
            clean_arr[y, x] = (1 - alpha) * arr[254, x] + alpha * arr[280, x]
            
    for y in range(295, 312):
        alpha = (y - 293) / (314 - 293)
        for x in list(range(260, 315)) + list(range(705, 760)):
            clean_arr[y, x] = (1 - alpha) * arr[293, x] + alpha * arr[314, x]
            
    for y in range(326, 346):
        alpha = (y - 323) / (348 - 323)
        for x in range(350, 674):
            clean_arr[y, x] = (1 - alpha) * arr[323, x] + alpha * arr[348, x]
            
    clean_base = Image.fromarray(np.clip(clean_arr, 0, 255).astype(np.uint8))
    
    # Target resolution: 960 width (super sharp, 16:6.4 widescreen)
    target_w = 960
    target_h = int(target_w * (h / w))
    clean_base = clean_base.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    base_np = np.array(clean_base).astype(np.float32)
    r = base_np[:, :, 0]
    g = base_np[:, :, 1]
    b = base_np[:, :, 2]
    
    # Calculate luminance & color characteristics
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    max_c = np.maximum(np.maximum(r, g), b)
    min_c = np.minimum(np.minimum(r, g), b)
    sat = (max_c - min_c) / (max_c + 1e-5)
    
    # Bounding region for DOPE typography
    y_min, y_max = int(target_h * 0.18), int(target_h * 0.68)
    x_min, x_max = int(target_w * 0.22), int(target_w * 0.78)
    
    # 1. Chrome Bevel Mask (Silver metal highlights on DOPE)
    chrome_mask = np.zeros((target_h, target_w), dtype=np.float32)
    lum_dope = lum[y_min:y_max, x_min:x_max]
    sat_dope = sat[y_min:y_max, x_min:x_max]
    
    # Metal is characterized by medium-to-high luminance and low/medium saturation
    m_val = np.clip((lum_dope - 70) / 100.0, 0, 1) * np.clip((0.65 - sat_dope) / 0.65, 0, 1)
    chrome_mask[y_min:y_max, x_min:x_max] = m_val
    
    # 2. Glowing Red Core / Fiery Wings Mask
    # Pure saturated reds
    red_flare_mask = np.clip((r - np.maximum(g, b) * 1.5) / 70.0, 0, 1) * np.clip(sat / 0.7, 0, 1)
    
    # 3. Center 'O' & Crown Core Mask (focal point ignition)
    center_x, center_y = target_w * 0.50, target_h * 0.44
    Y_grid, X_grid = np.ogrid[:target_h, :target_w]
    dist_center = np.sqrt((X_grid - center_x)**2 + ((Y_grid - center_y) * 1.8)**2)
    core_radial = np.clip(1.0 - (dist_center / 180.0), 0, 1) ** 2.0
    core_mask = red_flare_mask * core_radial
    
    # Build 48 ultra-smooth animation frames (25 FPS at 40ms)
    num_frames = 48
    frames = []
    
    print(f"Synthesizing {num_frames} ultra-smooth frames...")
    
    # Meshgrid for sweeping light glint
    X_f, Y_f = np.meshgrid(np.arange(target_w, dtype=np.float32), np.arange(target_h, dtype=np.float32))
    
    for f in range(num_frames):
        t = f / float(num_frames)
        # Sinusoidal organic breathing curves
        breath_1 = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        breath_2 = 0.5 + 0.5 * math.sin(t * 4 * math.pi + math.pi / 4)
        
        frame = base_np.copy()
        
        # --- A. Organic Crimson Flame Glow & Core Pulsing ---
        # Breathing glow on demonic wings and crown
        flame_intensity = 0.15 * breath_1 + 0.10 * breath_2
        frame[:, :, 0] = np.clip(frame[:, :, 0] + red_flare_mask * (30 * flame_intensity + 5), 0, 255)
        frame[:, :, 1] = np.clip(frame[:, :, 1] + red_flare_mask * (6 * flame_intensity), 0, 255)
        
        # Intense heart pulse in the center 'O' and crown
        core_boost = 0.35 * breath_1
        frame[:, :, 0] = np.clip(frame[:, :, 0] + core_mask * (55 * core_boost), 0, 255)
        frame[:, :, 1] = np.clip(frame[:, :, 1] + core_mask * (18 * core_boost), 0, 255)
        frame[:, :, 2] = np.clip(frame[:, :, 2] + core_mask * (22 * core_boost), 0, 255)
        
        # --- B. Silky Specular Chrome Light Sweep across DOPE ---
        # Smooth travel from left border of DOPE to right border
        sheen_center_x = (x_min - 100) + (x_max - x_min + 200) * t
        sheen_slant = -0.30  # Diagonal light angle
        sheen_dist = np.abs((X_f + (Y_f - target_h * 0.42) * sheen_slant) - sheen_center_x)
        
        # Soft Gaussian profile for the specular glint
        sheen_sigma = 42.0
        sheen_val = np.exp(-0.5 * (sheen_dist / sheen_sigma) ** 2) * chrome_mask
        
        # Add primary chrome glint + subtle secondary trail
        glint_r = sheen_val * 240.0
        glint_g = sheen_val * 215.0
        glint_b = sheen_val * 230.0
        
        frame[:, :, 0] = np.clip(frame[:, :, 0] + glint_r, 0, 255)
        frame[:, :, 1] = np.clip(frame[:, :, 1] + glint_g, 0, 255)
        frame[:, :, 2] = np.clip(frame[:, :, 2] + glint_b, 0, 255)
        
        # --- C. Subtle Ground Lava Shimmer ---
        # Bottom area y > target_h * 0.75
        ground_mask = np.clip((Y_f - target_h * 0.72) / (target_h * 0.28), 0, 1) * red_flare_mask
        frame[:, :, 0] = np.clip(frame[:, :, 0] + ground_mask * (20 * breath_1), 0, 255)
        
        # Convert to PIL Image
        img_frame = Image.fromarray(frame.astype(np.uint8))
        
        # Quantize for clean, flicker-free colors
        quant = img_frame.quantize(colors=160, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quant)
        
    out_path = os.path.join(assets_dir, 'dope-banner.gif')
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=40,  # 40ms = 25 FPS silky smooth
        loop=0,
        optimize=True
    )
    print(f"Smooth banner saved to {out_path} ({os.path.getsize(out_path) / 1024.0:.1f} KB)")

if __name__ == '__main__':
    create_smooth_cinematic_hero()
