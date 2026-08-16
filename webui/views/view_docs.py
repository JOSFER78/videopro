import streamlit as st

def render_view():
    st.markdown("**Guía Técnica y Estándares de Producción Netflix/Hollywood**")
    
    t1, t2, t3 = st.tabs([
        "Prompting DoP 7 Capas",
        "Consistencia de Actores (4 Anclas)",
        "Mastering de Audio 48kHz"
    ])

    with t1:
        st.markdown("""
- **Capa 1 (Sujeto & Acción):** Sujeto, micro-expresiones, vestuario y acción principal en presente.
- **Capa 2 (Entorno & Escenografía):** Arquitectura, volumen espacial, niebla atmosférica o partículas.
- **Capa 3 (Iluminación & Atmósfera):** Tipo de luz (Chiaroscuro, rim light, volumetric god rays, color temperature).
- **Capa 4 (Óptica & Cámara):** Lente específica (Cooke Anamorphic, ARRI Master Prime), apertura (T1.4), DoF.
- **Capa 5 (Movimiento de Cámara):** Vector de desplazamiento 6-DoF (Dolly in, crane shot, pan).
- **Capa 6 (Colorimetría & Textura):** LUT Film stock (Kodak Vision3 5219, ARRI Alexa LogC, Technicolor).
- **Capa 7 (Render & Aspecto):** 4K UHD, 24fps cinema cadence, photorealistic raw footage.
""")

    with t2:
        st.markdown("""
- **Ancla 1 (Rasgos Faciales Inmutables):** Estructura ósea, color de ojos y rasgos identitarios fijos.
- **Ancla 2 (Identificador de Nombre Único):** Uso de nombres propios constantes en cada plano.
- **Ancla 3 (Vestuario Coherente):** Descripción idéntica de vestimenta y accesorios clave por escena.
- **Ancla 4 (Consistencia Lumínica):** Mantener la misma clave de iluminación en la secuencia.
""")

    with t3:
        st.markdown("""
- **Locución Principal:** Masterizada a 24kHz / 48kHz con normalización ITU-R BS.1770-4 a -14 LUFS.
- **Sidechain Ducking:** Atenuación automática de música de fondo de -18dB a -24dB cuando hay voz activa.
- **Foley & FX:** 48kHz estéreo posicionado espacialmente en el timeline.
""")
