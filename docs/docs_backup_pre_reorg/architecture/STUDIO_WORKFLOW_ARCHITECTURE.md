# STUDIO WORKFLOW ARCHITECTURE — VIDEOPRO STUDIO

**Fecha de Implementación:** 16 de Agosto de 2026  
**Patrón de Arquitectura:** Layered Multi-Engine Orchestration (Pipeline as Code)  
**Principio Fundamental:**  
`REQUEST ➔ PLANNER ➔ WORKFLOW ➔ CAPABILITIES ➔ ENGINES ➔ PROVIDERS ➔ EXECUTION JOB ➔ RESULTS`

---

## 1. PRINCIPIOS DE DESACOPLAMIENTO Y FRONTERAS

1. **La UI no llama directamente a motores concretos**: La UI emite una petición normalizada o selecciona un Workflow; el Request Planner y el Orchestrator resuelven los motores y proveedores.
2. **Los Engines no conocen la arquitectura completa**: Cada motor implementa `BaseEngineAdapter` (`validate_input`, `execute`, `check_health`, `cancel`), encapsulando su lógica de invocación.
3. **Separación radical de Engine ("CÓMO") y Provider ("DÓNDE")**:
   - `flux_video` puede correr en `serverless_zerogpu`, `serverless_runpod`, o `local_gpu`.
   - `google_flow` puede correr en `local_headless` o `local_bridge`.
   - `vibevoice` puede correr en `serverless_zerogpu` o `local_vps`.
   - `comfyui` puede correr en `local` o `serverless_runpod`.
4. **Firestore es la fuente de verdad para metadatos y estado**, mientras que **Cloudflare R2 es el object storage para media** y el disco local es solo un buffer temporal.

---

## 2. MAPA DE CAPAS DEL STUDIO

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           1. REQUEST LAYER                              │
│  • Petición en lenguaje natural / parámetros de producción              │
│  • Normalización de duración, estilo, temática y formato óptico         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      2. REQUEST PLANNER & ROUTER                        │
│  • RequestPlanner: Resuelve la descomposición en capacidades            │
│  • SceneEngineRouter: Asignación multimotor por escena (Scene 1->Stock, │
│    Scene 2->Flow, Scene 3->FLUX 3, Scene 4->NanoBanana 2K, etc.)        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   3. WORKFLOWS & WORKFLOW DESIGNER                      │
│  • Plantillas: DOCUMENTARY_MASTER, FLOW_ONLY, FLUX_ONLY, STOCK_ONLY,    │
│    FLOW_FLUX_HYBRID, IMAGE_DOCUMENTARY, VOICE_ONLY, CUSTOM_COMFY       │
│  • Designer: Manipula grafos JSON (nodos, cables, sockets, versiones)   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         4. CAPABILITIES (QUÉ)                           │
│  • research, script, scene_planning, voice_generation, speech_to_text,  │
│    image_generation, video_generation, music_generation, foley_sfx,     │
│    subtitle_generation, post_processing, rendering, storage             │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           5. ENGINES (CÓMO)                             │
│  • google_flow, flux_video, nanobanana, ltx25, stock_db, vibevoice,    │
│    whisper, flow_music, vox_subtitles, ffmpeg, remotion, comfyui, hermes│
│  • Prioridades de coste ($0 ZeroGPU / Token Pool / Dedicated)           │
│  • Cadenas de Fallback (google_flow -> flux_video -> stock_db)          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         6. PROVIDERS (DÓNDE)                            │
│  • Local VPS, Antigravity Bridge, ZeroGPU Pool, RunPod, Cloudflare R2   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 7. EXECUTION JOBS & WORKFLOW EXECUTOR                   │
│  • ExecutionJob ➔ JobSteps con estados, duración, costes y logs         │
│  • Máquina de estados: queued ➔ running ➔ retrying ➔ fallback ➔ done    │
│  • Persistencia auditable en storage/jobs/ y Firestore                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CÓMO AÑADIR UN NUEVO MOTOR EN EL FUTURO

Para añadir un nuevo motor (ej: `new_video_engine`), **NO se modifica la UI, ni Firebase, ni el renderizador**. Únicamente se requiere:
1. Declarar su Capability en [app/core/orchestration/capabilities.py](file:///home/ubuntu/workspace/pro/hermes/10_videopro/app/core/orchestration/capabilities.py).
2. Declarar su `EngineSpec` con fallbacks y prioridades en [app/core/orchestration/engines.py](file:///home/ubuntu/workspace/pro/hermes/10_videopro/app/core/orchestration/engines.py).
3. Declarar sus `ProviderSpec` en [app/core/orchestration/providers.py](file:///home/ubuntu/workspace/pro/hermes/10_videopro/app/core/orchestration/providers.py).
4. Implementar su `BaseEngineAdapter` en `app/core/orchestration/adapters/` y registrarlo en `AdapterRegistry`.

El Request Planner, el Scene Router, el Workflow Designer y el Executor integrarán el nuevo motor automáticamente.

---

## 4. API REST ENDPOINTS OFICIALES

- `GET /api/v1/studio/manifest`: Manifiesto completo del ecosistema.
- `GET /api/v1/studio/capabilities`: Catálogo de capacidades.
- `GET /api/v1/studio/engines`: Catálogo de motores con health y fallbacks.
- `GET /api/v1/studio/providers`: Proveedores de infraestructura por motor.
- `GET /api/v1/studio/workflows`: Plantillas de workflows de producción.
- `POST /api/v1/studio/plan`: Genera un `ExecutionPlan` a partir de un prompt.
- `POST /api/v1/studio/execute`: Ejecuta un Job y devuelve la trazabilidad paso a paso.
- `GET /api/v1/studio/jobs`: Historial de ejecuciones auditables.
- `GET /api/v1/studio/jobs/{job_id}`: Detalle de ejecución, duración, costes y logs.
