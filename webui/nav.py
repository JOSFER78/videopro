"""
Módulo de Navegación Superior Ultra-Compacta (Dense Dashboard) — VideoPro
Estilo 100% sobrio, ultra-compacto, monocromático, sin colores chillones ni emoticonos.
"""

import streamlit as st

NAV_VIEWS = [
    ("main", "Generador"),
    ("settings_projects", "Proyectos y Ajustes"),
    ("ltx_flux", "LTX y FLUX"),
    ("audio_studio", "Audio y Música"),
    ("cinema_vault", "Galería y Vídeos"),
    ("docs", "Guía Técnica")
]

def render_top_navigation():
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "main"

    active = st.session_state["active_view"]

    # Inyección de estilos de máxima densidad y escala ultra-compacta
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

    /* Base oscura y tamaño de fuente denso tipo IDE */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #070a11 !important;
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Padding de página mínimo */
    .block-container {
        padding: 4px 8px !important;
        max-width: 100% !important;
    }

    /* Espaciado mínimo entre bloques */
    [data-testid="stVerticalBlock"] {
        gap: 2px !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 4px !important;
    }

    /* Títulos sobrios y ultra compactos */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    h1 { font-size: 12px !important; }
    h2 { font-size: 11.5px !important; }
    h3, h4 { font-size: 11px !important; }
    p, span, div {
        font-size: 11px !important;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        font-size: 10px !important;
        color: #64748b !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Etiquetas de controles ultra compactas */
    label, [data-testid="stWidgetLabel"] p {
        font-size: 10.5px !important;
        font-weight: 500 !important;
        margin: 0 0 1px 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
        color: #94a3b8 !important;
    }

    /* Inputs, Selectboxes ultra compactos (22px de alto) */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="select"] > div {
        min-height: 22px !important;
        height: 22px !important;
        padding: 0 !important;
        background-color: #0f172a !important;
        border-radius: 2px !important;
        border: 1px solid #1e293b !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        height: 20px !important;
        font-size: 10.5px !important;
        padding: 1px 5px !important;
        color: #f1f5f9 !important;
    }

    div[data-baseweb="select"] span {
        font-size: 10.5px !important;
    }

    /* Botones ultra compactos (20px de alto, sobrios) */
    .stButton button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
        font-size: 10.5px !important;
        height: 20px !important;
        min-height: 20px !important;
        padding: 0 6px !important;
        line-height: 18px !important;
        border-radius: 2px !important;
        border: 1px solid #334155 !important;
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        box-shadow: none !important;
        margin: 0 !important;
    }
    .stButton button:hover {
        background-color: #334155 !important;
        color: #f8fafc !important;
        border-color: #475569 !important;
    }

    /* Pestañas ultra compactas (20px de alto) */
    div[data-baseweb="tab-list"] {
        gap: 2px !important;
        margin-bottom: 2px !important;
        border-bottom: 1px solid #1e293b !important;
    }
    button[data-baseweb="tab"] {
        font-size: 10.5px !important;
        height: 20px !important;
        min-height: 20px !important;
        padding: 0 6px !important;
        color: #64748b !important;
        background: transparent !important;
        border: none !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #f8fafc !important;
        border-bottom: 2px solid #64748b !important;
        font-weight: 600 !important;
    }

    /* Textareas compactas */
    .stTextArea textarea {
        font-size: 10.5px !important;
        padding: 2px 4px !important;
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        color: #f1f5f9 !important;
        border-radius: 2px !important;
    }

    /* Contenedores ultra compactos */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 2px 4px !important;
        border-radius: 2px !important;
        border: 1px solid #1e293b !important;
        background-color: #090e1a !important;
    }

    /* Métricas */
    div[data-testid="stMetric"] {
        padding: 1px 3px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #f8fafc !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 9.5px !important;
        color: #64748b !important;
    }

    /* Separadores */
    hr {
        margin: 2px 0 !important;
        border-color: #1e293b !important;
    }

    /* Barra de navegación superior */
    .top-bar-row {
        display: flex;
        align-items: center;
        gap: 4px;
        padding-bottom: 3px;
        margin-bottom: 3px;
        border-bottom: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1 sola fila ultra compacta para la navegación
    cols = st.columns([1.0, 1.3, 1.7, 1.3, 1.3, 1.4, 1.1])
    
    with cols[0]:
        st.markdown("<div style='font-size:11px; font-weight:700; color:#e2e8f0; line-height:20px;'>VideoPro</div>", unsafe_allow_html=True)

    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        with cols[i + 1]:
            label_text = f"• {view_label}" if is_active else view_label
            if st.button(label_text, key=f"nav_btn_{view_key}", use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()
