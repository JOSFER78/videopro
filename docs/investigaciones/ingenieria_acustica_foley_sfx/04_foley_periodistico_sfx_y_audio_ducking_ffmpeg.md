# 🎧 Tratado de Ingeniería Acústica: Foley Periodístico, Psicoacústica y Audio Ducking

> **Categoría:** Psicoacústica & Procesamiento de Señal de Audio  
> **Ubicación:** `docs/investigaciones/03_ingenieria_acustica_y_psicoacustica/` / `docs/nodos_y_motores/music/03_foley_director_ducking_master/`  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA

---

## 📌 1. La Jerarquía Psicoacústica de 3 Capas

Para que un documental de alto impacto mantenga al espectador enganchado sin fatiga auditiva, la mezcla de sonido se estructura en una jerarquía tridimensional estricta:

```
┌────────────────────────────────────────────────────────┐
│ 1. LOCUCIÓN PRINCIPAL (VO / Narration)                 │  +10 dB (Máster Absoluto, Presencia 1-4 kHz)
├────────────────────────────────────────────────────────┤
│ 2. UNDERSCORE MUSICAL (BGM)                            │  Ducking dinámico a -22 dB durante la voz
├────────────────────────────────────────────────────────┤
│ 3. CAPA DE REALIDAD (Foley de Papel, Clics, Texturas)   │  -18 a -24 dB (Inmersión subconsciente)
└────────────────────────────────────────────────────────┘
```

---

## 📄 2. Catálogo de Texturas Analógicas & Foley de Papel

| Efecto de Sonido | Micrófono & Muestreo | Duración Óptima | Propósito Cinemático |
| :--- | :--- | :--- | :--- |
| **`paper_slide.wav`** | Neumann KM184 (24-bit / 96kHz) | `0.4s - 0.8s` | Deslizamiento de tarjetas, gráficos de datos y tercios inferiores |
| **`single_book_page.wav`** | Sound Devices 702 (24-bit / 96kHz) | `1.2s - 1.8s` | Transición entre capítulos o revelación de documentos históricos |
| **`typewriter_click.wav`** | Cápsula cardioide hiper-direccional | `0.05s` | Sincronización por carácter en efectos de texto mecanografiado |
| **`camera_shutter.wav`** | Grabación mecánica de diafragma | `0.2s` | Congelación de fotograma (Freeze 3D) e inserción de polaroids |
| **`subtle_whoosh.wav`** | Síntesis acústica sub-grave (120 Hz) | `0.5s` | Barridos rápidos de cámara y transiciones `whipPan` |

---

## 🎚️ 3. Pipeline Automatizado de Sidechain Ducking con FFmpeg

El filtro `sidechaincompress` de FFmpeg monitoriza la señal de voz del locutor y atenúa de forma automática e imperceptible el canal musical:

```bash
ffmpeg -y \
  -i raw_voiceover.wav \
  -i raw_background_music.wav \
  -filter_complex \
  "[0:a]asplit=2[vo_clean][vo_detector]; \
   [1:a]volume=1.0[bgm_base]; \
   [bgm_base][vo_detector]sidechaincompress=threshold=0.05:ratio=12.5:attack=10:release=120[bgm_ducked]; \
   [vo_clean][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=3[out_audio]" \
  -map "[out_audio]" \
  -c:a aac -b:a 256k master_audio_ducked.aac
```

### Parámetros Clave:
- **`threshold=0.05`:** Umbral de disparo instantáneo ante las primeras consonantes de la voz.
- **`ratio=12.5`:** Nivel de compresión que reduce el volumen musical en **`-22 dB`**.
- **`attack=10ms`:** Ataque ultrarrápido que evita que la música compita con el inicio de cada frase.
- **`release=120ms`:** Recuperación gradual y natural del fondo musical en las pausas de respiración.

---

## 🔇 4. Mitigación de Clics Digitales de Fase
Al realizar cortes y transiciones entre planos que contienen audio, la discontinuidad de la onda senoidal en el punto cero genera un chasquido perceptible en auriculares de alta gama.

> [!CAUTION]
> **Norma Inalterable:** Todo corte de audio en el timeline debe incorporar un **micro-crossfade de exactamente `30 ms`** (`afade=t=in:d=0.03`, `afade=t=out:d=0.03`) para asegurar una continuidad de fase impecable.
