import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def generate_smooth_bio_hud():
    repo_dir = r'C:\Users\Puzzz\.gemini\antigravity\scratch\Dopevibe-profile'
    assets_dir = os.path.join(repo_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # Load white Dope image and transform for dark theme
    white_dope_path = r'C:\Users\Puzzz\.gemini\antigravity\brain\a652c583-ed1f-4213-966a-c7803255cc3e\.user_uploaded\media_1791410551299.png'
    white_img = Image.open(white_dope_path).convert('RGB')
    w, h = white_img.size
    
    # Crop central calligraphy & crown/sun
    crop_box = (int(w * 0.15), int(h * 0.02), int(w * 0.75), int(h * 0.88))
    white_crop = white_img.crop(crop_box)
    
    # Dark blend: Invert calligraphy to metallic silver/white while preserving red crown & sun
    arr = np.array(white_crop).astype(np.float32)
    r_c, g_c, b_c = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    lum = (0.299*r_c + 0.587*g_c + 0.114*b_c) / 255.0
    
    is_red = (r_c > g_c * 1.35) & (r_c > b_c * 1.35) & (r_c > 80)
    
    new_r = np.where(is_red, r_c * 1.1, np.where(lum > 0.82, 10.0, (1.0 - lum) * 235.0 + 10.0))
    new_g = np.where(is_red, g_c * 0.9, np.where(lum > 0.82, 11.0, (1.0 - lum) * 215.0 + 11.0))
    new_b = np.where(is_red, b_c * 0.9, np.where(lum > 0.82, 16.0, (1.0 - lum) * 225.0 + 16.0))
    
    dark_emblem_np = np.stack([new_r, new_g, new_b], axis=-1)
    dark_emblem = Image.fromarray(np.clip(dark_emblem_np, 0, 255).astype(np.uint8))
    
    # Fit inside avatar box (size 135x135)
    av_box_size = 135
    target_w = 127
    target_h = int(target_w * (dark_emblem.height / dark_emblem.width))
    if target_h > 127:
        target_h = 127
        target_w = int(target_h * (dark_emblem.width / dark_emblem.height))
        
    emblem_resized = dark_emblem.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    bio_w = 900
    bio_h = 210  # Compact, perfectly proportioned height
    num_frames = 36
    bio_frames = []
    
    try:
        f_mono_bold = ImageFont.truetype(r'C:\Windows\Fonts\consolab.ttf', 11)
        f_mono = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 11)
        f_header = ImageFont.truetype(r'C:\Windows\Fonts\consolab.ttf', 16)
    except Exception:
        f_mono_bold = ImageFont.load_default()
        f_mono = f_mono_bold
        f_header = f_mono_bold
        
    print("Synthesizing Bio HUD with ABOUT ME and custom field specs...")
    for f in range(num_frames):
        t = f / float(num_frames)
        pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
        
        bframe = Image.new('RGBA', (bio_w, bio_h), (9, 9, 13, 255))
        bdraw = ImageDraw.Draw(bframe)
        
        # Subtle dark gothic HUD grid
        for gx in range(20, bio_w - 20, 40):
            bdraw.line([(gx, 10), (gx, bio_h - 10)], fill=(16, 17, 24, 255), width=1)
        for gy in range(20, bio_h - 10, 40):
            bdraw.line([(10, gy), (bio_w - 10, gy)], fill=(16, 17, 24, 255), width=1)
            
        # Top Scanning Laser Beam
        scan_y = int(12 + (bio_h - 24) * t)
        for sx in range(bio_w - 20):
            prog = sx / float(bio_w - 20)
            int_scan = math.sin(prog * math.pi) ** 1.5
            bdraw.point((10 + sx, scan_y), fill=(255, 30, 66, int(130 * int_scan)))
            if scan_y + 1 < bio_h - 10:
                bdraw.point((10 + sx, scan_y + 1), fill=(255, 80, 100, int(50 * int_scan)))
                
        # Outer Card Border & Corners
        bdraw.rectangle([6, 6, bio_w - 7, bio_h - 7], outline=(28, 30, 40, 255), width=1)
        bdraw.rectangle([10, 10, bio_w - 11, bio_h - 11], outline=(42, 45, 58, 255), width=1)
        
        # Glowing crimson corner brackets
        corner_c = (255, 30, 66, int(190 + 65 * pulse))
        bdraw.line([(10, 10), (10 + 20, 10)], fill=corner_c, width=2)
        bdraw.line([(10, 10), (10, 10 + 20)], fill=corner_c, width=2)
        bdraw.line([(bio_w - 11, 10), (bio_w - 11 - 20, 10)], fill=corner_c, width=2)
        bdraw.line([(bio_w - 11, 10), (bio_w - 11, 10 + 20)], fill=corner_c, width=2)
        bdraw.line([(10, bio_h - 11), (10 + 20, bio_h - 11)], fill=corner_c, width=2)
        bdraw.line([(10, bio_h - 11), (10, bio_h - 11 - 20)], fill=corner_c, width=2)
        bdraw.line([(bio_w - 11, bio_h - 11), (bio_w - 11 - 20, bio_h - 11)], fill=corner_c, width=2)
        bdraw.line([(bio_w - 11, bio_h - 11), (bio_w - 11, bio_h - 11 - 20)], fill=corner_c, width=2)
        
        # Avatar Frame
        av_box_x = 24
        av_box_y = 18
        bdraw.rectangle([av_box_x, av_box_y, av_box_x + av_box_size, av_box_y + av_box_size], outline=(48, 52, 68, 255), fill=(10, 11, 16, 255), width=1)
        bdraw.rectangle([av_box_x + 3, av_box_y + 3, av_box_x + av_box_size - 3, av_box_y + av_box_size - 3], outline=(255, 30, 66, int(100 + 60 * pulse)), width=1)
        
        # Paste Calligraphy Emblem
        epx = av_box_x + (av_box_size - target_w) // 2
        epy = av_box_y + (av_box_size - target_h) // 2
        bframe.paste(emblem_resized, (epx, epy))
        
        # Tag below avatar: DEVELOPER
        tag_y = av_box_y + av_box_size + 10
        bdraw.rectangle([av_box_x, tag_y, av_box_x + av_box_size, tag_y + 22], fill=(220, 38, 38, 35), outline=(255, 30, 66, 160))
        tag_str = "DEVELOPER"
        tag_tx = av_box_x + (av_box_size - draw_text_width(bdraw, tag_str, f_mono_bold)) // 2
        bdraw.text((tag_tx, tag_y + 5), tag_str, fill=(255, 230, 235, 255), font=f_mono_bold)
        
        # Right Side: Terminal Data
        rx = 185
        ry = 22
        
        # Header Bar: ABOUT ME
        bdraw.text((rx, ry), "ABOUT ME", fill=(255, 30, 66, 255), font=f_header)
        bdraw.line([(rx, ry + 24), (bio_w - 24, ry + 24)], fill=(40, 44, 56, 255), width=1)
        
        fields = [
            ("WORK", "Web Developer", (220, 225, 235)),
            ("SKILLS", "Frontend · Backend · Security", (255, 230, 235)),
            ("AI", "AI · Automation", (200, 210, 225)),
            ("FOCUS", "Build. Learn. Improve.", (255, 75, 95))
        ]
        
        fy = ry + 36
        for label, val, val_col in fields:
            bdraw.text((rx, fy), f"[{label}]", fill=(160, 165, 180, 240), font=f_mono_bold)
            bdraw.text((rx + 110, fy), val, fill=val_col, font=f_mono)
            fy += 28
            
        bquant = bframe.convert('RGB').quantize(colors=160, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        bio_frames.append(bquant)
        
    out_path = os.path.join(assets_dir, 'dope-bio-v7.gif')
    bio_frames[0].save(out_path, save_all=True, append_images=bio_frames[1:], duration=55, loop=0, optimize=True)
    print(f"Updated Bio HUD saved to {out_path} ({os.path.getsize(out_path) / 1024.0:.1f} KB)")

def draw_text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

if __name__ == '__main__':
    generate_smooth_bio_hud()
