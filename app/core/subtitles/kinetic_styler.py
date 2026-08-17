"""
Kinetic Dynamic Subtitles Styler (Vox / MrBeast Aesthetics)
===========================================================
Compiles aligned tokens into high-impact kinetic subtitles:
- ASS format with Karaoke timing (\k) and Gold (#FFD700) / Pure White (#FFFFFF) text styling
- Rounded pill bounding boxes / translucent dark glass backdrops
- Microcopy word-level pop animations and emphasis tagging
- SRT, VTT, and Structured JSON exports for Remotion & WebUI integration
"""

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.subtitles.forced_aligner import CanonicalToken


@dataclass
class SubtitleWord:
    word: str
    clean_word: str
    start: float
    end: float
    duration_cs: int  # Centiseconds (for ASS \k tags)
    is_key_word: bool = False
    shot_index: int = 0


@dataclass
class SubtitleChunk:
    chunk_index: int
    shot_index: int
    time_window: str
    start: float
    end: float
    words: List[SubtitleWord]
    full_text: str
    primary_highlight_word: Optional[str] = None


class KineticSubtitleStyler:
    """
    Transforms aligned tokens into Vox/MrBeast style kinetic subtitles across formats.
    """

    def __init__(
        self,
        min_words_per_chunk: int = 2,
        max_words_per_chunk: int = 5,
        target_resolution: str = "4k",  # "4k" (3840x2160) or "1080p" (1920x1080)
        font_family: str = "League Spartan",
        highlight_color_hex: str = "#FFD700",  # Gold
        text_color_hex: str = "#FFFFFF",       # Pure White
        bg_box_color: str = "&H350B0E14",       # Translucent dark glass
        margin_v: int = 150
    ):
        self.min_words = min_words_per_chunk
        self.max_words = max_words_per_chunk
        self.resolution = target_resolution.lower()
        self.font_family = font_family
        self.highlight_color_hex = highlight_color_hex
        self.text_color_hex = text_color_hex
        self.bg_box_color = bg_box_color

        if self.resolution == "4k":
            self.res_x = 3840
            self.res_y = 2160
            self.font_size = 110
            self.badge_font_size = 48
            self.outline_width = 5.0
            self.shadow_depth = 4.0
            self.margin_v = margin_v * 2
        else:
            self.res_x = 1920
            self.res_y = 1080
            self.font_size = 56
            self.badge_font_size = 24
            self.outline_width = 2.8
            self.shadow_depth = 2.0
            self.margin_v = margin_v

    @staticmethod
    def _hex_to_ass_color(hex_color: str, alpha_hex: str = "00") -> str:
        """Convert #RRGGBB hex to ASS format &HAABBGGRR&."""
        hex_clean = hex_color.lstrip("#")
        if len(hex_clean) == 6:
            r, g, b = hex_clean[0:2], hex_clean[2:4], hex_clean[4:6]
            return f"&H{alpha_hex}{b.upper()}{g.upper()}{r.upper()}&"
        return "&H00FFFFFF&"

    def build_chunks(self, aligned_tokens: List[CanonicalToken]) -> List[SubtitleChunk]:
        """
        Group words into natural cognitive chunks (2 to 5 words) respecting sentence pauses and shot transitions.
        """
        chunks: List[SubtitleChunk] = []
        if not aligned_tokens:
            return chunks

        current_words: List[SubtitleWord] = []
        current_shot = aligned_tokens[0].shot_index
        current_time_win = aligned_tokens[0].time_window
        chunk_idx = 1

        for i, tok in enumerate(aligned_tokens):
            w_start = tok.start if tok.start is not None else 0.0
            w_end = tok.end if tok.end is not None else (w_start + 0.3)
            dur_cs = max(1, int(round((w_end - w_start) * 100)))

            sub_word = SubtitleWord(
                word=tok.word,
                clean_word=tok.clean_word,
                start=round(w_start, 3),
                end=round(w_end, 3),
                duration_cs=dur_cs,
                is_key_word=tok.is_key_word,
                shot_index=tok.shot_index
            )

            # Decision to split chunk
            is_shot_boundary = (tok.shot_index != current_shot and current_words)
            is_punctuation_boundary = any(tok.word.endswith(p) for p in [".", "?", "!", "...", ":", ";"]) and len(current_words) >= self.min_words
            is_comma_boundary = tok.word.endswith(",") and len(current_words) >= self.min_words
            is_max_length = len(current_words) >= self.max_words

            current_words.append(sub_word)

            if is_shot_boundary or is_punctuation_boundary or is_comma_boundary or is_max_length or (i == len(aligned_tokens) - 1):
                chunk_start = current_words[0].start
                chunk_end = current_words[-1].end
                full_txt = " ".join(w.word for w in current_words)

                # Identify primary key word
                key_w = next((w.word for w in current_words if w.is_key_word), None)

                chunks.append(SubtitleChunk(
                    chunk_index=chunk_idx,
                    shot_index=current_shot,
                    time_window=current_time_win,
                    start=chunk_start,
                    end=chunk_end,
                    words=list(current_words),
                    full_text=full_txt,
                    primary_highlight_word=key_w
                ))

                chunk_idx += 1
                current_words = []
                if i + 1 < len(aligned_tokens):
                    current_shot = aligned_tokens[i + 1].shot_index
                    current_time_win = aligned_tokens[i + 1].time_window

        return chunks

    def generate_ass(self, chunks: List[SubtitleChunk], title: str = "VideoPro Kinetic Master") -> str:
        """
        Compile chunks into high-fidelity ASS script with Karaoke timing, Gold/White contrast, and Box styles.
        """
        ass_gold = self._hex_to_ass_color(self.highlight_color_hex)
        ass_white = self._hex_to_ass_color(self.text_color_hex)
        ass_outline = "&H00000000&"
        ass_shadow = "&H80000000&"

        lines = [
            "[Script Info]",
            f"Title: {title}",
            "ScriptType: v4.00+",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            f"PlayResX: {self.res_x}",
            f"PlayResY: {self.res_y}",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # VoxKinetic: White base, Gold karaoke secondary, robust black outline & soft shadow
            f"Style: VoxKinetic,{self.font_family},{self.font_size},{ass_white},{ass_gold},{ass_outline},{ass_shadow},-1,0,0,0,100,100,1.2,0,1,{self.outline_width},{self.shadow_depth},2,40,40,{self.margin_v},1",
            # VoxKineticBadge: Top left diegetic badge
            f"Style: VoxBadge,Liberation Mono,{self.badge_font_size},{ass_gold},{ass_white},&H00000000&,&H60000000&,-1,0,0,0,100,100,2.0,0,1,2.0,1.5,7,60,60,60,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ]

        def fmt_time(sec: float) -> str:
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            cs = int(round((sec - int(sec)) * 100))
            if cs >= 100:
                cs = 99
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        for ch in chunks:
            st = fmt_time(ch.start)
            et = fmt_time(ch.end)

            # Karaoke text assembly
            karaoke_parts = []
            for w in ch.words:
                dur_cs = w.duration_cs
                # If it's a key punchy word, add slight pop scaling in karaoke
                if w.is_key_word:
                    karaoke_parts.append(f"{{\\kf{dur_cs}\\fscx108\\fscy108}}{w.word}{{\\fscx100\\fscy100}}")
                else:
                    karaoke_parts.append(f"{{\\k{dur_cs}}}{w.word}")

            karaoke_text = " ".join(karaoke_parts)
            lines.append(f"Dialogue: 0,{st},{et},VoxKinetic,,0,0,0,,{karaoke_text}")

        return "\n".join(lines)

    def generate_srt(self, chunks: List[SubtitleChunk]) -> str:
        """Generate standard SRT subtitles."""
        def fmt_srt_time(sec: float) -> str:
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int(round((sec - int(sec)) * 1000))
            if ms >= 1000:
                ms = 999
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        lines = []
        for i, ch in enumerate(chunks, 1):
            st = fmt_srt_time(ch.start)
            et = fmt_srt_time(ch.end)
            # Emphasize key words with uppercase or gold color tags if supported
            words_formatted = []
            for w in ch.words:
                if w.is_key_word:
                    words_formatted.append(f"<b><font color=\"{self.highlight_color_hex}\">{w.word.upper()}</font></b>")
                else:
                    words_formatted.append(w.word)

            txt = " ".join(words_formatted)
            lines.append(f"{i}\n{st} --> {et}\n{txt}\n")

        return "\n".join(lines)

    def generate_vtt(self, chunks: List[SubtitleChunk]) -> str:
        """Generate WebVTT subtitles."""
        def fmt_vtt_time(sec: float) -> str:
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            ms = int(round((sec - int(sec)) * 1000))
            if ms >= 1000:
                ms = 999
            return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

        lines = ["WEBVTT", ""]
        for i, ch in enumerate(chunks, 1):
            st = fmt_vtt_time(ch.start)
            et = fmt_vtt_time(ch.end)
            words_formatted = []
            for w in ch.words:
                if w.is_key_word:
                    words_formatted.append(f"<c.gold>{w.word}</c>")
                else:
                    words_formatted.append(w.word)

            txt = " ".join(words_formatted)
            lines.append(f"{i}\n{st} --> {et}\n{txt}\n")

        return "\n".join(lines)

    def generate_json_manifest(self, chunks: List[SubtitleChunk], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate full JSON manifest for Remotion components and WebUI timeline integration.
        """
        chunks_data = []
        for ch in chunks:
            chunks_data.append({
                "chunk_index": ch.chunk_index,
                "shot_index": ch.shot_index,
                "time_window": ch.time_window,
                "start": ch.start,
                "end": ch.end,
                "duration": round(ch.end - ch.start, 3),
                "full_text": ch.full_text,
                "primary_highlight_word": ch.primary_highlight_word,
                "words": [asdict(w) for w in ch.words]
            })

        return {
            "version": "2.0-KineticVox",
            "style": {
                "font_family": self.font_family,
                "highlight_color": self.highlight_color_hex,
                "text_color": self.text_color_hex,
                "resolution": self.resolution,
                "margin_v": self.margin_v
            },
            "metadata": metadata or {},
            "total_chunks": len(chunks),
            "chunks": chunks_data
        }
