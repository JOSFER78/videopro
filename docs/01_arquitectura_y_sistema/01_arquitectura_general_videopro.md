# AUDITORÍA FORENSE REAL — VIDEOPRO STUDIO

**Fecha de Auditoría:** 16 de Agosto de 2026  
**Auditor Principal:** Lead Software Architect & DevOps Forensic Auditor  
**Principio Fundamental:** REAL-ONLY (Basado exclusivamente en evidencia comprobada en ejecución, filesystem y base de datos en vivo).

---

## 1. INVENTARIO Y ESTRUCTURA REAL DEL REPOSITORIO

### 1.1 Estructura Física Descubierta
```text
/home/ubuntu/workspace/pro/hermes/10_videopro/
├── app/                        # Backend principal de VideoPro
│   ├── asgi.py                 # Instancia principal FastAPI y montaje de middleware
│   ├── router.py               # Enrutador API REST (/api/v1/...)
│   ├── config/                 # Configuración central (config.py, config_manager.py)
│   ├── controllers/v1/         # Controladores REST (video.py, llm.py, matrix.py, pipeline.py)
│   ├── core/                   # Dominio limpio y registros (domain/, providers/, services/)
│   ├── models/                 # Esquemas Pydantic y constantes (schema.py, const.py, llm_provider.py)
│   ├── services/               # Servicios de generación, audio, subtítulos, storage, firebase
│   └── utils/                  # Utilidades seguras de archivos, logging y helpers
├── webui/                      # Frontend principal en Streamlit (Puerto 7001)
│   ├── Main.py                 # Entrada orquestadora de vistas y panel de capas
│   ├── nav.py                  # Barra superior de navegación unificada
│   ├── views/                  # Vistas modulares (projects, settings, pipeline, audio, etc.)
│   ├── steps/                  # Pipeline paso a paso (concept, visual, foley, captions, master)
│   ├── core/                   # Constantes y bridge de configuración
│   ├── i18n/                   # Localización multilingüe (9 idiomas)
│   └── styles.css              # Sistema de diseño CSS oscuro y glassmorphism
├── docs/                       # Documentación técnica e investigación
│   ├── architecture/           # Documentación arquitectónica oficial
│   ├── database/               # Esquemas y ciclo de vida de datos
│   ├── deployment/             # Runtime y guías de despliegue
│   └── investigaciones/        # HTMLs interactivos (comfy_pipeline_studio.html, proveedores_excel.html)
├── storage/                    # Persistencia local y artefactos
│   ├── providers_registry.json # Registro de 22 proveedores activos
│   ├── deleted_providers.json  # Proveedores eliminados/desactivados
│   ├── pipeline_graph.json     # Grafo de nodos del generador
│   ├── audio/                  # Muestras de audio
│   ├── references/             # Fotos y referencias visuales
│   ├── renders/                # Renders locales temporales
│   └── tasks/                  # Manifiestos de tareas (YYYY/MM/DD/task_id/script.json)
├── resource/                   # Fuentes tipográficas y pistas musicales base
│   ├── fonts/                  # Fuentes TTF/TTC para subtítulos ASS
│   └── songs/                  # 30 pistas musicales libres
├── scripts/                    # Scripts de utilidad, automatización Playwright y render
├── references/                 # Especificaciones técnicas de referencia
├── templates/                  # Manifiestos y plantillas de proyecto
├── tests/                      # Batería de pruebas unitarias y de integración
├── deploy/                     # Configuraciones Nginx y unit files
├── main.py                     # Entrypoint backend FastAPI (Puerto 8080)
├── run.sh / run_dev_7001.sh    # Entrypoints frontend Streamlit (Puerto 7001)
├── config.toml                 # Configuración viva del entorno
└── config.example.toml         # Plantilla de configuración
```

---

## 2. SISTEMAS REALES EN PRODUCCIÓN

| Sistema | Responsabilidad Real | Entrada | Salida | Persistencia | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **API Backend (FastAPI)** | Servir endpoints REST, orquestar tareas de generación y exponer control del pipeline. | HTTP Requests JSON | Respuestas JSON / Streams | No (Stateless) | **ACTIVO (Puerto 8080)** |
| **UI Frontend (Streamlit)** | Interfaz de usuario, configuración de proyectos, matriz de proveedores y control de capas. | Inputs de usuario / Chat | Peticiones API / WebUI state | `st.session_state` | **ACTIVO (Puerto 7001)** |
| **Pipeline Studio (Canvas)** | Editor de nodos estilo ComfyUI con asistente agéntico en lenguaje natural. | Grafo JSON / Prompts | Grafo mutado / Trazabilidad | `storage/pipeline_graph.json` | **ACTIVO (Inyectado en UI)** |
| **Matriz de Proveedores** | Catálogo vivo de inferencia local/cloud/serverless con toggle en tiempo real. | Ajustes de motor | `providers_registry.json` | Firestore + `storage/` | **ACTIVO** |
| **Sincronización Firebase** | Persistir en la nube configuraciones, claves y estado de proveedores. | `config.toml` + Registros | Documentos Firestore | Firestore (`ayuda-emilio-83261`) | **ACTIVO** |
| **Storage Cloudflare R2** | Depósito multipart de escenas y másters de vídeo sin coste de descarga ($0 egress). | Archivos MP4 / Clips | Presigned URLs / CDN | Bucket R2 (`videpro/videos/`) | **CONFIGURADO** |
| **Motor de Render FFmpeg** | Ensamblaje de pistas de vídeo, audio normalizado, ducking acústico y subtítulos ASS. | Clips + WAV + ASS | Máster MP4 | `storage/tasks/.../output.mp4` | **ACTIVO** |

---

## 3. FIREBASE & MODELO DE DATOS REAL

### 3.1 Proyecto Firebase Activo
- **Project ID:** `ayuda-emilio-83261` (DisplayName: *Ayuda Emilio Portal*)
- **Project Number:** `375420549895`
- **Hosting URL:** `https://videopro-studio.web.app`
- **Mecanismo de Auth:** Token OAuth2 via `~/.config/configstore/firebase-tools.json` / `FIREBASE_AUTH_TOKEN`.

### 3.2 Colecciones Reales de VideoPro en Firestore
1. **`videopro_settings`**:
   - `global_config`: Contiene `config_json` con la totalidad de ajustes de VideoPro (resoluciones, claves, endpoints, TTS, LLM, CRF, límites de concurrencia). **Fuente de Verdad de Configuración**.
   - `providers_registry`: Contiene `registry_json` (22 proveedores con infraestructura, categorías, preferencias) y `deleted_providers_json`. **Fuente de Verdad del Catálogo**.
2. **`videopro_system`**:
   - `status`: Metadatos del sistema, versión de la aplicación y último heartbeat.

---

## 4. ALMACENAMIENTO Y MEDIA: PERSISTENTE VS TEMPORAL

| Directorio / Ruta | Clasificación | Propósito Real | Política de Retención |
| :--- | :--- | :--- | :--- |
| `storage/providers_registry.json` | **PERSISTENTE (Espejo)** | Caché local del catálogo de proveedores sincronizado con Firestore. | Permanente. |
| `storage/pipeline_graph.json` | **PERSISTENTE (Espejo)** | Estado del grafo de nodos del generador ComfyUI. | Permanente. |
| `storage/tasks/YYYY/MM/DD/...` | **PERSISTENTE / ARTEFACTOS** | Almacena `script.json`, `materials/`, `subtitles.ass` y másters MP4 de cada trabajo generado. | Conservar según cuota de disco. |
| `storage/references/` | **ASSETS DE PRUEBA** | 6 imágenes JPEG de Shibuya y su `metadata.json` para validación de pipelines de prueba. | Mantener como fixture. |
| `storage/audio/` | **ASSETS DE PRUEBA** | Muestras de audio MP3 para calibración de ducking. | Mantener como fixture. |
| `resource/fonts/` | **PERSISTENTE (Core)** | Tipografías TTF/TTC requeridas por libass / FFmpeg para quemado de subtítulos. | Permanente. |
| `resource/songs/` | **PERSISTENTE (Core)** | 30 pistas musicales libres (`output000.mp3` a `output029.mp3`). | Permanente. |
| `/tmp/videopro_8080.log` | **TEMPORAL** | Logs de ejecución del backend. | Rotar en `/tmp`. |

---

## 5. RUNTIME, PUERTOS Y DEVOPS

### 5.1 Puertos y Procesos en VPS
- **Puerto 8080 (TCP):** FastAPI Backend (`main.py` -> `app.asgi:app`).
- **Puerto 7001 (TCP):** Streamlit WebUI (`webui/Main.py` vía `run_dev_7001.sh`).
- **Puerto 8742 (TCP):** Antigravity CLI Bridge (Gemini 3.7 Flash High sin consumo de tokens $0).
- **Puerto 6080 / 5900 (TCP):** noVNC / VNC desktop server.
- **Nginx Ingress:** Enrutamiento en `/etc/nginx/sites-available/pro` hacia `127.0.0.1:7895` y `127.0.0.1:8501`.

---

## 6. AUDITORÍA FORENSE DE PROBLEMAS, LEGACY Y BASURA

### 6.1 Problema Crítico de DevOps: Bucle de Reinicio de `videopro-v2.service`
- **Evidencia:** `videopro-v2.service` en systemd intentaba ejecutar `server/videopro_server.py` escuchando en el puerto `7001`.
- **Causa:** El puerto `7001` ya estaba en uso por Streamlit (`webui/Main.py`), provocando más de 813 fallos de reinicio consecutivos con `[Errno 98] Address already in use`.
- **Solución:** Desactivar el servicio obsoleto o reconfigurarlo para apuntar al backend moderno (`main.py` en puerto 8080).

### 6.2 Archivos Huérfanos / Legacy / Basura Identificados
1. **`server/` (`server/videopro_server.py`, `server/config.py`, `server/run_server.sh`)**: Prototipo anterior monolítico en desuso, reemplazado por la arquitectura limpia en `app/` y `main.py`.
2. **`web/index.html`**: Prototipo SPA antiguo que consumía el servidor monolítico de `server/`.
3. **`run_spa_7001.sh`**: Script para levantar el prototipo antiguo.
4. **`webui/Main.py.bak` y `webui/Main.py.monolith.bak`**: Copias de seguridad muertas.
5. **`videopro_7001.log` y `videopro_spa_7001.log`**: Logs viejos sueltos en la raíz del repositorio.

### 6.3 Relación con MoneyPrinterTurbo (MPT)
- VideoPro nació originalmente utilizando componentes base de MoneyPrinterTurbo (generación de subtítulos Whisper, manejo de tareas y utilidades de video).
- **Veredicto:** VideoPro utiliza el entorno virtual `/home/ubuntu/MoneyPrinterTurbo/.venv` para sus librerías de GPU/FFmpeg. El código interno de VideoPro en `app/` y `webui/` ya está desacoplado y funciona de manera autónoma, pero el `.venv` debe mantenerse como runtime compartido de dependencias.

---

## 7. MATRIZ DE ACCIÓN Y PLAN DE ESTABILIZACIÓN

| Componente | Clasificación | Acción Forense |
| :--- | :--- | :--- |
| `videopro-v2.service` | **FALLO RUNTIME** | Detener y deshabilitar el unit file obsoleto en systemd. |
| `webui/Main.py.bak*` | **BASURA** | Eliminar archivos `.bak`. |
| `videopro_*.log` | **BASURA** | Eliminar logs huérfanos en la raíz y actualizar `.gitignore`. |
| `server/` & `web/` | **LEGACY** | Archivar de forma segura en `legacy/` o eliminar al consolidar. |
| `docs/architecture/` | **NUEVO NÚCLEO** | Publicar la arquitectura real, sistemas, contratos y modelo de datos. |
| `config.toml` & `.gitignore` | **SEGURIDAD** | Asegurar que `.gitignore` proteja claves, tokens y temporales. |
