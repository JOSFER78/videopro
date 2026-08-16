import os
import sys
import json
import time
import shutil
import glob
from datetime import datetime
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.models import const
from app.utils import utils

def render_view():
    st.title("Ajustes, Control de Proveedores y Gestión de Proyectos")
    st.caption("Administración integral de la infraestructura, matriz de proveedores, gestor de APIs y proyectos de producción.")

    tab_matrix, tab_apis, tab_projects, tab_llm, tab_voice, tab_video, tab_subs, tab_render, tab_storage = st.tabs([
        "Matriz de Proveedores",
        "Gestor de APIs & Tokens",
        "Gestión de Proyectos",
        "Proveedores LLM",
        "Motores de Voz & Música",
        "Vídeo & GPU",
        "Subtítulos & Rótulos",
        "Render & FFmpeg",
        "Almacenamiento S3 / R2"
    ])

    tasks_dir = utils.task_dir() if hasattr(utils, "task_dir") else os.path.join(BASE_DIR, "storage", "tasks")
    os.makedirs(tasks_dir, exist_ok=True)

    # ---------------------------------------------------------
    # TAB 1: MATRIZ DE PROVEEDORES (EXACTA DE INVESTIGACIONES/CAPACIDADES)
    # ---------------------------------------------------------
    with tab_matrix:
        st.subheader("Matriz de Motores, Infraestructura y Comportamientos")
        st.caption("Control interactivo de los 14 motores verificados, reglas de calidad, descarte y comprobador en vivo de puertos.")

        matrix_file = "/home/ubuntu/workspace/pro/hermes/10_videopro/investigaciones/capacidades/proveedores_excel.html"
        
        if os.path.exists(matrix_file):
            try:
                with open(matrix_file, "r", encoding="utf-8") as f:
                    matrix_html = f.read()
                components.html(matrix_html, height=950, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar la tabla de proveedores: {e}")
        else:
            st.error(f"No se encontró el archivo de matriz en: {matrix_file}")


    # ---------------------------------------------------------
    # TAB 2: GESTOR DE APIS & TOKENS
    # ---------------------------------------------------------
    with tab_apis:
        st.subheader("Gestión Centralizada de Claves API & Tokens")
        st.caption("Configura y valida todas las claves de los 14 motores del ecosistema.")

        c_api1, c_api2 = st.columns(2)
        with c_api1:
            st.markdown("#### Modelos de Lenguaje & Director")
            gemini_key = st.text_input("Google Gemini API Key (AI Studio):", value=config.app.get("gemini_api_key", ""), type="password", key="api_gemini_k")
            config.app["gemini_api_key"] = gemini_key

            groq_key = st.text_input("Groq Cloud API Key:", value=config.app.get("groq_api_key", ""), type="password", key="api_groq_k")
            config.app["groq_api_key"] = groq_key

            openai_key = st.text_input("OpenAI API Key:", value=config.app.get("openai_api_key", ""), type="password", key="api_openai_k")
            config.app["openai_api_key"] = openai_key

            anthropic_key = st.text_input("Anthropic Claude API Key:", value=config.app.get("anthropic_api_key", ""), type="password", key="api_anthropic_k")
            config.app["anthropic_api_key"] = anthropic_key

            st.markdown("---")
            st.markdown("#### Clúster de GPU & Vídeo")
            rep_token = st.text_input("Replicate API Token (H100):", value=config.app.get("replicate_api_token", ""), type="password", placeholder="r8_xxxxxxxxxxxxxxxxxxxx", key="api_rep_k")
            config.app["replicate_api_token"] = rep_token

            hf_tokens = config.serverless_pool.get("hf_tokens", []) if hasattr(config, "serverless_pool") else []
            hf_text = st.text_area("Hugging Face ZeroGPU Pool (uno por línea):", value="\n".join(hf_tokens), height=90, key="api_hf_k")
            config.serverless_pool["hf_tokens"] = [t.strip() for t in hf_text.split("\n") if t.strip()]

        with c_api2:
            st.markdown("#### Locución Vocal & Composición Musical")
            el_key = st.text_input("ElevenLabs API Key:", value=config.app.get("elevenlabs_api_key", ""), type="password", key="api_el_k")
            config.app["elevenlabs_api_key"] = el_key

            fish_key = st.text_input("Fish Audio API Key:", value=config.app.get("fish_audio_api_key", ""), type="password", key="api_fish_k")
            config.app["fish_audio_api_key"] = fish_key

            flow_session = st.text_input("Google Flow Music Token / Cookie de Sesión:", value=config.app.get("flowmusic_session", ""), type="password", key="api_flow_k")
            config.app["flowmusic_session"] = flow_session

            st.markdown("---")
            st.markdown("#### Almacenamiento Cloudflare R2 / S3")
            s3_ep = st.text_input("S3 / R2 Endpoint:", value=config.app.get("s3_endpoint", ""), key="api_s3_ep")
            config.app["s3_endpoint"] = s3_ep

            s3_acc = st.text_input("S3 Access Key:", value=config.app.get("s3_access_key", ""), type="password", key="api_s3_acc")
            config.app["s3_access_key"] = s3_acc

            s3_sec = st.text_input("S3 Secret Key:", value=config.app.get("s3_secret_key", ""), type="password", key="api_s3_sec")
            config.app["s3_secret_key"] = s3_sec

            s3_bkt = st.text_input("S3 Bucket:", value=config.app.get("s3_bucket", "videopro-masters"), key="api_s3_bkt")
            config.app["s3_bucket"] = s3_bkt


    # ---------------------------------------------------------
    # TAB 3: GESTIÓN DE PROYECTOS
    # ---------------------------------------------------------
    with tab_projects:
        st.subheader("Proyectos y Tareas de Producción")
        
        def get_all_projects():
            projects = []
            if os.path.isdir(tasks_dir):
                for entry in os.scandir(tasks_dir):
                    if entry.name.startswith(".") or not entry.is_dir():
                        continue
                    task_path = entry.path
                    task_id = entry.name
                    mtime = entry.stat().st_mtime
                    
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
                    
                    video_files = []
                    for ext in ("*.mp4", "*.mkv", "*.mov"):
                        video_files.extend(glob.glob(os.path.join(task_path, ext)))
                    
                    final_video = video_files[0] if video_files else ""
                    
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

        col_act1, col_act2 = st.columns([1, 2])
        with col_act1:
            with st.expander("Crear Nuevo Proyecto", expanded=False):
                new_title = st.text_input("Título / Asunto:", placeholder="Ej: Documental Marte 4K")
                new_script = st.text_area("Guion Inicial:", placeholder="Escribe o pega aquí la narración...")
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
                        st.error("Introduce un título para el proyecto.")

        with col_act2:
            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                search_query = st.text_input("Buscar proyecto:", placeholder="Buscar por título, ID o contenido...", label_visibility="collapsed")
            with col_f2:
                filter_status = st.selectbox("Filtrar:", ["Todos", "Completados con Vídeo", "Borradores / Sin Vídeo"], label_visibility="collapsed")

        filtered = all_projects
        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [p for p in filtered if q in p["subject"].lower() or q in p["task_id"].lower() or q in p["script"].lower()]
        
        if filter_status == "Completados con Vídeo":
            filtered = [p for p in filtered if p["has_video"]]
        elif filter_status == "Borradores / Sin Vídeo":
            filtered = [p for p in filtered if not p["has_video"]]

        if not filtered:
            st.info("No se encontraron proyectos.")
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
                                st.session_state["active_view"] = "main"
                                st.toast(f"Proyecto {p['task_id']} cargado. Redirigiendo al Generador...")
                                st.rerun()
                        
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

                    with st.expander("Detalles del Guion y Parámetros"):
                        st.text_area("Guion Completo:", value=p["script"], height=100, disabled=True, key=f"script_view_{p['task_id']}")
                        if p["params"]:
                            st.json(p["params"])


    # ---------------------------------------------------------
    # TAB 4: PROVEEDORES LLM
    # ---------------------------------------------------------
    with tab_llm:
        st.subheader("Modelos de Lenguaje & Director Creativo")
        st.caption("Configura los modelos de IA para la co-creación de guiones, escaletas y prompting DoP.")

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
            gem_key = st.text_input("Google Gemini API Key (AI Studio):", value=config.app.get("gemini_api_key", ""), type="password")
            config.app["gemini_api_key"] = gem_key

            groq_key = st.text_input("Groq Cloud API Key:", value=config.app.get("groq_api_key", ""), type="password")
            config.app["groq_api_key"] = groq_key

            openai_key = st.text_input("OpenAI API Key:", value=config.app.get("openai_api_key", ""), type="password")
            config.app["openai_api_key"] = openai_key

            anthropic_key = st.text_input("Anthropic Claude API Key:", value=config.app.get("anthropic_api_key", ""), type="password")
            config.app["anthropic_api_key"] = anthropic_key

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
    # TAB 5: MOTORES DE VOZ & MÚSICA
    # ---------------------------------------------------------
    with tab_voice:
        st.subheader("Síntesis Vocal, Clonación y Música")
        st.caption("Ajusta los motores de locución neural en español/inglés y generación musical.")

        voice_options = [
            "Kokoro TTS HD (Local 24kHz - $0 Puerto 7892)",
            "VibeVoice 1.5B (Local ZeroGPU)",
            "Edge TTS (Microsoft Cloud Gratuito)",
            "ElevenLabs Turbo v2.5",
            "Fish Audio (Clonación Zero-Shot)"
        ]
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
        st.subheader("Google Flow Music (Lyria 3 Pro)")
        flow_cookie = st.text_input("Flow Music Token / Cookie de Sesión (flowmusic.app):", value=config.app.get("flowmusic_session", ""), type="password")
        config.app["flowmusic_session"] = flow_cookie


    # ---------------------------------------------------------
    # TAB 6: VÍDEO & GPU
    # ---------------------------------------------------------
    with tab_video:
        st.subheader("Motores de Vídeo & Aceleración GPU")
        st.caption("Configuración de clústeres Hugging Face ZeroGPU y Replicate H100 para FLUX 3 y LTX-2.5.")

        st.markdown("**1. Pool de Tokens Hugging Face (ZeroGPU - FLUX 3 & LTX-2.5)**")
        hf_tokens = config.serverless_pool.get("hf_tokens", []) if hasattr(config, "serverless_pool") else []
        if not hf_tokens:
            hf_tokens = ["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", "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"]

        st.caption(f"Tokens activos en rotación: {len(hf_tokens)}")
        
        hf_pool_text = st.text_area("Lista de Tokens Hugging Face (uno por línea):", value="\n".join(hf_tokens), height=100)
        config.serverless_pool["hf_tokens"] = [t.strip() for t in hf_pool_text.split("\n") if t.strip()]

        st.markdown("---")
        st.markdown("**2. Replicate Cloud (Inferencia Instantánea en H100)**")
        rep_key = st.text_input("Replicate API Token:", value=config.app.get("replicate_api_token", ""), type="password", placeholder="r8_xxxxxxxxxxxxxxxxxxxx")
        config.app["replicate_api_token"] = rep_key

        prio_rep = st.checkbox("Priorizar Replicate sobre ZeroGPU para evitar colas de espera", value=config.app.get("use_replicate_priority", False))
        config.app["use_replicate_priority"] = prio_rep


    # ---------------------------------------------------------
    # TAB 7: SUBTÍTULOS & RÓTULOS
    # ---------------------------------------------------------
    with tab_subs:
        st.subheader("Subtítulos Dinámicos ASS & Whisper")
        st.caption("Configuración de transcripción por IA para karaoke dinámico estilo Vox / Bloomberg.")

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            whisper_providers = ["Groq Whisper Cloud (Ultra-Rápido)", "Whisper Local CPU", "OpenAI Whisper API"]
            sel_whisper = st.selectbox("Proveedor de Transcripción Whisper:", whisper_providers, index=0)
            config.app["whisper_provider"] = sel_whisper

            words_per_sub = st.slider("Palabras máximas por línea en subtítulos:", 1, 6, int(config.app.get("subtitle_max_words", 2)))
            config.app["subtitle_max_words"] = words_per_sub

        with col_sub2:
            sub_styles = ["Vox Highlight (Amarillo Dinámico)", "TikTok Pop (Blanco con Borde)", "Minimalist Clean (Transparente)"]
            sel_sub_style = st.selectbox("Estilo Visual de Subtítulos:", sub_styles, index=0)
            config.app["subtitle_style"] = sel_sub_style


    # ---------------------------------------------------------
    # TAB 8: RENDER Y FFMPEG
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
    # TAB 9: ALMACENAMIENTO S3 / R2
    # ---------------------------------------------------------
    with tab_storage:
        st.subheader("Rutas del Sistema & Almacenamiento S3 / R2")
        st.caption("Configuración de directorios de trabajo y almacenamiento en Cloudflare R2.")

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
    if st.button("Guardar Ajustes y Configuración", type="primary", use_container_width=True):
        try:
            if hasattr(config, "save_config"):
                config.save_config()
            st.success("Configuración guardada correctamente en config.toml.")
        except Exception as e:
            st.error(f"Error al guardar la configuración: {e}")
