import streamlit as st

def render_top_navigation(current_page=""):
    """
    Barra de navegacion superior limpia, sobria y horizontal.
    Sin colores estridentes ni emoticonos.
    """
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:has(a[data-testid="stPageLink-NavLink"]) {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 4px 8px;
        margin-bottom: 16px;
        align-items: center;
    }
    a[data-testid="stPageLink-NavLink"] {
        padding: 4px 10px !important;
        border-radius: 4px !important;
        font-size: 13px !important;
        color: #cbd5e1 !important;
        transition: background 0.15s ease !important;
    }
    a[data-testid="stPageLink-NavLink"]:hover {
        background: #1e293b !important;
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns([1.3, 1.1, 1.1, 0.9, 1.1, 1.0, 1.0, 1.5, 0.9, 0.7], vertical_alignment="center", gap="small")
    
    with cols[0]:
        st.page_link("Main.py", label="Inicio / Generador")
    with cols[1]:
        st.page_link("pages/1_LTX25_FLUX3_Studio.py", label="LTX & FLUX")
    with cols[2]:
        st.page_link("pages/2_Voice_Studio.py", label="Voice Studio")
    with cols[3]:
        st.page_link("pages/3_Serverless_API_Hub.py", label="API Hub")
    with cols[4]:
        st.page_link("pages/4_Cinema_Player.py", label="Cinema Player")
    with cols[5]:
        st.page_link("pages/6_Flow_Music_Studio.py", label="Flow Music")
    with cols[6]:
        st.page_link("pages/7_Matriz_Maestra_Live.py", label="Matriz Live")
    with cols[7]:
        st.page_link("pages/8_Ajustes_y_Gestion_de_Proyectos.py", label="Ajustes y Proyectos")
    with cols[8]:
        st.page_link("pages/9_Boveda_Multimedia.py", label="Boveda")
    with cols[9]:
        st.page_link("pages/5_Docs_Guia_Maestra.py", label="Guia")
