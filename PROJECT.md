# VideoPro Studio — Estudio Cinematográfico Híbrido Autónomo

## 1. Visión y Propósito
**VideoPro Studio** es la plataforma unificada y autónoma de generación, edición y renderizado de vídeos cinematográficos y cortos (Shorts, Reels, TikToks, YouTube).
Integra un pipeline multimodal de 3 vías (Stock DB, FLUX 3 / LTX Video y Google Flow vía Playwright con Gemini Omni Flash), síntesis de voz neuronal local con VibeVoice en español (`es-emilio`), subtítulos dinámicos sincronizados y montaje automatizado con FFmpeg.

## 2. Arquitectura y Despliegue en VPS
- **Acceso Público HTTPS:** [`https://143-47-35-167.sslip.io/pro/videopro/`](https://143-47-35-167.sslip.io/pro/videopro/)
- **Directorio Principal de VideoPro:** `/home/ubuntu/workspace/pro/hermes/10_videopro`
- **Frontend WebUI Streamlit:** Puerto `7001` (Hot-Reload activo)
- **Backend FastAPI & Orquestador:** Puerto `8080` (FastAPI REST)
- **Servicios Systemd:**
  - `moneyprinter-api.service` (FastAPI en puerto 8080)
  - `moneyprinter-webui.service` (Streamlit en puerto 7001)

## 3. Los 3 Modos de Generación por Escena
1. **Modo 1 (Stock DB):** Ingesta y recorte de clips de alta calidad desde base de datos local y scrapers Pexels/Pixabay.
2. **Modo 2 (FLUX.1 Keyframe 0 / LTX Video):** Generación de fotogramas de referencia de alta fidelidad (Textura 35mm RAW, grano Kodak Vision3 500T, ARRI Alexa color science, consistencia de personaje) + animación 2.5D con movimiento de cámara orgánico (Ken Burns pan/zoom).
3. **Modo 3 (Google Flow vía Playwright):** Automatización desatendida conectada por CDP a Google Flow con Gemini Omni Flash en Display :99, inyección de foto de referencia en el slot de ingredientes, envío de prompt 7D y descarga del MP4 generado.

## 4. Motor de Voz VibeVoice 1.5B
- **Ejecutable Python:** `/home/ubuntu/vibevoice-venv/bin/python`
- **Voz Principal:** `es-emilio` (Español nativo, entonación cinematográfica y control emocional vía CFG Scale 1.0 - 2.5 y tags como `(con entusiasmo)`, `(con seriedad)`).
- **Subtítulos Sincronizados:** Alineación temporal automática a nivel de frase y palabra sin costes de API externa.
