"""
VideoPro Studio — Copilot Lateral Desplegable (Floating Drawer & AI Assistant)
Archivo: webui/components/copilot_drawer.py
"""

import json
import urllib.request
import urllib.error
from typing import Generator, Any, Optional, Dict, List
import streamlit as st

COPILOT_CSS = """
<style>
/* Variables de Diseño Dark Glassmorphism */
:root {
    --vp-bg-glass: rgba(15, 23, 42, 0.88);
    --vp-border-glass: rgba(56, 189, 248, 0.28);
    --vp-border-glow: rgba(56, 189, 248, 0.6);
    --vp-primary: #38bdf8;
    --vp-secondary: #818cf8;
    --vp-accent-emerald: #34d399;
    --vp-accent-purple: #c084fc;
    --vp-text-main: #f8fafc;
    --vp-text-muted: #94a3b8;
    --vp-card-bg: rgba(30, 41, 59, 0.7);
}

.vp-page-summary-card {
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(129, 140, 248, 0.05) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}

.vp-summary-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #38bdf8;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.vp-summary-text {
    font-size: 13px;
    line-height: 1.45;
    color: #e2e8f0;
    margin: 0;
}

.vp-quick-actions-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin: 12px 0 8px 0;
}

.vp-chat-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #38bdf8;
}

.vp-status-dot-live {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #34d399;
    box-shadow: 0 0 8px #34d399;
}
</style>
"""

PAGE_KNOWLEDGE_BASE = {
    "Preproducción": {
        "summary": "Estructura la investigación documental estándar BBC y define el estilo visual. Genera el desglose de escenas y personajes con continuidad.",
        "actions": [
            {"label": "🎬 Dossier BBC", "prompt": "Genera el dossier de investigación estilo BBC para el tema actual con fuentes verificadas."},
            {"label": "🎭 Estilo Vox Box", "prompt": "Configura la dirección de arte en estilo Vox Box 2.5D con capas kraft y rótulos Bloomberg."},
            {"label": "⏱️ Pacing WPS", "prompt": "Calcula el ritmo de locución óptimo (WPS) para una duración total de 60 segundos."}
        ]
    },
    "YouTube Monetization": {
        "summary": "Centro de Mando de Monetización y Canales: Aprende la economía de YouTube (RPM Tier 1), diagnostica el potencial de tus proyectos, genera SEO optimizado y audita el pipeline de producción.",
        "actions": [
            {"label": "💰 Explicar RPM Tier 1", "prompt": "¿Por qué los países de habla inglesa pagan hasta $35 RPM y cómo puedo adaptar mi canal para monetizar más?"},
            {"label": "🔍 Analizar Nicho", "prompt": "Evalúa el potencial del canal ChronoDrift y dime qué temáticas de viajes temporales tienen mayor CTR."},
            {"label": "🛡️ Evitar Desmonetización", "prompt": "¿Cómo previene VideoPro Studio el problema de 'contenido repetitivo con IA' en YouTube?"}
        ]
    },
    "Dashboard": {
        "summary": "Panel central de VideoPro Studio: supervisa el estado de los proyectos activos, la conectividad con Antigravity (puerto 8742) y los recursos de GPU/almacenamiento en disco.",
        "actions": [
            {"label": "📊 Resumen de Estado", "prompt": "Haz un chequeo general de los servicios: Antigravity CLI 8742 y estado del pipeline."},
            {"label": "🎬 Crear Nuevo Proyecto", "prompt": "Guíame paso a paso para inicializar un nuevo documental corto de 60 segundos."}
        ]
    }
}

def stream_copilot_response(
    messages: list[dict],
    page_name: str,
    page_context: dict | None = None,
    endpoint_url: str = "http://127.0.0.1:8742/v1/chat/completions",
    model_name: str = "gemini-3.6-flash-high"
) -> Generator[str, None, None]:
    system_prompt = (
        f"Eres el Copilot Técnico y Mentor Pedagógico de VideoPro Studio (Hermes Agent).\n"
        f"PANTALLA ACTUAL DEL USUARIO: {page_name}.\n"
        f"CONTEXTO ACTIVO: {json.dumps(page_context or {}, ensure_ascii=False)}.\n\n"
        f"DIRECTRICES DE RESPUESTA (MODO PRINCIPIANTE / 12 AÑOS):\n"
        f"1. Sé conciso, claro, didáctico y muy positivo. Usa analogías cotidianas para explicar fallos o términos técnicos.\n"
        f"2. Explica exactamente qué botones pulsar o qué valores ajustar en la pantalla actual.\n"
        f"3. Idioma obligatorio: Español."
    )

    payload = {
        "model": model_name,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": True,
        "temperature": 0.35,
        "max_tokens": 1500
    }

    req = urllib.request.Request(
        endpoint_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            for line in response:
                line_str = line.decode("utf-8").strip()
                if not line_str or line_str.startswith(":"):
                    continue
                if line_str.startswith("data: "):
                    data_body = line_str[6:]
                    if data_body == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_body)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except Exception as err:
        yield f"💡 **Consejo del Mentor:** El asistente de IA opera con el motor de inferencia local. (Aviso: `{err}`).\n\n"
        yield "¡Puedes seguir usando todas las funciones de la interfaz mientras el servidor de inferencia se actualiza!"

def render_copilot_drawer(
    page_name: str = "Dashboard",
    page_summary: str | None = None,
    page_context: dict | None = None,
    quick_actions: list[dict] | None = None,
    endpoint_url: str = "http://127.0.0.1:8742/v1/chat/completions",
    default_model: str = "gemini-3.6-flash-high"
) -> None:
    st.markdown(COPILOT_CSS, unsafe_allow_html=True)

    if "copilot_open" not in st.session_state:
        st.session_state.copilot_open = False
    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = []
    if "copilot_model" not in st.session_state:
        st.session_state.copilot_model = default_model
    if "copilot_pending_prompt" not in st.session_state:
        st.session_state.copilot_pending_prompt = None

    page_info = PAGE_KNOWLEDGE_BASE.get(page_name, {
        "summary": page_summary or f"Pantalla de {page_name} en VideoPro Studio. Aquí puedes aprender y gestionar tus contenidos paso a paso.",
        "actions": quick_actions or [
            {"label": "🔍 ¿Qué hace esta pantalla?", "prompt": f"Explícame para qué sirve la pantalla de {page_name} en palabras sencillas."},
            {"label": "⚡ ¿Qué debo hacer aquí?", "prompt": f"¿Cuál es el siguiente paso que debería hacer en {page_name}?"}
        ]
    })

    summary_text = page_summary or page_info["summary"]
    actions_list = quick_actions or page_info.get("actions", [])

    # Botón en cabecera / trigger
    col_main, col_trigger = st.columns([0.80, 0.20])
    with col_trigger:
        btn_label = "✖️ Ocultar Copilot" if st.session_state.copilot_open else "🤖 Mentor de IA"
        if st.button(btn_label, key=f"btn_copilot_toggle_{page_name}", use_container_width=True):
            st.session_state.copilot_open = not st.session_state.copilot_open
            st.rerun()

    if st.session_state.copilot_open:
        with st.sidebar:
            st.markdown(
                """
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div class="vp-chat-badge">
                        <div class="vp-status-dot-live"></div>
                        <span>Mentor IA • VideoPro Studio</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            c_mod, c_clear = st.columns([0.7, 0.3])
            with c_mod:
                selected_model = st.selectbox(
                    "Motor LLM",
                    options=["gemini-3.6-flash-high", "gemini-ultra", "claude-3-7-sonnet"],
                    index=0,
                    key="copilot_model_selector",
                    label_visibility="collapsed"
                )
                st.session_state.copilot_model = selected_model
            with c_clear:
                if st.button("🗑️", key="btn_clear_copilot_chat", use_container_width=True, help="Limpiar historial"):
                    st.session_state.copilot_messages = []
                    st.rerun()

            st.markdown(
                f"""
                <div class="vp-page-summary-card">
                    <div class="vp-summary-title">
                        🧭 ¿Qué hace esta pantalla? • {page_name}
                    </div>
                    <p class="vp-summary-text">{summary_text}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown('<div class="vp-quick-actions-title">⚡ Preguntas Rápidas</div>', unsafe_allow_html=True)
            qa_cols = st.columns(2)
            for idx, action in enumerate(actions_list):
                col = qa_cols[idx % 2]
                with col:
                    if st.button(action["label"], key=f"quick_action_{idx}_{page_name}", use_container_width=True):
                        st.session_state.copilot_pending_prompt = action["prompt"]
                        st.rerun()

            st.divider()

            chat_container = st.container(height=340)
            with chat_container:
                if not st.session_state.copilot_messages:
                    st.caption("👋 ¡Hola! Soy tu asistente de producción. Si no entiendes algún término o botón, pregúntame y te lo explico paso a paso.")
                
                for msg in st.session_state.copilot_messages:
                    avatar = "🎬" if msg["role"] == "assistant" else "👤"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])

            user_input = None
            if st.session_state.copilot_pending_prompt:
                user_input = st.session_state.copilot_pending_prompt
                st.session_state.copilot_pending_prompt = None
            else:
                user_input = st.chat_input("Pregúntame cualquier duda sobre esta pantalla...")

            if user_input:
                st.session_state.copilot_messages.append({"role": "user", "content": user_input})
                with chat_container:
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(user_input)

                    with st.chat_message("assistant", avatar="🎬"):
                        stream_gen = stream_copilot_response(
                            messages=st.session_state.copilot_messages,
                            page_name=page_name,
                            page_context=page_context,
                            endpoint_url=endpoint_url,
                            model_name=st.session_state.copilot_model
                        )
                        full_response = st.write_stream(stream_gen)
                
                st.session_state.copilot_messages.append({"role": "assistant", "content": full_response})
                st.rerun()
