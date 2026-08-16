"""
Módulo de Navegación Superior Ultra-Compacta (Single-Screen) — VideoPro
Estilo 100% sobrio, minimalista, ultra-compacto y sin emoticonos.
"""

import streamlit as st

NAV_VIEWS = [
    ("main", "Generador"),
    ("settings_projects", "Proyectos y Ajustes"),
    ("ltx_flux", "LTX & FLUX"),
    ("audio_studio", "Audio & Música"),
    ("cinema_vault", "Galería"),
    ("docs", "Guía")
]


def render_top_navigation():
    """
    Renderiza la barra de navegación superior ultra-minimalista y los estilos compactos.
    """
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "main"

    active = st.session_state["active_view"]

    st.markdown("""
    <style>
    /* 1. Ocultar sidebar y barras nativas de Streamlit */
    section[data-testid="stSidebar"], .stAppDeployButton, [data-testid="stSidebarCollapsedControl"], header[data-testid="stHeader"] {
    }
    
    /* 2. Contenedor principal ultra compacto - Ocupa toda la pantalla */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .block-container {
    }

    /* 3. Espaciado vertical mínimo */
    [data-testid="stVerticalBlock"] {
    }
    [data-testid="stHorizontalBlock"] {
    }

    /* 4. Tipografía mínima y elegante */
    h1 {
    }
    h2 {
    }
    h3, h4 {
    }
    p, span, label, div {
    }
    .stCaption, [data-testid="stCaptionContainer"] {
    }

    /* 5. Pestañas ultra compactas */
    div[data-baseweb="tab-list"] {
    }
    button[data-baseweb="tab"] {
    }

    /* 6. Botones mínimos */
    .stButton > button {
    }

    /* 7. Inputs, Textareas y Selectboxes ultra densos */
    div[data-baseweb="input"], div[data-baseweb="select"] {
    }
    div[data-baseweb="input"] input {
    }
    label[data-testid="stWidgetLabel"] {
    }
    label[data-testid="stWidgetLabel"] p {
    }
    .stTextArea textarea {
    }

    /* 8. Contenedores y Cards compactos */
    div[data-testid="stVerticalBlockBorderWrapper"] {
    }

    /* 9. Métricas compactas */
    div[data-testid="stMetric"] {
    }
    div[data-testid="stMetricValue"] {
    }
    div[data-testid="stMetricLabel"] {
    }

    /* 10. Expander ultra compacto */
    div[data-testid="stExpander"] details {
    }
    div[data-testid="stExpander"] details summary {
    }
    div[data-testid="stExpander"] details summary span {
    }
    div[data-testid="stExpander"] details div[data-testid="stExpanderDetails"] {
    }

    /* 11. Barra superior unificada mínima */
    .mini-brand-tag {
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #38bdf8;
        display: flex;
        align-items: center;
        height: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Barra horizontal ultra-mínima: Marca a la izquierda + 6 botones compactos
    cols = st.columns([1.6, 1.4, 1.7, 1.4, 1.5, 1.2, 1.2])
    
    with cols[0]:
        st.markdown("<div class='mini-brand-tag'>VideoPro <span style='font-size:0.65em; color:#94a3b8; margin-left:4px;'>v2.5</span></div>", unsafe_allow_html=True)

    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        btn_type = "primary" if is_active else "secondary"
        with cols[i + 1]:
            if st.button(view_label, key=f"nav_btn_{view_key}", type=btn_type, use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()

    # Si estamos en una vista secundaria, botón de retorno mínimo
    if active != "main":
        col_b, col_empty = st.columns([2.0, 8.0], vertical_alignment="center")
        with col_b:
            if st.button("← Volver al Generador", key="btn_global_return_home", type="secondary", use_container_width=True):
                st.session_state["active_view"] = "main"
                st.rerun()
