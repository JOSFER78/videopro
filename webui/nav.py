"""
Módulo de Navegación Superior Sobria y Ultra-Compacta — VideoPro
Estilo 100% sobrio, monocromático, limpio, sin colores estridentes ni emoticonos.
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
    """
    Renderiza la barra de navegación superior minimalista y sobria (sin colores llamativos).
    """
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "main"

    active = st.session_state["active_view"]

    st.markdown("""
    <style>
    /* 1. Eliminar cabeceras nativas y sidebars */
    section[data-testid="stSidebar"], 
    .stAppDeployButton, 
    [data-testid="stSidebarCollapsedControl"], 
    header[data-testid="stHeader"],
    #MainMenu, footer {
    }
    
    /* 2. Tema sobrio, neutral y oscuro profesional */
    .stApp {
    }
    .block-container {
    }

    /* 3. Espaciado ultra denso */
    [data-testid="stVerticalBlock"] {
    }
    [data-testid="stHorizontalBlock"] {
    }

    /* 4. Tipografía sobria y pequeña */
    h1, h2, h3, h4, h5, h6 {
    }
    p, span, label, div {
    }
    .stCaption, [data-testid="stCaptionContainer"] {
    }

    /* 5. Botones sobrios sin colores primarios rojos o chillones */
    .stButton > button {
    }
    .stButton > button:hover {
    }
    .stButton > button:active, .stButton > button:focus {
    }

    /* Botones de navegación activa (sobrio blanco sobre gris oscuro) */
    .nav-active-btn button {
    }

    /* 6. Inputs y Controles sobrios */
    div[data-baseweb="input"], div[data-baseweb="select"] {
    }
    div[data-baseweb="input"] input {
    }
    label[data-testid="stWidgetLabel"] p {
    }
    .stTextArea textarea {
    }

    /* 7. Pestañas sobrias */
    div[data-baseweb="tab-list"] {
    }
    button[data-baseweb="tab"] {
    }
    button[data-baseweb="tab"][aria-selected="true"] {
    }

    /* 8. Contenedores */
    div[data-testid="stVerticalBlockBorderWrapper"] {
    }

    /* 9. Barra superior inline */
    .top-nav-brand {
        font-size: 0.78rem;
        font-weight: 700;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        height: 22px;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 1 única fila para Marca + 6 botones de navegación
    cols = st.columns([1.2, 1.4, 1.7, 1.3, 1.4, 1.4, 1.2])
    
    with cols[0]:
        st.markdown("<div class='top-nav-brand'>VideoPro</div>", unsafe_allow_html=True)

    for i, (view_key, view_label) in enumerate(NAV_VIEWS):
        is_active = (active == view_key)
        with cols[i + 1]:
            # Aplicar clase CSS si está activo
            if is_active:
                st.markdown("<div class='nav-active-btn'>", unsafe_allow_html=True)
            if st.button(view_label, key=f"nav_btn_{view_key}", use_container_width=True):
                if st.session_state["active_view"] != view_key:
                    st.session_state["active_view"] = view_key
                    st.rerun()
            if is_active:
                st.markdown("</div>", unsafe_allow_html=True)

    # Si estamos en una vista secundaria, botón de retorno sutil
    if active != "main":
        col_b, _ = st.columns([1.8, 8.2])
        with col_b:
            if st.button("Volver al Generador", key="btn_global_return_home", use_container_width=True):
                st.session_state["active_view"] = "main"
                st.rerun()
