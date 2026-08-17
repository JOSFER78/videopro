# 🎚️ Masterización de Audio DSP, Sidechain Ducking y Anti-Blackdetect

## 1. Cadena de Masterización de Audio EBU R128 (-14 LUFS)

Para garantizar un estándar broadcast unificado compatible con YouTube, Shorts y TikTok, VideoPro implementa un pipeline de procesamiento audiófilo en 6 etapas:

```
[Voice VO] ────────────────────────┐
                                   ▼
[BGM Loop] ──► [Volume 0.25] ──► [Sidechain Compressor] ──► [amix] ──► [loudnorm -14 LUFS] ──► Master Audio
                                 (Threshold 0.08, Ratio 5)     ▲
[Foley SFX] ───────────────────────────────────────────────────┘
```

---

## 2. Filtergraph FFmpeg para Sidechain Dynamic Ducking

Atenúa automáticamente la música de fondo entre **-18 dB y -22 dB** cuando detecta presencia de voz humana:

```bash
ffmpeg -y -i input_video.mp4 -i narration_voice.wav -i background_music.mp3 \
  -filter_complex "\
    [0:v]null[v_out];\
    [2:a]volume=0.25,aloop=loop=-1:size=2e+09[bgm_loop];\
    [bgm_loop][1:a]sidechaincompress=threshold=0.08:ratio=5:attack=25:release=300[ducked_bgm];\
    [1:a][ducked_bgm]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:TP=-1.5[a_out]" \
  -map "[v_out]" -map "[a_out]" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  master_rendered_video.mp4
```

### Parámetros del Compresor Sidechain:
- **`threshold=0.08`**: Sensibilidad de activación ante la voz.
- **`ratio=5`**: Grado de compresión de la música (reduce el volumen al ~20%).
- **`attack=25`**: Tiempo de entrada en milisegundos (rápido para no tapar la primera sílaba).
- **`release=300`**: Tiempo de recuperación suave en milisegundos (recupera el volumen de la música sin saltos).
- **`loudnorm=I=-14:LRA=7:TP=-1.5`**: Normalización a -14 LUFS (Integrated Loudness) con True Peak de -1.5 dBFS.

---

## 3. Rampa Anti-Clicks de 30ms y Anti-Blackdetect

### Rampa de 30 ms en Cortes de Audio:
- Todo empalme de audio entre planos aplica un fundido cruzado `acrossfade=d=0.03` o `afade=t=in:d=0.03` para evitar discontinuidades de fase (*phase-clicks*).

### Fondo Seguro Anti-Blackdetect:
- **Regla Estricta**: No usar negro digital puro `RGB (0,0,0)`.
- Usar el color institucional **`RGB (36,48,72)`** (`#243048`). Evita falsos positivos en analizadores automáticos de pantalla negra (`blackdetect`) en pipelines de QA.
