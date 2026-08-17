# 🎧 Tratado de Ingeniería Acústica: Jerarquía Psicoacústica, Foley Analógico, Sidechain Ducking y Masterización EBU R128

> **Pilar:** Ingeniería de Audio & DSP  
> **Estado:** 🟢 ESPECIFICACIÓN TÉCNICA CANÓNICA  

---

## 1. La Jerarquía Psicoacústica de 3 Capas

Para garantizar la máxima inteligibilidad del mensaje, profundidad tridimensional y evitar la fatiga auditiva:

```text
┌────────────────────────────────────────────────────────┐
│ 1. LOCUCIÓN PRINCIPAL (VO / Narration)                 │  +10 dB (Máster Absoluto, Presencia 1-4 kHz)
├────────────────────────────────────────────────────────┤
│ 2. UNDERSCORE MUSICAL (BGM)                            │  Ducking dinámico a -22 dB (-18 a -24 dB) durante la voz
├────────────────────────────────────────────────────────┤
│ 3. CAPA DE REALIDAD (Foley Analógico, Clics, Texturas)  │  -18 a -24 dB (Inmersión subconsciente)
└────────────────────────────────────────────────────────┘
```

- **Capa 1: Locución Principal (VO)**: Nivel máster de referencia (+10 dB relativo). Claridad espectral afinada entre 1 kHz y 4 kHz.
- **Capa 2: Underscore Musical (BGM)**: Ducking dinámico automático entre **-18 dB y -24 dB** (típico **-22 dB**) mediante compresión por cadena lateral (*sidechain*) cuando la voz está activa.
- **Capa 3: Capa de Realidad (Foley Analógico & SFX)**: Calibrado entre **-18 dB y -24 dB** en el espacio estéreo/binaural sin competir con la voz ni embarrar los sub-graves.

---

## 2. Catálogo Canónico de Foley Analógico (Neumann KM184 24-bit / 96kHz)

| Archivo / Efecto | Micrófono & Muestreo | Duración | Aplicación Cinemática |
| :--- | :--- | :--- | :--- |
| **`paper_slide.wav`** | Neumann KM184 (24-bit / 96kHz) | `0.4s - 0.8s` | Deslizamiento de tarjetas, gráficos de datos y *lower thirds*. |
| **`single_book_page.wav`** | Sound Devices 702 (24-bit / 96kHz) | `1.2s - 1.8s` | Transición entre capítulos y revelación de documentos históricos. |
| **`typewriter_click.wav`** | Cápsula cardioide hiper-direccional | `0.05s` | Mecanografiado síncrono por carácter en textos typewriter. |
| **`camera_shutter.wav`** | Grabación mecánica de diafragma | `0.2s` | Congelación de fotograma (*Freeze 3D*) y polaroids. |
| **`subtle_whoosh.wav`** | Síntesis acústica sub-grave (120 Hz) | `0.5s` | Barridos rápidos de cámara y transiciones `whipPan`. |

---

## 3. Comandos FFmpeg de Synchronous Sidechain Ducking

### A. Ducking Canónico VO + BGM (-22 dB)
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

### B. Mezcla Sidechain Multicanal 3 Vías (VO + BGM + Foley)
```bash
ffmpeg -y \
  -i vo_track.wav \
  -i bgm_track.wav \
  -i foley_track.wav \
  -filter_complex \
  "[1:a][0:a]sidechaincompress=threshold=0.08:ratio=6:attack=30:release=250:level_in=1[ducked_bgm]; \
   [2:a][0:a]sidechaincompress=threshold=0.10:ratio=4:attack=20:release=200:level_in=0.8[ducked_foley]; \
   [0:a]volume=1.0[vo]; \
   [ducked_bgm][ducked_foley][vo]amix=inputs=3:weights=1.0 0.85 1.2:normalize=0[mixed]" \
  -map "[mixed]" -ar 48000 -c:a pcm_s24le raw_audio_mix.wav
```

---

## 4. Mitigación de Clics Digitales de Fase

### Micro-Crossfade de 30 ms
En cada corte o transición entre planos con audio activo, aplicar una rampa obligatoria de **30 ms**:
```text
afade=t=in:d=0.03,afade=t=out:d=0.03
```

### Concatenación Continua (Curva S-Curve de 6s en Suites de 15 min)
```bash
ffmpeg -y \
  -i p1.wav -i p2.wav -i p3.wav -i p4.wav -i p5.wav \
  -filter_complex "\
    [0:a][1:a]acrossfade=d=6:c1=exp:c2=exp[a01]; \
    [a01][2:a]acrossfade=d=6:c1=exp:c2=exp[a02]; \
    [a02][3:a]acrossfade=d=6:c1=exp:c2=exp[a03]; \
    [a03][4:a]acrossfade=d=6:c1=exp:c2=exp[out] \
  " -map "[out]" -c:a pcm_s24le suite_stitched.wav
```

---

## 5. Masterización EBU R128 / ITU-R BS.1770-4

### Parámetros Normativos:
- **Loudness Integrado ($I$)**: `-14.0 LUFS` ($\pm 0.5\text{ LU}$) para YouTube/Broadcast; `-16.0 LUFS` en perfil audiófilo.
- **True Peak Máximo ($TP$)**: `-1.0 dBTP` (evita distorsión inter-sample en DACs).
- **Loudness Range ($LRA$)**: `7.0 - 11.0 LU`.
- **Frecuencia de Muestreo**: `48000 Hz` / `24-bit PCM`.

### Comando Todo-en-Uno Audiófilo + Crossfeed Binaural (`bs2b`)
```bash
ffmpeg -y -i raw_audio_mix.wav -af "\
  highpass=f=20:p=2, \
  equalizer=f=320:t=q:w=0.8:g=-1.2, \
  equalizer=f=4200:t=q:w=2.8:g=-1.5, \
  equalizer=f=14000:t=h:g=2.2, \
  bs2b=profile=default, \
  stereowiden=delay=18:feedback=0.1:crossfeed=0.2:drymix=0.8, \
  loudnorm=I=-14.0:TP=-1.0:LRA=10 \
" -ar 48000 -c:a pcm_s24le master_final_ebur128.wav
```
