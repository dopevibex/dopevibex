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
    
    # Dark blend: Invert calligraphy to metallic silver/white while preserving red crown & sun, matching dark theme background (10, 11, 16)
    arr = np.array(white_crop).astype(np.float32)
    r_c, g_c, b_c = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    lum = (0.299*r_c + 0.587*g_c + 0.114*b_c) / 255.0
    
    # Red detection
    is_red = (r_c > g_c * 1.35) & (r_c > b_c * 1.35) & (r_c > 80)
    
    # Construct seamless dark artwork
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
    bio_h = 240
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
        
    print("Synthesizing Bio HUD with seamlessly integrated dark Dope calligraphy avatar...")
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
        av_box_y = 24
        bdraw.rectangle([av_box_x, av_box_y, av_box_x + av_box_size, av_box_y + av_box_size], outline=(48, 52, 68, 255), fill=(10, 11, 16, 255), width=1)
        bdraw.rectangle([av_box_x + 3, av_box_y + 3, av_box_x + av_box_size - 3, av_box_y + av_box_size - 3], outline=(255, 30, 66, int(100 + 60 * pulse)), width=1)
        
        # Paste Dark-Blended Calligraphy Emblem inside Avatar Box
        epx = av_box_x + (av_box_size - target_w) // 2
        epy = av_box_y + (av_box_size - target_h) // 2
        bframe.paste(emblem_resized, (epx, epy))
        
        # Tag below avatar
        tag_y = av_box_y + av_box_size + 14
        bdraw.rectangle([av_box_x, tag_y, av_box_x + av_box_size, tag_y + 22], fill=(220, 38, 38, 35), outline=(255, 30, 66, 160))
        bdraw.text((av_box_x + 14, tag_y + 5), "SOVEREIGN // APEX", fill=(255, 230, 235, 255), font=f_mono_bold)
        
        # Right Side: Terminal Data
        rx = 185
        ry = 26
        
        # Top Header Bar (Removed [STATUS: ACTIVE TELEMETRY])
        bdraw.text((rx, ry), "OPERATOR IDENTITY // DOPE", fill=(255, 30, 66, 255), font=f_header)
        
        bdraw.line([(rx, ry + 24), (bio_w - 24, ry + 24)], fill=(40, 44, 56, 255), width=1)
        
        fields = [
            ("DISCIPLINE", "Full-Stack Web Engineering · Modern Web Apps · Scalable APIs", (220, 225, 235)),
            ("PRIMARY ARSENAL", "Next.js · React · Node.js · PHP 8 · TypeScript · MySQL", (255, 230, 235)),
            ("DEFENSIVE SHIELD", "Network Traffic Analysis · SOC Telemetry · System Hardening", (200, 210, 225)),
            ("AI CAPABILITIES", "Agentic Systems · Model Context Protocol (MCP) · Automated Workflows", (210, 215, 225)),
            ("CORE DIRECTIVE", "Engineered for speed, built for resilience, hardened against intrusion", (255, 75, 95))
        ]
        
        fy = ry + 34
        for label, val, val_col in fields:
            bdraw.text((rx, fy), f"[{label}]", fill=(160, 165, 180, 240), font=f_mono_bold)
            bdraw.text((rx + 160, fy), val, fill=val_col, font=f_mono)
            fy += 26
            
        my = fy + 6
        bdraw.line([(rx, my), (bio_w - 24, my)], fill=(32, 35, 45, 255), width=1)
        my += 10
        
        # Bottom Metrics Row (Removed CODE INTEGRITY: 100%)
        metrics = [
            ("DEFENSIVE STATUS", "INVIOLABLE", (255, 30, 66)),
            ("RUNTIME STATUS", "OPTIMAL", (255, 75, 95)),
            ("SECURITY TRACE", "0-TRACE", (220, 225, 235))
        ]
        mx = rx
        for m_name, m_val, m_col in metrics:
            bdraw.text((mx, my), f"{m_name}:", fill=(130, 135, 150, 240), font=f_mono)
            val_offset = int(bdraw.textlength(f"{m_name}: ", font=f_mono))
            bdraw.text((mx + val_offset, my), m_val, fill=m_col, font=f_mono_bold)
            mx += 225
            
        bquant = bframe.convert('RGB').quantize(colors=160, method=Image.Resampling.LANCZOS, dither=Image.Dither.FLOYDSTEINBERG)
        bio_frames.append(bquant)
        
    out_path = os.path.join(assets_dir, 'dope-bio-v5.gif')
    bio_frames[0].save(out_path, save_all=True, append_images=bio_frames[1:], duration=55, loop=0, optimize=True)
    print(f"Refined Bio HUD saved to {out_path} ({os.path.getsize(out_path) / 1024.0:.1f} KB)")

if __name__ == '__main__':
    generate_smooth_bio_hud()
