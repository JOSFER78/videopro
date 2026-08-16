import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
from webui.nav import render_top_navigation
import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="Matriz Maestra Live — VideoPro", layout="wide")

# Barra de navegacion superior
render_top_navigation()

col_back, col_title = st.columns([1.5, 8.5], vertical_alignment="center")
with col_back:
    st.page_link("Main.py", label="← Volver al Inicio")
with col_title:
    st.title("Matriz Maestra Live")
st.caption("Monitor de telemetria y estado de servicios en vivo.")


# Custom CSS


st.title("📊 Matriz Maestra de Proveedores, Infraestructura & Opciones en Vivo")
st.caption("Configuración atómica asistida por IA con sincronización en tiempo real de APIs (Replicate josfer78, ZeroGPU, Cloudflare R2, Kokoro 7892, Bridge 8742).")

html_file_path = "/home/ubuntu/MoneyPrinterTurbo/docs/architecture/proveedores_excel.html"

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=950, scrolling=True)
else:
    st.error("No se encontró el archivo de matriz interactiva en docs/architecture/proveedores_excel.html")
