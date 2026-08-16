# Pipeline de Montaje y Masterización DSP de 15 Minutos para Flow Music

Este documento detalla la ingeniería de audio para encadenar las 5 fases generadas por Google Flow Music y aplicar el procesamiento de audio de ultra-alta fidelidad (432Hz/528Hz, 3D Binaural HRTF y realce micro-ASMR).

---

## 1. Diagrama de Bloques del Pipeline

```text
[Fase 1: 0-3m] ──┐
[Fase 2: 3-6m] ──┼─► [S-Curve Overlap Crossfade] ──► [Master Raw 15:00]
[Fase 3: 6-9m] ──┤                                            │
[Fase 4: 9-12m] ─┤                                            ▼
[Fase 5: 12-15m] ┘                          [1. De-Harshing & De-Ringing (4.5kHz)]
                                                              │
                                                              ▼
                                            [2. 432Hz/528Hz Harmonic Realignment]
                                                              │
                                                              ▼
                                            [3. Mono-Sub (<80Hz) & M/S Balancing]
                                                              │
                                                              ▼
                                            [4. Bauer/Meier 3D Crossfeed (bs2b)]
                                                              │
                                                              ▼
                                            [5. Micro-ASMR Upward Compression]
                                                              │
                                                              ▼
                                            [6. Dual-Target Limiting & Mastering]
                                            ┌─────────────────┴─────────────────┐
                                            ▼                                   ▼
                               [YouTube (-14 LUFS, TP -1.0dB)]   [Cascos Lujo (24/96 FLAC, -16 LUFS)]
```

---

## 2. Fase 1: Ensamblado Continuo de las 5 Pistas (Crossfade S-Curve)

Cada fase tiene una duración típica de 180 segundos. Para lograr una transición imperceptible:
- **Duración del Crossfade**: 6.0 segundos.
- **Tipo de Curva**: Exponencial (`c1=exp:c2=exp`) o Seno Cuadrático (`c1=qsin:c2=qsin`).

### Comando FFmpeg de Ensamblado:
```bash
ffmpeg -y \
  -i phase1.wav \
  -i phase2.wav \
  -i phase3.wav \
  -i phase4.wav \
  -i phase5.wav \
  -filter_complex "\
    [0:a][1:a]acrossfade=d=6:c1=exp:c2=exp[a01]; \
    [a01][2:a]acrossfade=d=6:c1=exp:c2=exp[a02]; \
    [a02][3:a]acrossfade=d=6:c1=exp:c2=exp[a03]; \
    [a03][4:a]acrossfade=d=6:c1=exp:c2=exp[out] \
  " -map "[out]" -c:a pcm_s24le /tmp/suite_15min_stitched.wav
```

---

## 3. Fase 2: Cadena DSP Audiófila y 3D ASMR

### A. Limpieza Quirúrgica y Des-aspereza (De-Ringing)
- **Highpass 20Hz (24dB/oct)**: Elimina rumble subsónico innecesario.
- **Parametric EQ Notch en 4.5kHz y 5.8kHz (-2.0dB, Q=2.5)**: Atenúa las frecuencias de resonancia digital generadas por los modelos de difusión de audio.

### B. Ecualización Baxandall Air Band y Mono-Sub
- **Low-Shelf Colapso Mono en 80Hz**: Mantiene los sub-graves totalmente centrados y sin desfase en auriculares.
- **High-Shelf Air Band en 14kHz (+2.2dB)**: Proporciona la sensación de aire, apertura acústica y tridimensionalidad.

### C. Espacialización 3D Crossfeed (`bs2b`)
- Implementa el circuito **Bauer-Binaural (Meier)** que simula la sombra acústica de la cabeza humana:
  - Elimina el aislamiento duro L/R.
  - Genera una imagen frontal tridimensional natural y evita fatiga auditiva.

### D. Realce Dinámico Micro-ASMR
- **Upward Compresor**: Eleva las texturas de bajo nivel (crujidos, pasos, foley, brisa) en +4dB a +6dB cuando el volumen general baja, creando un efecto ASMR envolvente e íntimo.

---

## 4. Comando Maestro de Procesamiento Todo-en-Uno (FFmpeg)

```bash
ffmpeg -y -i /tmp/suite_15min_stitched.wav -af "\
  highpass=f=20:p=2, \
  equalizer=f=250:t=q:w=1.2:g=-1.8, \
  equalizer=f=4500:t=q:w=2.0:g=-1.5, \
  equalizer=f=14000:t=h:g=2.2, \
  bs2b=profile=default, \
  stereowiden=w=1.15:de=0.8, \
  loudnorm=I=-14.0:LRA=10:TP=-1.0 \
" -ar 48000 -c:a pcm_s24le output_15min_youtube_master.wav
```
