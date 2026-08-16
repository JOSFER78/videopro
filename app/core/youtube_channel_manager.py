"""
app/core/youtube_channel_manager.py
================================================================================
GESTOR CENTRAL DE CANALES DE YOUTUBE & ECOSISTEMA VIDEOPRO
================================================================================
Gestiona el escaneo, parseo, lectura y creación de canales en el sistema
de archivos de `docs/02_canales_youtube/mis_canales/`.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHANNELS_DIR = BASE_DIR / "docs" / "02_canales_youtube" / "mis_canales"
ESTRATEGIA_DIR = BASE_DIR / "docs" / "02_canales_youtube" / "estrategia_y_crecimiento"


class YouTubeChannelManager:
    """Gestor de canales y metadatos del ecosistema de YouTube."""

    FALLBACK_CHANNELS = {
        "01_CHRONODRIFT": {
            "channel_id": "01_CHRONODRIFT",
            "brand_name": "CHRONODRIFT",
            "handle": "@ChronoDriftOfficial",
            "tagline": "Urban Time Travel & Future Cities (1626 ➔ 2026 ➔ 2226)",
            "nicho": "Vuelos FPV Tritemporales por Ciudades con Música Flow y Datos Científicos",
            "target_rpm_usd": "$18.50 – $28.00 USD",
            "target_geo": "USA, UK, Alemania, Japón (Tier 1)",
            "status": "PRODUCCION",
            "status_label": "🟢 PRODUCCIÓN ACTIVA (12 Ciudades Listas)",
            "progreso": 100,
            "episodios_count": 12,
            "salud_score": 98,
            "pipeline": "FLUX 3 Master + LTX-2.5 6-DoF + Remotion Vox Lower Thirds + Foley 48kHz (-14 LUFS)",
            "fuentes_ingreso": ["AdSense 4K UHD ($24+ RPM)", "Afiliados de viajes y fotografía", "Venta de LUTs ACEScg", "Patrocinios VPN/Tech"]
        },
        "02_TERRAMORPH": {
            "channel_id": "02_TERRAMORPH",
            "brand_name": "TERRAMORPH",
            "handle": "@TerraMorphAI",
            "tagline": "Geología Extrema, Tectónica & Megaestructuras Planetarias",
            "nicho": "Transformaciones Geológicas Cataclísmicas & Topografía 4K",
            "target_rpm_usd": "$18.00 – $22.00 USD",
            "target_geo": "USA, Canadá, Australia",
            "status": "DESARROLLO",
            "status_label": "🟡 EN DESARROLLO (ASSETS & PROMPTS)",
            "progreso": 60,
            "episodios_count": 10,
            "salud_score": 84,
            "pipeline": "FLUX 3 D-Depth + LTX Flow Matching + Bloomberg Stat Cards + Sub-bass 40Hz",
            "fuentes_ingreso": ["AdSense Tier 1", "Software de modelado 3D / GIS", "Libros divulgativos de geología"]
        },
        "03_NANOVERSE": {
            "channel_id": "03_NANOVERSE",
            "brand_name": "NANOVERSE",
            "handle": "@NanoVerseExplore",
            "tagline": "Biología Celular, Inmunología & Zoom Infinito Cuántico",
            "nicho": "Microscopía Electrónica SEM 4K & Guerra Celular",
            "target_rpm_usd": "$15.50 – $19.00 USD",
            "target_geo": "Global Tier 1 + Comunidad Educativa",
            "status": "PLANIFICADO",
            "status_label": "🔵 PLANIFICADO (ESTUDIO DE AUDIENCIA)",
            "progreso": 30,
            "episodios_count": 10,
            "salud_score": 72,
            "pipeline": "Micro-Prompting 7-Capas + Lyria 3 Pro Ambient + Remotion Deep Zoom",
            "fuentes_ingreso": ["AdSense Educativo", "Afiliados de microscopía y óptica", "Licencias documentales"]
        },
        "04_LIVING_CANVAS": {
            "channel_id": "04_LIVING_CANVAS",
            "brand_name": "LIVING CANVAS",
            "handle": "@LivingCanvasArt",
            "tagline": "Historia del Arte, Museos en 3D & Cuadros Clásicos Vivos",
            "nicho": "Animación Inmersiva 3D de Cuadros Históricos y Arte Sacro",
            "target_rpm_usd": "$19.00 – $24.00 USD",
            "target_geo": "Europa Tier 1, USA",
            "status": "PLANIFICADO",
            "status_label": "🔵 PLANIFICADO (BIBLIA VISUAL)",
            "progreso": 20,
            "episodios_count": 10,
            "salud_score": 60,
            "pipeline": "Segmentación SAM-2 + FLUX Inpainting + Música Clásica Lo-Fi 48kHz",
            "fuentes_ingreso": ["AdSense Alta Retención", "Venta de Prints Fine Art 4K", "Licencias de animación"]
        },
        "05_ASTRODRIFT": {
            "channel_id": "05_ASTRODRIFT",
            "brand_name": "ASTRODRIFT",
            "handle": "@AstroDriftCosmos",
            "tagline": "Astrofísica Teórica, Agujeros Negros & Cosmología Relativista",
            "nicho": "Viajes FPV por el Espacio Profundo y Fenómenos Extremos",
            "target_rpm_usd": "$26.00 – $35.00 USD",
            "target_geo": "USA, UK, Tier 1 Global",
            "status": "PLANIFICADO",
            "status_label": "🔵 PLANIFICADO (CONCEPT SCRIPT)",
            "progreso": 15,
            "episodios_count": 10,
            "salud_score": 55,
            "pipeline": "Ray-Marching Relativista + LTX-2.5 Space Flight + VibeVoice Deep Resonance",
            "fuentes_ingreso": ["AdSense Máximo RPM ($30+)", "Afiliados de telescopios (Celestron)", "BSO Spotify"]
        }
    }

    @classmethod
    def list_channels(cls) -> List[Dict[str, Any]]:
        """Lista todos los canales escaneando carpetas en mis_canales."""
        channels = []
        if not CHANNELS_DIR.exists():
            return list(cls.FALLBACK_CHANNELS.values())

        for entry in sorted(os.listdir(CHANNELS_DIR)):
            channel_path = CHANNELS_DIR / entry
            if channel_path.is_dir() and not entry.startswith((".", "_")):
                config_file = channel_path / "channel_config.json"
                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            cfg = json.load(f)
                            channels.append(cls._format_channel_summary(entry, cfg, channel_path))
                    except Exception:
                        fallback = cls.FALLBACK_CHANNELS.get(entry)
                        if fallback:
                            channels.append(fallback)
                        else:
                            channels.append(cls._generate_minimal_summary(entry, channel_path))
                else:
                    fallback = cls.FALLBACK_CHANNELS.get(entry)
                    if fallback:
                        channels.append(fallback)
                    else:
                        channels.append(cls._generate_minimal_summary(entry, channel_path))

        if not channels:
            channels = list(cls.FALLBACK_CHANNELS.values())

        return channels

    @classmethod
    def get_channel_detail(cls, channel_id: str) -> Dict[str, Any]:
        """Obtiene información completa y detallada de un canal específico."""
        channel_path = CHANNELS_DIR / channel_id
        data = {
            "channel_id": channel_id,
            "brand_name": channel_id,
            "handle": f"@{channel_id.lower()}",
            "tagline": "Canal Automatizado VideoPro",
            "nicho": "Contenido Audiovisual 4K",
            "target_rpm_usd": "$18.00 - $25.00",
            "target_geo": "Tier 1 (USA, UK, DE)",
            "status": "PLANIFICADO",
            "progreso": 20,
            "episodes": [],
            "thumbnails_config": {},
            "docs_available": [],
            "raw_config": {}
        }

        fallback = cls.FALLBACK_CHANNELS.get(channel_id, {})
        data.update(fallback)

        if channel_path.exists():
            # Leer channel_config.json
            cfg_file = channel_path / "channel_config.json"
            if cfg_file.exists():
                try:
                    with open(cfg_file, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        data["raw_config"] = cfg
                        if "brand_name" in cfg:
                            data["brand_name"] = cfg["brand_name"]
                        if "handle" in cfg:
                            data["handle"] = cfg["handle"]
                        if "tagline" in cfg:
                            data["tagline"] = cfg["tagline"]
                        if "nicho" in cfg:
                            data["nicho"] = cfg["nicho"]
                        if "target_rpm_usd" in cfg:
                            data["target_rpm_usd"] = cfg["target_rpm_usd"]
                except Exception:
                    pass

            # Leer thumbnail_templates.json
            thumb_file = channel_path / "thumbnail_templates.json"
            if thumb_file.exists():
                try:
                    with open(thumb_file, "r", encoding="utf-8") as f:
                        data["thumbnails_config"] = json.load(f)
                except Exception:
                    pass

            # Leer y parsear 08_escaleta_10_primeros_episodios.md
            escaleta_file = channel_path / "08_escaleta_10_primeros_episodios.md"
            if escaleta_file.exists():
                try:
                    with open(escaleta_file, "r", encoding="utf-8") as f:
                        content = f.read()
                        data["episodes"] = cls._parse_escaleta_markdown(content, channel_id)
                except Exception:
                    pass

            # Listar documentos disponibles
            for doc_f in sorted(channel_path.glob("*.md")):
                data["docs_available"].append({
                    "filename": doc_f.name,
                    "title": doc_f.stem.replace("_", " ").title(),
                    "size_kb": round(doc_f.stat().st_size / 1024, 1)
                })

        return data

    @classmethod
    def _parse_escaleta_markdown(cls, md_text: str, channel_id: str) -> List[Dict[str, Any]]:
        """Extrae de forma estructurada los episodios a partir del archivo markdown de escaleta."""
        episodes = []
        pattern = r"###?\s*🎬\s*Episodio\s*(\d+)[:\s]+([^\n\r]+)(.*?)(?=(?:###?\s*🎬\s*Episodio|\Z))"
        matches = re.findall(pattern, md_text, re.DOTALL | re.IGNORECASE)

        for ep_num, title, block in matches:
            ep_info = {
                "number": int(ep_num),
                "title": title.strip(),
                "hook": "",
                "acts": [],
                "seo_titles": [],
                "raw_block": block.strip()
            }

            # Extraer Gancho de Inicio
            hook_match = re.search(r"\*\s*\*\*Gancho[^\*]*\*\*:\s*([^\n\r]+)", block, re.IGNORECASE)
            if hook_match:
                ep_info["hook"] = hook_match.group(1).strip()

            # Extraer Actos
            act_matches = re.findall(r"\d+\.\s*\*\*Acto\s*([IVX\d]+)[^\*]*\*\*:\s*([^\n\r]+)", block, re.IGNORECASE)
            if act_matches:
                for act_n, act_desc in act_matches:
                    ep_info["acts"].append(f"Acto {act_n}: {act_desc.strip()}")

            # Extraer opciones de títulos SEO
            title_matches = re.findall(r"\*\s*\*\*Opción\s*[A-C][^\*]*\*\*:\s*`([^`]+)`", block)
            if title_matches:
                ep_info["seo_titles"] = title_matches

            episodes.append(ep_info)

        # Si no encontró coincidencias con el regex anterior, intentar parseo por líneas simples
        if not episodes:
            lines = md_text.splitlines()
            cur_ep = None
            for line in lines:
                if "Episodio" in line and ("##" in line or "###" in line):
                    if cur_ep:
                        episodes.append(cur_ep)
                    title_clean = line.replace("#", "").replace("🎬", "").replace("Episodio", "").strip()
                    cur_ep = {
                        "number": len(episodes) + 1,
                        "title": title_clean,
                        "hook": "Gancho cinemático 4K optimizado para retención >70%",
                        "acts": ["Pasado Histórico", "Presente 4K", "Futuro Científico"],
                        "seo_titles": [],
                        "raw_block": ""
                    }
            if cur_ep:
                episodes.append(cur_ep)

        return episodes

    @classmethod
    def _format_channel_summary(cls, folder_name: str, cfg: Dict[str, Any], path: Path) -> Dict[str, Any]:
        """Formatea un resumen homogéneo a partir del config JSON."""
        channel_id = cfg.get("channel_id", folder_name)
        fallback = cls.FALLBACK_CHANNELS.get(folder_name, {})

        rpm = cfg.get("target_rpm_usd", fallback.get("target_rpm_usd", "$18.00 – $25.00"))
        brand_name = cfg.get("brand_name", folder_name)
        handle = cfg.get("handle", f"@{brand_name.lower()}")
        tagline = cfg.get("tagline", fallback.get("tagline", "Canal Automatizado VideoPro"))
        niche = cfg.get("niche", fallback.get("nicho", "Documental 4K"))

        episodes_count = fallback.get("episodios_count", 10)
        status = fallback.get("status", "PLANIFICADO")
        status_label = fallback.get("status_label", "🔵 PLANIFICADO")
        progreso = fallback.get("progreso", 25)
        salud_score = fallback.get("salud_score", 70)

        return {
            "id": folder_name,
            "channel_id": channel_id,
            "nombre": brand_name,
            "handle": handle,
            "tagline": tagline,
            "nicho": niche,
            "geo_target": fallback.get("target_geo", "Tier 1 (USA, UK, DE)"),
            "rpm_display": rpm,
            "estado": status,
            "estado_label": status_label,
            "progreso": progreso,
            "episodios_listos": episodes_count,
            "salud_score": salud_score,
            "pipeline": fallback.get("pipeline", "FLUX 3 + LTX-2.5 + Remotion + EBU R128"),
            "fuentes_ingreso": fallback.get("fuentes_ingreso", ["AdSense 4K", "Afiliados", "Patrocinios Directos"]),
            "recomendacion": f"Continuar producción batch de los 10 episodios y mantener masterización -14 LUFS."
        }

    @classmethod
    def _generate_minimal_summary(cls, folder_name: str, path: Path) -> Dict[str, Any]:
        """Genera un resumen mínimo para carpetas sin config completa."""
        return {
            "id": folder_name,
            "channel_id": folder_name,
            "nombre": folder_name.replace("_", " ").title(),
            "handle": f"@{folder_name.lower()}",
            "tagline": "Canal del Ecosistema VideoPro",
            "nicho": "Documental / Exploración 4K",
            "geo_target": "Tier 1 (USA, UK, DE)",
            "rpm_display": "$18.00 - $24.00",
            "estado": "PLANIFICADO",
            "estado_label": "🔵 PLANIFICADO",
            "progreso": 15,
            "episodios_listos": 0,
            "salud_score": 50,
            "pipeline": "FLUX 3 + LTX-2.5 + Remotion",
            "fuentes_ingreso": ["AdSense Tier 1", "Afiliados"],
            "recomendacion": "Estructurar la biblia visual y redactar la escaleta de los primeros 10 episodios."
        }

    @classmethod
    def create_new_channel(
        cls,
        channel_slug: str,
        brand_name: str,
        handle: str,
        tagline: str,
        niche: str,
        target_rpm: str = "$18.00 - $26.00",
        target_geo: str = "USA, UK, DE (Tier 1)"
    ) -> Dict[str, Any]:
        """Crea la estructura física completa en disco para un nuevo canal."""
        clean_slug = re.sub(r'[^A-Z0-9_]', '', channel_slug.upper().strip())
        if not clean_slug.startswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
            existing = [d for d in os.listdir(CHANNELS_DIR) if (CHANNELS_DIR / d).is_dir()]
            next_num = len(existing) + 1
            clean_slug = f"{next_num:02d}_{clean_slug}"

        target_dir = CHANNELS_DIR / clean_slug
        os.makedirs(target_dir, exist_ok=True)

        config_data = {
            "channel_id": clean_slug,
            "brand_name": brand_name,
            "handle": handle if handle.startswith("@") else f"@{handle}",
            "tagline": tagline,
            "nicho": niche,
            "target_rpm_usd": target_rpm,
            "target_retention": "90% (1m) / 68% (AVD)",
            "brand_colors": {
                "primary": "#00e5ff",
                "secondary": "#ffb300",
                "accent": "#7c4dff",
                "void_black": "#07090e"
            },
            "video_generator": {
                "engine": "gemini-omni-flash-preview",
                "zero_veo3_mandate": True,
                "keyframes_per_shot": 7,
                "keyframe_generator_model": "gemini-3.1-flash-image (Nano Banana Pro)"
            },
            "audio_engineering": {
                "bpm": 118,
                "dynamic_ducking": {"attenuation_under_vo_db": -18.0},
                "master_standards": {"target_integrated_lufs": -14.0}
            }
        }

        with open(target_dir / "channel_config.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        escaleta_content = f"""# 📜 Escaleta y Guiones de los 10 Primeros Episodios
## Canal: {brand_name} ({handle})
**Tagline:** {tagline}  
**Nicho:** {niche}  
**RPM Proyectado:** {target_rpm}

---

### 🎬 Episodio 01: Génesis y Revelación Inicial
* **Gancho de Inicio (0–5s):** Transición cinemática de alto impacto que establece la premisa dramática en los primeros 1.5 segundos.
* **Estructura del Vuelo en 3 Actos:**
  1. **Acto I (Origen / Fundamento):** El misterio inicial y contexto fundamental.
  2. **Acto II (Desarrollo / Evidencia 4K):** Exploración visual detallada con telemetría HUD.
  3. **Acto III (Revelación / Clímax):** Desenlace y proyección futura.
* **BGM & Audio:** Master EBU R128 a -14 LUFS con ducking a -18dB.

### 🎬 Episodio 02: El Gran Enigma
* **Gancho de Inicio (0–5s):** Pregunta provocativa visualmente anclada.
* **Estructura del Vuelo en 3 Actos:**
  1. **Acto I:** Introducción al fenómeno.
  2. **Acto II:** Análisis microscópico / temporal.
  3. **Acto III:** Conclusión transformadora.

### 🎬 Episodio 03: Horizontes Extremos
* **Gancho de Inicio (0–5s):** Zoom hipnótico y aceleración controlada.
* **Estructura del Vuelo en 3 Actos:**
  1. **Acto I:** Planteamiento espacial.
  2. **Acto II:** Recorrido cinematográfico.
  3. **Acto III:** Síntesis científica.
"""
        with open(target_dir / "08_escaleta_10_primeros_episodios.md", "w", encoding="utf-8") as f:
            f.write(escaleta_content)

        return {
            "success": True,
            "channel_id": clean_slug,
            "folder_path": str(target_dir),
            "message": f"Canal '{brand_name}' registrado exitosamente en {clean_slug}."
        }

    @classmethod
    def get_dashboard_html_paths(cls) -> Dict[str, str]:
        """Devuelve las rutas absolutas y nombres de los dashboards HTML disponibles."""
        dashboards = {}
        
        d1 = CHANNELS_DIR / "dashboard_canales_youtube.html"
        if d1.exists():
            dashboards["Canales de YouTube (Ecosistema 01-05)"] = str(d1)

        d2 = ESTRATEGIA_DIR / "dashboards_y_metricas" / "10_dashboard_demanda_retencion_ciudades.html"
        if d2.exists():
            dashboards["Demanda & Retención Ciudades Tritemporales"] = str(d2)

        d3 = ESTRATEGIA_DIR / "dashboards_y_metricas" / "canales_alto_impacto.html"
        if d3.exists():
            dashboards["Canales de Alto Impacto (Micro-Cosmos & Geo-Forensic)"] = str(d3)

        return dashboards
