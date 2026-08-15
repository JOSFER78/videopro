"""
SOTA Karaoke & Dynamic Kinetic Subtitle Generator for VideoPro
Supports Vox/Johnny Harris (1-2 words per line, hard drop-shadow), TikTok Pop, and Onirópolis Steampunk styles.
"""
import os
import re
from loguru import logger

class KaraokeSubtitleStyle:
    VOX_HARRIS = "vox_harris"        # 1-2 words, UPPERCASE, yellow highlight, hard dropshadow
    TIKTOK_POP = "tiktok_pop"        # 1 word jump, neon green pop, dynamic scale
    DOCUMENTARY = "documentary"      # 3-5 words clean with highlighter sweep
    STEAMPUNK = "steampunk"          # Amber gold, vintage serif / gothic shadow

def generate_dynamic_ass_subtitles(
    segments: list,
    output_ass_path: str,
    style: str = KaraokeSubtitleStyle.VOX_HARRIS,
    video_width: int = 1080,
    video_height: int = 1920
) -> str:
    """
    Generates an Advanced SubStation Alpha (.ass) subtitle file formatted for maximum viewer retention.
    """
    os.makedirs(os.path.dirname(output_ass_path), exist_ok=True)
    
    # ASS Colors are in &HAABBGGRR format (Hex)
    if style == KaraokeSubtitleStyle.VOX_HARRIS:
        font_name = "Arial Black"
        font_size = 72 if video_height > 1080 else 44
        primary_color = "&H00FFFFFF"       # White text
        secondary_color = "&H0024C9FF"     # Vox Yellow highlight (#FFC924 -> BGR: 24, C9, FF)
        outline_color = "&H00000000"       # Black outline
        back_color = "&H00000000"          # Hard drop shadow
        outline = 3
        shadow = 4
        bold = 1
        alignment = 2                      # Bottom Center
        margin_v = 180 if video_height > 1080 else 80
    elif style == KaraokeSubtitleStyle.TIKTOK_POP:
        font_name = "Arial Black"
        font_size = 78 if video_height > 1080 else 48
        primary_color = "&H00FFFFFF"
        secondary_color = "&H009DFF00"     # Neon Green (#00FF9D -> BGR: 9D, FF, 00)
        outline_color = "&H00000000"
        back_color = "&H00000000"
        outline = 4
        shadow = 4
        bold = 1
        alignment = 2
        margin_v = 220 if video_height > 1080 else 100
    elif style == KaraokeSubtitleStyle.STEAMPUNK:
        font_name = "Georgia"
        font_size = 64 if video_height > 1080 else 38
        primary_color = "&H00D4E6F1"       # Sepia ivory
        secondary_color = "&H002580B8"     # Amber bronze (#B88025 -> BGR: 25, 80, B8)
        outline_color = "&H000B1726"       # Dark rust
        back_color = "&H00000000"
        outline = 2
        shadow = 3
        bold = 1
        alignment = 2
        margin_v = 160 if video_height > 1080 else 70
    else: # Documentary clean
        font_name = "Helvetica"
        font_size = 56 if video_height > 1080 else 34
        primary_color = "&H00F5F5F7"
        secondary_color = "&H0000D0FF"     # Gold highlight
        outline_color = "&H00000000"
        back_color = "&H60000000"
        outline = 2
        shadow = 2
        bold = 1
        alignment = 2
        margin_v = 140 if video_height > 1080 else 60

    ass_header = f"""[Script Info]
Title: VideoPro Dynamic Karaoke Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: {video_width}
PlayResY: {video_height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},{secondary_color},{outline_color},{back_color},{bold},0,0,0,100,100,0,0,1,{outline},{shadow},{alignment},40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def format_ass_time(sec: float) -> str:
        hours = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        centis = int(round((sec - int(sec)) * 100))
        if centis == 100:
            secs += 1
            centis = 0
        return f"{hours:01d}:{mins:02d}:{secs:02d}.{centis:02d}"

    events = []
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            # Fallback to chunking segment text into 2-word groups
            raw_text = str(seg.get("text", "")).strip().upper()
            tokens = raw_text.split()
            seg_start = float(seg.get("start", 0.0))
            seg_end = float(seg.get("end", seg_start + 2.0))
            dur = max(0.5, seg_end - seg_start)
            
            # 2 words per chunk
            chunk_size = 2 if style == KaraokeSubtitleStyle.VOX_HARRIS else 3
            chunks = [" ".join(tokens[i:i+chunk_size]) for i in range(0, len(tokens), chunk_size)]
            if not chunks:
                continue
            chunk_dur = dur / len(chunks)
            for idx, chk in enumerate(chunks):
                c_start = seg_start + idx * chunk_dur
                c_end = c_start + chunk_dur
                events.append(f"Dialogue: 0,{format_ass_time(c_start)},{format_ass_time(c_end)},Default,,0,0,0,,{{\\c{secondary_color}}}{chk}{{\\c{primary_color}}}")
        else:
            # High-precision word-level karaoke tags
            # Group into 2 words per screen for Vox style
            chunk_size = 2 if style in [KaraokeSubtitleStyle.VOX_HARRIS, KaraokeSubtitleStyle.TIKTOK_POP] else 3
            for i in range(0, len(words), chunk_size):
                w_group = words[i:i+chunk_size]
                if not w_group:
                    continue
                g_start = float(w_group[0].get("start", 0.0))
                g_end = float(w_group[-1].get("end", g_start + 1.0))
                
                # Build karaoke tag string \k<duration_in_centis>
                k_text = ""
                for w in w_group:
                    w_start = float(w.get("start", g_start))
                    w_end = float(w.get("end", w_start + 0.3))
                    w_dur_centi = max(10, int(round((w_end - w_start) * 100)))
                    word_str = str(w.get("word", "")).strip().upper()
                    k_text += f"{{\\k{w_dur_centi}}}{word_str} "
                    
                events.append(f"Dialogue: 0,{format_ass_time(g_start)},{format_ass_time(g_end)},Default,,0,0,0,,{k_text.strip()}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(events) + "\n")
        
    logger.info(f"Generated {len(events)} ASS dynamic subtitle dialogues at: {output_ass_path}")
    return output_ass_path
