import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def generate_animated_hero():
    repo_dir = r'C:\Users\Puzzz\.gemini\antigravity\scratch\Dopevibe-profile'
    assets_dir = os.path.join(repo_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # 1. Clean the master image
    src_path = r'C:\Users\Puzzz\.gemini\antigravity\brain\a652c583-ed1f-4213-966a-c7803255cc3e\.user_uploaded\media_1791409275162.png'
    raw_img = Image.open(src_path).convert('RGB')
    w, h = raw_img.size
    arr = np.array(raw_img).astype(np.float32)
    
    clean_arr = arr.copy()
    
    # Seamless inpaint of the lower decorative lines & trident
    # Line 1: y=258 to 276
    for y in range(258, 276):
        alpha = (y - 254) / (280 - 254)
        for x in range(320, 704):
            clean_arr[y, x] = (1 - alpha) * arr[254, x] + alpha * arr[280, x]
            
    # Arrows: y=295 to 312
    for y in range(295, 312):
        alpha = (y - 293) / (314 - 293)
        for x in list(range(260, 315)) + list(range(705, 760)):
            clean_arr[y, x] = (1 - alpha) * arr[293, x] + alpha * arr[314, x]
            
    # Bottom line & trident: y=326 to 346
    for y in range(326, 346):
        alpha = (y - 323) / (348 - 323)
        for x in range(350, 674):
            clean_arr[y, x] = (1 - alpha) * arr[323, x] + alpha * arr[348, x]
            
    clean_base = Image.fromarray(np.clip(clean_arr, 0, 255).astype(np.uint8))
    
    # Resize to standard hero width for crisp markdown display (e.g. 900x360)
    target_w = 900
    target_h = int(target_w * (h / w))
    clean_base = clean_base.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Extract metal chrome mask (where brightness is high and saturation is lower)
    base_np = np.array(clean_base).astype(np.float32)
    r_ch = base_np[:, :, 0]
    g_ch = base_np[:, :, 1]
    b_ch = base_np[:, :, 2]
    
    # Luminance & Saturation
    lum = 0.299 * r_ch + 0.587 * g_ch + 0.114 * b_ch
    max_c = np.maximum(np.maximum(r_ch, g_ch), b_ch)
    min_c = np.minimum(np.minimum(r_ch, g_ch), b_ch)
    sat = (max_c - min_c) / (max_c + 1e-5)
    
    # Metal highlights mask: high luminance, DOPE region (y roughly 60 to 260)
    metal_mask = np.zeros((target_h, target_w), dtype=np.float32)
    y_min, y_max = int(target_h * 0.15), int(target_h * 0.68)
    x_min, x_max = int(target_w * 0.20), int(target_w * 0.80)
    
    # High luminance pixels inside DOPE bounding box
    metal_mask[y_min:y_max, x_min:x_max] = np.clip((lum[y_min:y_max, x_min:x_max] - 80) / 120.0, 0, 1)
    # Exclude heavily saturated red areas
    metal_mask = metal_mask * np.clip((0.6 - sat), 0, 1) / 0.6
    
    # Crimson Fire Glow mask: high red, high saturation
    crimson_mask = np.clip((r_ch - np.maximum(g_ch, b_ch) * 1.6) / 80.0, 0, 1)
    
    # 2. Setup Ember Particles
    np.random.seed(777)
    random.seed(777)
    particle_count = 50
    particles = []
    for _ in range(particle_count):
        particles.append({
            'x_base': random.uniform(40, target_w - 40),
            'y_base': random.uniform(30, target_h - 20),
            'speed_y': random.uniform(0.9, 2.2),
            'drift_x': random.uniform(10, 28),
            'drift_freq': random.uniform(0.8, 1.8),
            'size': random.uniform(0.9, 2.2),
            'alpha_base': random.uniform(0.4, 0.95),
            'color': random.choice([
                (255, 30, 66),
                (255, 75, 95),
                (255, 130, 150),
                (255, 200, 210),
                (255, 240, 245)
            ])
        })
        
    num_frames = 36
    frames = []
    
    print(f"Generating {num_frames} animation frames...")
    for f in range(num_frames):
        t = f / float(num_frames)
        # Smooth pulse
        pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        pulse_fast = 0.5 + 0.5 * math.sin(t * 4 * math.pi)
        
        frame_np = base_np.copy()
        
        # 1. Crimson Breathing Glow
        # Modulate the red channels on fiery wings and ground reflections
        glow_boost = 1.0 + 0.22 * pulse
        frame_np[:, :, 0] = np.clip(frame_np[:, :, 0] + crimson_mask * 35 * pulse, 0, 255)
        frame_np[:, :, 1] = np.clip(frame_np[:, :, 1] + crimson_mask * 8 * pulse, 0, 255)
        
        # 2. Metallic Light Sweep across DOPE Letters
        # Sheen moves from x_min - 100 to x_max + 100
        sheen_x = (x_min - 80) + (x_max - x_min + 160) * t
        sheen_width = 120.0
        
        # Create X grid
        x_indices = np.arange(target_w, dtype=np.float32)
        # Angled sheen slant (dx = -0.35 * dy)
        y_indices = np.arange(target_h, dtype=np.float32)
        X, Y = np.meshgrid(x_indices, y_indices)
        
        dist = np.abs((X + (Y - target_h*0.4) * 0.35) - sheen_x)
        sheen_factor = np.clip(1.0 - (dist / (sheen_width / 2.0)), 0, 1)
        sheen_factor = np.power(sheen_factor, 2.5) * metal_mask
        
        # Apply sheen (pure bright silver-white with subtle crimson edge)
        frame_np[:, :, 0] = np.clip(frame_np[:, :, 0] + sheen_factor * 220, 0, 255)
        frame_np[:, :, 1] = np.clip(frame_np[:, :, 1] + sheen_factor * 190, 0, 255)
        frame_np[:, :, 2] = np.clip(frame_np[:, :, 2] + sheen_factor * 210, 0, 255)
        
        frame_img = Image.fromarray(frame_np.astype(np.uint8)).convert('RGBA')
        draw = ImageDraw.Draw(frame_img)
        
        # 3. Render Floating Embers
        for p in particles:
            y_pos = (p['y_base'] - (t * num_frames * p['speed_y'])) % (target_h - 20) + 10
            x_pos = p['x_base'] + math.sin(t * 2 * math.pi * p['drift_freq'] + p['y_base']) * p['drift_x']
            alpha = p['alpha_base'] * (0.6 + 0.4 * math.sin(t * 2 * math.pi * 2 + p['x_base']))
            c = p['color']
            ember_rgba = (c[0], c[1], c[2], int(alpha * 255))
            r_sz = p['size']
            
            draw.ellipse([x_pos - r_sz, y_pos - r_sz, x_pos + r_sz, y_pos + r_sz], fill=ember_rgba)
            if r_sz > 1.4:
                # Add sparkle glint cross
                glint_len = r_sz * 1.8
                draw.line([(x_pos - glint_len, y_pos), (x_pos + glint_len, y_pos)], fill=(255, 255, 255, int(alpha * 180)), width=1)
                draw.line([(x_pos, y_pos - glint_len), (x_pos, y_pos + glint_len)], fill=(255, 255, 255, int(alpha * 180)), width=1)
                
        # 4. Refined subtle border & glowing corner accents
        draw.rectangle([4, 4, target_w - 5, target_h - 5], outline=(28, 30, 40, 180), width=1)
        corner_c = (255, 30, 66, int(180 + 75 * pulse))
        c_len = 28
        draw.line([(4, 4), (4 + c_len, 4)], fill=corner_c, width=2)
        draw.line([(4, 4), (4, 4 + c_len)], fill=corner_c, width=2)
        draw.line([(target_w - 5, 4), (target_w - 5 - c_len, 4)], fill=corner_c, width=2)
        draw.line([(target_w - 5, 4), (target_w - 5, 4 + c_len)], fill=corner_c, width=2)
        draw.line([(4, target_h - 5), (4 + c_len, target_h - 5)], fill=corner_c, width=2)
        draw.line([(4, target_h - 5), (4, target_h - 5 - c_len)], fill=corner_c, width=2)
        draw.line([(target_w - 5, target_h - 5), (target_w - 5 - c_len, target_h - 5)], fill=corner_c, width=2)
        draw.line([(target_w - 5, target_h - 5), (target_w - 5, target_h - 5 - c_len)], fill=corner_c, width=2)
        
        # Quantize for optimal GIF compression & fidelity
        quantized = frame_img.convert('RGB').quantize(colors=128, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        frames.append(quantized)
        
    hero_out = os.path.join(assets_dir, 'dope-hero.gif')
    frames[0].save(
        hero_out,
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0,
        optimize=True
    )
    print(f"New dope-hero.gif saved ({os.path.getsize(hero_out) / 1024.0:.1f} KB)")

if __name__ == '__main__':
    generate_animated_hero()
