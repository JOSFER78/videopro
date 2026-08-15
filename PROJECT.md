# VideoPro Studio — Estudio Cinematográfico Híbrido Autónomo

## 1. Visión y Propósito
**VideoPro Studio** es la plataforma unificada y autónoma de generación, edición y renderizado de vídeos cinematográficos y cortos (Shorts, Reels, TikToks, YouTube) para el ecosistema `/home/ubuntu/workspace/pro/`.
Integra un pipeline multimodal de 3 vías (Stock DB, FLUX.1 Keyframe 0 y Google Flow vía Playwright con Gemini Omni Flash), síntesis de voz neuronal local con VibeVoice 1.5B a coste cero en español (`es-emilio`), subtítulos dinámicos sincronizados y montaje automatizado con FFmpeg 6.1.1.

## 2. Arquitectura y Despliegue en VPS
- **Acceso Público HTTPS:** [`https://143-47-35-167.sslip.io/pro/videopro/`](https://143-47-35-167.sslip.io/pro/videopro/)
- **Proxy API REST:** [`https://143-47-35-167.sslip.io/pro/videopro/api/`](https://143-47-35-167.sslip.io/pro/videopro/api/) (enrutado a `http://127.0.0.1:8080/`)
- **Documentación Swagger:** [`https://143-47-35-167.sslip.io/pro/videopro/api/docs`](https://143-47-35-167.sslip.io/pro/videopro/api/docs)
- **Directorio de Código y Workspace:** `/home/ubuntu/workspace/pro/webs/11-videopro/`
- **Directorio Web Estático Nginx:** `/var/www/pro/videopro/`
- **Motor Backend:** `/home/ubuntu/MoneyPrinterTurbo/`
- **Servicios Systemd:**
  - `moneyprinter-api.service` (FastAPI en puerto 8080)
  - `moneyprinter-webui.service` (Streamlit en puerto 8501)

## 3. Los 3 Modos de Generación por Escena
1. **Modo 1 (Stock DB):** Ingesta y recorte de clips de alta calidad desde base de datos local y scrapers Pexels/Pixabay.
2. **Modo 2 (FLUX.1 Keyframe 0):** Generación de fotogramas de referencia de alta fidelidad (Textura 35mm RAW, grano Kodak Vision3 500T, ARRI Alexa color science, consistencia de personaje) + animación 2.5D con movimiento de cámara orgánico (Ken Burns pan/zoom).
3. **Modo 3 (Google Flow vía Playwright):** Automatización desatendida conectada por CDP a Google Flow con Gemini Omni Flash en Display :99, inyección de foto de referencia en el slot de ingredientes, envío de prompt 7D y descarga del MP4 generado.

## 4. Motor de Voz VibeVoice 1.5B
- **Ejecutable Python:** `/home/ubuntu/vibevoice-venv/bin/python`
- **Voz Principal:** `es-emilio` (Español nativo, entonación cinematográfica y control emocional vía CFG Scale 1.0 - 2.5 y tags como `(con entusiasmo)`, `(con seriedad)`).
- **Subtítulos Sincronizados:** Alineación temporal automática a nivel de frase y palabra sin costes de API externa.
