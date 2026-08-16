# Cadena DSP & Filtros para Masterización Audiófila en Linux / VPS

## 1. Topología de la Cadena DSP (Procesamiento en 32-bit Float)

La cadena de procesamiento debe ejecutarse siempre en punto flotante de 32 o 64 bits para evitar pérdidas por redondeo o truncamiento digital antes del dithering final.

```text
[Input Audio (AI/Raw)]
         │
         ▼
[1. Resampling Hi-Res 96kHz / 32-bit Float (Sinc Interpolation)]
         │
         ▼
[2. Infrasonic Filter (HPF 18Hz, 18dB/oct Butterworth)]
         │
         ▼
[3. Surgical Notch & Dynamic EQ (350Hz Boxiness Dip, 4.2kHz Ear Notch)]
         │
         ▼
[4. M/S Matrix Split (Mid / Side Separation)]
    ├── Mid:  [Mono Bass Low-Cut Pass-thru] ──┐
    └── Side: [High-Pass 80Hz + Air Boost 12kHz (+1.2dB)] ──┤
         │                                                    │
         └─────────────► [M/S Matrix Sum (L/R)] ◄─────────────┘
                                  │
                                  ▼
[5. Harmonic Tape/Tube Saturation (Soft Tanh / 2nd-Harmonic Injector)]
                                  │
                                  ▼
[6. Bauer/Meier Headphone Crossfeed (Cutoff: 650Hz, Level: -6dB, Delay: 300µs)]
                                  │
                                  ▼
[7. EBU R128 True Peak Limiter / Auto-Gain (-14 LUFS, Ceiling -1.0 dBTP)]
                                  │
                                  ▼
[Output: 24-bit / 96kHz FLAC + 320kbps Lossless Proxy]
```

---

## 2. Comandos FFmpeg y Filtros Nativos

FFmpeg incluye una suite avanzada de filtros de audio para emular esta cadena completa por línea de comandos:

### Cadena Completa en FFmpeg:
```bash
ffmpeg -i input_flow_music.wav -af "\
aresample=96000:resampler=soxr:precision=28,\
highpass=f=20:p=2,\
equalizer=f=320:t=q:w=0.8:g=-1.2,\
equalizer=f=4200:t=q:w=2.8:g=-1.5,\
stereowiden=delay=18:feedback=0.1:crossfeed=0.2:drymix=0.8,\
bs2b=profile=default,\
loudnorm=I=-14:TP=-1.0:LRA=11:print_format=summary\
" -c:a flac -sample_fmt s24 output_luxury_master.flac
```

### Explicación de los Filtros FFmpeg:
1. **`aresample=96000:resampler=soxr`**: Remuestreo a 96kHz usando libsoxr con 28-bit de precisión para máxima fidelidad en transitorios.
2. **`highpass=f=20:p=2`**: Filtro pasa-altos de 2º orden a 20Hz para eliminar sub-frecuencias inaudibles.
3. **`equalizer`**: Ecualizadores paramétricos quirúrgicos para despejar la zona de 320Hz y suavizar resonancias de 4.2kHz.
4. **`bs2b=profile=default`**: Implementación nativa del filtro **Bauer stereophonic-to-binaural (BS2B)**, que calcula la difracción y retardo acústico de la cabeza humana para una escucha en cascos sin fatiga.
5. **`loudnorm=I=-14:TP=-1.0:LRA=11`**: Normalización inteligente EBU R128 para preservar un rango dinámico amplio (LRA 11-14) con True Peak seguro a -1.0 dBTP.

---

## 3. Especificaciones de Presets según Tipo de Auricular de Lujo

### Preset 1: Flagship Planar-Magnéticos (Audeze LCD-5, HiFiMan Susvara, Meze Empyrean)
- *Características*: Respuesta ultra-lineal en sub-graves, agudos rápidos y planos.
- *Ajuste DSP*:
  - Sub-bass boost suave (+1.0 dB shelf en 35Hz).
  - Crossfeed moderado (BS2B nivel alto 700Hz/4.5dB).
  - Saturación armónica de 2º armónico muy sutil para otorgar calidez orgánica a las membranas planas.

### Preset 2: Flagship Dinámicos Abiertos (Sennheiser HD800S, Focal Utopia)
- *Características*: Escenario sonoro gigantesco, pero propensos a fatiga en 5.8kHz–6.5kHz.
- *Ajuste DSP*:
  - Notch quirúrgico de -2.0 dB en 5.9kHz (Q=3.0) para compensar el "HD800S peak".
  - Refuerzo en medios-bajos (150Hz +0.8 dB) para dar cuerpo y presencia física al escenario.
  - Crossfeed sutil (BS2B nivel estándar).

### Preset 3: In-Ear Monitors (IEMs) de Lujo Multi-BA / Electrostáticos
- *Características*: Aislamiento total, cercanía extrema al tímpano, riesgo alto de fatiga "en la cabeza".
- *Ajuste DSP*:
  - Crossfeed intensivo (BS2B nivel agresivo 650Hz/6dB) para empujar el sonido fuera del conducto auditivo.
  - De-esser dinámico activo en 7.5kHz - 9kHz.
