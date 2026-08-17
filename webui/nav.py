"""
Módulo de Navegación Superior y Tema Visual — VideoPro Studio
Diseño profesional, moderno, oscuro (Dark IDE Theme) con alta legibilidad.
"""

import streamlit as st

NAV_VIEWS = [
    ("studio", "🚀 Empezar"),
    ("hermes_control", "🤖 Hermes Control"),
    ("pipeline", "🏛️ Workflows"),
    ("projects", "📁 Proyectos"),
    ("youtube_monetization", "💰 Monetización & Canales"),
    ("cinema_vault", "🎞️ Bóveda Multimedia"),
    ("audio_studio", "🎙️ Audio & Voces"),
    ("settings", "⚙️ Ajustes"),
    ("docs", "📖 Documentación")
]

def render_top_navigation():
    if "active_view" not in st.session_state or st.session_state["active_view"] in ("main", "generator"):
        st.session_state["active_view"] = "home"

    active = st.session_state["active_view"]

    # Inyección de estilos CSS modernos, profesionales y legibles
    st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    section[data-testid="stSidebar"], 
    .stAppDeployButton, 
    [data-testid="stSidebarCollapsedControl"], 
    header[data-testid="stHeader"],
    #MainMenu, footer {
        display: none !important;
    }

    /* Tema oscuro profundo y tipografía refinada */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #070b14 !important;
        color: #cbd5e1 !important;
        font-size: 13px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Padding de página equilibrado */
    .block-container {
        padding: 8px 16px 24px 16px !important;
        max-width: 100% !important;
    }

    /* Espaciado vertical natural */
    [data-testid="stVerticalBlock"] {
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 8px !important;
    }

    /* Títulos sobrios y claros */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        margin: 4px 0 !important;
        line-height: 1.3 !important;
    }
    h1 { font-size: 18px !important; }
    h2 { font-size: 16px !important; }
    h3 { font-size: 14px !important; }
    h4 { font-size: 13px !important; }

    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 11.5px !important;
        color: #64748b !important;
    }

    /* Etiquetas de controles legibles y bien posicionadas */
    label, [data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        font-weight: 500 !important;
        margin-bottom: 4px !important;
        color: #94a3b8 !important;
    }

    /* Inputs y Selectboxes con altura estándar y texto visible */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        min-height: 34px !important;
        height: 34px !important;
        background-color: #0f172a !important;
        border-radius: 6px !important;
        border: 1px solid #334155 !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        height: 32px !important;
        font-size: 12.5px !important;
        padding: 4px 8px !important;
        color: #f8fafc !important;
    }

    div[data-baseweb="select"] span {
        font-size: 12px !important;
        color: #f8fafc !important;
    }

    /* Textareas con scroll y altura cómoda */
    .stTextArea textarea {
        font-size: 12.5px !important;
        padding: 8px 10px !important;
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }

    /* Botones estándar con buena interacción */
    .stButton button, [data-testid="stBaseButton-secondary"] {
        font-size: 11.5px !important;
        font-weight: 500 !important;
        height: 30px !important;
        min-height: 30px !important;
        padding: 0 10px !important;
        border-radius: 5px !important;
        border: 1px solid #334155 !important;
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
        white-space: nowrap !important;
    }

    .stButton button:hover, [data-testid="stBaseButton-secondary"]:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #475569 !important;
    }

    [data-testid="stBaseButton-primary"] {
        font-size: 11.5px !important;
        font-weight: 600 !important;
        height: 30px !important;
        min-height: 30px !important;
        padding: 0 12px !important;
        border-radius: 5px !important;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: 1px solid #3b82f6 !important;
        color: #ffffff !important;
        white-space: nowrap !important;
    }

    [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 0 8px rgba(59, 130, 246, 0.4) !important;
    }

    /* Pestañas (Tabs) claras y bien separadas */
    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        margin-bottom: 8px !important;
        border-bottom: 1px solid #1e293b !important;
        padding-bottom: 2px !important;
    }

    button[data-baseweb="tab"] {
        font-size: 12px !important;
        font-weight: 500 !important;
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 12px !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border-radius: 4px 4px 0 0 !important;
        border: none !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #e2e8f0 !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom: 2px solid #38bdf8 !important;
        font-weight: 600 !important;
    }

    /* Contenedores con borde */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 8px 12px !important;
        border-radius: 6px !important;
        border: 1px solid #1e293b !important;
        background-color: #0b1120 !important;
    }

    /* Separadores */
    hr {
        margin: 8px 0 !important;
        border-color: #1e293b !important;
    }

    /* Barra de navegación superior */
    .top-nav-container {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 0 8px 0;
        margin-bottom: 8px;
        border-bottom: 1px solid #1e293b;
    }
    /* Botón Logo Home */
    div:has(> button[key="nav_btn_home_logo"]) button,
    button[key="nav_btn_home_logo"] {
        font-weight: 800 !important;
        font-size: 12px !important;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.22), rgba(124, 58, 237, 0.22)) !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        color: #38bdf8 !important;
        border-radius: 6px !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.15) !important;
    }
    div:has(> button[key="nav_btn_home_logo"]) button:hover,
    button[key="nav_btn_home_logo"]:hover {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.4), rgba(124, 58, 237, 0.4)) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.35) !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Barra superior de navegación moderna con anchos proporcionados
    col_widths = [1.0] + [1.2] * len(NAV_VIEWS)
    cols = st.columns(col_widths, vertical_alignment="center")
    
    with cols[0]:
        is_home_active = (active == "home")
        logo_type = "primary" if is_home_active else "secondary"
        if st.button("🏠 Home", key="nav_btn_home_logo", help="🏠 Centro de Control & Resumen Global", type=logo_type, use_container_width=True):
            if st.session_state.get("active_view") != "home":
                st.session_state["active_view"] = "home"
                st.rerun()

    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        with cols[i + 1]:
            btn_type = "primary" if is_active else "secondary"
            if st.button(view_label, key=f"nav_btn_{view_key}", type=btn_type, use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()
