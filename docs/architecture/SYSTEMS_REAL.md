# SISTEMAS REALES Y LÍMITES ARQUITECTÓNICOS — VIDEOPRO STUDIO

**Principio Rector:**  
*UNA RESPONSABILIDAD → UN SISTEMA → UNA FUENTE DE VERDAD → UN CONTRATO CLARO.*  
*CAMBIAR UN SISTEMA NO DEBE ROMPER OTRO SISTEMA POR ACOPLAMIENTO OCULTO.*

---

## 1. MAPA DE DEPENDENCIAS PERMITIDAS

```text
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                     │
│  • Streamlit WebUI (Puerto 7001)                            │
│  • ComfyUI Pipeline Studio Canvas (HTML/SVG inyectado)      │
└──────────────────────────────┬──────────────────────────────┘
                               │  (HTTP REST / JSON Contracts)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     CAPA DE CONTROL (API)                   │
│  • FastAPI Application (app/asgi.py, Puerto 8080)           │
│  • Controllers (video.py, llm.py, matrix.py, pipeline.py)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   CAPA DE APLICACIÓN & SERVICIOS            │
│  • Task Manager (app/services/task.py)                      │
│  • Creative Director & Scripting (app/services/llm.py)       │
│  • Acoustic & Foley Engine (app/services/audio/)             │
│  • Voice Synthesis & STT (app/services/voice.py, whisper)   │
│  • Pipeline Graph Mutator (app/controllers/v1/pipeline.py)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAPA DE DOMINIO & CONTRATOS                │
│  • Entities & Value Objects (app/core/domain/entities.py)   │
│  • Specifications & Enums (app/core/domain/specs.py)        │
│  • Provider Registries & Adapters (app/core/providers/)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                CAPA DE INFRAESTRUCTURA & STORAGE            │
│  • Firebase Firestore Database (ayuda-emilio-83261)         │
│  • Cloudflare R2 Object Storage (S3-compatible)             │
│  • FFmpeg 6.x Local Subprocess Engine                       │
│  • Local Task Filesystem (storage/tasks/)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. CATÁLOGO DE SISTEMAS Y RESPONSABILIDADES

### 2.1 Sistema de Control y API (`app/controllers/v1/`)
- **Responsabilidad:** Exponer contratos REST validados vía Pydantic, coordinar ejecución asíncrona y deserializar peticiones.
- **Entrada:** JSON estructurado en endpoints `/api/v1/*`.
- **Salida:** Respuestas JSON estandarizadas con códigos HTTP semánticos (200, 400, 404, 500).
- **Dependencias Permitidas:** `app.services.*`, `app.models.*`, `app.core.*`.
- **Dependencias Prohibidas:** Acceso directo a binarios externos sin pasar por servicios, manipulación de Streamlit session state.

### 2.2 Sistema de Dominio y Proveedores (`app/core/`)
- **Responsabilidad:** Mantener la lógica pura de negocio, reglas de validación de escenas, especificaciones de formato (16:9, 9:16) y registros de proveedores de inferencia.
- **Entrada:** Entidades de dominio (`Project`, `Scene`, `Script`, `ProviderSpec`).
- **Salida:** Validación de especificaciones e instancias inmutables.
- **Dependencias Prohibidas:** FastAPI request/response, Streamlit, Firebase SDK directo.

### 2.3 Sistema de Base de Datos y Persistencia (`app/services/firebase_sync.py` & `storage/`)
- **Responsabilidad:** Sincronizar de forma bidireccional y asíncrona los ajustes de configuración y la matriz de proveedores entre el servidor y Firebase Firestore.
- **Fuente de Verdad:** Firestore en `projects/ayuda-emilio-83261/databases/(default)/documents/videopro_settings/`.
- **Caché Local:** `storage/providers_registry.json` y `storage/pipeline_graph.json`.
- **Dependencias Prohibidas:** Bloquear el hilo principal de renderizado con peticiones de red síncronas.

### 2.4 Sistema de Renderizado y Ensamble (`app/services/video.py` & FFmpeg)
- **Responsabilidad:** Componer capas de vídeo (clips/imágenes con Ken Burns), audio normalizado (-16 LUFS), ducking de banda sonora (-22 dB bajo voz) y subtítulos ASS estilizados con karaoke.
- **Entrada:** `VideoParams`, pistas de audio generadas, marcas de tiempo STT y metraje visual.
- **Salida:** Archivo máster `output.mp4` codificado en H.264 / AAC.
- **Dependencias Permitidas:** `ffmpeg` binario del sistema, `moviepy`, `app.services.audio.*`.
