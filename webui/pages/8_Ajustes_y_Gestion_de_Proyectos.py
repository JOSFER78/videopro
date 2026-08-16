import os
import sys
import json
import time
import shutil
import glob
from datetime import datetime
from pathlib import Path
import streamlit as st

# Setup base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.models import const
from app.utils import utils
from app.services import state as sm

st.set_page_config(
    page_title="Ajustes y Gestión de Proyectos — VideoPro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header simple y limpio (sin colores estridentes ni emojis excesivos)
st.title("Ajustes y Gestión de Proyectos")
st.caption("Administración de proyectos, historial de producción, motores de IA y configuración del sistema.")

# Pestañas principales
tab_projects, tab_llm, tab_voice, tab_video, tab_render, tab_storage = st.tabs([
    "Gestión de Proyectos",
    "Proveedores LLM",
    "Motores de Voz",
    "Vídeo y GPU",
    "Render y FFmpeg",
    "Almacenamiento y Rutas"
])

tasks_dir = utils.task_dir() if hasattr(utils, "task_dir") else os.path.join(BASE_DIR, "storage", "tasks")
os.makedirs(tasks_dir, exist_ok=True)

# ---------------------------------------------------------
# TAB 1: GESTIÓN DE PROYECTOS
# ---------------------------------------------------------
with tab_projects:
    st.subheader("Proyectos y Tareas de Producción")
    
    # 1. Escaneo de tareas / proyectos
    def get_all_projects():
        projects = []
        if os.path.isdir(tasks_dir):
            for entry in os.scandir(tasks_dir):
                if entry.name.startswith(".") or not entry.is_dir():
                    continue
                task_path = entry.path
                task_id = entry.name
                mtime = entry.stat().st_mtime
                
                # Leer script.json si existe
                script_file = os.path.join(task_path, "script.json")
                script_data = {}
                if os.path.isfile(script_file):
                    try:
                        with open(script_file, "r", encoding="utf-8") as f:
                            script_data = json.load(f)
                    except Exception:
                        pass
                
                params = script_data.get("params", {})
                subject = params.get("video_subject") or script_data.get("script", "")[:60] or task_id
                script_text = script_data.get("script", "")
                
                # Buscar vídeos finales
                video_files = []
                for ext in ("*.mp4", "*.mkv", "*.mov"):
                    video_files.extend(glob.glob(os.path.join(task_path, ext)))
                
                final_video = video_files[0] if video_files else ""
                
                # Tamaño de la carpeta
                folder_size = 0
                for root, _, files in os.walk(task_path):
                    for file in files:
                        try:
                            folder_size += os.path.getsize(os.path.join(root, file))
                        except Exception:
                            pass
                
                projects.append({
                    "task_id": task_id,
                    "task_path": task_path,
                    "subject": subject,
                    "script": script_text,
                    "params": params,
                    "final_video": final_video,
                    "mtime": mtime,
                    "size_mb": round(folder_size / (1024 * 1024), 2),
                    "has_video": bool(final_video and os.path.isfile(final_video))
                })
        
        projects.sort(key=lambda p: p["mtime"], reverse=True)
        return projects

    all_projects = get_all_projects()
    total_projects = len(all_projects)
    completed_projects = sum(1 for p in all_projects if p["has_video"])
    total_size_mb = sum(p["size_mb"] for p in all_projects)

    # Métricas
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total de Proyectos", total_projects)
    with col_m2:
        st.metric("Proyectos con Vídeo", completed_projects)
    with col_m3:
        st.metric("Borradores / En Proceso", total_projects - completed_projects)
    with col_m4:
        st.metric("Espacio Utilizado", f"{total_size_mb:.1f} MB")

    st.markdown("---")

    # Acciones superiores: Crear nuevo proyecto y filtros
    col_act1, col_act2 = st.columns([1, 2])
    with col_act1:
        with st.expander("Crear Nuevo Proyecto", expanded=False):
            new_title = st.text_input("Título / Asunto del Proyecto:", placeholder="Ej: Documental Marte 4K")
            new_script = st.text_area("Guion Inicial (opcional):", placeholder="Escribe o pega aquí la narración...")
            new_aspect = st.selectbox("Formato / Relación de Aspecto:", ["9:16 (Vertical TikTok/Reels)", "16:9 (Horizontal YouTube)", "1:1 (Cuadrado)"])
            
            if st.button("Guardar Proyecto", type="primary"):
                if new_title.strip():
                    new_id = f"project_{int(time.time())}"
                    new_folder = os.path.join(tasks_dir, new_id)
                    os.makedirs(new_folder, exist_ok=True)
                    
                    aspect_val = "9:16" if "9:16" in new_aspect else ("16:9" if "16:9" in new_aspect else "1:1")
                    proj_payload = {
                        "script": new_script.strip(),
                        "params": {
                            "video_subject": new_title.strip(),
                            "video_script": new_script.strip(),
                            "video_aspect": aspect_val
                        }
                    }
                    with open(os.path.join(new_folder, "script.json"), "w", encoding="utf-8") as f:
                        json.dump(proj_payload, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"Proyecto '{new_title}' creado con éxito.")
                    st.rerun()
                else:
                    st.error("Por favor, introduce un título para el proyecto.")

    with col_act2:
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            search_query = st.text_input("Buscar proyecto:", placeholder="Buscar por título, ID o contenido...", label_visibility="collapsed")
        with col_f2:
            filter_status = st.selectbox("Filtrar:", ["Todos", "Completados con Vídeo", "Borradores / Sin Vídeo"], label_visibility="collapsed")

    # Filtrar proyectos
    filtered = all_projects
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [p for p in filtered if q in p["subject"].lower() or q in p["task_id"].lower() or q in p["script"].lower()]
    
    if filter_status == "Completados con Vídeo":
        filtered = [p for p in filtered if p["has_video"]]
    elif filter_status == "Borradores / Sin Vídeo":
        filtered = [p for p in filtered if not p["has_video"]]

    # Listado de Proyectos
    if not filtered:
        st.info("No se encontraron proyectos que coincidan con la búsqueda o filtro.")
    else:
        for p in filtered:
            with st.container(border=True):
                c_info, c_actions = st.columns([3, 2])
                
                with c_info:
                    formatted_time = datetime.fromtimestamp(p["mtime"]).strftime("%Y-%m-%d %H:%M:%S")
                    status_text = "Completado" if p["has_video"] else "Borrador / Sin vídeo final"
                    
                    st.markdown(f"**{p['subject']}**")
                    st.caption(f"ID: `{p['task_id']}` | Fecha: {formatted_time} | Tamaño: {p['size_mb']} MB | Estado: **{status_text}**")
                    
                    if p["script"]:
                        preview_script = p["script"][:120] + ("..." if len(p["script"]) > 120 else "")
                        st.markdown(f"*{preview_script}*")

                with c_actions:
                    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                    
                    with btn_col1:
                        if st.button("Cargar", key=f"load_{p['task_id']}", help="Cargar en el Generador Principal"):
                            st.session_state["task_restore_candidate_id"] = p["task_id"]
                            st.toast(f"Proyecto {p['task_id']} preparado para restaurar.")
                    
                    with btn_col2:
                        if st.button("Clonar", key=f"clone_{p['task_id']}", help="Duplicar como nuevo proyecto"):
                            clone_id = f"{p['task_id']}_copia_{int(time.time())}"
                            clone_dir = os.path.join(tasks_dir, clone_id)
                            shutil.copytree(p["task_path"], clone_dir)
                            st.toast(f"Proyecto duplicado: {clone_id}")
                            st.rerun()

                    with btn_col3:
                        if p["has_video"]:
                            if st.button("Ver", key=f"preview_{p['task_id']}", help="Previsualizar vídeo"):
                                st.session_state[f"show_video_{p['task_id']}"] = not st.session_state.get(f"show_video_{p['task_id']}", False)
                        else:
                            st.button("Ver", key=f"preview_dis_{p['task_id']}", disabled=True)

                    with btn_col4:
                        if st.button("Borrar", key=f"del_{p['task_id']}", help="Eliminar proyecto"):
                            try:
                                shutil.rmtree(p["task_path"])
                                st.toast(f"Proyecto {p['task_id']} eliminado.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar: {e}")

                # Si se solicita previsualizar el vídeo
                if st.session_state.get(f"show_video_{p['task_id']}", False) and p["has_video"]:
                    st.video(p["final_video"])
                    with open(p["final_video"], "rb") as vf:
                        st.download_button(
                            label="Descargar Vídeo MP4",
                            data=vf.read(),
                            file_name=f"{p['task_id']}.mp4",
                            mime="video/mp4",
                            key=f"dl_{p['task_id']}"
                        )

                # Expander con detalles y script completo
                with st.expander("Detalles del Guion y Parámetros"):
                    st.text_area("Guion Completo:", value=p["script"], height=100, disabled=True, key=f"script_view_{p['task_id']}")
                    if p["params"]:
                        st.json(p["params"])


# ---------------------------------------------------------
# TAB 2: PROVEEDORES LLM
# ---------------------------------------------------------
with tab_llm:
    st.subheader("Modelos de Lenguaje & Director Creativo")
    st.caption("Configura los modelos de IA utilizados para estructurar guiones y escaletas cinematográficas.")

    current_llm_prov = config.app.get("llm_provider", "Gemini (Google AI Studio)")
    llm_providers = [
        "Gemini (Google AI Studio)",
        "Antigravity Bridge (Puerto 8742)",
        "Groq Cloud (Llama 3.3 / DeepSeek R1)",
        "OpenAI (GPT-4o / GPT-4.1)",
        "Anthropic Claude (Claude 3.7)",
        "DeepSeek Directo",
        "Ollama Local"
    ]
    sel_llm = st.selectbox("Proveedor LLM Principal:", llm_providers, index=0)
    config.app["llm_provider"] = sel_llm

    col_llm1, col_llm2 = st.columns(2)
    with col_llm1:
        gem_key = st.text_input("Google Gemini API Key:", value=config.app.get("gemini_api_key", ""), type="password")
        config.app["gemini_api_key"] = gem_key

        groq_key = st.text_input("Groq Cloud API Key:", value=config.app.get("groq_api_key", ""), type="password")
        config.app["groq_api_key"] = groq_key

        openai_key = st.text_input("OpenAI API Key:", value=config.app.get("openai_api_key", ""), type="password")
        config.app["openai_api_key"] = openai_key

    with col_llm2:
        model_name = st.text_input("Nombre del Modelo Específico:", value=config.app.get("llm_model_name", "gemini-2.5-flash"))
        config.app["llm_model_name"] = model_name

        temp = st.slider("Temperatura Creativa:", 0.0, 1.5, float(config.app.get("llm_temperature", 0.7)), 0.05)
        config.app["llm_temperature"] = temp

        max_tokens = st.number_input("Máximo de Tokens de Salida:", 512, 16384, int(config.app.get("llm_max_tokens", 4096)))
        config.app["llm_max_tokens"] = max_tokens

    st.text_area(
        "Prompt Maestro del Director Creativo:",
        value=config.app.get("director_prompt", "Eres un Director Creativo Cinematográfico de clase mundial. Analiza la petición del usuario y estructura guiones visuales con planos de cámara, iluminación, paleta cromática e indicaciones sonoras precisas."),
        height=120,
        key="cfg_director_prompt"
    )


# ---------------------------------------------------------
# TAB 3: MOTORES DE VOZ
# ---------------------------------------------------------
with tab_voice:
    st.subheader("Síntesis y Clonación Vocal")
    st.caption("Ajusta los motores de locución neural en español, clonación y composición musical.")

    voice_options = [
        "Kokoro TTS HD (Local 24kHz - $0)",
        "VibeVoice 1.5B (Local ZeroGPU)",
        "Edge TTS (Microsoft Cloud Gratuito)",
        "ElevenLabs Turbo v2.5",
        "Fish Audio (Clonación Zero-Shot)"
    ]
    cur_voice = config.app.get("voice_provider", voice_options[0])
    sel_voice = st.selectbox("Motor Vocal Predeterminado:", voice_options, index=0)
    config.app["voice_provider"] = sel_voice

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        el_key = st.text_input("ElevenLabs API Key:", value=config.app.get("elevenlabs_api_key", ""), type="password")
        config.app["elevenlabs_api_key"] = el_key

        fish_key = st.text_input("Fish Audio API Key:", value=config.app.get("fish_audio_api_key", ""), type="password")
        config.app["fish_audio_api_key"] = fish_key

    with col_v2:
        rate = st.slider("Velocidad de Locución Global (Rate):", 0.7, 1.5, float(config.app.get("voice_rate", 1.0)), 0.05)
        config.app["voice_rate"] = rate

        ducking = st.slider("Atenuación de Música / Ducking (dB):", -30, -6, int(config.app.get("ducking_level", -22)), 1)
        config.app["ducking_level"] = ducking

    st.markdown("---")
    st.subheader("Google Flow Music (Lyria 3)")
    flow_cookie = st.text_input("Flow Music Token / Cookie de Sesión:", value=config.app.get("flowmusic_session", ""), type="password")
    config.app["flowmusic_session"] = flow_cookie


# ---------------------------------------------------------
# TAB 4: VÍDEO Y GPU
# ---------------------------------------------------------
with tab_video:
    st.subheader("Motores de Vídeo & Aceleración GPU")
    st.caption("Configuración de clústeres Hugging Face ZeroGPU y Replicate H100.")

    st.markdown("**1. Pool de Tokens Hugging Face (ZeroGPU - FLUX 3 & LTX-2.5)**")
    hf_tokens = config.serverless_pool.get("hf_tokens", []) if hasattr(config, "serverless_pool") else []
    if not hf_tokens:
        hf_tokens = ["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", "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"]

    st.caption(f"Tokens activos en rotación: {len(hf_tokens)}")
    
    col_hf1, col_hf2 = st.columns([3, 1])
    with col_hf1:
        new_hf_tok = st.text_input("Añadir nuevo token Hugging Face:", type="password", placeholder="hf_xxxxxxxxxxxxxxxxxxxx")
    with col_hf2:
        if st.button("Añadir Token HF"):
            if new_hf_tok.strip() and new_hf_tok.strip() not in hf_tokens:
                hf_tokens.append(new_hf_tok.strip())
                st.toast("Token añadido al pool.")
                st.rerun()

    st.markdown("---")
    st.markdown("**2. Replicate Cloud (Inferencia Instantánea en H100)**")
    rep_key = st.text_input("Replicate API Token:", value=config.app.get("replicate_api_token", ""), type="password", placeholder="r8_xxxxxxxxxxxxxxxxxxxx")
    config.app["replicate_api_token"] = rep_key

    prio_rep = st.checkbox("Priorizar Replicate sobre ZeroGPU para evitar colas de espera", value=config.app.get("use_replicate_priority", False))
    config.app["use_replicate_priority"] = prio_rep


# ---------------------------------------------------------
# TAB 5: RENDER Y FFMPEG
# ---------------------------------------------------------
with tab_render:
    st.subheader("Parámetros de Renderizado de Vídeo")
    st.caption("Ajuste de códecs de compresión, hilos y formato por defecto.")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        codecs = ["libx264 (H.264 Universal)", "libx265 (HEVC 10-bit)", "h264_nvenc (NVIDIA Hardware)"]
        sel_codec = st.selectbox("Códec de Vídeo Primario:", codecs, index=0)
        config.app["video_codec"] = sel_codec

        resolutions = [
            "1080x1920 (Vertical 9:16 TikTok / Shorts)",
            "1920x1080 (Horizontal 16:9 YouTube / Cine)",
            "1080x1080 (Cuadrado 1:1 Instagram)"
        ]
        sel_res = st.selectbox("Resolución Predeterminada:", resolutions, index=0)
        config.app["default_resolution"] = sel_res

    with col_r2:
        fps_options = [24, 30, 60]
        sel_fps = st.selectbox("Tasa de Fotogramas (FPS):", fps_options, index=0)
        config.app["default_fps"] = sel_fps

        threads = st.number_input("Hilos de CPU para Renderizado FFmpeg:", 1, 32, int(config.app.get("ffmpeg_threads", 4)))
        config.app["ffmpeg_threads"] = threads


# ---------------------------------------------------------
# TAB 6: ALMACENAMIENTO Y RUTAS
# ---------------------------------------------------------
with tab_storage:
    st.subheader("Rutas del Sistema & Almacenamiento S3 / R2")
    st.caption("Configuración de directorios de trabajo y almacenamiento en la nube.")

    st.text_input("Directorio de Tareas y Proyectos:", value=tasks_dir, disabled=True)
    st.text_input("Directorio de Música de Fondo:", value=os.path.join(BASE_DIR, "resource", "songs"), disabled=True)
    st.text_input("Directorio de Fuentes Tipográficas:", value=os.path.join(BASE_DIR, "resource", "fonts"), disabled=True)

    st.markdown("---")
    st.subheader("Cloudflare R2 / AWS S3 Object Storage")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        s3_endpoint = st.text_input("S3 / R2 Endpoint URL:", value=config.app.get("s3_endpoint", ""), placeholder="https://<account_id>.r2.cloudflarestorage.com")
        config.app["s3_endpoint"] = s3_endpoint

        s3_access = st.text_input("S3 Access Key ID:", value=config.app.get("s3_access_key", ""), type="password")
        config.app["s3_access_key"] = s3_access

    with col_s2:
        s3_bucket = st.text_input("S3 Bucket Name:", value=config.app.get("s3_bucket", "videopro-masters"))
        config.app["s3_bucket"] = s3_bucket

        s3_secret = st.text_input("S3 Secret Access Key:", value=config.app.get("s3_secret_key", ""), type="password")
        config.app["s3_secret_key"] = s3_secret

    auto_r2 = st.checkbox("Subir automáticamente vídeos terminados a Cloudflare R2", value=config.app.get("auto_upload_r2", False))
    config.app["auto_upload_r2"] = auto_r2


# ---------------------------------------------------------
# BOTÓN GLOBAL DE GUARDADO
# ---------------------------------------------------------
st.markdown("---")
if st.button("Guardar Ajustes y Configuración", type="primary"):
    try:
        if hasattr(config, "save_config"):
            config.save_config()
        st.success("Configuración guardada correctamente en config.toml.")
    except Exception as e:
        st.error(f"Error al guardar la configuración: {e}")
