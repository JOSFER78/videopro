# Arquitectura de BSO de 15 Minutos en Flow Music: Extensión por Fases y Ensamblado Continuo Automatizado

## 1. El Desafío de la Larga Duración en Flow Music

Google Flow Music (Lyria 3 Pro / MusicFX) impone una **restricción estructural**: cada generación directa está limitada a aproximadamente **3 minutos (180 segundos)**.

Cuando un usuario interactúa con la interfaz web de Flow Music solicitando una obra de 15 minutos "en oneshot", el agente interno (*Producer AI*) responde con la limitación del sistema:

> *"I can't automatically stitch them into a single 15-minute file, as track generations are capped at around 3 minutes each. But we can pick your favorite clip from Phase 1 right now and extend it step-by-step!"*

### El Flujo Nativo de la Web UI de Flow Music:
1. **Fase 1 (0:00 – 3:00)**: Genera 2 variantes del clip inicial (ej. "Wide Horizon").
2. **Selección del Usuario**: El usuario elige *"Extend first clip"* o *"Extend second clip"*.
3. **Fases 2 a 5**: Se encadenan extensiones consecutivas (3:00-6:00, 6:00-9:00, 9:00-12:00, 12:00-15:00).
4. **Problema**: La interfaz web entrega los clips separados o en un timeline interno no exportable en un único archivo master continuo de alta resolución con procesado 3D ASMR.

---

## 2. La Solución VideoPro: Arquitectura en 3 Capas

VideoPro automatiza este proceso de principio a fin eliminando cualquier intervención manual:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. CAPA DE PLANIFICACIÓN Y CONTRATO COMPOSITIVO (JSON / Prompt Blueprint)                   │
│    - Suite de 5 Fases con coherencia de tonalidad (432Hz/528Hz), tempo, orquestación y arco. │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. CAPA DE GENERACIÓN SECUENCIAL AUTÓNOMA (Playwright / CDP)                                │
│    - Conexión a Chrome Web UI de Flow Music.                                                │
│    - Inyección de Fase 1 -> Selección de Clip -> Extensión Fase 2 -> Fase 3 -> 4 -> 5.      │
│    - Descarga de stems / clips brutos (.wav / .mp3) sin pérdida.                            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. CAPA DE ENSAMBLADO S-CURVE Y MASTERIZACIÓN DSP 3D ASMR                                   │
│    - Cosido seamless con crossfades exponenciales de 6s (anulando saltos y clicks).         │
│    - De-harshing digital (4.5kHz) + Air Band 14kHz + Mono-Sub <80Hz.                       │
│    - Espacialización 3D Binaural HRTF (bs2b) + Compresión Upward para Micro-ASMR.           │
│    - Exportación Dual: Master YouTube (-14 LUFS) y Master Cascos Lujo (24/96 FLAC, -16 LUFS)│
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Desglose del Contrato Musical de las 5 Fases (15 Minutos)

Para que las 5 fases mantengan total coherencia armónica, tímbrica y estructural, cada prompt debe obedecer a una función compositiva estricta:

| Fase | Minutaje | Función Compositiva | Elementos Clave del Prompt | Energía Dinámica |
| :--- | :--- | :--- | :--- | :--- |
| **Fase 1: Pista Base** | 0:00 – 3:00 | Introducción y Anclaje Tonal | Sintonización 432Hz, cuerdas atmosféricas, sintetizadores envolventes, micro-texturas ASMR oído a oído, tempo lento, sin batería, campo estéreo ultra amplio. | Nivel 1 (Ambient Suave) |
| **Fase 2: Primera Extensión** | 3:00 – 6:00 | Desarrollo Temático & Pulso | Mantener tonalidad y tempo exactos. Introducir pulso grave constante y redoble sutil de timbal, desarrollo progresivo de trompa francesa, transición fluida y sin cortes. | Nivel 2 (Crecimiento Constante) |
| **Fase 3: Segunda Extensión** | 6:00 – 9:00 | Variación Armónica & Amplitud | Mantener progresión armónica. Cambio rítmico dinámico, capas de cuerdas sinfónicas ricas, expansión de armonías de metales, impulso ascendente, paneo binaural amplio. | Nivel 3 (Momento Emocional) |
| **Fase 4: Tercera Extensión** | 9:00 – 12:00 | Clímax Épico & Resolución | Construcción hacia la energía máxima. Crescendo orquestal triunfante, trompas y oleadas de metales potentes, clímax emocional épico, resolución majestuosa y expansiva. | Nivel 5 (Pico Máximo) |
| **Fase 5: Cuarta Extensión** | 12:00 – 15:00 | Cierre & Decrescendo Hipnótico | Decrescendo suave. Desvanecimiento de percusión y ritmo, cuerdas suaves persistentes y drones ambientales cálidos, decaimiento gradual hacia el silencio, outro pacífico. | Nivel 1 (Disolución Serena) |

---

## 4. Algoritmo de Ensamblado y Transición S-Curve (Crossfade)

Para unir los 5 clips generados en una única pista sin clicks, desfases acústicos ni saltos de volumen:

### A. Cálculo de Superposición (Overlap de 6 Segundos):
Cada segmento de 3 minutos (180 segundos) se solapa 6 segundos con el siguiente:
$$\text{Duración Efectiva} = 5 \times 180\text{ s} - (4 \times 6\text{ s}) = 900\text{ s} - 24\text{ s} = 876\text{ s} \approx 14\text{m } 36\text{s}$$
*(Si cada fase se genera a 186 segundos, el master resultante clava exactamente 900 segundos = 15m 00s)*.

### B. Curva de Fundido Exponencial S-Curve:
Para evitar la caída de volumen de -3 dB en el centro del fundido (típica del crossfade lineal), se aplica la curva exponencial `c1=exp:c2=exp` o seno cuadrático `c1=qsin:c2=qsin` en FFmpeg:

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
  " -map "[out]" -c:a pcm_s24le /tmp/stitched_15min_raw.wav
```

---

## 5. Procesamiento DSP de Vanguardia para la BSO Ensamblada

Una vez unidas las 5 fases, el archivo pasa por la cadena de masterización audiófila de 6 etapas:

1. **De-Ringing Espectral (3.5 kHz – 6.8 kHz)**:
   - Filtro dinámico con Q estrecho para eliminar los micro-artefactos de difusión propios de los modelos de IA generativa.
2. **Harmonic Resonator (432Hz / 528Hz)**:
   - Realce suave de la frecuencia fundamental en 432Hz para anclar la sensación de relajación y bienestar.
3. **Mono Sub-Bass (< 80 Hz)**:
   - Canalización a mono puro en sub-graves para evitar cancelación de fase en altavoces y cascos.
4. **Bauer/Meier Crossfeed 3D (bs2b)**:
   - Modelado psicoacústico de cabeza (HRTF) para extraer el sonido de "dentro del cráneo" y proyectarlo a un escenario holográfico de 180°.
5. **Upward Compression para Micro-ASMR**:
   - Realce del micro-detalle (pasos, brisa, foley) manteniendo los picos orquestales bajo control.
6. **Masterización de Doble Destino**:
   - **YouTube / Streaming**: -14 LUFS Integrado, True Peak -1.0 dBFS.
   - **Cascos de Lujo (Audiophile Hi-Res)**: -16 LUFS, Dynamic Range >13 dB, 24-bit 96kHz FLAC.
