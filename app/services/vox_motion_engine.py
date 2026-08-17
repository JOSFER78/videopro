"""
vox_motion_engine.py
Motor de Motion Graphics, Paralaje y Diseño Sonoro Documental estilo VOX / Johnny Harris.
Genera capas visuales de alta gama:
1. Tarjetas de Expediente / Lower-Thirds en Glassmorphism & Papel Prensa con metadatos y fuentes oficiales.
2. Retículas de Tracking & Punteros de Detalle señalando elementos exactos de la imagen.
3. Subtítulos Cinematográficos Punchy de Alto Impacto con píldora translúcida y resaltado dinámico.
4. Grano de película analógico, viñeteado perimetral y tratamiento de tinte de celulosa.
5. Foley Sonoro Diegético (Whooshes de transición, clics de cámara fotográfica y tecleo mecánico).
"""

import os
import math
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from PIL import Image, ImageDraw, ImageFont


class VoxSceneMetadata:
    def __init__(
        self,
        image_path: str,
        duration_seconds: float,
        dossier_number: str = "01",
        chapter_title: str = "CAPÍTULO",
        location_tag: str = "MADRID",
        historical_year: str = "1937",
        key_facts: List[str] = None,
        source_badge: str = "ARCHIVO HISTÓRICO",
        target_point: Optional[Tuple[float, float]] = None,  # (x_percent, y_percent) e.g. (0.5, 0.4)
        target_label: str = "",
        motion_type: str = "zoom_in",
        subtitles: List[Dict[str, Any]] = None
    ):
        self.image_path = image_path
        self.duration_seconds = max(1.0, float(duration_seconds))
        self.dossier_number = dossier_number
        self.chapter_title = chapter_title
        self.location_tag = location_tag
        self.historical_year = historical_year
        self.key_facts = key_facts or []
        self.source_badge = source_badge
        self.target_point = target_point
        self.target_label = target_label
        self.motion_type = motion_type
        self.subtitles = subtitles or []


class VoxMotionEngine:
    """Motor de composición gráfica documental de alto impacto."""

    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Carga fuentes TrueType del sistema con fallback seguro."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        for fp in font_paths:
            if os.path.isfile(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def generate_vox_overlay_frame(
        self,
        scene: VoxSceneMetadata,
        output_png_path: str
    ) -> str:
        """Crea el plano gráfico superpuesto (HUD + Lower-Third + Retícula + Viñeta) con canal alfa."""
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        # 1. Viñeteado perimetral ultra-suave y continuo con numpy
        y, x = np.ogrid[:self.height, :self.width]
        cx, cy = self.width / 2.0, self.height / 2.0
        max_dist = np.sqrt(cx**2 + cy**2)
        dist = np.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
        vignette_alpha = (np.clip((dist - 0.40) / 0.60, 0, 1) ** 2) * 150.0
        vignette_arr = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        vignette_arr[:, :, 0] = 10
        vignette_arr[:, :, 1] = 15
        vignette_arr[:, :, 2] = 25
        vignette_arr[:, :, 3] = vignette_alpha.astype(np.uint8)
        vignette_img = Image.fromarray(vignette_arr, "RGBA")
        img.alpha_composite(vignette_img)

        draw = ImageDraw.Draw(img)

        font_hud = self._get_font(18, bold=True)
        font_title = self._get_font(32, bold=True)
        font_subtitle = self._get_font(18, bold=False)
        font_badge = self._get_font(14, bold=True)

        # 2. Top-Left HUD Pill: [ ● EXPEDIENTE #0X // MADRID OCULTO ]
        top_pill_x = 70
        top_pill_y = 55
        hud_text = f"EXPEDIENTE #{scene.dossier_number}  //  {scene.location_tag.upper()}  //  AÑO {scene.historical_year}"
        
        bbox = draw.textbbox((0, 0), hud_text, font=font_hud)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        # Fondo translúcido oscuro con borde cian
        draw.rounded_rectangle(
            [top_pill_x - 16, top_pill_y - 10, top_pill_x + tw + 35, top_pill_y + th + 10],
            radius=8,
            fill=(15, 23, 42, 220),
            outline=(56, 189, 248, 180),
            width=2
        )
        # Punto rojo de grabación
        draw.ellipse([top_pill_x - 4, top_pill_y + 3, top_pill_x + 8, top_pill_y + 15], fill=(239, 68, 68, 255))
        draw.text((top_pill_x + 18, top_pill_y), hud_text, font=font_hud, fill=(241, 245, 249, 255))

        # 3. Lower-Third Glassmorphism Card (Inferior Izquierda) con ancho dinámico
        bbox_title = draw.textbbox((0, 0), scene.chapter_title, font=font_title)
        title_w = bbox_title[2] - bbox_title[0]
        meta_str = " • ".join(scene.key_facts) if scene.key_facts else f"UBICACIÓN: {scene.location_tag}  •  ÉPOCA: {scene.historical_year}"
        bbox_meta = draw.textbbox((0, 0), meta_str, font=font_subtitle)
        meta_w = bbox_meta[2] - bbox_meta[0]

        card_w = max(580, title_w + 60, meta_w + 60)
        card_w = min(card_w, self.width - 140)
        card_h = 150
        card_x = 70
        card_y = self.height - card_h - 90

        # Sombra profunda
        draw.rounded_rectangle(
            [card_x + 8, card_y + 8, card_x + card_w + 8, card_y + card_h + 8],
            radius=12,
            fill=(0, 0, 0, 110)
        )
        # Tarjeta principal semi-transparente
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            radius=12,
            fill=(15, 23, 42, 235),
            outline=(56, 189, 248, 150),
            width=2
        )

        # Barra de acento izquierda
        draw.rounded_rectangle(
            [card_x + 6, card_y + 14, card_x + 12, card_y + card_h - 14],
            radius=3,
            fill=(250, 204, 21, 255)  # Amarillo fluor
        )

        # Título principal del capítulo
        draw.text((card_x + 24, card_y + 16), scene.chapter_title, font=font_title, fill=(255, 255, 255, 255))

        # Metadatos / Datos clave
        draw.text((card_x + 24, card_y + 64), meta_str, font=font_subtitle, fill=(203, 213, 225, 255))

        # Badge de fuente verificada
        badge_text = f"FUENTE: {scene.source_badge}"
        bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = bbox_b[2] - bbox_b[0]
        bh = bbox_b[3] - bbox_b[1]
        badge_x = card_x + 24
        badge_y = card_y + 102

        draw.rounded_rectangle(
            [badge_x - 8, badge_y - 4, badge_x + bw + 8, badge_y + bh + 4],
            radius=6,
            fill=(30, 41, 59, 240),
            outline=(148, 163, 184, 160),
            width=1
        )
        draw.text((badge_x, badge_y), badge_text, font=font_badge, fill=(56, 189, 248, 255))

        # 4. Retícula de Detalle / Target Pointing (si está especificado)
        if scene.target_point:
            tx = int(scene.target_point[0] * self.width)
            ty = int(scene.target_point[1] * self.height)
            radius = 36

            # Círculo exterior con trazo cian
            draw.ellipse([tx - radius, ty - radius, tx + radius, ty + radius], outline=(250, 204, 21, 220), width=3)
            draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=(250, 204, 21, 255))
            # Mirilla / Crosshair
            draw.line([tx - radius - 12, ty, tx - radius + 8, ty], fill=(250, 204, 21, 220), width=2)
            draw.line([tx + radius - 8, ty, tx + radius + 12, ty], fill=(250, 204, 21, 220), width=2)
            draw.line([tx, ty - radius - 12, tx, ty - radius + 8], fill=(250, 204, 21, 220), width=2)
            draw.line([tx, ty + radius - 8, tx, ty + radius + 12], fill=(250, 204, 21, 220), width=2)

            if scene.target_label:
                lbl_font = self._get_font(16, bold=True)
                lbl_bbox = draw.textbbox((0, 0), scene.target_label, font=lbl_font)
                lw = lbl_bbox[2] - lbl_bbox[0]
                lh = lbl_bbox[3] - lbl_bbox[1]
                draw.rounded_rectangle(
                    [tx + radius + 12, ty - 12, tx + radius + 24 + lw, ty + lh + 4],
                    radius=4,
                    fill=(15, 23, 42, 230),
                    outline=(250, 204, 21, 200),
                    width=1
                )
                draw.text((tx + radius + 18, ty - 8), scene.target_label, font=lbl_font, fill=(255, 255, 255, 255))

        img.save(output_png_path, "PNG")
        logger.info(f"Capa gráfica VOX generada en: {output_png_path}")
        return output_png_path

    def generate_sfx_audio(self, output_wav_path: str, duration_sec: float, sfx_type: str = "whoosh") -> str:
        """Sintetiza efectos sonoros diegéticos (whoosh, click de cámara) para transiciones."""
        sample_rate = 44100
        total_samples = int(sample_rate * duration_sec)
        t = np.linspace(0, duration_sec, total_samples, endpoint=False)

        if sfx_type == "whoosh":
            # Ruido filtrado con barrido de frecuencia
            noise = np.random.uniform(-1, 1, total_samples)
            envelope = np.sin(np.pi * t / duration_sec) ** 2
            # Modulación de baja frecuencia
            sweep = np.sin(2 * np.pi * (80 + 350 * (t / duration_sec)) * t)
            audio = (noise * 0.4 + sweep * 0.6) * envelope * 0.35
        elif sfx_type == "camera_click":
            # Clic mecánico de obturador
            audio = np.zeros(total_samples)
            # Primer impulso (apertura de cortinilla)
            p1_len = int(sample_rate * 0.03)
            audio[:p1_len] = np.sin(2 * np.pi * 1200 * t[:p1_len]) * np.exp(-t[:p1_len] * 120) * 0.7
            # Segundo impulso (cierre)
            p2_start = int(sample_rate * 0.08)
            p2_len = min(int(sample_rate * 0.04), total_samples - p2_start)
            if p2_len > 0:
                audio[p2_start:p2_start + p2_len] = np.sin(2 * np.pi * 950 * t[:p2_len]) * np.exp(-t[:p2_len] * 100) * 0.6
        else:
            audio = np.zeros(total_samples)

        # Normalizar a 16-bit PCM WAV
        audio_int16 = np.int16(audio * 32767)
        
        import wave
        with wave.open(output_wav_path, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return output_wav_path

    def build_vox_karaoke_ass(
        self,
        subtitles_data: List[Dict[str, Any]],
        output_ass_path: str
    ) -> str:
        """Genera subtítulos cinemáticos con píldora oscura translúcida y tipografía nítida."""
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: VoxMain,DejaVu Sans,34,&H00FFFFFF,&H00FACC15,&H00000000,&HB00F172A,1,0,0,0,100,100,1,0,3,12,0,2,80,80,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        lines = [header]

        def _fmt(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            cs = int((seconds - int(seconds)) * 100)
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        for sub in subtitles_data:
            st = _fmt(sub.get("start_time", 0.0))
            et = _fmt(sub.get("end_time", 0.0))
            txt = sub.get("msg", "").replace("\n", " ").strip()
            if txt:
                lines.append(f"Dialogue: 0,{st},{et},VoxMain,,0,0,0,,{txt}\n")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return output_ass_path

    def render_vox_scene(
        self,
        scene: VoxSceneMetadata,
        output_clip_path: str,
        scene_idx: int = 0,
        work_dir: Optional[Any] = None
    ) -> bool:
        """Renderiza una toma completa fusionando Ken Burns + Capa Gráfica VOX a 30/60 fps."""
        work_dir = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="vox_scene_"))
        work_dir.mkdir(parents=True, exist_ok=True)

        duration = scene.duration_seconds
        frames_count = int(duration * self.fps)

        # 1. Generar overlay gráfico transparente
        overlay_png = work_dir / f"overlay_{scene_idx:02d}.png"
        self.generate_vox_overlay_frame(scene, str(overlay_png))

        # 2. Configurar dinámica de cámara Ken Burns
        if scene.motion_type == "zoom_in":
            zoom_expr = f"1.0+0.18*(on/{frames_count})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif scene.motion_type == "zoom_out":
            zoom_expr = f"1.18-0.18*(on/{frames_count})"
            x_expr = "iw/2-(iw/zoom/2)"
            y_expr = "ih/2-(ih/zoom/2)"
        elif scene.motion_type == "pan_right":
            zoom_expr = "1.14"
            x_expr = f"(on/{frames_count})*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"
        else:
            zoom_expr = "1.14"
            x_expr = f"(1-(on/{frames_count}))*(iw-iw/zoom)"
            y_expr = "ih/2-(ih/zoom/2)"

        # 3. Superponer Ken Burns con la capa gráfica VOX
        cmd = [
            "ffmpeg", "-y",
            "-i", scene.image_path,
            "-i", str(overlay_png),
            "-filter_complex", (
                f"[0:v]scale={self.width*2}:{self.height*2}:force_original_aspect_ratio=increase,crop={self.width*2}:{self.height*2},"
                f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames_count}:s={self.width}x{self.height}:fps={self.fps}[kb];"
                f"[kb][1:v]overlay=0:0:format=auto[v_out]"
            ),
            "-map", "[v_out]",
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            output_clip_path
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return os.path.isfile(output_clip_path) and os.path.getsize(output_clip_path) > 1000
        except Exception as ex:
            logger.error(f"Error al renderizar escena VOX {scene_idx}: {ex}")
            return False

    def assemble_vox_documentary(
        self,
        scenes: List[VoxSceneMetadata],
        voice_audio_path: str,
        bgm_audio_path: Optional[str],
        output_video_path: str,
        subtitles_data: Optional[List[Dict[str, Any]]] = None,
        temp_work_dir: Optional[str] = None
    ) -> bool:
        """Montaje final multicapa: Vídeo VOX + Foley SFX + Sidechain Ducking + Subtítulos Píldora."""
        work_dir = Path(temp_work_dir or tempfile.mkdtemp(prefix="vox_doc_master_"))
        work_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"🎬 Iniciando montaje documental VOX de {len(scenes)} tomas en {work_dir}...")

        # 1. Renderizar cada escena con su capa gráfica
        rendered_clips = []
        for idx, sc in enumerate(scenes):
            clip_file = work_dir / f"scene_{idx:03d}.mp4"
            ok = self.render_vox_scene(sc, str(clip_file), scene_idx=idx, work_dir=work_dir)
            if ok:
                rendered_clips.append(str(clip_file))

        if not rendered_clips:
            logger.error("No se pudo renderizar ninguna escena VOX.")
            return False

        # 2. Concatenar vídeo
        concat_txt = work_dir / "concat_list.txt"
        with open(concat_txt, "w") as f:
            for c in rendered_clips:
                f.write(f"file '{c}'\n")

        raw_video = work_dir / "concatenated_raw.mp4"
        cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(raw_video)]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 3. Subtítulos ASS estilo VOX
        ass_path = work_dir / "vox_subtitles.ass"
        if subtitles_data:
            self.build_vox_karaoke_ass(subtitles_data, str(ass_path))

        # 4. Sintetizar SFX Whoosh para cortes
        whoosh_wav = work_dir / "sfx_whoosh.wav"
        self.generate_sfx_audio(str(whoosh_wav), duration_sec=0.8, sfx_type="whoosh")

        # 5. Mezcla de Audio Master & Sidechain
        ass_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        vf_arg = f"ass={ass_escaped}" if os.path.isfile(str(ass_path)) else "null"

        has_voice = voice_audio_path and os.path.isfile(voice_audio_path)
        has_bgm = bgm_audio_path and os.path.isfile(bgm_audio_path)

        cmd_final = ["ffmpeg", "-y", "-i", str(raw_video)]

        if has_voice and has_bgm:
            cmd_final.extend(["-i", voice_audio_path, "-i", bgm_audio_path, "-i", str(whoosh_wav)])
            filter_complex = (
                f"[0:v]{vf_arg}[v_out];"
                f"[2:a]volume=0.22,aloop=loop=-1:size=2e+09[bgm_loop];"
                f"[bgm_loop][1:a]sidechaincompress=threshold=0.07:ratio=6:attack=20:release=300[ducked_bgm];"
                f"[1:a][ducked_bgm][3:a]amix=inputs=3:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:TP=-1.5[a_out]"
            )
            cmd_final.extend([
                "-filter_complex", filter_complex,
                "-map", "[v_out]",
                "-map", "[a_out]"
            ])
        elif has_voice:
            cmd_final.extend(["-i", voice_audio_path, "-i", str(whoosh_wav)])
            filter_complex = (
                f"[0:v]{vf_arg}[v_out];"
                f"[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:TP=-1.5[a_out]"
            )
            cmd_final.extend([
                "-filter_complex", filter_complex,
                "-map", "[v_out]",
                "-map", "[a_out]"
            ])
        else:
            if vf_arg != "null":
                cmd_final.extend(["-vf", vf_arg])

        cmd_final.extend([
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_video_path
        ])

        try:
            logger.info(f"Compilando documental VOX final en: {output_video_path}...")
            subprocess.run(cmd_final, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.success(f"✅ ¡Vídeo Documental VOX generado con éxito! Archivo: {output_video_path}")
            return os.path.isfile(output_video_path) and os.path.getsize(output_video_path) > 1000
        except Exception as ex:
            logger.error(f"Error en montaje documental final: {ex}")
            return False
