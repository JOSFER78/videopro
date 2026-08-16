# VIDEOPRO — MATRIZ DE REALIDAD EMPÍRICA (REALITY_MATRIX.md)

**Versión:** 1.0.0 — Canónica  
**Estado:** `CURRENT / EMPIRICALLY VERIFIED`  
**Última Actualización:** Agosto 2026

Esta matriz audita y clasifica **únicamente componentes verificados físicamente** en el código, sistema de archivos, procesos en ejecución (`systemd`), puertos y servicios remotos.

---

## 📊 MATRIZ MAESTRA DE ESTADO DE COMPONENTES

| Componente | Qué es | Existe Físicamente | Activo en Runtime | Externo | Estado Actual | Ubicación en Código | Responsable / Infraestructura |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **VideoPro Backend** | API REST FastAPI | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `main.py`, `app/` (Puerto 8080) | VideoPro Core |
| **VideoPro Frontend** | WebUI Streamlit | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `webui/Main.py` (Puerto 7001) | VideoPro Studio |
| **Workflow Designer** | Editor Visual de Nodos | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `webui/views/view_comfy_pipeline.py` | VideoPro Studio |
| **Request Planner** | Planificador de Producción | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `app/core/orchestration/planner.py` | VideoPro Core |
| **Scene Engine Router** | Ruteo Multimotor por Escena| ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `app/core/orchestration/scene_router.py`| VideoPro Core |
| **Workflow Executor** | Motor de Ejecución de Jobs | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `app/core/orchestration/executor.py` | VideoPro Core |
| **Antigravity Bridge** | Inferencia LLM Local | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | Proceso CLI en `http://127.0.0.1:8742` | Bridge Local |
| **Google Flow Engine** | Generador de Vídeo 4K/Dron | ✅ Sí | ✅ Sí | ✅ Sí | **PRODUCCIÓN (ONLINE)** | `scripts/google_flow_batch_generator.py` | Google Flow (Playwright) |
| **NanoBanana Pro 2K/4K** | Motor Visual / Keyframes | ✅ Sí | ✅ Sí | ⚠️ Local | **PRODUCCIÓN (ONLINE)** | `app/core/orchestration/adapters/` | Local Bridge (Puerto 8742) |
| **FLUX 3 Video** | Generador Visual / LoRA | ✅ Sí | ✅ Sí | ✅ Sí | **PRODUCCIÓN (ONLINE)** | `app/services/video_providers/` | Serverless ZeroGPU / Replicate |
| **VibeVoice 1.5B** | Síntesis de Voz Documental | ✅ Sí | ✅ Sí | ⚠️ Local | **PRODUCCIÓN (ONLINE)** | `app/services/voice.py` | ZeroGPU / Local HF |
| **Whisper STT** | Timestamps y Transcripción | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `app/services/subtitle.py` | Local VPS (CPU/GPU) |
| **FFmpeg Master Engine**| Ensamblaje y Ducking | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `app/services/video.py` | Local VPS (Binario FFmpeg) |
| **Remotion / React** | Infografías Animadas 4K | ✅ Sí | ✅ Sí | ❌ No | **PRODUCCIÓN (ONLINE)** | `scripts/render_remotion.py` | Local Node.js / Remotion |
| **Hermes Subagents** | Scraping e Investigación | ✅ Sí | ✅ Sí | ✅ Sí | **PRODUCCIÓN (ONLINE)** | `app/core/orchestration/adapters/` | Hermes Subagent Pool |
| **Firebase Firestore** | Base de Datos NoSQL Estado | ✅ Sí | ✅ Sí | ✅ Sí | **PRODUCCIÓN (ONLINE)** | `app/services/firebase_sync.py` | Google Cloud (ayuda-emilio-83261) |
| **Cloudflare R2** | Almacenamiento de Vídeos | ✅ Sí | ✅ Sí | ✅ Sí | **PRODUCCIÓN (ONLINE)** | `app/services/storage_manager.py` | Cloudflare Storage (S3 API) |
| **MoneyPrinterTurbo** | Runtime Python Virtualenv | ✅ Sí | ✅ Sí | ✅ Sí | **DEPENDENCIA EXTERNA** | `/home/ubuntu/MoneyPrinterTurbo/.venv` | Shared Python Virtualenv |
| **ComfyUI Runtime** | Servidor ComfyUI Externo | ⚠️ Adaptador | ❌ Inactivo | ✅ Sí | **PLANNED / FUTURE INTEGRATION** | `app/core/orchestration/adapters/` | Servidor Externo (Puerto 8188) |
| **RunPod Serverless** | Cómputo GPU en la Nube | ⚠️ Schema | ❌ Inactivo | ✅ Sí | **PLANNED / FUTURE INTEGRATION** | `app/core/orchestration/providers.py` | RunPod Cloud Workers |

---

## 🔍 EVIDENCIAS DE AUDITORÍA FÍSICA

1. **Servicios de Sistema (`systemd --user`)**:
   - `moneyprinter-api.service`: Activo y escuchando en `127.0.0.1:8080`.
   - `moneyprinter-webui.service`: Activo y escuchando en `0.0.0.0:7001`.
   - `hermes-antigravity-provider.service`: Activo y escuchando en `0.0.0.0:8742`.
2. **Persistencia Verificada**:
   - Firestore: Sincronización asíncrona de `pipeline_graph` y `providers_registry`.
   - Local: Bóveda de Jobs en `storage/jobs/`, Workflows en `storage/workflows/`.
   - Cloudflare R2: Cliente S3 funcional con fallback local buffer en `storage/renders/`.
3. **Desacoplamiento ComfyUI**:
   - VideoPro ejecuta pipelines nativos multimotor (Google Flow, FLUX, NanoBanana, FFmpeg, VibeVoice).
   - El soporte para despachar tareas a servidores ComfyUI externos está desacoplado a través de `ComfyUIAdapter` para cuando se conecte un endpoint en el futuro.
