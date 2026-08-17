# 🏛️ Arquitectura de Backend, APIs y Grafo de Nodos — VideoPro Studio

## 1. Topología del Servidor ASGI (Puerto 8080)

VideoPro Studio expone su backend API de alto rendimiento mediante FastAPI (`app.asgi:app`) en el puerto 8080:

```
       [ Client / WebUI / SDK ]
                 │
                 ▼ HTTP / REST (Puerto 8080)
      ┌──────────────────────────────────────────────┐
      │               FastAPI (ASGI)                 │
      │  ┌────────────────────────────────────────┐  │
      │  │  Router Root (ping, v1 controllers)    │  │
      │  │  - /api/v1/videos, /tasks, /voices     │  │
      │  │  - /api/v1/pipeline (ComfyUI Graph)    │  │
      │  │  - /api/v1/studio (Archetypes/Jobs)    │  │
      │  │  - /api/v1/matrix (Provider Engine)    │  │
      │  └────────────────────────────────────────┘  │
      └──────────────────────┬───────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   [ InMemoryTaskManager ]          [ RedisTaskManager ]
   (Threading.Lock + Pool)          (Redis List + LPUSH/RPOP)
            │                                 │
            └────────────────┬────────────────┘
                             ▼
                    [ tm.start Pipeline ]
   (Script -> Terms -> Audio -> Subtitle -> Materials -> Render -> R2/Cloud)
```

---

## 2. Mapa Completo de Controladores REST

| Módulo / Prefijo | Endpoint | Método | Schema Request | Schema Response | Función Principal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Video & Render** (`/api/v1`) | `/videos` | `POST` | `TaskVideoRequest` | `TaskResponse` (200) | Inicia pipeline completo de vídeo |
| | `/subtitle` | `POST` | `SubtitleRequest` | `TaskResponse` (200) | Genera solo pista de subtítulos |
| | `/audio` | `POST` | `AudioRequest` | `TaskResponse` (200) | Genera locución y banda sonora |
| | `/voices` | `GET` | — | `{"voices": [...]}` | Lista voces disponibles (VibeVoice, EdgeTTS) |
| | `/voice/preview` | `POST` | `{"text", "voice_name"}` | `{"preview_id", "url"}` | Preview fonético rápido |
| | `/scene/generate` | `POST` | `{"scene_id", "mode", ...}` | `{"clip_file", "url"}` | Genera clip individual (3 Modos) |
| | `/tasks` | `GET` | `page: int`, `page_size: int` | `TaskListResponse` | Listado paginado con estados |
| | `/tasks/{task_id}` | `GET` | `task_id: str` | `TaskQueryResponse` | Consulta telemetría y estado de tarea |
| | `/stream/{path}` | `GET` | `Range: bytes=start-end` | `StreamingResponse` (206) | Streaming de vídeo con seek y byte-range |
| **Director Creativo** (`/api/v1`) | `/scripts` | `POST` | `VideoScriptRequest` | `VideoScriptResponse` | Guion estructurado por escenas |
| | `/terms` | `POST` | `VideoTermsRequest` | `VideoTermsResponse` | Extracción de keywords 5D |
| **Pipeline Visual Nodos** (`/api/v1/pipeline`) | `/graph` | `GET`/`POST`| `Dict[str, Any]` (Topología) | `{"nodes", "connections"}` | Obtiene/Guarda grafo ComfyUI de 10 nodos |
| | `/reset` | `POST` | — | `get_canonical_pipeline_graph()` | Restaura topología oficial de producción |
| | `/validate` | `POST` | `{"nodes", "connections"}` | `{"valid": bool, "errors": [...]}` | Valida integridad y conexiones del grafo |
| | `/agent` | `POST` | `{"prompt": str}` | Grafo optimizado por LLM | Asistente agéntico para compilar grafos |
| **Studio & Orchestration** (`/api/v1/studio`) | `/manifest` | `GET` | — | Manifiesto de 4 niveles | Árbol completo de Capabilities/Engines |
| | `/archetypes` | `GET` | — | `List[Archetype]` | Catálogo de arquetipos (Pixar, Vox, etc.) |
| | `/execute` | `POST` | `ExecuteRequest` | `ExecutionJob` | Ejecuta y traza un Job de producción |
| **Provider Matrix** (`/api/v1/matrix`) | `/data` | `GET` | — | `{"items": [...]}` | Estado y latencia de todos los motores |
| | `/toggle` | `POST` | `ToggleRequest` | `{"enabled": bool}` | Habilita/Deshabilita proveedor en caliente |

---

## 3. Ontología de 4 Niveles y Grafo ComfyUI

```
┌────────────────────────────────────────────────────────────────────────┐
│ NIVEL 4: WORKFLOWS & ARQUETIPOS DE PRODUCCIÓN                          │
│ [Pixar 3D]   [Historical Scraping]   [City Beats]   [Deep Explainer]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ NIVEL 3: GRAFO DE 10 NODOS DE PRODUCCIÓN (ComfyUI Style Pipeline)      │
│ (1.Intent) ➔ (Research) ➔ (2.LLM) ➔ (3.Voice) ➔ (4.Whisper) ➔          │
│ (5.Subtitles) ➔ (6.Visual) ➔ (7.BGM Ducking) ➔ (8.Render) ➔ (9.Cloud)  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ NIVEL 2: CAPABILITIES ATÓMICAS (Unidades Ejecutables de Producción)     │
│ [cap_flux3_keyframe]  [cap_vibevoice_tts]  [cap_ffmpeg_ducking] ...     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ NIVEL 1: MOTORES & PROVEEDORES DE INFRAESTRUCTURA (API / Servidores)   │
│ [Pollinations FLUX]  [Google Flow CDP]  [ZeroGPU A100]  [R2 Storage]   │
└────────────────────────────────────────────────────────────────────────┘
```
