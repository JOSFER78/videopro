# VideoPro Studio — Suite de Producción Audiovisual Multimotor

VideoPro es una plataforma de producción audiovisual, co-creación con inteligencia artificial y renderizado cinemático basada en workflows desacoplados y ruteo multimotor.

---

## 1. ❓ Qué es VideoPro
VideoPro unifica el proceso completo de creación audiovisual:
- **Director Creativo Semántico:** Co-creación y pulido de guiones, tonos y estilos ópticos mediante IA interactiva.
- **Orquestador de Workflows:** Pipelines desacoplados por arquetipo (Animación 3D, Documental Histórico con Scraping, Rutas Urbanas con Beats, Shorts Virales y Videoensayos).
- **Workflow Designer:** Editor e inspector visual de la topología de nodos y sockets de datos.
- **Ruteo de Motores Visuales:** Selección automática por escena entre Google Flow 4K, FLUX 3, NanoBanana Pro 2K/4K y BBDD de Stock.
- **Suite de Audio:** Síntesis de voz documental con VibeVoice 1.5B (`es-emilio`), Flow Music Lyria 3, Foley procedural y auto-ducking acústico (-22dB).

---

## 2. ⚡ Qué Funciona Actualmente
- **Frontend WebUI:** Streamlit en puerto `7001` con navegación integrada, diseño dark glassmorphism y Director Semántico interactivo.
- **Backend REST API:** FastAPI en puerto `8080` (`/api/v1/studio`, `/api/v1/pipeline`, `/api/v1/projects`).
- **5 Arquetipos de Producción:** Entrevistas adaptativas y pipelines dinámicos para Pixar 3D, Documental Histórico, Rutas Urbanas, Shorts Virales y Videoensayos.
- **Generación Visual:** Google Flow 4K (vuelos orbitales vía Playwright), FLUX 3 (ZeroGPU / Serverless), NanoBanana Pro 2K/4K (Local Bridge 8742).
- **Audio y Subtítulos:** VibeVoice 1.5B, Whisper STT con timestamps palabra por palabra y subtítulos karaoke `.ass`.
- **Renderizado Final:** FFmpeg con composición por capas, corrección de color y sincronización rítmica.

---

## 3. 🚀 Cómo Arrancarlo

### En Desarrollo Local:
```bash
# 1. Iniciar el Backend API (Puerto 8080)
/home/ubuntu/MoneyPrinterTurbo/.venv/bin/python main.py

# 2. Iniciar el Frontend WebUI (Puerto 7001)
/home/ubuntu/MoneyPrinterTurbo/.venv/bin/python -m streamlit run webui/Main.py --server.port 7001 --server.address 0.0.0.0
```

### Gestión de Servicios (systemd):
```bash
systemctl --user restart moneyprinter-api.service    # Reiniciar Backend
systemctl --user restart moneyprinter-webui.service  # Reiniciar Frontend
systemctl --user status moneyprinter-api.service     # Ver estado
```

---

## 4. ⚙️ Qué Servicios Necesita
- **Python 3.11** con entorno virtual (`/home/ubuntu/MoneyPrinterTurbo/.venv`).
- **FFmpeg** instalado en el sistema para renderizado y composición.
- **Antigravity Bridge** en `http://127.0.0.1:8742/v1` para inferencia local LLM y generación de imágenes NanoBanana.

---

## 5. 🗄️ Dónde Están los Datos (Metadatos y Configuración)
- **Local:** `storage/workflows/`, `storage/jobs/`, `storage/pipeline_graph.json`, `config.toml`.
- **Cloud:** **Firebase Firestore** (`ayuda-emilio-83261`) — Colecciones `videopro_settings`, `workflows`, `projects`.

---

## 6. 📦 Dónde Están los Artefactos (Vídeos, Audios y Renders)
- **Buffer Local:** `storage/renders/`, `storage/audio/`, `storage/tasks/`.
- **Cloud Storage:** **Cloudflare R2** (Bucket multimedia S3-compatible).

---

## 7. 🔌 Qué Integraciones Existen
- **Google Flow (Headless Playwright):** Generación desatendida de tomas de dron y planos 4K.
- **FLUX 3 Video:** Keyframes y secuencias de movimiento (ZeroGPU / Replicate).
- **VibeVoice 1.5B:** Locución hiperrealista en español.
- **Hermes Subagents:** Scraping y verificación documental en archivos históricos.
- **Remotion / React TSX:** Renderizado programático de infografías de datos 4K.

---

## 8. 🔮 Qué Está Planificado (PLANNED)
- **ComfyUI Server Runtime:** Ejecución remota de grafos ComfyUI en servidores externos dedicados (Puerto `8188`).
- **RunPod Serverless GPU:** Workers de GPU bajo demanda para aceleración de renderizado.

---

## 📚 Documentación Canónica
Para detalles de arquitectura y especificaciones, consulta:
- [NAMING.md](docs/architecture/NAMING.md) — Diccionario oficial y vocabulario canónico.
- [REALITY_MATRIX.md](docs/architecture/REALITY_MATRIX.md) — Matriz de estado real de cada componente.
- [RUNTIME_MAP.md](docs/architecture/RUNTIME_MAP.md) — Mapa de puertos y procesos en ejecución.
- [SYSTEM_MAP.md](docs/architecture/SYSTEM_MAP.md) — Diagrama de relaciones arquitectónicas.
