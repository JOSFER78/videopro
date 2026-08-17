# 🧠 ESTÁNDARES ÁUREOS Y MOTOR DE APRENDIZAJE CONTINUO (LEARNING MEMORY)

Fuente de Verdad extraída de `app/services/learning_memory_engine.py` y `storage/learning_memory/lessons_catalog.json` en VideoPro (`/home/ubuntu/workspace/pro/hermes/10_videopro`).

---

## 🌟 1. LAS 6 REGLAS DE ORO DE LA PRODUCCIÓN AUDIOVISUAL

### 1.1 Ritmo Cinemático y Variación Visual Dinámica (3s - 5s)
- **ID:** `rule_dynamic_visual_cutaways_3s` | **Severidad:** `CRITICAL`
- **Fallo común:** Planos fijos o estáticos prolongados (>6-10s) mientras la voz avanza, provocando pérdida de retención y sensación de vídeo aficionado estático.
- **Regla Áurea:** Cambiar de ángulo de cámara, aplicar movimiento Ken-Burns dinámico (`zoompan`), o alternar B-Roll/fotogramas de detalle macro cada **3 a 5 segundos como máximo**.
- **Nodos aplicables:** `node_03_ingesta_multimedia_4k`, `node_04_composicion_motion_graphics`.

### 1.2 Tipografía Broadcast: Tercios Inferiores Limpios
- **ID:** `rule_sleek_broadcast_typography` | **Severidad:** `CRITICAL`
- **Fallo común:** Uso de recuadros negros toscos con texto invasivo, fuentes genéricas y leyendas explícitas como "FUENTE: https://..." que degradan la estética visual.
- **Regla Áurea:** Diseño tipográfico sutil y moderno (Inter / Outfit / JetBrains Mono para datos), sombras suaves de texto (`drop-shadow: 0 4px 12px rgba(0,0,0,0.5)`), lower-thirds de alta gama con márgenes elegantes (80px del borde) y sin URLs crudas.
- **Nodos aplicables:** `node_04_composicion_motion_graphics`, `node_05_render_master`.

### 1.3 Sidechain Ducking Dinámico en Audio (-18 dB a -22 dB)
- **ID:** `rule_audio_ducking_minus20db` | **Severidad:** `CRITICAL`
- **Fallo común:** Música de fondo (BGM) compitiendo en volumen con la voz del narrador o cortes bruscos de volumen que fatigan el oído.
- **Regla Áurea:** Atenuar automáticamente la pista BGM entre **-18 dB y -22 dB** de ganancia en cada intervalo donde haya presencia de voz en off (`vo_durations.json`). Aplicar un ataque de **150ms** y una relajación (*release*) de **350ms** con rampa síncrona.
- **Nodos aplicables:** `node_02_sintesis_voz_foley`, `node_05_render_master`.

### 1.4 Subtítulos de Alto Contraste (Karaoke Centrado Inferior)
- **ID:** `rule_high_contrast_karaoke_captions` | **Severidad:** `HIGH`
- **Fallo común:** Subtítulos pegados a los bordes inferiores, fuentes sin reborde ilegibles sobre fondos claros, o bloques largos de texto que tapan la acción.
- **Regla Áurea:** Subtítulos palabra por palabra dinámicos con resaltado amarillo `#FFD700` o blanco sobre fondo crema/oscuro, tipografía gruesa sans-serif, contorno sutil (`stroke: 2px #000000`), posición centrada al **82% de altura** (para 16:9) o **75%** (para 9:16 vertical, evitando solapar interfaz de TikTok/YouTube Shorts).
- **Nodos aplicables:** `node_04_composicion_motion_graphics`.

### 1.5 Paleta Anti-Blackdetect (Fondo Navy Industrial)
- **ID:** `rule_zero_blackdetect_palette` | **Severidad:** `CRITICAL`
- **Fallo común:** Uso de negro puro `RGB (0,0,0)` en fondos de transición o composición que dispara falsos positivos en analizadores automáticos de vídeo (*blackdetect filters*).
- **Regla Áurea:** Usar siempre azul marino oscuro industrial `RGB (36,48,72)` / Hex `#243048` o gris grafito cálido `#1A1D24` como base de canvas.
- **Nodos aplicables:** `node_04_composicion_motion_graphics`, `node_05_render_master`.

### 1.6 Mitigación de Clics de Fase (Crossfade de 30ms)
- **ID:** `rule_audio_crossfade_30ms` | **Severidad:** `HIGH`
- **Fallo común:** Clics y chasquidos audibles producidos por cortes abruptos en clips de audio sin cruce por cero (*zero-crossing*).
- **Regla Áurea:** Aplicar un *fade-in* y *fade-out* suave de **30 ms** (`afade=t=in:ss=0:d=0.03,afade=t=out:st=END-0.03:d=0.03`) en cada corte de audio o fragmento ensamblado.
- **Nodos aplicables:** `node_02_sintesis_voz_foley`.

---

## 📊 2. ESQUEMA DE AUDITORÍA Y CRÍTICA POST-PRODUCCIÓN

Todo proyecto ejecutado evalúa automáticamente su calidad mediante el siguiente esquema JSON de evaluación:

```json
{
  "project_id": "2026-08-16_workflow_madrid_curiosities_3min",
  "overall_score": 0.96,
  "metrics": {
    "visual_pacing_score": 0.98,
    "typography_elegance_score": 0.95,
    "audio_intelligibility_score": 0.97,
    "blackdetect_clean_score": 1.00,
    "foley_sync_score": 0.94
  },
  "identified_critiques": [],
  "passed_golden_rules": [
    "rule_dynamic_visual_cutaways_3s",
    "rule_sleek_broadcast_typography",
    "rule_audio_ducking_minus20db",
    "rule_high_contrast_karaoke_captions",
    "rule_zero_blackdetect_palette",
    "rule_audio_crossfade_30ms"
  ]
}
```
