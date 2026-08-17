"""
05_learning_and_workflows.py
============================
Página Web Interactiva de Aprendizaje Continuo y Control de Workflows — VideoPro Studio.
Accesible de forma directa como subpágina en el enrutamiento multipage de Streamlit y desde la barra superior.
"""

import os
import sys
from pathlib import Path

# Configurar path raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

st.set_page_config(
    page_title="Aprendizaje & Control de Workflows — VideoPro Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

from webui.nav import render_top_navigation
from webui.views.view_learning_workflows import render_learning_workflows_view

# Renderizar barra de navegación superior sincronizada
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "learning_workflows"

render_top_navigation()

# Renderizar vista principal de aprendizaje y workflows
render_learning_workflows_view()
