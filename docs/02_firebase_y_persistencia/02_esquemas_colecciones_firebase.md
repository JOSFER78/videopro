# 📄 Esquemas de Colecciones de Firebase Firestore

**Proyecto:** `ayuda-emilio-83261` | **Base de Datos:** `(default)` | **Hosting:** `https://videopro-studio.web.app`

---

## 1. Colección `videopro_settings`

### Documento `global_config`
Persiste la configuración completa de la aplicación (`config.app`):
* `app_name`: `"VideoPro Creative Studio"`
* `hosting_url`: URL pública de la aplicación
* `config_json`: JSON serializado con flags de proveedores, timeouts y preferencias
* `updated_at`: Timestamp ISO-8601

### Documento `providers_registry`
Persiste el registro maestro de los 20 proveedores/motores activos divididos en las 6 categorías canónicas:
* `visual`: `nanobanana`, `flux_zerogpu`, `ltx25`, `pexels`, `pixabay`, `google_flow`, `real_news`
* `voice`: `vibevoice_serverless`, `edge_tts`, `kokoro_tts`
* `music`: `flowmusic` (Lyria 3)
* `programacion`: `vox_subtitles`, `whisper_stt`, `ffmpeg_core`, `remotion_engine`, `hyperframes_engine`
* `llm`: `antigravity` (Gemini 3.7 Flash High / Puerto 8742), `openai`, `cloudflare_ai`
* `cloud`: `r2_storage`, `firebase_db`

---

## 2. Colección `videopro_projects`

Cada documento almacena un proyecto (`proj_<slug>_<timestamp>`):
* `project_id`: Identificador único
* `title` / `subject`: Título del proyecto
* `workflow_id`: ID del arquetipo (`PIXAR_3D_ANIMATION`, `CHRONODRIFT_TRITEMPORAL`, etc.)
* `workflow_name`: Nombre legible del workflow
* `status`: Estado del ciclo de vida (`DRAFT`, `PLANNED`, `GENERATING`, `COMPLETED`, `FAILED`)
* `aspect_ratio`: Relación de aspecto (`16:9`, `9:16`, `1:1`)
* `voice_id`: Preset de voz seleccionado (`es-emilio`, `kokoro-hd`, etc.)
* `scenes_count`: Número de escenas planificadas
* `has_video`: Flag booleano de disponibilidad de vídeo final
* `cloud_synced`: Flag de sincronización con Cloudflare R2
* `cloud_url`: URL pública del MP4 en Cloudflare R2
* `director_spec_json`: Especificación completa del Director Creativo (personajes, conflicto, clímax, CoT)
* `scenes_json`: Lista estructurada de escenas con planes visuales y de audio
* `messages_json`: Historial conversacional de co-creación con el Director Creativo
* `updated_at` / `created_at`: Marcas temporales

---

## 3. Colección `videopro_system`

### Documento `status`
* `app_name`: Nombre del sistema
* `hosting_url`: URL pública
* `updated_at`: Timestamp de último heartbeat
