import os
import streamlit as st
import streamlit.components.v1 as components

def render_view():
    st.title("Matriz Maestra Live")
    st.caption("Monitor interactivo de capacidades, proveedores, infraestructura y opciones del ecosistema VideoPro.")

    possible_paths = [
        "/home/ubuntu/workspace/pro/hermes/10_videopro/investigaciones/capacidades/proveedores_excel.html",
        "/home/ubuntu/MoneyPrinterTurbo/docs/architecture/proveedores_excel.html"
    ]
    
    html_code = None
    for p in possible_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    html_code = f.read()
                break
            except Exception:
                pass

    if html_code:
        components.html(html_code, height=950, scrolling=True)
    else:
        st.info("Visualizador de matriz interactiva no encontrado en rutas locales.")
