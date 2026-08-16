# VideoPro Studio v2.0 — Estudio Cinematográfico Híbrido Autónomo

> **Ubicación Canónica de la Aplicación:** `/home/ubuntu/workspace/pro/hermes/10_videopro/` (Acceso rápido: `/home/ubuntu/workspace/pro/hermes/videopro`)  
> **URL Producción:** [`https://143-47-35-167.sslip.io/pro/videopro/`](https://143-47-35-167.sslip.io/pro/videopro/)  
> **API Swagger / Docs:** [`https://143-47-35-167.sslip.io/pro/videopro/api/docs`](https://143-47-35-167.sslip.io/pro/videopro/api/docs)  
> **Paquete Zip Limpio:** [`https://143-47-35-167.sslip.io/pro/videopro.zip`](https://143-47-35-167.sslip.io/pro/videopro.zip)

---

## 🌟 Visión General

**VideoPro Studio** es una plataforma integral de producción y montaje cinematográfico asistido por inteligencia artificial que combina tres pilares fundamentales:
1. **Motor de Voz Local VibeVoice 1.5B:** Calidad ElevenLabs en español (`es-emilio`), modulación de emociones y alineación de subtítulos con timestamps exactos a coste $0.
2. **Generación Multimodal por Escena (3 Modos):**
   - **Modo 1 (Stock DB):** Recuperación y recorte de clips de alta calidad desde el repositorio local y Pexels.
   - **Modo 2 (FLUX.1 Keyframe 0):** Fotogramas de referencia fotorrealistas (grano analógico 35mm, Kodak Vision3 500T) con síntesis de movimiento 2.5D Ken Burns.
   - **Modo 3 (Google Flow Playwright):** Automatización desatendida vía Chrome CDP en puerto 9222 con Gemini Omni Flash, inyección de ingredientes y descarga desatendida de MP4.
3. **Pipeline de Postproducción Automático (MoviePy + FFmpeg):** Ensamble de clips, transiciones cinematográficas, ducking de música de fondo (-18dB) y renderizado de subtítulos dinámicos en formatos vertical (9:16) y horizontal (16:9).

---

## 🔒 Política Estricta de Seguridad: CERO Tokens y CERO Contenido en Repositorios

> [!IMPORTANT]
> **REGLA DE ORO DE SEGURIDAD:**
> 1. **NUNCA subir claves API, tokens, secretos o credenciales** (`config.toml`, `.env`, `*key*.json`, `*secret*.json`, `serviceAccountKey*.json`, tokens de Replicate, Gemini, OpenAI, Groq, Cloudflare R2, ElevenLabs, HuggingFace, etc.) al repositorio Git ni a GitHub.
> 2. **NUNCA subir contenido multimedia generado o renders locales** (`storage/tasks/`, `outputs/`, archivos `.mp4`, `.mov`, `.wav`, `.mp3`, `.mkv`). Todo el contenido generado se almacena de forma local o sincronizado remotamente en Cloudflare R2 / S3 / Firestore bajo credenciales privadas.
> 3. **Gestión de Configuración Segura:**
>    - El archivo [config.example.toml](file:///home/ubuntu/workspace/pro/hermes/10_videopro/config.example.toml) sirve como plantilla pública sin claves.
>    - El archivo local `config.toml` contiene las claves de trabajo locales y está **100% excluido e ignorado en [.gitignore](file:///home/ubuntu/workspace/pro/hermes/10_videopro/.gitignore)**.
>    - La persistencia y respaldo en la nube se gestiona de forma segura a través de **Firebase Firestore** y **Cloudflare R2** desde la pestaña de **Ajustes** en la WebUI, nunca mediante commits a Git.

---

## 📁 Estructura del Proyecto

```
/home/ubuntu/workspace/pro/hermes/10_videopro/
├── README.md                      # Documentación maestra de la aplicación
├── IDEA.md                        # Visión y conceptos fundacionales
├── PROJECT.md                     # Alcance técnico y contratos
├── DECISIONS.md                   # Registro de decisiones de arquitectura (ADR)
├── STATUS.json                    # Estado operativo y puertos
│
├── server/                        # Backend FastAPI & Motores de Inferencia
│   ├── videopro_server.py         # Servidor principal (VibeVoice + FLUX + FFmpeg + Static UI)
│   ├── config.py                  # Rutas absolutas, modelos y constantes del sistema
│   └── run_server.sh              # Script de arranque del backend
│
├── web/                           # Frontend WebUI de Producción
│   ├── index.html                 # Interfaz Dark Glassmorphism de VideoPro Studio
│   └── assets/                    # Iconografía, previsualizaciones y estilos
│
├── scripts/                       # Herramientas y Automatizaciones CLI
│   ├── google_flow_general_automation.py  # Automatización Playwright desatendida en Google Flow
│   ├── flow_studio_full_auth.py           # Verificación de sesión y autenticación Gemini Ultra
│   ├── google_flow_batch_generator.py     # Generación en lote de escenas en Google Flow
│   ├── render_vertical_video.py           # Pipeline de ensamble MoviePy / FFmpeg
│   ├── render_from_plan.py                # Ensamble a partir de guiones JSON
│   ├── render_remotion.py                 # Renderizado de motion graphics con Remotion
│   ├── download_clips.py                  # Ingesta de stock clips y assets
│   ├── video_storage_manager.py           # Gestión y organización cronológica de renders
│   └── validate_skill.py                  # Verificación de integridad del sistema
│
├── investigaciones/               # Dossiers de Investigación Cinematográfica
│   ├── 00_INDICE_INVESTIGACIONES.md
│   ├── 01_metodologia_documental_cinematografica.md
│   ├── 02_benchmark_google_flow_vs_flux3.md
│   ├── 03_arquitectura_documentary_director.md
│   ├── 04_contratos_y_prompts_maestros.md
│   ├── 05_integracion_google_flow_web_y_consistencia.md
│   ├── schemas/                   # Esquemas JSON de validación
│   └── templates/                 # Plantillas de biblia visual y dossiers
│
├── references/                    # Guías de Referencia Técnica
│   ├── omni_flash_syntax.md       # Sintaxis 7D para prompts de Google Flow
│   ├── google_flow_cdp_automation.md
│   ├── storage-pipeline.md
│   └── documentary_7shot_sync_workflow.md
│
├── templates/                     # Plantillas de Proyecto y Storyboards
├── tests/                         # Suite de Pruebas Automatizadas
├── deploy/                        # Archivos de Despliegue en VPS
│   ├── videopro-v2.service        # Servicio Systemd
│   └── nginx_videopro.conf        # Configuración Nginx Reverse Proxy
│
└── outputs/                       # Directorio de Proyectos y Renders
    └── YYYY/MM/YYYY-MM-DD_<slug>/v1/
```

---

## 🚀 Puesta en Marcha y Servicios

### 1. Iniciar Servicio de Backend con Systemd
```bash
sudo systemctl restart videopro-v2.service
sudo systemctl status videopro-v2.service
```

### 2. Ejecutar de Forma Manual
```bash
cd /home/ubuntu/workspace/pro/hermes/10_videopro/server
/home/ubuntu/vibevoice-venv/bin/python videopro_server.py
```

### 3. Puertos del Ecosistema
- **Puerto 7895:** Backend FastAPI + WebUI Integrada de VideoPro Studio.
- **Puerto 8501:** Streamlit WebUI (MoneyPrinterTurbo Core).
- **Puerto 8080:** FastAPI REST API (MoneyPrinterTurbo Backend).
- **Puerto 9222:** Chrome Headless / CDP para automatización de Google Flow.
- **Display :99:** Xvfb Virtual Framebuffer para automatización gráfica de navegadores.

---

## 🌐 Configuración de Red y Nginx

La aplicación está completamente mapeada a través de Nginx en `/etc/nginx/sites-available/pro`:
- **WebUI Principal:** `https://143-47-35-167.sslip.io/pro/videopro/`
- **API REST:** `https://143-47-35-167.sslip.io/pro/videopro/api/`
- **Descarga de Zip:** `https://143-47-35-167.sslip.io/pro/videopro.zip`

---

## 🎙️ Motor de Voz VibeVoice 1.5B Local

- **Ubicación del Modelo:** `/home/ubuntu/models/VibeVoice-1.5B/`
- **Entorno Python:** `/home/ubuntu/vibevoice-venv/bin/python`
- **Voz Principal:** `es-emilio` (Español Neutro, Calidad Documental 24kHz).
- **Modulación Emocional:** Mediante acotaciones en el guion:
  - `(con tono intrigante)`
  - `(con entusiasmo)`
  - `(con gravedad)`

---

## 🎬 Generación Multimodal de Escenas

### Modo 1: Stock DB
- Busca metraje local en `/var/www/pro/webasset/` o descarga vía Pexels API.
- Ideal para clips de transición, tomas aéreas y ambientación documental.

### Modo 2: FLUX.1 (Keyframe 0 + Ken Burns)
- Genera imágenes fotorrealistas en 35mm utilizando el motor FLUX.1.
- Aplica transformaciones 2.5D con `ffmpeg zoompan` para dar sensación de movimiento de cámara fluida.

### Modo 3: Google Flow (Gemini Omni Flash)
- Lanza Playwright sobre Chromium con la sesión autenticada de Gemini Ultra.
- Inyecta la imagen de referencia como ingrediente.
- Envía el prompt 7D estructurado.
- Descarga el vídeo MP4 resultante de forma 100% desatendida.

---

## 🛡️ Reglas de Mantenimiento
1. **No mezclar la aplicación con la skill:** La aplicación vive en `/home/ubuntu/workspace/pro/hermes/10_videopro/`, mientras que la skill de agente para Hermes reside en `~/.hermes/skills/creative/videopro/SKILL.md`.
2. **Organización cronológica estricta:** Todos los renders deben guardarse en `outputs/YYYY/MM/YYYY-MM-DD_<slug>/v1/`.
3. **Cero dependencias de APIs de pago:** VibeVoice 1.5B y Whisper resuelven voz y subtítulos localmente.
