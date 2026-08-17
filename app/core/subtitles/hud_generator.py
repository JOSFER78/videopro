"""
HUD Telemetry & Diegetic Temporal Badge Generator (VideoPro Modern Suite)
========================================================================
Generates ultra-modern telemetry overlays, diegetic temporal badges,
6-DoF targeting reticles, and glassmorphism lower-thirds.
Supports 4K UHD (3840x2160) and 1080p (1920x1080) in PNG/SVG and Remotion TSX.
"""

import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class ModernHUDGenerator:
    """
    Renders high-impact cinematic HUD overlays, diegetic temporal badges, and telemetry.
    """

    def __init__(
        self,
        resolution: str = "4k",
        primary_cyan: str = "#00E5FF",
        accent_gold: str = "#FFD700",
        accent_purple: str = "#B388FF",
        dark_glass_rgba: Tuple[int, int, int, int] = (7, 9, 14, 210)
    ):
        self.resolution = resolution.lower()
        self.primary_cyan = primary_cyan
        self.accent_gold = accent_gold
        self.accent_purple = accent_purple
        self.dark_glass_rgba = dark_glass_rgba

        if self.resolution == "4k":
            self.width = 3840
            self.height = 2160
            self.padding = 96
            self.font_scale = 2.0
            self.line_width = 3
        else:
            self.width = 1920
            self.height = 1080
            self.padding = 48
            self.font_scale = 1.0
            self.line_width = 2

        self._load_fonts()

    def _load_fonts(self):
        """Load robust system fonts with graceful fallback."""
        base_size_title = int(24 * self.font_scale)
        base_size_body = int(18 * self.font_scale)
        base_size_small = int(14 * self.font_scale)
        base_size_huge = int(36 * self.font_scale)

        font_paths = [
            "/usr/share/fonts/opentype/league-spartan/LeagueSpartan-Bold.otf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        mono_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        ]

        def get_font(paths, size):
            for p in paths:
                if Path(p).exists():
                    try:
                        return ImageFont.truetype(p, size)
                    except Exception:
                        pass
            return ImageFont.load_default()

        self.font_huge = get_font(font_paths, base_size_huge)
        self.font_title = get_font(font_paths, base_size_title)
        self.font_body = get_font(mono_paths, base_size_body)
        self.font_small = get_font(mono_paths, base_size_small)

    def generate_shot_hud_image(
        self,
        shot_data: Dict[str, Any],
        total_shots: int = 24,
        output_path: Optional[Path] = None
    ) -> Image.Image:
        """
        Generates a transparent 4K/1080p RGBA overlay with:
        1. Top-Left: Diegetic Temporal Badge & Location
        2. Top-Right: Telemetry & SMPTE Timecode & Audio Standards
        3. Bottom-Left: Lower Third with Glowing Border & Scientific Lower-Third
        4. Bottom-Right: Shot Progress & Quantum Coherence Matrix
        5. Center: Minimalist 6-DoF Tactical Reticle Brackets
        """
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        shot_idx = shot_data.get("shot_index", 1)
        shot_id = shot_data.get("shot_id", f"SHOT_{shot_idx:02d}")
        time_win = shot_data.get("time_window", "00:00 - 00:05")
        act = shot_data.get("act", "Acto I: La Grieta en la Realidad")
        hud_info = shot_data.get("hud_overlay_telemetry", {})
        
        location = hud_info.get("location", "Quantum Subterranean Facility")
        telemetry = hud_info.get("telemetry", "TEMP: 10.2 mK | COHERENCE: 99.98% | LATENCY: 0.12ms")
        lower_third_text = hud_info.get("lower_third", "SISTEMA CUÁNTICO COHERENTE DE SILICIO")
        timestamp_code = hud_info.get("timestamp_code", f"00:00:{(shot_idx-1)*5:02d}:00")

        # -------------------------------------------------------------
        # 1. TOP-LEFT: Diegetic Temporal Badge
        # -------------------------------------------------------------
        tl_x, tl_y = self.padding, self.padding
        badge_w, badge_h = int(620 * self.font_scale / 1.5), int(130 * self.font_scale / 1.5)

        # Glass background
        draw.rounded_rectangle(
            [tl_x, tl_y, tl_x + badge_w, tl_y + badge_h],
            radius=int(8 * self.font_scale),
            fill=self.dark_glass_rgba,
            outline=(255, 255, 255, 30),
            width=self.line_width
        )
        # Gold accent bar
        draw.rectangle(
            [tl_x, tl_y, tl_x + int(6 * self.font_scale), tl_y + badge_h],
            fill=(255, 215, 0, 255)
        )
        # Content
        draw.text(
            (tl_x + int(20 * self.font_scale), tl_y + int(14 * self.font_scale)),
            f"● {act.upper()}",
            font=self.font_small,
            fill=(255, 215, 0, 230)
        )
        draw.text(
            (tl_x + int(20 * self.font_scale), tl_y + int(36 * self.font_scale)),
            f"{location}",
            font=self.font_title,
            fill=(255, 255, 255, 255)
        )
        draw.text(
            (tl_x + int(20 * self.font_scale), tl_y + int(62 * self.font_scale)),
            f"WINDOW: {time_win} | CODE: {shot_id}",
            font=self.font_small,
            fill=(0, 229, 255, 220)
        )

        # -------------------------------------------------------------
        # 2. TOP-RIGHT: Telemetry & Timecode
        # -------------------------------------------------------------
        tr_w, tr_h = int(580 * self.font_scale / 1.5), int(130 * self.font_scale / 1.5)
        tr_x = self.width - self.padding - tr_w
        tr_y = self.padding

        draw.rounded_rectangle(
            [tr_x, tr_y, tr_x + tr_w, tr_y + tr_h],
            radius=int(8 * self.font_scale),
            fill=self.dark_glass_rgba,
            outline=(255, 255, 255, 30),
            width=self.line_width
        )
        # Cyan accent bar
        draw.rectangle(
            [tr_x + tr_w - int(6 * self.font_scale), tr_y, tr_x + tr_w, tr_y + tr_h],
            fill=(0, 229, 255, 255)
        )
        draw.text(
            (tr_x + int(20 * self.font_scale), tr_y + int(14 * self.font_scale)),
            "AUDIO EBU R128 (-14 LUFS) // DUCKING -18dB",
            font=self.font_small,
            fill=(179, 136, 255, 230)
        )
        draw.text(
            (tr_x + int(20 * self.font_scale), tr_y + int(36 * self.font_scale)),
            f"TC: {timestamp_code}",
            font=self.font_title,
            fill=(255, 255, 255, 255)
        )
        draw.text(
            (tr_x + int(20 * self.font_scale), tr_y + int(62 * self.font_scale)),
            "KODAK VISION3 500T // 4K 60FPS CINEMA",
            font=self.font_small,
            fill=(0, 229, 255, 220)
        )

        # -------------------------------------------------------------
        # 3. BOTTOM-LEFT: Lower-Third Scientific Metadata
        # -------------------------------------------------------------
        bl_x = self.padding
        bl_w = int(760 * self.font_scale / 1.5)
        bl_h = int(140 * self.font_scale / 1.5)
        bl_y = self.height - self.padding - bl_h

        draw.rounded_rectangle(
            [bl_x, bl_y, bl_x + bl_w, bl_y + bl_h],
            radius=int(8 * self.font_scale),
            fill=self.dark_glass_rgba,
            outline=(0, 229, 255, 80),
            width=self.line_width
        )
        # Left Purple Accent
        draw.rectangle(
            [bl_x, bl_y, bl_x + int(6 * self.font_scale), bl_y + bl_h],
            fill=(179, 136, 255, 255)
        )
        draw.text(
            (bl_x + int(20 * self.font_scale), bl_y + int(14 * self.font_scale)),
            f"INFRAESTRUCTURA & CIENCIA // {lower_third_text}",
            font=self.font_title,
            fill=(255, 215, 0, 255)
        )
        draw.text(
            (bl_x + int(20 * self.font_scale), bl_y + int(42 * self.font_scale)),
            f"TELEMETRÍA: {telemetry}",
            font=self.font_small,
            fill=(255, 255, 255, 210)
        )
        draw.text(
            (bl_x + int(20 * self.font_scale), bl_y + int(66 * self.font_scale)),
            "CANONICAL DOP 7-LAYER // DETERMINISTIC LEVENSHTEIN ALIGNED",
            font=self.font_small,
            fill=(0, 229, 255, 200)
        )

        # -------------------------------------------------------------
        # 4. BOTTOM-RIGHT: Progress & Quantum Index
        # -------------------------------------------------------------
        br_w = int(480 * self.font_scale / 1.5)
        br_h = int(140 * self.font_scale / 1.5)
        br_x = self.width - self.padding - br_w
        br_y = self.height - self.padding - br_h

        draw.rounded_rectangle(
            [br_x, br_y, br_x + br_w, br_y + br_h],
            radius=int(8 * self.font_scale),
            fill=self.dark_glass_rgba,
            outline=(255, 255, 255, 30),
            width=self.line_width
        )
        draw.text(
            (br_x + int(20 * self.font_scale), br_y + int(14 * self.font_scale)),
            "SECUENCIA DE TOMA",
            font=self.font_small,
            fill=(0, 229, 255, 220)
        )
        draw.text(
            (br_x + int(20 * self.font_scale), br_y + int(36 * self.font_scale)),
            f"SHOT [{shot_idx:02d}/{total_shots:02d}]",
            font=self.font_huge,
            fill=(255, 255, 255, 255)
        )
        # Visual Progress Bar
        bar_x = br_x + int(20 * self.font_scale)
        bar_y = br_y + int(76 * self.font_scale)
        bar_w = br_w - int(40 * self.font_scale)
        bar_h = int(8 * self.font_scale)

        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=(40, 50, 65, 200))
        prog_w = int(bar_w * (shot_idx / total_shots))
        draw.rectangle([bar_x, bar_y, bar_x + prog_w, bar_y + bar_h], fill=(255, 215, 0, 255))

        # -------------------------------------------------------------
        # 5. CENTER: 6-DoF Tactical Reticle Brackets
        # -------------------------------------------------------------
        cx, cy = self.width // 2, self.height // 2
        reticle_r = int(120 * self.font_scale / 1.5)
        bracket_len = int(30 * self.font_scale / 1.5)
        ret_color = (0, 229, 255, 110)

        # Top-Left Bracket
        draw.line([cx - reticle_r, cy - reticle_r, cx - reticle_r + bracket_len, cy - reticle_r], fill=ret_color, width=self.line_width)
        draw.line([cx - reticle_r, cy - reticle_r, cx - reticle_r, cy - reticle_r + bracket_len], fill=ret_color, width=self.line_width)
        # Top-Right Bracket
        draw.line([cx + reticle_r, cy - reticle_r, cx + reticle_r - bracket_len, cy - reticle_r], fill=ret_color, width=self.line_width)
        draw.line([cx + reticle_r, cy - reticle_r, cx + reticle_r, cy - reticle_r + bracket_len], fill=ret_color, width=self.line_width)
        # Bottom-Left Bracket
        draw.line([cx - reticle_r, cy + reticle_r, cx - reticle_r + bracket_len, cy + reticle_r], fill=ret_color, width=self.line_width)
        draw.line([cx - reticle_r, cy + reticle_r, cx - reticle_r, cy + reticle_r - bracket_len], fill=ret_color, width=self.line_width)
        # Bottom-Right Bracket
        draw.line([cx + reticle_r, cy + reticle_r, cx + reticle_r - bracket_len, cy + reticle_r], fill=ret_color, width=self.line_width)
        draw.line([cx + reticle_r, cy + reticle_r, cx + reticle_r, cy + reticle_r - bracket_len], fill=ret_color, width=self.line_width)
        # Center Target Dot
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 215, 0, 200))

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "PNG")

        return img

    def generate_all_shots_overlays(
        self,
        shots_data: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[Path]:
        """Generate PNG overlays for all shots in sequence."""
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        total = len(shots_data)
        for s in shots_data:
            idx = s.get("shot_index", 1)
            p = output_dir / f"hud_overlay_shot_{idx:02d}_{self.resolution}.png"
            self.generate_shot_hud_image(s, total_shots=total, output_path=p)
            paths.append(p)
        return paths
