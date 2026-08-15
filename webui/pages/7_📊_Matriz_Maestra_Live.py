import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Matriz Maestra de Proveedores & APIs — VideoPro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 98%;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Matriz Maestra de Proveedores, Infraestructura & Opciones en Vivo")
st.caption("Configuración atómica asistida por IA con sincronización en tiempo real de APIs (Replicate josfer78, ZeroGPU, Cloudflare R2, Kokoro 7892, Bridge 8742).")

html_file_path = "/home/ubuntu/MoneyPrinterTurbo/docs/architecture/proveedores_excel.html"

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=950, scrolling=True)
else:
    st.error("No se encontró el archivo de matriz interactiva en docs/architecture/proveedores_excel.html")
