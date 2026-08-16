# VIDEOPRO — MAPA DE ARQUITECTURA DEL SISTEMA (SYSTEM_MAP.md)

**Versión:** 1.0.0 — Canónica  
**Estado:** `CURRENT / ARCHITECTURAL BLUEPRINT`  
**Última Actualización:** Agosto 2026

Este documento visualiza las relaciones funcionales, desacopladas y reales entre las distintas capas de VideoPro.

---

## 🏛️ DIAGRAMA MAESTRO DE RELACIONES

```text
                                 ┌─────────────────────────┐
                                 │        VIDEOPRO         │
                                 │  (Aplicación Principal) │
                                 └────────────┬────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    │                                                   │
         ┌──────────▼──────────┐                             ┌──────────▼──────────┐
         │   VIDEOPRO STUDIO   │                             │   VIDEOPRO BACKEND  │
         │  (Streamlit :7001)  │                             │   (FastAPI :8080)   │
         └──────────┬──────────┘                             └──────────┬──────────┘
                    │                                                   │
         ┌──────────▼──────────┐                             ┌──────────▼──────────┐
         │  WORKFLOW DESIGNER  │                             │  STUDIO CONTROLLER  │
         │  (Editor de Nodos)  │                             │   (/api/v1/studio)  │
         └──────────┬──────────┘                             └──────────┬──────────┘
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │     REQUEST PLANNER     │
                                 │  (Compilador de Planes) │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │    SCENE-LEVEL ROUTER   │
                                 │  (Ruteo Multimotor 4K)  │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────┐
                                 │    WORKFLOW EXECUTOR    │
                                 │   (Ejecución de Jobs)   │
                                 └────────────┬────────────┘
                                              │
                                              ▼
                    ┌───────────────────────────────────────────────────┐
                    │               CAPABILITIES & ADAPTERS             │
                    │        (Capa de Aislamiento e Integración)        │
                    └─────────┬───────────────────────────────┬─────────┘
                              │                               │
            ┌─────────────────┴────────────────┐              │
            │ MOTORES Y SERVICIOS ACTIVOS     │              │
            ├──────────────────────────────────┤              │
            │ • Google Flow Engine (4K Dron)   │              │
            │ • FLUX 3 / ZeroGPU (Visual)      │              │
            │ • NanoBanana Pro (2K/4K Render)  │              │
            │ • VibeVoice 1.5B (es-emilio TTS) │              │
            │ • Whisper STT (Timestamps)       │              │
            │ • FFmpeg Master & Ducking        │              │
            │ • Remotion React (Infografías)   │              │
            │ • Hermes Subagents (Investigac.) │              │
            └──────────────────────────────────┘              │
                                                              │
            ┌──────────────────────────────────┐              │
            │ INTEGRACIONES FUTURAS (PLANNED)  │              │
            ├──────────────────────────────────┤              │
            │ • ComfyUI Server (:8188)         │              │
            │ • RunPod Cloud GPU Workers       │              │
            └──────────────────────────────────┘              │
                                                              │
                    ┌─────────────────────────────────────────┴─────────┐
                    │                CAPA DE PERSISTENCIA               │
                    └─────────┬───────────────────────────────┬─────────┘
                              │                               │
                    ┌─────────▼─────────┐           ┌─────────▼─────────┐
                    │     FIRESTORE     │           │   CLOUDFLARE R2   │
                    │   (Base NoSQL)    │           │ (Object Storage)  │
                    ├───────────────────┤           ├───────────────────┤
                    │ • Metadatos       │           │ • Vídeos MP4      │
                    │ • Workflows JSON  │           │ • Fotos 4K        │
                    │ • Trazas de Jobs  │           │ • Pistas de Audio │
                    │ • Estado UI       │           │ • Renders Finales │
                    └───────────────────┘           └───────────────────┘
```

---

## 📐 PRINCIPIOS DE DISEÑO Y DESACOPLAMIENTO

1. **El Workflow no conoce la Infraestructura**:
   - Un nodo del workflow solicita una Capacidad (`Capability.VIDEO_GENERATION`). El `RequestPlanner` y el `SceneEngineRouter` resuelven qué motor y qué proveedor ejecutar según prioridad, salud y coste.
2. **Ningún motor está acoplado al núcleo**:
   - Cada motor externo (`Google Flow`, `FLUX`, `VibeVoice`, `ComfyUI`, `Hermes`) se comunica exclusivamente a través de su clase `BaseEngineAdapter` en `app/core/orchestration/adapters/`.
3. **Persistencia Bifurcada**:
   - **Metadatos y Estado:** Firestore (`ayuda-emilio-83261`).
   - **Cargas Binarias:** Cloudflare R2 con buffer local en `storage/renders/`.
