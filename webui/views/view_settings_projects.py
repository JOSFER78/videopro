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
        matrix_file = os.path.join(BASE_DIR, "docs", "investigaciones", "capacidades", "proveedores_excel.html")
        if not os.path.exists(matrix_file):
            matrix_file = os.path.join(BASE_DIR, "investigaciones", "capacidades", "proveedores_excel.html")
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
    # TAB 3: GESTOR DE APIS & TOKENS (ORGANIZADO POR TEMAS + LINKS + ASISTENTE)
    # ---------------------------------------------------------
    with tab_apis:
        subtab_llm, subtab_video, subtab_voice, subtab_music, subtab_storage, subtab_custom = st.tabs([
            "1. LLMs y Director",
            "2. Vídeo y Visual",
            "3. Voz y Locución",
            "4. Música y Foley",
            "5. Storage y CDN",
            "6. Añadir Proveedor (Asistente IA)"
        ])

        # --- SUBTAB 1: LLMs ---
        with subtab_llm:
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Google Gemini</b> (AI Studio)</span><a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["gemini_api_key"] = st.text_input("Gemini Key:", value=config.app.get("gemini_api_key", ""), type="password", key="api_gemini_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>Groq Cloud</b> (Llama 3.3 70B Fast)</span><a href='https://console.groq.com/keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["groq_api_key"] = st.text_input("Groq Key:", value=config.app.get("groq_api_key", ""), type="password", key="api_groq_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>OpenAI</b> (GPT-4o / Whisper)</span><a href='https://platform.openai.com/api-keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["openai_api_key"] = st.text_input("OpenAI Key:", value=config.app.get("openai_api_key", ""), type="password", key="api_openai_k", label_visibility="collapsed")

            with col_l2:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Anthropic Claude</b> (Claude 3.5 Sonnet)</span><a href='https://console.anthropic.com/settings/keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["anthropic_api_key"] = st.text_input("Claude Key:", value=config.app.get("anthropic_api_key", ""), type="password", key="api_anthropic_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>SiliconFlow</b> (DeepSeek / Qwen Serverless)</span><a href='https://cloud.siliconflow.cn/account/ak' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["siliconflow_api_key"] = st.text_input("SiliconFlow Key:", value=config.app.get("siliconflow_api_key", ""), type="password", key="api_silicon_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>DeepSeek Oficial</b> (DeepSeek-V3 / R1)</span><a href='https://platform.deepseek.com/api_keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["deepseek_api_key"] = st.text_input("DeepSeek Key:", value=config.app.get("deepseek_api_key", ""), type="password", key="api_deepseek_k", label_visibility="collapsed")

        # --- SUBTAB 2: VÍDEO & VISUAL ---
        with subtab_video:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Replicate</b> (Clúster GPU H100 FLUX / LTX)</span><a href='https://replicate.com/account/api-tokens' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener token ↗</a></div>", unsafe_allow_html=True)
                config.app["replicate_api_token"] = st.text_input("Replicate Token:", value=config.app.get("replicate_api_token", ""), type="password", key="api_rep_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>Fal.ai</b> (FLUX 1.1 Pro / Fast Video)</span><a href='https://fal.ai/dashboard/keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["fal_api_key"] = st.text_input("Fal Key:", value=config.app.get("fal_api_key", ""), type="password", key="api_fal_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>Pexels Video API</b> (Stock 4K Gratuito)</span><a href='https://www.pexels.com/api/new/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["pexels_api_key"] = st.text_input("Pexels Key:", value=config.app.get("pexels_api_key", ""), type="password", key="api_pexels_k", label_visibility="collapsed")

            with col_v2:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Hugging Face ZeroGPU Pool</b> (1 token por línea)</span><a href='https://huggingface.co/settings/tokens' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener tokens ↗</a></div>", unsafe_allow_html=True)
                hf_tokens = []
                if hasattr(config, "serverless_pool") and isinstance(config.serverless_pool, dict):
                    hf_tokens = config.serverless_pool.get("hf_tokens", [])
                if not hf_tokens:
                    hf_tokens = ["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", "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"]
                hf_text = st.text_area("HF Tokens:", value="\n".join(hf_tokens), height=55, key="api_hf_k", label_visibility="collapsed")
                if hasattr(config, "serverless_pool"):
                    config.serverless_pool["hf_tokens"] = [t.strip() for t in hf_text.split("\n") if t.strip()]

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>Pixabay API</b> (Stock Video y Foley)</span><a href='https://pixabay.com/api/docs/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["pixabay_api_key"] = st.text_input("Pixabay Key:", value=config.app.get("pixabay_api_key", ""), type="password", key="api_pixabay_k", label_visibility="collapsed")

        # --- SUBTAB 3: VOZ & LOCUCIÓN ---
        with subtab_voice:
            col_vo1, col_vo2 = st.columns(2)
            with col_vo1:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>ElevenLabs</b> (Cinema Voices & Voice Cloning)</span><a href='https://elevenlabs.io/app/settings/api-keys' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["elevenlabs_api_key"] = st.text_input("ElevenLabs Key:", value=config.app.get("elevenlabs_api_key", ""), type="password", key="api_el_k", label_visibility="collapsed")

                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center; margin-top:4px;'><span><b>Fish Audio</b> (Multilingual 48kHz SOTA)</span><a href='https://fish.audio/app/api-keys/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["fish_audio_api_key"] = st.text_input("Fish Audio Key:", value=config.app.get("fish_audio_api_key", ""), type="password", key="api_fish_k", label_visibility="collapsed")

            with col_vo2:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>MiniMax TTS</b> (Voice Large Studio)</span><a href='https://api.minimax.chat/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Obtener clave ↗</a></div>", unsafe_allow_html=True)
                config.app["minimax_api_key"] = st.text_input("MiniMax Key:", value=config.app.get("minimax_api_key", ""), type="password", key="api_minimax_k", label_visibility="collapsed")

                st.caption("Motores Locales Activos sin coste: **Kokoro TTS HD** (Puerto 7892) y **Edge-TTS Neural** (Puerto 7893).")

        # --- SUBTAB 4: MÚSICA & FOLEY ---
        with subtab_music:
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Google Flow Music</b> (Lyria 3 Pro Session Token)</span><a href='https://flowmusic.app/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Abrir Flow Music ↗</a></div>", unsafe_allow_html=True)
                config.app["flowmusic_session"] = st.text_input("Flow Music Token / Cookie:", value=config.app.get("flowmusic_session", ""), type="password", key="api_flow_k", label_visibility="collapsed")

            with col_m2:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Suno AI API</b> (Opcional v3 / v4)</span><a href='https://suno.com' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Web Oficial ↗</a></div>", unsafe_allow_html=True)
                config.app["suno_api_key"] = st.text_input("Suno Key:", value=config.app.get("suno_api_key", ""), type="password", key="api_suno_k", label_visibility="collapsed")

        # --- SUBTAB 5: STORAGE & CDN ---
        with subtab_storage:
            col_st1, col_st2 = st.columns(2)
            with col_st1:
                st.markdown("<div style='display:flex; justify-content:space-between; align-items:center;'><span><b>Cloudflare R2 / S3 Endpoint</b></span><a href='https://dash.cloudflare.com/' target='_blank' style='color:#60a5fa; font-size:10px; text-decoration:none;'>Consola R2 ↗</a></div>", unsafe_allow_html=True)
                config.app["s3_endpoint"] = st.text_input("Endpoint:", value=config.app.get("s3_endpoint", ""), key="api_s3_ep", label_visibility="collapsed")

                st.caption("Access Key:")
                config.app["s3_access_key"] = st.text_input("Access Key:", value=config.app.get("s3_access_key", ""), type="password", key="api_s3_acc", label_visibility="collapsed")

            with col_st2:
                st.caption("Secret Key:")
                config.app["s3_secret_key"] = st.text_input("Secret Key:", value=config.app.get("s3_secret_key", ""), type="password", key="api_s3_sec", label_visibility="collapsed")

                st.caption("Bucket Name:")
                config.app["s3_bucket"] = st.text_input("Bucket:", value=config.app.get("s3_bucket", "videopro-masters"), key="api_s3_bkt", label_visibility="collapsed")

        # --- SUBTAB 6: ASISTENTE IA PARA AÑADIR PROVEEDOR ---
        with subtab_custom:
            st.markdown("**Asistente para Añadir Nuevos Proveedores & Endpoints Custom**")
            st.caption("Registra cualquier motor compatible con OpenAI (vLLM, Ollama, Together AI, OpenRouter, Mistral, RunPod).")
            
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                new_p_name = st.text_input("Nombre Proveedor:", placeholder="Ej: Together AI / Local vLLM", key="cp_name")
                new_p_type = st.selectbox("Tipo de Motor:", ["LLM (Lenguaje)", "Vídeo / Imagen", "TTS (Voz)", "Música / Foley", "Storage"], key="cp_type")
            with cp2:
                new_p_url = st.text_input("Base URL:", placeholder="https://api.together.xyz/v1", key="cp_url")
                new_p_model = st.text_input("Modelo por Defecto:", placeholder="deepseek-ai/DeepSeek-V3", key="cp_model")
            with cp3:
                new_p_key = st.text_input("API Key / Token:", placeholder="sk-...", type="password", key="cp_key")
                if st.button("Registrar Nuevo Proveedor", type="primary", use_container_width=True, key="cp_btn"):
                    if new_p_name.strip() and new_p_url.strip():
                        custom_list = config.app.get("custom_providers", [])
                        if not isinstance(custom_list, list): custom_list = []
                        custom_list.append({
                            "name": new_p_name.strip(),
                            "type": new_p_type,
                            "base_url": new_p_url.strip(),
                            "model": new_p_model.strip(),
                            "key": new_p_key.strip(),
                            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        config.app["custom_providers"] = custom_list
                        if hasattr(config, "save_config"): config.save_config()
                        st.success(f"Proveedor {new_p_name} registrado correctamente.")
                        st.rerun()
                    else:
                        st.error("Indica al menos el nombre y la Base URL.")

            # Listado de custom registrados
            registered = config.app.get("custom_providers", [])
            if registered and isinstance(registered, list):
                st.markdown("**Proveedores Personalizados Activos:**")
                for idx, cp in enumerate(registered):
                    with st.container(border=True):
                        ci1, ci2 = st.columns([8, 2])
                        with ci1:
                            st.markdown(f"**{cp.get('name')}** ({cp.get('type')}) — `{cp.get('base_url')}` | Modelo: `{cp.get('model')}`")
                        with ci2:
                            if st.button("Eliminar", key=f"del_cp_{idx}", use_container_width=True):
                                registered.pop(idx)
                                config.app["custom_providers"] = registered
                                if hasattr(config, "save_config"): config.save_config()
                                st.rerun()

        st.markdown("---")
        c_save, _ = st.columns([2.5, 7.5])
        with c_save:
            if st.button("Guardar Todas las Claves API", type="primary", use_container_width=True, key="save_apis_btn"):
                try:
                    if hasattr(config, "save_config"): config.save_config()
                    st.toast("Todas las claves han sido guardadas y sincronizadas.")
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

        c_sys_save, _ = st.columns([2.5, 7.5])
        with c_sys_save:
            if st.button("Guardar Ajustes Sistema", type="primary", use_container_width=True, key="save_sys_btn"):
                try:
                    if hasattr(config, "save_config"): config.save_config()
                    st.toast("Ajustes guardados.")
                except Exception as e:
                    st.error(f"Error: {e}")
