# 🎬 ARQUITECTURA DEL SUBMÓDULO `DOCUMENTARY_DIRECTOR`

Este documento describe la arquitectura de software, roles agénticos, algoritmos de sincronización y protocolos de control de calidad para el orquestador cinematográfico de **videopro**.

---

## 1. ESTRUCTURA Y ROLES AGÉNTICOS

El submódulo `DOCUMENTARY_DIRECTOR` orquesta 4 disciplinas especializadas en una cadena de producción autónoma:

```text
                  ┌──────────────────────────────────────────────┐
                  │          DOCUMENTARY_DIRECTOR               │
                  │        (Master Video Orchestrator)           │
                  └──────────────────────┬───────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌──────────────────┐           ┌──────────────────┐           ┌──────────────────┐
│  INVESTIGADOR &  │           │   DIRECTOR DE    │           │   DIRECTOR DE    │
│  FACT-CHECKER    │           │ FOTOGRAFÍA & ARTE│           │ SONIDO & MONTAJE │
│ (Dossier BBC 2x) │           │ (7-Shot & Flow)  │           │(VO-First & Duck) │
└────────┬─────────┘           └────────┬─────────┘           └────────┬─────────┘
         │                               │                               │
         └───────────────────────────────┼───────────────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────┐
                        │   SUPERVISOR DE CONTINUIDAD &   │
                        │       CALIDAD MULTIMODAL        │
                        │   (Face/Costume/Gate >5KB)      │
                        └─────────────────────────────────┘
```

### 1.1 Responsabilidades por Sub-Rol:
1. **Investigador Principal & Fact-Checker:** Redacta `RESEARCH_DOSSIER.md` auditando cada afirmación con doble fuente y clasificando los hechos (`[FACT]`, `[REC]`, `[INTERP]`).
2. **Director de Fotografía & Arte:** Genera las 4 Biblias Visuales, ingredientes/turnarounds y los prompts canónicos 7D (desglose obligatorio de 7 planos por escena).
3. **Director de Sonido & Montaje (VO-First Lead):** Sintetiza la locución con `VibeVoice`, `ElevenLabs` o `Edge-TTS`, extrae marcas de tiempo de palabras con Whisper y sincroniza el montaje elástico.
4. **Supervisor de Continuidad y Calidad (QA Lead):** Audita la regla de oro (> 5 KB), analiza la similitud facial ($\ge 0.82$) y ejecuta el bucle de auto-regeneración ante desviaciones.

---

## 2. SINCRONIZACIÓN VO-FIRST Y ALGORITMO DE MONTAJE ELÁSTICO

El montaje audiovisual nunca se basa en duraciones fijas arbitrarias; la locución humana o sintética actúa como el **ancla temporal soberana**:

```text
[Guion Narrativo] ──► [TTS: VibeVoice/Edge-TTS] ──► [Locución narration.mp3]
                                                             │
                                                             ▼
                                                    [Whisper Stable-TS]
                                                             │
                                                             ▼
                                                    [vo_durations.json]
                                              (Marcas a nivel de palabra)
                                                             │
┌────────────────────────────────────────────────────────────┴──────────────────────────────────────────┐
│ ALGORITMO DE MONTAJE ELÁSTICO (ELASTIC SHOT SNAPPING)                                                 │
│                                                                                                       │
│ Frase 1 (0.0s - 3.2s)           │ Silencio (0.4s) │ Frase 2 (3.6s - 7.1s)      │ Cierre (7.1s - 10.0s) │
│ ────────────────────────────────┴─────────────────┴────────────────────────────┴───────────────────────│
│ Plano 1 (EWS)      │ Plano 2 (WS)                 │ Plano 3 (MS)   │ Plano 4 (CU) │ Plano 5 (Reveal)  │
│ [Ken Burns In]     │ [Tracking Lateral]           │ [Paper Cutout] │ [Macro Data] │ [Zoom Out Pan]    │
│ (2.0s)             │ (1.6s)                       │ (2.0s)         │ (1.5s)       │ (2.9s)            │
└────────────────────────────────────────────────────────────┬──────────────────────────────────────────┘
                                                             │
                                                             ▼
                                                [Mezcla Master de Audio]
                                                • VO: -14 LUFS (EBU R128)
                                                • BGM: -18dB a -22dB Ducking
                                                • SFX Foley: 30ms Crossfade
```

---

## 3. PROTOCOLO DE CONTINUIDAD Y AUTO-REGENERACIÓN (CLOSED-LOOP QA)

```text
                ┌──────────────────────────────────────┐
                │     Activos Generados (Fotos/Clips)  │
                └──────────────────┬───────────────────┘
                                   │
                                   ▼
                ┌──────────────────────────────────────┐
                │      Gate 1: Regla > 5 KB &          │
                │      Integridad Técnica (ffprobe)    │
                └──────────────────┬───────────────────┘
                                   │ [Aprobado]
                                   ▼
                ┌──────────────────────────────────────┐
                │      Gate 2: Análisis Multimodal     │
                │      (Gemini Vision / Embeddings)    │
                │  • Consistencia Facial (Cosine ≥0.82)│
                │  • Consistencia Vestuario/Colores    │
                │  • Detección de Anacronismos         │
                └──────────────────┬───────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
          [Score ≥ 0.85: PASS]          [Score < 0.85: FAIL]
                    │                             │
                    ▼                             ▼
       ┌────────────────────────┐    ┌────────────────────────┐
       │ Proceder al Render     │    │ Auto-Regenerate Loop   │
       │ (MoviePy / FFmpeg)     │    │ • Refinar Prompt       │
       └────────────────────────┘    │ • Aumentar Ref Weight  │
                                     │ • Reintentos: Máx 3    │
                                     └────────────┬───────────┘
                                                  │
                                                  ▼
                                     [Reingresar a Generación]
```

### Criterios de Aceptación:
1. **Fidelidad Facial:** Similitud del coseno de embeddings faciales $\ge 0.82$ respecto a la Character Bible.
2. **Vestuario & Paleta:** Coherencia de colores institucionales y ausencia de prendas anacrónicas.
3. **Regla de Oro:** Todo activo generado debe pesar $> 5\text{ KB}$ y superar la verificación con `ffprobe` o `Pillow`.
4. **Fondo Anti-Blackdetect:** Prohibición expresa de negro puro `#000000` (se utiliza `#243048`).
