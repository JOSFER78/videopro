# Plan Maestro: Dominio de Flow Music & Generación de Audio Atmosférico

## 1. Visión y Objetivos
El objetivo de esta investigación y sistema es dominar **Flow Music** (y arquitecturas generativas de audio musical de vanguardia) para la producción autónoma de dos tipos clave de activos sonoros:
1. **BSO Ambient y Orquestal de Larga Duración (15 a 60 min)**: Metodología de 5 fases consecutivas y ensamblado con fundidos exponenciales S-Curve para superar el límite de 3 minutos de la app web.
2. **Audio Neural, Frecuencias (432Hz/528Hz), Espacialización 3D y Micro-texturas ASMR**: Generación de paisajes sonoros psicoacústicos diseñados para máxima retención, relajación profunda y estimulación sensorial inmersiva.
3. **Automatización Web 100% Autónoma (Playwright / CDP :9222)**: Solución definitiva para explotar y monetizar créditos masivos acumulados en la interfaz web de Flow Music sin fricción ni APIs externas de pago.

---

## 2. Estructura de Carpetas en el Proyecto
```bash
docs/investigaciones/nodos_capacidades/flowmusic-via-playwright/
├── 00_plan_maestro_flow_music.md                     # Este documento
├── 03_automatizacion_autonoma_playwright_cdp.md     # Guía técnica de automatización Playwright/CDP :9222
├── 04_estrategia_quema_creditos_y_lotes_flowmusic.md # Estrategia de producción masiva por lotes
├── bso_larga_duracion/
│   ├── 01_guia_bso_ambient_continua.md               # Metodología de loops, stems, transiciones y progresión armónica
│   └── 02_arquitectura_oneshot_15min_y_extension_por_fases.md # Arquitectura de 5 fases (15 min) y ensamblado continuo
├── efectos_neurales_mhz_3d_asmr/
│   ├── 01_frecuencias_binaural_3d_asmr.md            # Guía psicoacústica (432Hz, ondas theta/alpha, HRTF 3D, ASMR)
│   └── 02_procesamiento_audio_audiophilo_y_cascos.md # Cadena de masterización dual (Lujo vs Consumo)
├── mastering_cascos_lujo/
│   ├── 01_guia_mastering_audiofilo_cascos_lujo.md    # 8 Pilares de masterización para cascos flagship
│   ├── 02_cadena_dsp_y_filtros.md                    # Topología DSP 32-bit float, filtros FFmpeg & curvas
│   ├── 03_pipeline_montaje_y_mastering_15min.md      # Pipeline de montaje y masterización de 15 minutos
│   ├── presets/audiophile_luxury_chain.json          # Preset JSON de parámetros y ecualización quirúrgica
│   └── scripts/audiophile_audio_processor.py         # Procesador DSP Python con Crossfeed Meier y M/S Matrix
├── prompts/
│   ├── biblioteca_prompts_maestros.md                # Catálogo de prompts bilingües optimizados (EN/ES)
│   └── 02_planes_fases_15min_orquestal_y_cinematico.md # Suites completas de 5 fases (Wide Horizon, Tritemporal, ASMR)
└── templates/
    ├── prompt_template_flow_music.json               # Esquema JSON reutilizable para generación programática
    └── batch_flow_music_prompts.json                 # Lote de prompts para generación desatendida masiva
```

---

## 3. Plan de Aprendizaje y Ejecución en 7 Fases

### Fase 1: Sintaxis y Gramática de Prompts para Flow Music
- **Estructura de Prompt Óptima**:
  `[Género / Función Primaria] + [Instrumentación & Capas Timbres] + [Afinación/Frecuencias Clave] + [Diseño Espacial & Estéreo 3D] + [Texturas ASMR / Foley Orgánico] + [Tempo & Dinámica] + [Restricciones Negativas]`
- **Uso preferente del inglés**: Flow Music responde con mayor precisión y riqueza armónica a descriptores técnicos en inglés (`warm 432Hz sub drones`, `binaural spatial field`, `panning organic foley`, `no percussive transients`).

### Fase 2: Arquitectura de 15 Minutos en 5 Fases Consecutivas
- Superación del límite de 3 minutos de Flow Music mediante el modelo de 5 fases estructuradas:
  - **Fase 1 (0:00–3:00)**: Pista Base / Intro (Tonalidad, tempo, 432Hz/528Hz, textura ASMR, sin batería).
  - **Fase 2 (3:00–6:00)**: Primera Extensión (Desarrollo temático, pulso grave constante).
  - **Fase 3 (6:00–9:00)**: Segunda Extensión (Amplitud armónica, cuerdas sinfónicas, paneo binaural).
  - **Fase 4 (9:00–12:00)**: Tercera Extensión / Clímax (Crescendo orquestal triunfante, energía máxima).
  - **Fase 5 (12:00–15:00)**: Cuarta Extensión / Cierre (Decrescendo progresivo, drones persistentes y disolución en silencio).

### Fase 3: Ensamblado Continuo Automatizado (S-Curve Crossfade)
- Unión matemática mediante `flow_music_phase_assembler.py` aplicando crossfade exponencial S-Curve (`c1=exp:c2=exp`) de 6 segundos entre fases para garantizar continuidad sonora perfecta y cero caídas de volumen o fase.

### Fase 4: Audio Psicoacústico y Micro-ASMR 3D
- **Frecuencias Sagradas & Ondas Cerebrales**: Sintonización fundamental a 432Hz y 528Hz, ondas Alpha/Theta integradas.
- **Espacialización 3D**: Modelado psicoacústico de cabeza (HRTF) con Bauer/Meier Crossfeed (`bs2b`) para proyectar el audio fuera de la cabeza.
- **Compresión Upward ASMR**: Respaldo dinámico para hacer audibles micro-texturas íntimas (adoquines, brisa, foley).

### Fase 5: Masterización de Altas Prestaciones para Cascos de Lujo y YouTube
- **YouTube Standard**: `-14.0 LUFS`, True Peak `-1.0 dBFS`, Air Band 14kHz (+2.2dB), 24-bit 48kHz WAV.
- **Audiophile Luxury**: `-16.0 LUFS`, True Peak `-1.5 dBFS`, 24-bit 96kHz FLAC sin fatiga auditiva.

### Fase 6: Automatización Web Desatendida (Playwright + CDP :9222)
- Acoplamiento directo a la sesión de navegador autenticada en el VPS mediante Chrome DevTools Protocol (`connect_over_cdp("http://localhost:9222")`).
- Ejecución desatendida de prompts, control de sliders, bypass de modales y captura de streams / blobs de audio generados.
- Quema automatizada de créditos en segundo plano sin intervención manual ni riesgo de bloqueos.

### Fase 7: Pipeline de Integración con VideoPro y CHRONODRIFT
- Servicio unificado en [`app/services/audio/flowmusic_service.py`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/app/services/audio/flowmusic_service.py) para solicitar suites completas de 15 minutos en tiempo real durante la generación de escenas de vídeo.
- Almacenamiento y registro automático en [`VideoStorageManager`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/scripts/video_storage_manager.py) bajo `storage/music/flowmusic/`.
