"""
Ajustes y Configuración Integral — VideoPro Studio
Gestor Dinámico de Credenciales de APIs, Modelos, Enlaces Funcionales y Ayuda Técnica
100% sincronizado con la Matriz Maestra y los selectores del Generador.
"""

import os
import sys
import json
import logging
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.services import firebase_sync
from app.core.providers import health_checker, registry

logger = logging.getLogger("videopro.settings")

# Soporte para diálogos nativos limpios de Streamlit
dialog_fn = getattr(st, "dialog", getattr(st, "experimental_dialog", None))


@st.cache_data(show_spinner=False)
def _load_cached_matrix_html(path: str) -> str:
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _badge_html(badge_str: str) -> str:
    """Convierte el string de badge de health_checker en una etiqueta HTML con estilo."""
    if "ONLINE" in badge_str or "🟢" in badge_str:
        return f"<span style='background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.35); color:#34d399; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    elif "OFFLINE" in badge_str or "🔴" in badge_str:
        return f"<span style='background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.35); color:#f87171; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    elif "🟡" in badge_str:
        return f"<span style='background:rgba(234,179,8,0.15); border:1px solid rgba(234,179,8,0.35); color:#facc15; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"
    else:
        return f"<span style='background:rgba(148,163,184,0.1); border:1px solid rgba(148,163,184,0.25); color:#94a3b8; font-size:11px; font-weight:700; padding:2px 8px; border-radius:12px;'>{badge_str}</span>"


def _get_badge(matrix: dict, key: str, default: str = "⚪ Sin configurar") -> str:
    """Helper seguro para obtener el badge HTML de un proveedor."""
    entry = matrix.get(key, {})
    if isinstance(entry, dict):
        return _badge_html(entry.get("badge", default))
    return _badge_html(default)


def _render_category_api_manager(reg: dict, matrix: dict, category_code: str, help_title: str):
    """Renderiza dinámicamente las fichas de configuración de APIs basándose estrictamente en los motores ACTIVOS en la Matriz."""
    cat_providers = [
        (p_id, p_info) for p_id, p_info in reg.items()
        if p_info.get("category") == category_code and p_info.get("enabled", True)
    ]
    
    if not cat_providers:
        st.info(f"💡 No hay motores de {help_title} activos. Activa el interruptor 'USAR' en la pestaña Matriz Maestra para configurar sus credenciales y modelos.")
        return

    col_1, col_2 = st.columns(2, gap="medium")
    for idx, (p_id, p_info) in enumerate(cat_providers):
        target_col = col_1 if idx % 2 == 0 else col_2
        with target_col:
            p_name = p_info.get("name", p_id)
            p_desc = p_info.get("description", "")
            doc_link = p_info.get("doc_link", "")
            doc_link_text = p_info.get("doc_link_text", "Obtener clave / Consola ↗")
            link_html = f" · <a href='{doc_link}' target='_blank' style='color:#38bdf8; text-decoration:none; font-weight:600;'>{doc_link_text}</a>" if doc_link else ""
            
            badge_html = _get_badge(matrix, p_id)
            st.markdown(f"**{p_name}** {badge_html}{link_html}", unsafe_allow_html=True)
            if p_desc:
                st.caption(p_desc)

            # Input de clave API si aplica
            api_field = p_info.get("api_key_field")
            if api_field:
                cur_k = config.app.get(api_field, "")
                if api_field == "hf_token":
                    new_k = st.text_area("Tokens Hugging Face (uno por línea):", value=cur_k, height=70, key=f"dyn_k_{p_id}", placeholder="hf_token1\nhf_token2")
                else:
                    new_k = st.text_input(f"Clave API ({p_name}):", value=cur_k, type="password", key=f"dyn_k_{p_id}", placeholder=f"Introduce la clave para {p_name}...")
                if new_k != cur_k:
                    config.app[api_field] = new_k

            # Input de Endpoint si aplica
            ep_field = p_info.get("endpoint_field")
            if ep_field:
                cur_ep = config.app.get(ep_field, p_info.get("endpoint_default", ""))
                new_ep = st.text_input(f"Endpoint URL ({p_name}):", value=cur_ep, key=f"dyn_ep_{p_id}", placeholder="http://...")
                if new_ep != cur_ep:
                    config.app[ep_field] = new_ep

            # Selector de Modelo si aplica
            md_field = p_info.get("model_field")
            if md_field:
                cur_md = config.app.get(md_field, p_info.get("model_default", ""))
                md_opts = p_info.get("model_options")
                if md_opts and isinstance(md_opts, list):
                    sel_idx = md_opts.index(cur_md) if cur_md in md_opts else 0
                    new_md = st.selectbox(f"Modelo ({p_name}):", options=md_opts, index=sel_idx, key=f"dyn_md_{p_id}")
                else:
                    new_md = st.text_input(f"Modelo ({p_name}):", value=cur_md, key=f"dyn_md_{p_id}")
                if new_md != cur_md:
                    config.app[md_field] = new_md

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# Mapeo Ontológico Oficial de Proveedores a Capacidades y Nodos de VideoPro Studio
ONTOLOGY_MAP = {
    # --- VISUAL, 3D & CARTOGRAFÍA ---
    "nanobanana": {
        "id": "nanobanana",
        "name": "NanoBanana Pro 2",
        "canonical_api_id": "local_antigravity_bridge_8742",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0)",
        "capabilities": ["cap_nanobanana_antigravity_bridge", "cap_nanobanana_google_api", "cap_photoreal_scene_generation"],
        "nodes": ["node_03_generacion_activos_vox", "node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K", "Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Generación de fotogramas 4K hiperrealistas y keyframes fotorrealistas vía puerto local 8742",
                "Composición de planos macro de documentos antiguos, patentes y objetos históricos",
                "Creación de texturas de fondo y planos estáticos de alta densidad visual"
            ],
            "tech_caps": [
                "Resolución nativa: 2K / 4K UHD (3840x2160)",
                "Ratios de aspecto: 16:9 (Horizontal) y 9:16 (Vertical)",
                "Control de iluminación diegética y adherencia fotográfica sin marcas de agua"
            ],
            "limitations": [
                "No genera vídeo en movimiento continuo (solo keyframes o fondos estáticos)",
                "Requiere puente Antigravity activo en puerto 8742 para modo coste cero ($0)"
            ]
        }
    },
    "qgis_cartography": {
        "id": "qgis_cartography",
        "name": "QGIS 4K Vector Cartography",
        "canonical_api_id": "qgis_cartography_engine",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_qgis_vector_dash78", "cap_vox_cinematic_map_3d"],
        "nodes": ["node_03_generacion_activos_vox", "node_04_composicion_3d_parallax"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K", "Nodo 4: Composición 3D Parallax"],
        "ai_help": {
            "mini_skills": [
                "Renderizado de mapas vectoriales transparentes en 4K UHD con estilo analógico Vox",
                "Animación de rutas y fronteras con trazado de pluma y parámetro Dash=78 (Trim Paths)",
                "Integración de modelos digitales de elevación (DEM -14M) y sombreado de relieve"
            ],
            "tech_caps": [
                "Resolución: 3840x2160 a 60 FPS con canal alfa (PNG/ProRes transparente)",
                "Interpolación Bezier en curvas de desplazamiento y zoom orbital",
                "Capa con Z-offset (+0.001) para evitar artefactos de Z-fighting en 3D"
            ],
            "limitations": [
                "Requiere capas vectoriales GeoJSON/SHP descargadas o conexión OpenStreetMap",
                "El renderizado de mapas complejos de alta densidad requiere 2-4 segundos por fotograma clave"
            ]
        }
    },
    "qgis": {
        "id": "qgis",
        "name": "QGIS 4K Vector Maps",
        "canonical_api_id": "qgis_cartography_engine",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_qgis_vector_dash78", "cap_vox_cinematic_map_3d"],
        "nodes": ["node_03_generacion_activos_vox", "node_04_composicion_3d_parallax"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K", "Nodo 4: Composición 3D Parallax"],
        "ai_help": {
            "mini_skills": [
                "Trazado dinámico de trayectorias con dash a 78 y curvas de pluma estilográfica",
                "Exportación de mapas en capas separadas (terreno, agua, carreteras, etiquetas) para paralaje 3D"
            ],
            "tech_caps": [
                "Canal alfa nativo 4K para superposición directa sobre metraje real",
                "Soporte de coordenadas geográficas exactas EPSG:4326 / EPSG:3857"
            ],
            "limitations": [
                "No procesa audio ni texto narrativo (solo cartografía visual)"
            ]
        }
    },
    "remotion": {
        "id": "remotion",
        "name": "Remotion React 18 Motion Engine",
        "canonical_api_id": "local_remotion_cli",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_newspaper_roughen_parallax", "cap_blueprint_dem_elevation", "cap_vox_paper_parallax_3d", "cap_kinetic_word_subtitles", "cap_stagger_psicoacustico_motion"],
        "nodes": ["node_04_composicion_3d_parallax", "node_05_subtitulos_y_hud"],
        "node_labels": ["Nodo 4: Composición 3D Parallax", "Nodo 5: Subtítulos & HUD"],
        "ai_help": {
            "mini_skills": [
                "Montaje de vídeo programático con React 18 y tokens de diseño unificados (theme.ts)",
                "Cámara 3D virtual con paralaje multicapa, rotación angular y sombras difusas",
                "Efecto periódico histórico 1919 con Roughen Edges y resaltador flúor animado",
                "Stagger psicoacústico de 3-5 fotogramas en elementos gráficos para máxima retención"
            ],
            "tech_caps": [
                "Render determinista fotograma a fotograma f(frame, fps) a 60 FPS",
                "Componente <OffthreadVideo> para decodificación frame-accurate sin desincronización",
                "Físicas elásticas con función spring() y cinemática natural"
            ],
            "limitations": [
                "Requiere Node.js 18+ y compilación de componentes TypeScript/TSX",
                "El renderizado local consume CPU/GPU proporcional a la duración de la línea de tiempo"
            ]
        }
    },
    "remotion_engine": {
        "id": "remotion_engine",
        "name": "Remotion React CLI",
        "canonical_api_id": "local_remotion_cli",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_newspaper_roughen_parallax", "cap_blueprint_dem_elevation", "cap_vox_paper_parallax_3d", "cap_kinetic_word_subtitles", "cap_stagger_psicoacustico_motion"],
        "nodes": ["node_04_composicion_3d_parallax", "node_05_subtitulos_y_hud"],
        "node_labels": ["Nodo 4: Composición 3D Parallax", "Nodo 5: Subtítulos & HUD"],
        "ai_help": {
            "mini_skills": [
                "Renderizado por CLI local de composiciones React frame a frame",
                "Integración de texturas de papel periódico analógico con blend mode multiply a 27% opacidad"
            ],
            "tech_caps": ["60 FPS 4K UHD", "Pipeline React 18 determinista"],
            "limitations": ["No genera texto ni guiones de forma autónoma"]
        }
    },
    "ffmpeg": {
        "id": "ffmpeg",
        "name": "FFmpeg 6.x Audio/Video DSP",
        "canonical_api_id": "local_ffmpeg_engine",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_sidechain_ducking_audio", "cap_foley_diegetic_soundscape", "cap_macro_horology_patent", "cap_contact_sheet_builder"],
        "nodes": ["node_02_audio_first_y_foley", "node_06_masterizacion_ebu_r128", "node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 2: Audio-First & Foley", "Nodo 6: Masterización EBU R128", "Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": [
                "Mezcla acústica multicanal con sidechain ducking automático (-18 dB a -22 dB bajo locución)",
                "Masterización y normalización sonora a estándar EBU R128 (-14 LUFS / -1.5 dBTP)",
                "Inyección de foley diegético (whooshes de papel, obturador de cámara, tecleo de máquina)",
                "Generación de mosaicos de contacto QA 4K para validación fotograma a fotograma"
            ],
            "tech_caps": [
                "Filtros de audio: sidechaincompress, loudnorm, asetrate, anlmdn",
                "Aceleración por hardware libx264/h264_nvenc a CRF 18 y preset ultrafast",
                "Ensamblado multicapa de pistas de vídeo, subtítulos ASS y audio master"
            ],
            "limitations": [
                "No renderiza componentes vectoriales React interactivos (procesa flujos rasterizados y filtros)",
                "Requiere rutas absolutas de archivos multimedia existentes"
            ]
        }
    },
    "ffmpeg_core": {
        "id": "ffmpeg_core",
        "name": "FFmpeg Core Pipeline",
        "canonical_api_id": "local_ffmpeg_engine",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_sidechain_ducking_audio", "cap_foley_diegetic_soundscape", "cap_macro_horology_patent", "cap_contact_sheet_builder"],
        "nodes": ["node_02_audio_first_y_foley", "node_06_masterizacion_ebu_r128", "node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 2: Audio-First & Foley", "Nodo 6: Masterización EBU R128", "Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": [
                "Compresión y conversión de formatos de vídeo (MP4, WebM, MOV) con sincronización de audio",
                "Generación de contact sheets 4K para control de calidad antes de entrega"
            ],
            "tech_caps": ["Conversión lossless/near-lossless", "Filtro loudnorm EBU R128 integrado"],
            "limitations": ["No genera contenido generativo autónomo por IA"]
        }
    },
    "flux_zerogpu": {
        "id": "flux_zerogpu",
        "name": "FLUX.3 Serverless ZeroGPU",
        "canonical_api_id": "serverless_zerogpu_flux",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_flux3_serverless_free", "cap_photoreal_scene_generation"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Generación de planos fotorrealistas de alta fidelidad estética sin coste de API",
                "Adherencia tipográfica en rótulos y cartelería de época"
            ],
            "tech_caps": [
                "Resolución: 1024x1024 a 1920x1080",
                "Modelo: FLUX.1 / FLUX.3 en HuggingFace Spaces ZeroGPU"
            ],
            "limitations": [
                "Posible cola de espera en horas punta del pool serverless gratuito",
                "No genera secuencias animadas de vídeo continuo"
            ]
        }
    },
    "flux_replicate": {
        "id": "flux_replicate",
        "name": "FLUX.3 Replicate Cloud H100",
        "canonical_api_id": "serverless_replicate_flux",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_flux3_replicate_cloud", "cap_photoreal_scene_generation"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Inferencia inmediata y sin colas de FLUX.1 Pro / Schnell en hardware H100 dedicado",
                "Generación de escenas hiperdetalladas para primeros planos cinematográficos"
            ],
            "tech_caps": ["Latencia < 3 segundos", "Resolución 4K reescalada de alta definición"],
            "limitations": ["Requiere saldo / API Key en Replicate (coste por imagen)"]
        }
    },
    "comfyui_runpod_flux": {
        "id": "comfyui_runpod_flux",
        "name": "FLUX.3 ComfyUI Node Graph (Cloud)",
        "canonical_api_id": "comfyui_runpod_flux",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_flux3_comfyui_runpod"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Ejecución de pipelines de nodos ComfyUI con ControlNet, inpainting y LoRAs",
                "Generación de activos con control posicional milimétrico"
            ],
            "tech_caps": ["ControlNet Canny/Depth", "Reescalado Ultimate SD Upscale 4K"],
            "limitations": ["Requiere pod GPU RunPod o Modal en ejecución"]
        }
    },
    "comfyui_local_flux": {
        "id": "comfyui_local_flux",
        "name": "FLUX.3 ComfyUI Local VPS Bridge",
        "canonical_api_id": "comfyui_local_flux",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0)",
        "capabilities": ["cap_flux3_comfyui_local"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Inferencia local en servidor propio vía API ComfyUI (puerto 8188)",
                "Procesamiento por lotes sin coste de tráfico ni APIs externas"
            ],
            "tech_caps": ["Conexión WebSocket local", "Semilla reproducible 100% determinista"],
            "limitations": ["Requiere GPU local con al menos 12 GB de VRAM"]
        }
    },
    "ltx25": {
        "id": "ltx25",
        "name": "LTX-Video 2.5 MMDiT 22B",
        "canonical_api_id": "api_ltx25_mmdit",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_ltx25_lip_sync_24fps"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Generación de vídeo cinemático a 24 FPS con sincronización labial y movimiento fluido",
                "Animación de planos de personajes históricos o presentadores"
            ],
            "tech_caps": ["24 FPS cinemático nativo", "Sincronización labial mediante MMDiT"],
            "limitations": ["Duración máxima por clip de 5 a 10 segundos"]
        }
    },
    "wan21": {
        "id": "wan21",
        "name": "Wan 2.1 Video DiT 14B",
        "canonical_api_id": "api_wan21_alibaba",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_wan21_t2v_cinematic"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Generación de tomas cinemáticas de gran movimiento con modelo DiT de 14B de Alibaba",
                "Planos aéreos y de atmósfera con iluminación volumétrica realista"
            ],
            "tech_caps": ["Resolución 720p / 1080p", "Excelente consistencia temporal entre fotogramas"],
            "limitations": ["Tiempo de generación de 30-60s por toma"]
        }
    },
    "minimax_h3": {
        "id": "minimax_h3",
        "name": "MiniMax Hailuo-02 Video",
        "canonical_api_id": "api_minimax_h3",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_minimax_h3_motion"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Generación de planos con movimiento humano hiperrealista y físicas de telas/cabello",
                "Tomas nocturnas e interiores de gran atmósfera"
            ],
            "tech_caps": ["1080p a 25 FPS", "Altísima coherencia en interacción física"],
            "limitations": ["Requiere API key de MiniMax o Replicate"]
        }
    },
    "seedance": {
        "id": "seedance",
        "name": "SeaDance 2.5 Coreografía",
        "canonical_api_id": "api_seedance",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_seedance_choreography"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Coreografía cinemática y movimientos corporales complejos sincronizados con el ritmo"
            ],
            "tech_caps": ["Control preciso de trayectorias corporales"],
            "limitations": ["Disponibilidad en pasarelas seleccionadas"]
        }
    },
    "pexels": {
        "id": "pexels",
        "name": "Pexels 4K UHD Stock Scraping",
        "canonical_api_id": "api_pexels_stock",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada ($0 API)",
        "capabilities": ["cap_stock_scraping_pexels_4k"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Búsqueda semántica y descarga automática de clips de vídeo reales 4K UHD",
                "Aporte de material B-roll auténtico para ambientación de planos"
            ],
            "tech_caps": ["Vídeos nativos 4K (3840x2160) en MP4", "Licencia libre de royalties"],
            "limitations": ["Sujeto a existencia en catálogo para términos específicos"]
        }
    },
    "pexels_stock": {
        "id": "pexels_stock",
        "name": "Pexels Video Engine",
        "canonical_api_id": "api_pexels_stock",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada ($0 API)",
        "capabilities": ["cap_stock_scraping_pexels_4k"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": ["Descarga de metraje de apoyo B-roll"],
            "tech_caps": ["Descarga directa MP4 4K"],
            "limitations": ["Sin audio diegético propio"]
        }
    },
    "pixabay": {
        "id": "pixabay",
        "name": "Pixabay Stock Media 4K",
        "canonical_api_id": "api_pixabay_media",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada ($0 API)",
        "capabilities": ["cap_pixabay_stock_media"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Búsqueda y descarga de fotografías y metraje histórico o de stock",
                "Ingesta de texturas y fondos complementarios"
            ],
            "tech_caps": ["Archivos JPG/MP4 HD y 4K"],
            "limitations": ["Requiere clave Pixabay API configurada"]
        }
    },
    "pixabay_stock": {
        "id": "pixabay_stock",
        "name": "Pixabay Media Engine",
        "canonical_api_id": "api_pixabay_media",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada ($0 API)",
        "capabilities": ["cap_pixabay_stock_media"],
        "nodes": ["node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": ["Descarga de material gráfico de stock"],
            "tech_caps": ["Imágenes de alta resolución"],
            "limitations": ["Uso secundario frente a fuentes oficiales"]
        }
    },
    "google_flow": {
        "id": "google_flow",
        "name": "Google Flow 3D Canvas (Playwright)",
        "canonical_api_id": "browser_playwright_flow",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0 Headless)",
        "capabilities": ["cap_nanobanana_flow_browser", "cap_orbital_trajectories_4k"],
        "nodes": ["node_03_generacion_activos_vox", "node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 3: Generación Activos VOX 4K", "Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Vuelos orbitales 6-DoF sobre edificios y ciudades en Google Earth/Flow 3D",
                "Captura de texturas interactivas y recorridos sin marcas de agua vía Playwright"
            ],
            "tech_caps": ["Grabación 60 FPS sin pérdida de fotogramas", "Control de cámara orbital"],
            "limitations": ["Requiere entorno de navegador Chromium con WebGL habilitado"]
        }
    },
    "real_news": {
        "id": "real_news",
        "name": "Wikimedia Historical Archive",
        "canonical_api_id": "api_wikimedia_commons",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_web_search_scrappers", "cap_historical_archive_scraping"],
        "nodes": ["node_01_investigacion_y_storyboard", "node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 1: Investigación & Storyboard", "Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": [
                "Descarga de documentos históricos de dominio público, periódicos antiguos y patentes",
                "Extracción de metadatos de autoría y fecha exacta de los artefactos históricos"
            ],
            "tech_caps": ["Imágenes TIFF/JPG de alta resolución sin copyright", "Metadatos abiertos"],
            "limitations": ["La calidad depende de la digitalización original del archivo"]
        }
    },
    "duckduckgo_media": {
        "id": "duckduckgo_media",
        "name": "DuckDuckGo Deep Scraper",
        "canonical_api_id": "api_wikimedia_commons",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_web_search_scrappers", "cap_historical_archive_scraping"],
        "nodes": ["node_01_investigacion_y_storyboard", "node_03_generacion_activos_vox"],
        "node_labels": ["Nodo 1: Investigación & Storyboard", "Nodo 3: Generación Activos VOX 4K"],
        "ai_help": {
            "mini_skills": ["Búsqueda profunda de artículos históricos y planos de archivo"],
            "tech_caps": ["Extracción de texto e imágenes sin rate-limits"],
            "limitations": ["Filtrado manual de calidad por parte del agente"]
        }
    },

    # --- DIRECTORES LLM & STORYBOARD STUDIO ---
    "antigravity": {
        "id": "antigravity",
        "name": "Antigravity Agent Orchestrator",
        "canonical_api_id": "local_antigravity_agent_orchestrator",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0 In-House)",
        "capabilities": ["cap_llm_antigravity_agentic", "cap_llm_story_director", "cap_storyboard_shot_planner"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Orquestación agéntica autónoma de Hermes con razonamiento Chain-of-Thought (CoT)",
                "Desglose escena a escena por tipo de plano documental (QGIS Dash=78, Roughen, Blueprint, Patente)",
                "Despacho asíncrono en background y sincronización en Firestore"
            ],
            "tech_caps": ["Persistencia de misiones en disco y nube", "Thinking logs en streaming"],
            "limitations": ["Requiere contrato de misión con tema y formato definido"]
        }
    },
    "gemini": {
        "id": "gemini",
        "name": "Google Gemini Pro 2.5/3.0",
        "canonical_api_id": "api_google_gemini_llm",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_llm_story_director", "cap_storyboard_shot_planner", "cap_scriptwriting_3acts"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Redacción del guion en 3 actos con cálculo silábico y ganchos de retención",
                "Generación de esquemas de planos y descripción de capas visuales para Remotion"
            ],
            "tech_caps": ["Ventana de contexto de 1M+ tokens", "Razonamiento multimodal nativo"],
            "limitations": ["Requiere Gemini API Key configurada"]
        }
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI GPT-4o / GPT-5.5",
        "canonical_api_id": "api_openai_gpt",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_llm_story_director", "cap_storyboard_shot_planner"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Estructuración de narrativa dialéctica y corrección de estilo documental",
                "Formateo de contratos JSON con validación estricta de esquemas Pydantic"
            ],
            "tech_caps": ["Structured Outputs garantizados", "Excelente adherencia gramatical"],
            "limitations": ["Coste por millón de tokens"]
        }
    },
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek R1 CoT Reasoning",
        "canonical_api_id": "api_deepseek",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_deepseek_reasoning_cot", "cap_storyboard_shot_planner"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": [
                "Razonamiento profundo paso a paso para contraste de datos históricos y desmentir mitos",
                "Estructuración lógica de misterios y revelaciones progresivas"
            ],
            "tech_caps": ["Pensamiento crítico exhaustivo", "Coste ultra-bajo por token"],
            "limitations": ["Mayor latencia de respuesta debido al proceso de razonamiento"]
        }
    },
    "cloudflare_ai": {
        "id": "cloudflare_ai",
        "name": "Cloudflare Workers AI",
        "canonical_api_id": "api_cloudflare_workers_ai",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_llm_story_director"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": ["Extracción rápida de entidades y palabras clave en el Edge"],
            "tech_caps": ["Latencia < 500ms en red CDN"],
            "limitations": ["Ventana de contexto estándar"]
        }
    },
    "siliconflow": {
        "id": "siliconflow",
        "name": "SiliconFlow Pasarela LLM",
        "canonical_api_id": "api_siliconflow",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_llm_story_director"],
        "nodes": ["node_01_investigacion_y_storyboard"],
        "node_labels": ["Nodo 1: Investigación & Storyboard"],
        "ai_help": {
            "mini_skills": ["Acceso a modelos abiertos DeepSeek / Qwen con baja latencia"],
            "tech_caps": ["Pasarela rápida de inferencia"],
            "limitations": ["Requiere API key de SiliconFlow"]
        }
    },

    # --- VOZ & FOLEY ---
    "vibevoice": {
        "id": "vibevoice",
        "name": "VibeVoice 1.5B Neural TTS",
        "canonical_api_id": "serverless_vibevoice_tts",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_vibevoice_serverless_free", "cap_vibevoice_local_vps", "cap_neural_multilingual_voice"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": [
                "Síntesis de locución documental con entonación profunda y pausas dramáticas",
                "Generación de pista de voz WAV de referencia para la calibración de la línea de tiempo"
            ],
            "tech_caps": ["24 kHz WAV sin compresión", "Acento castellano neutro y expresivo"],
            "limitations": ["Requiere texto puntuado correctamente para modular las pausas"]
        }
    },
    "vibevoice_serverless": {
        "id": "vibevoice_serverless",
        "name": "VibeVoice Serverless Space",
        "canonical_api_id": "serverless_vibevoice_tts",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0)",
        "capabilities": ["cap_vibevoice_serverless_free", "cap_neural_multilingual_voice"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": ["Locución documental sin coste vía espacio serverless"],
            "tech_caps": ["Voz neural multilingüe"],
            "limitations": ["Cola de espera ocasional en servidor público"]
        }
    },
    "vibevoice_local": {
        "id": "vibevoice_local",
        "name": "VibeVoice Local ONNX VPS",
        "canonical_api_id": "local_vibevoice_onnx",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0 ONNX)",
        "capabilities": ["cap_vibevoice_local_vps", "cap_neural_multilingual_voice"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": ["Inferencia de voz en hardware local sin latencia de red"],
            "tech_caps": ["Ejecución directa en CPU/GPU local"],
            "limitations": ["Requiere runtime ONNX instalado en el servidor"]
        }
    },
    "edge_tts": {
        "id": "edge_tts",
        "name": "Microsoft Edge Neural TTS",
        "canonical_api_id": "api_edge_tts_free",
        "infra_type": "serverless",
        "infra_label": "☁️ Serverless Pool ($0 Free)",
        "capabilities": ["cap_edgetts_fast_narration", "cap_neural_multilingual_voice"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": [
                "Locución instantánea multi-idioma sin necesidad de API key ni coste",
                "Múltiples variantes de voces masculinas y femeninas por idioma"
            ],
            "tech_caps": ["Descarga directa de streaming MP3", "Alta velocidad (< 2s)"],
            "limitations": ["Menor flexibilidad en respiraciones sutiles"]
        }
    },
    "elevenlabs": {
        "id": "elevenlabs",
        "name": "ElevenLabs Studio Voice",
        "canonical_api_id": "api_elevenlabs_cloud",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_elevenlabs_voice_cloning", "cap_neural_multilingual_voice"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": [
                "Locución cinematográfica con máxima expresividad y clonación de voces de autor",
                "Control granular de estabilidad, claridad y dinamismo emocional"
            ],
            "tech_caps": ["44.1 kHz broadcast", "Fidelidad vocal idéntica a presentadores reales"],
            "limitations": ["Consumo de caracteres por suscripción"]
        }
    },
    "fish_audio": {
        "id": "fish_audio",
        "name": "Fish Audio S2.1 Pro",
        "canonical_api_id": "api_fish_audio",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_fish_audio_voice_cloning"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": ["Clonación rápida de voz a partir de muestras cortas de audio (10-30s)"],
            "tech_caps": ["S2.1 Pro Voice Model"],
            "limitations": ["Requiere API key de Fish Audio"]
        }
    },
    "minimax": {
        "id": "minimax",
        "name": "MiniMax Speech 01",
        "canonical_api_id": "api_minimax_speech",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_minimax_speech_t2s"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": ["Síntesis de voz ultra-realista con respiraciones naturales"],
            "tech_caps": ["Emocionalidad fluida"],
            "limitations": ["Requiere clave API"]
        }
    },

    # --- MÚSICA & BEATS ---
    "flowmusic": {
        "id": "flowmusic",
        "name": "Google Flow Music Studio",
        "canonical_api_id": "browser_playwright_flowmusic",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0 Headless)",
        "capabilities": ["cap_flowmusic_browser_gen", "cap_audio_beat_transient_detector", "cap_flow_music_synthesizer"],
        "nodes": ["node_02_audio_first_y_foley", "node_06_masterizacion_ebu_r128"],
        "node_labels": ["Nodo 2: Audio-First & Foley", "Nodo 6: Masterización EBU R128"],
        "ai_help": {
            "mini_skills": [
                "Generación y descarga automatizada de bandas sonoras a compás exacto (118-128 BPM)",
                "Pistas de audio libres de derechos con instrumentación acústica y electrónica"
            ],
            "tech_caps": ["Exportación WAV master 44.1 kHz", "Sincronización a BPM fijo"],
            "limitations": ["Requiere sesión de navegador headless Playwright"]
        }
    },
    "flow_music": {
        "id": "flow_music",
        "name": "Google Flow Music Engine",
        "canonical_api_id": "browser_playwright_flowmusic",
        "infra_type": "local",
        "infra_label": "🖥️ Local VPS ($0 Headless)",
        "capabilities": ["cap_flowmusic_browser_gen", "cap_audio_beat_transient_detector", "cap_flow_music_synthesizer"],
        "nodes": ["node_02_audio_first_y_foley", "node_06_masterizacion_ebu_r128"],
        "node_labels": ["Nodo 2: Audio-First & Foley", "Nodo 6: Masterización EBU R128"],
        "ai_help": {
            "mini_skills": ["Generación de bandas sonoras a compás"],
            "tech_caps": ["Formato WAV sin compresión"],
            "limitations": ["Requiere sesión headless"]
        }
    },
    "suno": {
        "id": "suno",
        "name": "Suno AI Music Generator",
        "canonical_api_id": "api_suno_ai",
        "infra_type": "cloud",
        "infra_label": "🚀 Cloud Dedicada",
        "capabilities": ["cap_suno_song_generation", "cap_flow_music_synthesizer"],
        "nodes": ["node_02_audio_first_y_foley"],
        "node_labels": ["Nodo 2: Audio-First & Foley"],
        "ai_help": {
            "mini_skills": [
                "Composición musical completa con arreglos instrumentales, dinámicas y melodías cinemáticas"
            ],
            "tech_caps": ["Temas musicales de hasta 4 minutos a 320 kbps"],
            "limitations": ["Generación asíncrona (1-2 minutos)"]
        }
    },

    # --- SUBTÍTULOS & MOTION GRAPHICS ---
    "whisper": {
        "id": "whisper",
        "name": "Whisper STT Word Alignment",
        "canonical_api_id": "local_whisper_stt",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_audio_beat_transient_detector", "cap_whisper_word_level_timestamps", "cap_kinetic_word_subtitles"],
        "nodes": ["node_02_audio_first_y_foley", "node_05_subtitulos_y_hud"],
        "node_labels": ["Nodo 2: Audio-First & Foley", "Nodo 5: Subtítulos & HUD"],
        "ai_help": {
            "mini_skills": [
                "Alineación temporal palabra por palabra (Word-Level Timestamps) sobre el archivo de voz master",
                "Generación de subtítulos cinemáticos en formato ASS y JSON con resaltado elástico"
            ],
            "tech_caps": ["Precisión de milisegundos en marcas temporales", "Salida de subtítulos .ass con estilos"],
            "limitations": ["Requiere modelo Whisper instalado en local"]
        }
    },
    "whisper_stt": {
        "id": "whisper_stt",
        "name": "Whisper STT Engine",
        "canonical_api_id": "local_whisper_stt",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_whisper_word_level_timestamps", "cap_kinetic_word_subtitles"],
        "nodes": ["node_05_subtitulos_y_hud"],
        "node_labels": ["Nodo 5: Subtítulos & HUD"],
        "ai_help": {
            "mini_skills": ["Alineación fonética y timestamps de sílabas"],
            "tech_caps": ["Alineación milimétrica"],
            "limitations": ["Requiere archivo WAV limpio"]
        }
    },
    "vox_subtitles": {
        "id": "vox_subtitles",
        "name": "VOX Kinetic Subtitles",
        "canonical_api_id": "local_whisper_stt",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_whisper_word_level_timestamps", "cap_kinetic_word_subtitles"],
        "nodes": ["node_05_subtitulos_y_hud"],
        "node_labels": ["Nodo 5: Subtítulos & HUD"],
        "ai_help": {
            "mini_skills": ["Subtítulos en píldora translúcida con resaltado de palabra activo estilo Vox"],
            "tech_caps": ["Tipografía Inter/Montserrat con animaciones spring()"],
            "limitations": ["No superponer sobre rostros principales"]
        }
    },
    "hyperframes_engine": {
        "id": "hyperframes_engine",
        "name": "HyperFrames WebGL Shaders",
        "canonical_api_id": "local_hyperframes_engine",
        "infra_type": "local",
        "infra_label": "⚙️ Código & DSP ($0)",
        "capabilities": ["cap_hyperframes_motion_fx"],
        "nodes": ["node_04_composicion_3d_parallax"],
        "node_labels": ["Nodo 4: Composición 3D Parallax"],
        "ai_help": {
            "mini_skills": ["Shaders WebGL y transiciones de distorsión óptica aceleradas por GPU"],
            "tech_caps": ["Render WebGL 60 FPS"],
            "limitations": ["Requiere soporte gráfico en el navegador/servidor"]
        }
    },

    # --- CLOUD & BD ---
    "r2": {
        "id": "r2",
        "name": "Cloudflare R2 Object Storage",
        "canonical_api_id": "api_cloudflare_r2",
        "infra_type": "cloud",
        "infra_label": "☁️ Cloudflare Zero-Egress",
        "capabilities": ["cap_firebase_sync_engine"],
        "nodes": ["node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": [
                "Alojamiento en la nube de vídeos máster finales, clips individuales y mosaicos QA",
                "Enlaces públicos CDN de alta velocidad sin coste de egress por descarga"
            ],
            "tech_caps": ["Compatibilidad S3 API", "Zero Egress Fee ilimitado"],
            "limitations": ["Requiere credenciales S3 (Access Key, Secret Key, Endpoint)"]
        }
    },
    "r2_storage": {
        "id": "r2_storage",
        "name": "Cloudflare R2 CDN",
        "canonical_api_id": "api_cloudflare_r2",
        "infra_type": "cloud",
        "infra_label": "☁️ Cloudflare Zero-Egress",
        "capabilities": ["cap_firebase_sync_engine"],
        "nodes": ["node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": ["Almacenamiento S3 de producción"],
            "tech_caps": ["Subidas multiparte aceleradas"],
            "limitations": ["Requiere bucket configurado"]
        }
    },
    "firestore": {
        "id": "firestore",
        "name": "Firebase Firestore DB",
        "canonical_api_id": "firebase_firestore",
        "infra_type": "cloud",
        "infra_label": "🔥 Firebase Cloud DB",
        "capabilities": ["cap_firebase_sync_engine"],
        "nodes": ["node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": [
                "Persistencia y sincronización en tiempo real de misiones de Hermes, logs CoT y estado del sistema",
                "Sincronización bidireccional entre la WebUI, el backend agéntico y Firebase Hosting"
            ],
            "tech_caps": ["Colección NoSQL videopro_missions / videopro_system", "WebSockets en vivo"],
            "limitations": ["Requiere Service Account JSON o inicialización por defecto"]
        }
    },
    "firebase_db": {
        "id": "firebase_db",
        "name": "Firebase Realtime DB",
        "canonical_api_id": "firebase_firestore",
        "infra_type": "cloud",
        "infra_label": "🔥 Firebase Cloud DB",
        "capabilities": ["cap_firebase_sync_engine"],
        "nodes": ["node_07_qa_contact_sheet_sync"],
        "node_labels": ["Nodo 7: QA & Cloud Sync"],
        "ai_help": {
            "mini_skills": ["Persistencia de metadatos de producción"],
            "tech_caps": ["Sincronización en la nube"],
            "limitations": ["Requiere conexión a internet"]
        }
    }
}


def _render_native_matrix_view(reg: dict, matrix: dict):
    """Renderizador nativo de la Matriz Maestra estructurada por Nodos, Infraestructura y Fichas IA de Mini-Skills."""

    NODE_FILTER_OPTS = [
        ("all", "🌐 Todos los Nodos (1 a 7)"),
        ("node_01", "Nodo 1: Investigación, Guion & Storyboard"),
        ("node_02", "Nodo 2: Audio-First, Locución & Foley"),
        ("node_03", "Nodo 3: Generación Activos VOX 4K"),
        ("node_04", "Nodo 4: Composición 3D Parallax"),
        ("node_05", "Nodo 5: Subtítulos Cinematográficos & HUD"),
        ("node_06", "Nodo 6: Masterización EBU R128"),
        ("node_07", "Nodo 7: QA Loop & Cloud Sync")
    ]

    INFRA_FILTER_OPTS = [
        ("all", "🌐 Todas las Infraestructuras"),
        ("local", "🖥️ Local VPS ($0 In-House)"),
        ("serverless", "☁️ Serverless Pool ($0 Free)"),
        ("cloud", "🚀 Cloud Dedicada (API Key / On-Demand)"),
        ("code", "⚙️ Código & DSP ($0 Local Engine)")
    ]

    category_map = [
        ("visual", "🎬 1. Visual, Vídeo & Keyframes 4K (QGIS, FLUX.3, NanoBanana, LTX, Pexels)"),
        ("llm", "🧠 2. Directores Creativos, LLMs & Storyboard Studio (DeepSeek R1, Gemini, OpenAI)"),
        ("voice", "🎙️ 3. Voces Neurales, Locución & Foley Diegético (VibeVoice 1.5B, ElevenLabs, Edge TTS)"),
        ("music", "🎵 4. Bandas Sonoras & Beats (Google Flow Music, Suno AI, Transients)"),
        ("programacion", "⚙️ 5. Motion Graphics, Video-as-Code & DSP (Remotion React 18, Roughen Edges, FFmpeg)"),
        ("cloud", "☁️ 6. Almacenamiento & Base de Datos (Cloudflare R2, Firebase Firestore)")
    ]

    # Barra superior con filtros por Nodo, Infraestructura y Buscador Global
    col_f1, col_f2, col_f3 = st.columns([3.5, 3.5, 3.0])
    with col_f1:
        sel_node = st.selectbox(
            "🎯 Filtrar por Nodo de Producción:",
            options=[k for k, _ in NODE_FILTER_OPTS],
            format_func=lambda x: dict(NODE_FILTER_OPTS).get(x, x),
            key="mat_filter_node"
        )
    with col_f2:
        sel_infra = st.selectbox(
            "🖥️ Filtrar por Infraestructura:",
            options=[k for k, _ in INFRA_FILTER_OPTS],
            format_func=lambda x: dict(INFRA_FILTER_OPTS).get(x, x),
            key="mat_filter_infra"
        )
    with col_f3:
        search_query = st.text_input(
            "🔍 Buscador Global:",
            placeholder="Motor, cap_*, node_*, API...",
            key="mat_filter_search"
        ).strip().lower()

    for cat_key, cat_title in category_map:
        cat_providers = [(p_id, p_info) for p_id, p_info in reg.items() if p_info.get("category") == cat_key]

        # 1. Filtro por búsqueda
        if search_query:
            cat_providers = [
                (p_id, p_info) for p_id, p_info in cat_providers
                if search_query in p_id.lower()
                or search_query in p_info.get("name", "").lower()
                or search_query in p_info.get("description", "").lower()
                or any(search_query in c.lower() for c in ONTOLOGY_MAP.get(p_id, {}).get("capabilities", []))
                or any(search_query in n.lower() for n in ONTOLOGY_MAP.get(p_id, {}).get("nodes", []))
            ]

        # 2. Filtro por Nodo de producción
        if sel_node != "all":
            cat_providers = [
                (p_id, p_info) for p_id, p_info in cat_providers
                if any(sel_node in n for n in ONTOLOGY_MAP.get(p_id, {}).get("nodes", []))
            ]

        # 3. Filtro por Infraestructura
        if sel_infra != "all":
            cat_providers = [
                (p_id, p_info) for p_id, p_info in cat_providers
                if ONTOLOGY_MAP.get(p_id, {}).get("infra_type", p_info.get("infra_type", "cloud")) in (sel_infra, f"{sel_infra}_headless")
            ]

        if not cat_providers:
            continue

        with st.expander(f"{cat_title} — ({len(cat_providers)} Motores Sincronizados)", expanded=True):
            # Encabezado de la tabla Excel
            st.markdown("""
                <div style="display: grid; grid-template-columns: 2.2fr 1.2fr 1.8fr 2.4fr 1.0fr 1.0fr 0.6fr; gap: 8px; background: #1e293b; padding: 7px 12px; border-radius: 6px; font-size: 10.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; border-bottom: 2px solid #334155; margin-bottom: 4px;">
                    <div>Motor & Identificador API</div>
                    <div>Infraestructura</div>
                    <div>Nodo de Montaje</div>
                    <div>Capacidades / Mini-Skills</div>
                    <div style="text-align: center;">Ficha IA 💡</div>
                    <div>Estado en Vivo</div>
                    <div style="text-align: center;">Usar</div>
                </div>
            """, unsafe_allow_html=True)

            for idx, (p_id, p_info) in enumerate(cat_providers):
                p_name = p_info.get("name", p_id)
                p_enabled = bool(p_info.get("enabled", True))
                p_infra = p_info.get("infra_type", "cloud")

                onto_info = ONTOLOGY_MAP.get(p_id, {
                    "id": p_id,
                    "name": p_name,
                    "canonical_api_id": f"api_{p_id}",
                    "infra_label": "🚀 Cloud Dedicada",
                    "capabilities": [f"cap_{p_id}"],
                    "nodes": ["node_03_generacion_activos_vox"],
                    "node_labels": ["Nodo 3: Generación Activos VOX 4K"],
                    "ai_help": {
                        "mini_skills": [f"Ejecución de tareas especializadas con {p_name}"],
                        "tech_caps": ["Integración estándar en VideoPro"],
                        "limitations": ["Consultar documentación técnica del proveedor"]
                    }
                })

                canonical_api_id = onto_info.get("canonical_api_id", f"api_{p_id}")
                caps_list = onto_info.get("capabilities", [])
                node_labels = onto_info.get("node_labels", [f"Nodo {n}" for n in onto_info.get("nodes", [])])
                infra_badge_txt = onto_info.get("infra_label", "🚀 Cloud Dedicada")
                ai_help = onto_info.get("ai_help", {})

                infra_color = "#34d399" if "$0" in infra_badge_txt else "#38bdf8"
                badge_str = matrix.get(p_id, {}).get("badge", "🟢 Configurado" if p_enabled else "⚪ Inactivo")
                badge_html = _badge_html(badge_str)

                caps_html = " ".join([f"<span style='background:#020617; border:1px solid #1e293b; color:#c084fc; font-size:10px; padding:1px 5px; border-radius:4px; font-family:monospace; margin-right:3px; display:inline-block;'>{c}</span>" for c in caps_list])
                nodes_html = "<br>".join([f"<span style='background:#0f172a; border-left:2px solid #34d399; color:#34d399; font-size:10px; padding:1px 5px; border-radius:3px; display:inline-block; margin-bottom:2px;'>{nl}</span>" for nl in node_labels])

                bg_row = "rgba(15, 23, 42, 0.75)" if idx % 2 == 0 else "rgba(30, 41, 59, 0.45)"

                c_row_info, c_row_pop, c_row_tog = st.columns([8.2, 1.2, 0.6], vertical_alignment="center")
                with c_row_info:
                    st.markdown(f"""
                        <div style="display: grid; grid-template-columns: 2.2fr 1.2fr 1.8fr 2.4fr 1.0fr; gap: 8px; background: {bg_row}; padding: 7px 12px; border-radius: 6px; font-size: 11.5px; border: 1px solid #1e293b; align-items: center;">
                            <div>
                                <b style="color: #f8fafc;">{p_name}</b><br>
                                <span style="font-size: 10px; color: #64748b; font-family: monospace;">{canonical_api_id}</span>
                            </div>
                            <div>
                                <span style="font-size: 10.5px; color: {infra_color}; font-weight: 600;">{infra_badge_txt}</span>
                            </div>
                            <div>
                                {nodes_html}
                            </div>
                            <div>
                                {caps_html}
                            </div>
                            <div>
                                {badge_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with c_row_pop:
                    with st.popover("💡 Ficha IA", help=f"Ficha técnica, mini-skills para Hermes y límites de {p_name}"):
                        st.markdown(f"### 🤖 Ficha Técnica de Mini-Skills: {p_name}")
                        st.markdown(f"**Identificador Canónico:** `api_{p_id}` | **Infraestructura:** {infra_badge_txt}")
                        st.markdown("---")
                        
                        st.markdown("#### 🎯 Mini-Skills que Otorga a Hermes Agent:")
                        for sk in ai_help.get("mini_skills", []):
                            st.markdown(f"- ✨ {sk}")
                        
                        st.markdown("#### ⚡ Especificaciones y Capacidades Técnicas:")
                        for tc in ai_help.get("tech_caps", []):
                            st.markdown(f"- 🔬 {tc}")
                            
                        st.markdown("#### ⚠️ Limitaciones y Reglas de Uso:")
                        for lm in ai_help.get("limitations", []):
                            st.markdown(f"- 🛑 {lm}")

                with c_row_tog:
                    new_val = st.toggle("Activar", value=p_enabled, key=f"mat_excel_tog_{p_id}", label_visibility="collapsed")
                    if new_val != p_enabled:
                        registry.set_provider_enabled(p_id, new_val)
                        firebase_sync.save_settings_to_firebase_async()
                        st.toast(f"✅ {p_name} {'activado' if new_val else 'desactivado'}.")
                        st.rerun()


def render_view():
    # Notificación de borrado previo si existe
    if "deleted_provider_toast" in st.session_state:
        st.toast(st.session_state.pop("deleted_provider_toast"))

    # Modal nativo de confirmación de borrado seguro (elimina el bug de saltar al siguiente)
    if "confirm_delete_provider" in st.session_state and st.session_state["confirm_delete_provider"]:
        del_id, del_name = st.session_state["confirm_delete_provider"]
        if dialog_fn:
            @dialog_fn("⚠️ Confirmar Eliminación de Motor")
            def _show_delete_modal(id_to_del, name_to_del):
                st.markdown(f"¿Estás seguro de que deseas eliminar permanentemente a **«{name_to_del}»** de la Matriz y del Generador?")
                st.caption("Esta acción es irreversible y eliminará el motor del catálogo activo.")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    if st.button("❌ Cancelar", use_container_width=True, key="dlg_btn_cancel"):
                        st.session_state["confirm_delete_provider"] = None
                        st.rerun()
                with c_d2:
                    if st.button("🗑️ Sí, Eliminar", type="primary", use_container_width=True, key="dlg_btn_confirm_del"):
                        registry.delete_provider(id_to_del)
                        firebase_sync.save_settings_to_firebase_async()
                        st.session_state["confirm_delete_provider"] = None
                        st.session_state["deleted_provider_toast"] = f"✅ «{name_to_del}» borrado OK, todo listo."
                        st.rerun()
            _show_delete_modal(del_id, del_name)
        else:
            # Fallback si dialog no está disponible
            st.warning(f"⚠️ ¿Eliminar **«{del_name}»**?")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                if st.button("❌ Cancelar", key="fb_canc_btn"):
                    st.session_state["confirm_delete_provider"] = None
                    st.rerun()
            with c_d2:
                if st.button("🗑️ Confirmar Eliminación", type="primary", key="fb_conf_btn"):
                    registry.delete_provider(del_id)
                    firebase_sync.save_settings_to_firebase_async()
                    st.session_state["confirm_delete_provider"] = None
                    st.session_state["deleted_provider_toast"] = f"✅ «{del_name}» borrado OK, todo listo."
                    st.rerun()

    st.markdown("""
    <div style='display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;'>
        <div>
            <h2 style='margin:0; font-size:24px; font-weight:800; color:#f8fafc;'>⚙️ Ajustes & Ecosistema de VideoPro</h2>
            <div style='font-size:13px; color:#94a3b8; margin-top:2px;'>
                Gestión integral de claves de APIs, infraestructura ($0 Local VPS, Serverless Pool, Cloud), directores y reglas de producción.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    force_check = st.session_state.get("force_health_refresh", False)
    if force_check:
        st.session_state["force_health_refresh"] = False
        with st.spinner("⚡ Ejecutando diagnóstico en vivo de todos los proveedores en paralelo..."):
            matrix = health_checker.get_all_providers_matrix(force=True)
            st.toast("✅ Diagnóstico de salud completado y guardado en disco.")
    else:
        matrix = health_checker.get_all_providers_matrix(force=False)

    reg = registry.load_registry()
    meta = health_checker.get_health_meta()

    # Métricas de resumen rápido del estado
    total_services = meta.get("total", len(matrix))
    active_services = meta.get("active", sum(1 for v in matrix.values() if isinstance(v, dict) and "🟢" in v.get("badge", "")))
    error_items = [(k, v) for k, v in matrix.items() if isinstance(v, dict) and "🔴" in v.get("badge", "")]

    c_m1, c_m2, c_m3, c_m4 = st.columns([1.3, 1.3, 1.4, 1.4], gap="small")
    with c_m1:
        st.markdown(f"""
        <div style='background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); border-radius:6px; padding:6px 12px;'>
            <div style='font-size:11px; color:#94a3b8; font-weight:600;'>Estado General</div>
            <div style='font-size:14px; font-weight:800; color:#38bdf8;'>{active_services}/{total_services} APIs Listas</div>
        </div>
        """, unsafe_allow_html=True)
    with c_m2:
        st.markdown(f"""
        <div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:6px; padding:6px 12px;'>
            <div style='font-size:11px; color:#34d399; font-weight:600;'>🟢 Motores Operativos</div>
            <div style='font-size:14px; font-weight:800; color:#10b981;'>{active_services} Conectados ($0/Cloud)</div>
        </div>
        """, unsafe_allow_html=True)
    with c_m3:
        st.markdown(f"""
        <div style='background:rgba(148,163,184,0.06); border:1px solid rgba(148,163,184,0.2); border-radius:6px; padding:6px 12px;'>
            <div style='font-size:11px; color:#94a3b8; font-weight:600;'>🕒 Último Diagnóstico</div>
            <div style='font-size:13px; font-weight:700; color:#cbd5e1;'>{meta.get('last_checked_str', 'Guardado')} ({meta.get('time_ago', '')})</div>
        </div>
        """, unsafe_allow_html=True)
    with c_m4:
        if st.button("⚡ Diagnóstico Manual", use_container_width=True, help="Ejecuta la comprobación manual de salud de todas las APIs y actualiza el estado guardado (Recomendado cada 12h/24h)"):
            st.session_state["force_health_refresh"] = True
            st.rerun()

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    tab_apis, tab_matrix, tab_storage, tab_firebase, tab_system, tab_lang = st.tabs([
        "🔑 Gestor de APIs & Credenciales",
        "📊 Matriz Maestra de Proveedores",
        "☁️ Cloud Storage (Cloudflare R2)",
        "🔥 Firebase Firestore & Hosting",
        "⚙️ Sistema y Render FFmpeg",
        "🌐 Idioma de la Interfaz"
    ])

    # =========================================================
    # TAB 1: GESTOR DINÁMICO DE APIS & CREDENCIALES (100% SINCRONIZADO)
    # =========================================================
    with tab_apis:
        subtab_llm, subtab_video, subtab_voice, subtab_music = st.tabs([
            "1. LLMs & Directores de Guion",
            "2. Vídeo, Visual e Imágenes",
            "3. Voz, Locución & Foley",
            "4. Música y Bandas Sonoras"
        ])

        with subtab_llm:
            _render_category_api_manager(reg, matrix, "llm", "Directores de Guion / LLM")

        with subtab_video:
            _render_category_api_manager(reg, matrix, "visual", "Vídeo e Imágenes")

        with subtab_voice:
            _render_category_api_manager(reg, matrix, "voice", "Voces y Locución")

        with subtab_music:
            _render_category_api_manager(reg, matrix, "music", "Música y Foley")

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("💾 Guardar y Persistir Credenciales en Firestore", type="primary", use_container_width=True, key="btn_save_creds_dyn"):
            firebase_sync.save_settings_to_firebase_async()
            st.toast("✅ Credenciales guardadas y sincronizadas con éxito.")

    # =========================================================
    # =========================================================
    # TAB 2: MATRIZ MAESTRA DE PROVEEDORES & REGLAS
    # =========================================================
    with tab_matrix:
        total_p = len(reg)
        enabled_p = sum(1 for v in reg.values() if v.get("enabled", True))
        local_p = sum(1 for v in reg.values() if v.get("infra_type") in ("local", "local_headless", "code") and v.get("enabled", True))
        serverless_p = sum(1 for v in reg.values() if v.get("infra_type") == "serverless" and v.get("enabled", True))
        cloud_p = sum(1 for v in reg.values() if v.get("infra_type") == "cloud" and v.get("enabled", True))

        cm_1, cm_2, cm_3, cm_4 = st.columns(4)
        with cm_1:
            st.metric("Total Motores", f"{enabled_p}/{total_p} Activos")
        with cm_2:
            st.metric("🖥️ Local VPS / DSP ($0)", f"{local_p} Motores")
        with cm_3:
            st.metric("☁️ Serverless Pool ($0)", f"{serverless_p} Espacios")
        with cm_4:
            st.metric("🚀 Cloud Dedicada", f"{cloud_p} APIs")

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        # Selector de Vista: Hoja de Cálculo Excel Interactiva vs Bloques Nativos
        tab_excel_view, tab_native_view = st.tabs([
            "📊 Hoja de Cálculo Excel Interactiva (Desglose Mini-Skills & Modales IA)",
            "⚡ Gestor Rápido en Bloques & Parámetros"
        ])

        with tab_excel_view:
            st.caption("Hoja de cálculo interactiva en tiempo real con control granular por capacidad, asignación de Nodos 1-7, infraestructura ($0 VPS, Serverless, Cloud API, Código) y fichas técnicas de mini-skills para Hermes.")
            
            excel_path = os.path.join(BASE_DIR, "webui", "assets", "proveedores_excel.html")
            if not os.path.isfile(excel_path):
                excel_path = os.path.join(BASE_DIR, "docs", "dashboards_y_estudios_web", "proveedores_excel.html")

            raw_html = _load_cached_matrix_html(excel_path)
            if raw_html:
                # Inyección de datos vivos del registro maestro
                live_table_data = registry.get_matrix_table_data()
                injected_script = f"<script>window.INJECTED_MATRIX_DATA = {json.dumps(live_table_data, ensure_ascii=False)};</script>"
                enhanced_html = raw_html.replace("</head>", f"{injected_script}\n</head>")
                components.html(enhanced_html, height=920, scrolling=True)
            else:
                st.warning("No se localizó el archivo proveedores_excel.html. Mostrando vista nativa a continuación.")
                _render_native_matrix_view(reg, matrix)

        with tab_native_view:
            with st.expander("➕ Registrar Nuevo Proveedor / Capacidad Personalizada", expanded=False):
                col_hdr1, col_hdr2 = st.columns([7, 3], vertical_alignment="center")
                with col_hdr1:
                    st.markdown("**Control de Activación del Generador de Vídeo**")
                with col_hdr2:
                    with st.popover("➕ Añadir Motor"):
                        st.markdown("**Registrar Nuevo Proveedor**")
                        new_p_id = st.text_input("ID único:", key="add_p_id_exp").strip().lower().replace(" ", "_")
                        new_p_name = st.text_input("Nombre:", key="add_p_name_exp")
                        new_p_cat = st.selectbox("Categoría:", ["visual", "llm", "voice", "music", "programacion", "cloud"], key="add_p_cat_exp")
                        new_p_infra = st.selectbox("Infraestructura:", ["local", "serverless", "cloud", "code"], key="add_p_infra_exp")
                        new_p_desc = st.text_input("Descripción técnica:", key="add_p_desc_exp")
                        if st.button("Guardar Motor", type="primary", use_container_width=True, key="btn_save_exp_motor"):
                            if new_p_id and new_p_name:
                                reg[new_p_id] = {
                                    "id": new_p_id,
                                    "name": new_p_name,
                                    "category": new_p_cat,
                                    "infra_type": new_p_infra,
                                    "enabled": True,
                                    "label": f"{new_p_name} ({new_p_infra.upper()})",
                                    "description": new_p_desc or "Motor personalizado",
                                    "categories": [{"text": "Inferencia Activa", "checked": True}],
                                    "infrastructure": [{"text": f"Modo {new_p_infra.upper()}", "checked": True}],
                                    "preferences": [{"text": "Preferencia activa", "checked": True}],
                                    "behaviors": [{"text": "Regla de procesamiento", "checked": True}],
                                    "notes": new_p_desc or "Personalizado"
                                }
                                registry.save_registry(reg)
                                firebase_sync.save_settings_to_firebase_async()
                                st.toast(f"✅ {new_p_name} añadido.")
                                st.rerun()

            _render_native_matrix_view(reg, matrix)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        c_act1, c_act2 = st.columns(2)
        with c_act1:
            if st.button("⚡ Diagnosticar Todas las Conexiones", use_container_width=True, key="mat_btn_diag_bot_2"):
                st.session_state["force_health_refresh"] = True
                st.toast("Comprobando conexiones de todos los proveedores...")
                st.rerun()
        with c_act2:
            if st.button("🔄 Guardar y Sincronizar Estado en Firestore", type="primary", use_container_width=True, key="mat_btn_sync_bot_2"):
                try:
                    registry.save_registry(reg)
                    firebase_sync.save_settings_to_firebase_async()
                    st.toast("✅ Matriz y estado de proveedores guardados con éxito.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # =========================================================
    # TAB 3: CLOUD STORAGE & CDN (CLOUDFLARE R2)
    # =========================================================
    with tab_storage:
        b_r2 = _get_badge(matrix, "r2")
        st.markdown(f"#### ☁️ Cloudflare R2 Object Storage (S3 API Compatible) {b_r2}")
        st.caption("Almacenamiento en la nube de coste cero por descarga (Zero Egress) para hospedar vídeos máster, previsualizaciones y escenas.")

        col_r1, col_r2 = st.columns(2, gap="medium")
        with col_r1:
            r2_enable = st.toggle("Habilitar Sincronización Automática con Cloudflare R2", value=config.app.get("s3_enabled", False), key="s_r2_en")
            config.app["s3_enabled"] = r2_enable

            r2_endpoint = st.text_input("S3 / R2 Endpoint URL:", value=config.app.get("s3_endpoint", ""), key="s_r2_ep", placeholder="https://<ACCOUNT_ID>.r2.cloudflarestorage.com")
            config.app["s3_endpoint"] = r2_endpoint

            r2_bucket = st.text_input("Nombre del Bucket R2:", value=config.app.get("s3_bucket", "videopro-masters"), key="s_r2_bk")
            config.app["s3_bucket"] = r2_bucket

        with col_r2:
            r2_ak = st.text_input("Access Key ID:", value=config.app.get("s3_access_key", ""), key="s_r2_ak")
            config.app["s3_access_key"] = r2_ak

            r2_sk = st.text_input("Secret Access Key:", value=config.app.get("s3_secret_key", ""), type="password", key="s_r2_sk")
            config.app["s3_secret_key"] = r2_sk

            r2_cdn = st.text_input("Dominio Público / CDN Custom URL (Opcional):", value=config.app.get("s3_public_url", ""), key="s_r2_cdn", placeholder="https://media.videopro.studio")
            config.app["s3_public_url"] = r2_cdn

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        col_test_r2, col_info_r2 = st.columns([1, 2])
        with col_test_r2:
            if st.button("🧪 Probar Subida Multipart a R2", key="btn_test_r2_upload", use_container_width=True):
                from app.services import r2_storage
                with st.spinner("Probando transferencia a Cloudflare R2..."):
                    res = r2_storage.test_r2_upload_diagnostic()
                    if res.get("success"):
                        st.success(res.get("message"))
                    else:
                        st.error(res.get("message"))
                        if res.get("hint"):
                            st.info(f"💡 **Recomendación:** {res.get('hint')}")

        with col_info_r2:
            st.caption("""
            ℹ️ **Credenciales S3 de Cloudflare R2:**
            En *Cloudflare Dashboard > R2 > Manage R2 API Tokens*, crea un token con permisos de administración (Read & Write). Cloudflare generará un **Access Key ID** (32 caracteres) y un **Secret Access Key** (64 caracteres).
            """)

    # =========================================================
    # TAB 4: FIREBASE FIRESTORE & HOSTING
    # =========================================================
    with tab_firebase:
        b_fb = _get_badge(matrix, "firebase")
        st.markdown(f"#### 🔥 Firebase Firestore & Hosting {b_fb}")
        st.caption("Persistencia y sincronización en la nube de proyectos, metadatos y preferencias.")

        col_fb1, col_fb2 = st.columns(2, gap="medium")
        with col_fb1:
            fb_pid = st.text_input("Firebase Project ID:", value=config.app.get("firebase_project_id", "ayuda-emilio-83261"), key="s_fb_pid")
            config.app["firebase_project_id"] = fb_pid
            
            fb_url = st.text_input("URL de Hosting Público:", value=config.app.get("firebase_hosting_url", "https://videopro-studio.web.app"), key="s_fb_hurl")
            config.app["firebase_hosting_url"] = fb_url

        with col_fb2:
            st.markdown("**Acciones de Sincronización con Firestore:**")
            if st.button("📤 Guardar Configuración en Firestore Ahora", use_container_width=True, key="btn_fb_save_now"):
                ok, msg = firebase_sync.save_settings_to_firebase()
                if ok:
                    st.session_state["flash_message"] = ("success", msg)
                    st.rerun()
                else:
                    st.session_state["flash_message"] = ("error", msg)
                    st.rerun()

            if st.button("📥 Restaurar Configuración desde Firestore", use_container_width=True, key="btn_fb_load_now"):
                ok, msg = firebase_sync.load_settings_from_firebase()
                if ok:
                    st.session_state["flash_message"] = ("success", msg)
                    st.rerun()
                else:
                    st.session_state["flash_message"] = ("error", msg)
                    st.rerun()

    # =========================================================
    # TAB 5: AJUSTES DEL SISTEMA & RENDER FFMPEG
    # =========================================================
    with tab_system:
        st.markdown("#### ⚙️ Parámetros del Motor de Render & Concurrencia")
        col_sys1, col_sys2 = st.columns(2, gap="medium")
        with col_sys1:
            max_conc = st.slider("Concurrencia Máxima de Generación de Escenas:", min_value=1, max_value=8, value=int(config.app.get("max_concurrent_scenes", 3)), key="s_sys_conc")
            config.app["max_concurrent_scenes"] = max_conc

            crf_val = st.slider("Calidad de Codificación FFmpeg (CRF - Menor es mayor calidad):", min_value=14, max_value=28, value=int(config.app.get("ffmpeg_crf", 19)), key="s_sys_crf")
            config.app["ffmpeg_crf"] = crf_val

        with col_sys2:
            preset_val = st.selectbox("Preset de Codificación x264/NVENC:", ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"], index=2, key="s_sys_preset")
            config.app["ffmpeg_preset"] = preset_val

            keep_temp = st.toggle("Conservar fotogramas temporales y WAVs intermedios", value=config.app.get("keep_temp_files", False), key="s_sys_temp")
            config.app["keep_temp_files"] = keep_temp

    # =========================================================
    # TAB 6: IDIOMA DE LA INTERFAZ
    # =========================================================
    with tab_lang:
        st.markdown("#### 🌐 Idioma y Localización de la Interfaz")
        col_l1, col_l2 = st.columns([1, 1])
        with col_l1:
            cur_lang = config.ui.get("language", "es")
            lang_opts = ["es", "en", "zh-CN", "zh-TW", "ja", "ko", "ru", "fr", "de"]
            lang_labels = {
                "es": "🇪🇸 Español (Castellano)",
                "en": "🇬🇧 English (International)",
                "zh-CN": "🇨🇳 简体中文 (Simplified Chinese)",
                "zh-TW": "🇹🇼 繁體中文 (Traditional Chinese)",
                "ja": "🇯🇵 日本語 (Japanese)",
                "ko": "🇰🇷 한국어 (Korean)",
                "ru": "🇷🇺 Русский (Russian)",
                "fr": "🇫🇷 Français (French)",
                "de": "🇩🇪 Deutsch (German)"
            }
            sel_lang = st.selectbox(
                "Seleccionar Idioma de VideoPro:",
                options=lang_opts,
                index=lang_opts.index(cur_lang) if cur_lang in lang_opts else 0,
                format_func=lambda x: lang_labels.get(x, x),
                key="s_lang_sel"
            )
            if sel_lang != cur_lang:
                config.ui["language"] = sel_lang
                st.toast(f"Idioma cambiado a {lang_labels.get(sel_lang, sel_lang)}")
                st.rerun()
