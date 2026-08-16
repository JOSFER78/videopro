import os
import sys
import json
import time
import shutil
import glob
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.utils import utils

def render_view():
    tab_projects, tab_matrix, tab_apis, tab_system = st.tabs([
        "Proyectos",
        "Matriz Proveedores",
        "Gestor APIs y Tokens",
        "Ajustes Sistema y Render"
    ])

    tasks_dir = utils.task_dir() if hasattr(utils, "task_dir") else os.path.join(BASE_DIR, "storage", "tasks")
    os.makedirs(tasks_dir, exist_ok=True)

    # ---------------------------------------------------------
    # TAB 1: PROYECTOS
    # ---------------------------------------------------------
    with tab_projects:
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
                    subject = params.get("video_subject") or script_data.get("script", "")[:45] or task_id
                    script_text = script_data.get("script", "")
                    
                    video_files = []
                    for ext in ("*.mp4", "*.mkv", "*.mov"):
                        video_files.extend(glob.glob(os.path.join(task_path, ext)))
                    final_video = video_files[0] if video_files else ""
                    
                    projects.append({
                        "task_id": task_id,
                        "task_path": task_path,
                        "subject": subject,
                        "script": script_text,
                        "params": params,
                        "final_video": final_video,
                        "mtime": mtime,
                        "has_video": bool(final_video and os.path.isfile(final_video))
                    })
            projects.sort(key=lambda p: p["mtime"], reverse=True)
            return projects

        all_projects = get_all_projects()
        
        # Fila superior de acciones
        c_top1, c_top2, c_top3 = st.columns([2.5, 3.5, 4.0])
        with c_top1:
            st.caption(f"Total: {len(all_projects)} proyectos ({sum(1 for p in all_projects if p['has_video'])} con vídeo)")
        with c_top2:
            search_query = st.text_input("Buscar:", placeholder="Filtrar por título o ID...", label_visibility="collapsed")
        with c_top3:
            with st.expander("Nuevo Proyecto", expanded=False):
                np_col1, np_col2 = st.columns([3, 1])
                with np_col1:
                    new_title = st.text_input("Título:", placeholder="Ej: Documental 4K", label_visibility="collapsed")
                with np_col2:
                    if st.button("Crear", type="primary", use_container_width=True):
                        if new_title.strip():
                            new_id = f"proj_{int(time.time())}"
                            new_folder = os.path.join(tasks_dir, new_id)
                            os.makedirs(new_folder, exist_ok=True)
                            with open(os.path.join(new_folder, "script.json"), "w", encoding="utf-8") as f:
                                json.dump({"script": "", "params": {"video_subject": new_title.strip()}}, f)
                            st.rerun()

        filtered = all_projects
        if search_query.strip():
            q = search_query.strip().lower()
            filtered = [p for p in filtered if q in p["subject"].lower() or q in p["task_id"].lower()]

        if not filtered:
            st.caption("No hay proyectos.")
        else:
            for p in filtered[:15]:
                with st.container(border=True):
                    c_info, c_acts = st.columns([6.5, 3.5])
                    with c_info:
                        f_time = datetime.fromtimestamp(p["mtime"]).strftime("%d/%m %H:%M")
                        st.markdown(f"**{p['subject']}** `{p['task_id']}` <span style='font-size:10px; color:#64748b;'>{f_time}</span>", unsafe_allow_html=True)
                    with c_acts:
                        b1, b2, b3, b4 = st.columns(4)
                        with b1:
                            if st.button("Cargar", key=f"ld_{p['task_id']}", use_container_width=True):
                                st.session_state["task_restore_candidate_id"] = p["task_id"]
                                st.session_state["active_view"] = "main"
                                st.rerun()
                        with b2:
                            if st.button("Clonar", key=f"cl_{p['task_id']}", use_container_width=True):
                                shutil.copytree(p["task_path"], os.path.join(tasks_dir, f"{p['task_id']}_c"))
                                st.rerun()
                        with b3:
                            if p["has_video"]:
                                if st.button("Ver", key=f"v_{p['task_id']}", use_container_width=True):
                                    st.session_state[f"show_{p['task_id']}"] = not st.session_state.get(f"show_{p['task_id']}", False)
                            else:
                                st.button("-", key=f"dis_{p['task_id']}", disabled=True, use_container_width=True)
                        with b4:
                            if st.button("Del", key=f"d_{p['task_id']}", use_container_width=True):
                                shutil.rmtree(p["task_path"])
                                st.rerun()
                    if st.session_state.get(f"show_{p['task_id']}", False) and p["has_video"]:
                        st.video(p["final_video"])

    # ---------------------------------------------------------
    # TAB 2: MATRIZ DE PROVEEDORES
    # ---------------------------------------------------------
    with tab_matrix:
        matrix_file = "/home/ubuntu/workspace/pro/hermes/10_videopro/investigaciones/capacidades/proveedores_excel.html"
        if os.path.exists(matrix_file):
            try:
                with open(matrix_file, "r", encoding="utf-8") as f:
                    matrix_html = f.read()
                components.html(matrix_html, height=650, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar matriz: {e}")
        else:
            st.error("Archivo de matriz no encontrado.")

    # ---------------------------------------------------------
    # TAB 3: GESTOR DE APIS & TOKENS (3 COLUMNAS COMPACTAS)
    # ---------------------------------------------------------
    with tab_apis:
        c_api1, c_api2, c_api3 = st.columns(3)
        with c_api1:
            st.markdown("**LLMs & Director**")
            gemini_key = st.text_input("Gemini API Key:", value=config.app.get("gemini_api_key", ""), type="password", key="api_gemini_k")
            config.app["gemini_api_key"] = gemini_key

            groq_key = st.text_input("Groq API Key:", value=config.app.get("groq_api_key", ""), type="password", key="api_groq_k")
            config.app["groq_api_key"] = groq_key

            openai_key = st.text_input("OpenAI Key:", value=config.app.get("openai_api_key", ""), type="password", key="api_openai_k")
            config.app["openai_api_key"] = openai_key

            anthropic_key = st.text_input("Claude Key:", value=config.app.get("anthropic_api_key", ""), type="password", key="api_anthropic_k")
            config.app["anthropic_api_key"] = anthropic_key

        with c_api2:
            st.markdown("**GPU & Vídeo (FLUX/LTX)**")
            rep_token = st.text_input("Replicate Token (H100):", value=config.app.get("replicate_api_token", ""), type="password", key="api_rep_k")
            config.app["replicate_api_token"] = rep_token

            hf_tokens = []
            if hasattr(config, "serverless_pool") and isinstance(config.serverless_pool, dict):
                hf_tokens = config.serverless_pool.get("hf_tokens", [])
            if not hf_tokens:
                hf_tokens = ["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", "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"]

            hf_text = st.text_area("HF ZeroGPU Tokens:", value="\n".join(hf_tokens), height=58, key="api_hf_k")
            if hasattr(config, "serverless_pool"):
                config.serverless_pool["hf_tokens"] = [t.strip() for t in hf_text.split("\n") if t.strip()]

        with c_api3:
            st.markdown("**Audio & Cloud Storage**")
            el_key = st.text_input("ElevenLabs Key:", value=config.app.get("elevenlabs_api_key", ""), type="password", key="api_el_k")
            config.app["elevenlabs_api_key"] = el_key

            fish_key = st.text_input("Fish Audio Key:", value=config.app.get("fish_audio_api_key", ""), type="password", key="api_fish_k")
            config.app["fish_audio_api_key"] = fish_key

            flow_session = st.text_input("Flow Music Token:", value=config.app.get("flowmusic_session", ""), type="password", key="api_flow_k")
            config.app["flowmusic_session"] = flow_session

            s3_ep = st.text_input("S3/R2 Endpoint:", value=config.app.get("s3_endpoint", ""), key="api_s3_ep")
            config.app["s3_endpoint"] = s3_ep

        c_save, _ = st.columns([2, 8])
        with c_save:
            if st.button("Guardar Claves API", type="primary", use_container_width=True, key="save_apis_btn"):
                try:
                    if hasattr(config, "save_config"): config.save_config()
                    st.toast("Claves guardadas.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # ---------------------------------------------------------
    # TAB 4: AJUSTES DEL SISTEMA & RENDER (3 COLUMNAS COMPACTAS)
    # ---------------------------------------------------------
    with tab_system:
        c_s1, c_s2, c_s3 = st.columns(3)
        with c_s1:
            st.markdown("**Renderizado FFmpeg**")
            codecs = ["libx264 (H.264 Universal)", "libx265 (HEVC 10-bit)", "h264_nvenc (NVIDIA)"]
            config.app["video_codec"] = st.selectbox("Códec:", codecs, index=0)
            
            resolutions = ["1080x1920 (9:16 Vertical)", "1920x1080 (16:9 Horizontal)", "1080x1080 (1:1 Cuadrado)"]
            config.app["default_resolution"] = st.selectbox("Resolución:", resolutions, index=0)

        with c_s2:
            st.markdown("**Cadencia y Rendimiento**")
            config.app["default_fps"] = st.selectbox("FPS:", [24, 30, 60], index=0)
            config.app["ffmpeg_threads"] = st.number_input("Hilos CPU:", 1, 32, int(config.app.get("ffmpeg_threads", 4)))

        with c_s3:
            st.markdown("**Subtítulos y Transcripción**")
            whisper_providers = ["Groq Whisper Cloud", "Whisper Local CPU", "OpenAI Whisper API"]
            config.app["whisper_provider"] = st.selectbox("Whisper:", whisper_providers, index=0)
            config.app["subtitle_max_words"] = st.slider("Palabras por línea:", 1, 6, int(config.app.get("subtitle_max_words", 2)))

        c_sys_save, _ = st.columns([2, 8])
        with c_sys_save:
            if st.button("Guardar Ajustes Sistema", type="primary", use_container_width=True, key="save_sys_btn"):
                try:
                    if hasattr(config, "save_config"): config.save_config()
                    st.toast("Ajustes guardados.")
                except Exception as e:
                    st.error(f"Error: {e}")
