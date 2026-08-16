# 🛠️ Workflow Técnico de Producción en VideoPro
## Canal: CHRONODRIFT (Urban Time Travel & Future Cities)
**Canal:** `@ChronoDriftOfficial` | **Engine:** Gemini Omni Flash (`gemini-omni-flash-preview`) | **Keyframes:** Nano Banana Pro (`gemini-3.1-flash-image`)

---

### 1. 🏗️ Arquitectura Integral del Pipeline de Producción VideoPro v4.0 Ultra

El canal **CHRONODRIFT** produce vuelos FPV cinemáticos tritemporales (**1626 ➔ 2026 ➔ 2226**) mediante un pipeline de automatización 100% modular, determinista y anti-alucinaciones. La generación de vídeo **prescinde por completo de Veo 3** debido a sus inconsistencias aerodinámicas en trayectorias 6-DoF, deformaciones morfológicas en match-cuts temporales y latencias de inferencia no lineales. En su lugar, el pipeline opera exclusivamente sobre el motor multimodal ultrarrápido **Gemini Omni Flash** (`gemini-omni-flash-preview`) en Google Flow, anclado a **7 keyframes consistentes por plano** renderizados con **Nano Banana Pro** (`gemini-3.1-flash-image`).

```mermaid
graph TD
    subgraph FASE 1: INGESTA & GROUNDING FACTICO 360°
        A1[Google Street View API 360° Master 8K] --> A3[Extracción 6 Perspectivas Canónicas 6-DoF]
        A2[OpenStreetMap Overpass 3D + Copernicus DEM] --> A4[Malla Vectorial & Altitud Barométrica AGL]
        A3 & A4 --> A5[Filtro Óptico: Var Laplaciana >=100.0 & Res >=4K]
    end

    subgraph FASE 2: KEYFRAMING & INFERENCIA GEMINI OMNI FLASH
        A5 --> B1[Generación 7 Keyframes Consistentes con Nano Banana Pro]
        B1 --> B2[Motor Google Flow: Gemini Omni Flash]
        B2 --> B3[Shotlist Canónico 7D FPV: 6-DoF Motion Spline]
        B3 --> B4[Match-Cut Tritemporal 1626 ➔ 2026 ➔ 2226]
    end

    subgraph FASE 3: AUDIO ENGINEERING VO-FIRST & MASTER EBU R128
        C1[Guión Aprobado + Edge-TTS Master] --> C2[Whisper Stable-TS: Word-Level Timestamps]
        C3[BGM Flow Chillhop / Darksynth @ 118 BPM] --> C4[Dynamic Ducking -18dB bajo Voz]
        C5[Foley 3D: Doppler FPV + Diegético Temporal + Sub-Bass 35Hz] --> C6[Master EBU R128: -14 LUFS / -1.0 dBTP]
        C2 & C4 & C6 --> C7[Timeline Maestro de Audio Sincronizado]
    end

    subgraph FASE 4: COMPOSICION REMOTION 4.X & QA GATES
        B4 & C7 --> D1[Remotion 4.x: Composición 4K 60fps GPU]
        D1 --> D2[HUD Vectorial 3D + Billboard Tracking + Telemetría]
        D2 --> D3[Render GPU + QA Multimodal ffprobe & video_analyze]
        D3 --> D4[Master Final MP4 H.264 / AAC 96k <50MB]
    end

    style A1 fill:#1e293b,stroke:#00e5ff,stroke-width:2px,color:#fff
    style B2 fill:#00e5ff,stroke:#00e5ff,stroke-width:3px,color:#000
    style C6 fill:#1e293b,stroke:#ffb300,stroke-width:2px,color:#fff
    style D1 fill:#1e293b,stroke:#b388ff,stroke-width:2px,color:#fff
    style D4 fill:#059669,stroke:#10b981,stroke-width:2px,color:#fff
```

---

### 2. 🛰️ Fase 1: Scraping Street View Multi-Ángulo 360° & Grounding Fáctico 6-DoF

Para garantizar la verdad fundamental del entorno urbano y evitar la deformación arquitectónica, el script `streetview_multitemporal_scraper.py` extrae y procesa una matriz georreferenciada con 6 grados de libertad (6-DoF):

#### A. Las 6 Perspectivas Canónicas de Captura 6-DoF
Por cada waypoint geodésico, se adquieren 6 perspectivas ortogonales y angulares calibradas:

| Perspectiva | Heading ($\theta$) | Pitch ($\phi$) | Roll ($\psi$) | FOV | Propósito Técnico en Pipeline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`CAM_N`** | $0.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Vector de referencia axial norte y fachada frontal |
| **`CAM_E`** | $90.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Paraje lateral derecho y continuidad de horizonte |
| **`CAM_S`** | $180.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Retro-perspectiva y anclaje de fuga trasera |
| **`CAM_W`** | $270.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Paraje lateral izquierdo y paralaje de sombra |
| **`CAM_PITCH_DOWN`** | Target Vector | $-20.0^\circ$ | $0.0^\circ$ | $100^\circ$ | Textura de calzada, escala peatonal y relieve basal |
| **`CAM_PITCH_UP`** | Target Vector | $+25.0^\circ$ | $0.0^\circ$ | $100^\circ$ | Cúspide de rascacielos, cañón urbano y cielo abierto |

```
                 [CAM_PITCH_UP (+25°)] (Cúspide / Cielo)
                           ^
                           |
  [CAM_W (270°)] <--- [CAM_N (0°)] ---> [CAM_E (90°)]   [Plano Horizontal 360°]
                           |
                           v
                [CAM_PITCH_DOWN (-20°)] (Calzada / Escala Peatonal)
                           |
                    [CAM_S (180°)] (Retro-Fuga)
```

#### B. Proyección Equirrectangular 360° y Descomposición Cubemap
* **Resolución Master:** $7680 \times 3840$ píxeles ($2:1$ Equirrectangular).
* **Descomposición Cubemap de 6 Caras:**
  $$\text{Cubemap} = \{\text{Front}(0^\circ), \text{Right}(90^\circ), \text{Back}(180^\circ), \text{Left}(270^\circ), \text{Top}(+90^\circ), \text{Bottom}(-90^\circ)\}$$

#### C. Geometrías 3D de OpenStreetMap Overpass & Copernicus DEM 30m
El scraper extrae polígonos volumétricos y alturas de edificios mediante consultas Overpass estructuradas dentro de un radio de $500\text{ m}$:

```python
# Consulta estructurada OSM Overpass para geometría 3D urbana
def build_osm_overpass_query(lat: float, lon: float, radius_meters: int = 500) -> str:
    return f"""
    [out:json][timeout:25];
    (
      way["building"](around:{radius_meters},{lat},{lon});
      relation["building"](around:{radius_meters},{lat},{lon});
      way["historic"](around:{radius_meters},{lat},{lon});
      way["highway"](around:{radius_meters},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """
```

#### D. Quality Gate Óptico Automatizado (Filtro Laplaciano)
Todo fotograma descargado debe superar estrictamente tres compuertas antes de ser aceptado como referencia:
1. **Resolución:** $\ge 3840 \times 2160$ px (4K UHD nativo).
2. **Peso de Archivo:** $> 5.0\text{ KB}$ con verificación de integridad de cabecera.
3. **Nitidez Laplaciana:** Varianza de Laplace $\sigma^2(\nabla^2 I) \ge 100.0$:
   $$\text{Var}(\nabla^2 I) = \frac{1}{N} \sum_{x,y} \left( \nabla^2 I(x,y) - \mu_{\nabla^2 I} \right)^2 \ge 100.0$$

---

### 3. 🎨 Fase 2: Prompts de Reimaginación & Keyframing Consistente con Gemini Omni Flash (Sin Veo 3)

#### A. Mandato Cero Veo 3: Justificación Técnica
* **Veo 3 descartado:** Inconsistencia en la inercia de trayectorias 6-DoF, tiempos de inferencia impredecibles, morphing geométrico inaceptable en transformaciones match-cut y deformación de líneas verticales en rascacielos.
* **Gemini Omni Flash (`gemini-omni-flash-preview`):** Interpretación nativa de hasta 7 imágenes de referencia (`<FIRST_FRAME>` + `<IMAGE_REF_0..5>`), spline de trayectoria de cámara sin artefactos visuales, renderizado nativo a 60fps y consistencia estructural perfecta.

#### B. Generación de 7 Keyframes Consistentes con Nano Banana Pro
Para cada plano se generan **7 keyframes secuenciales fotorrealistas** con `gemini-3.1-flash-image` (Nano Banana Pro) bajo una misma semilla (*seed preservation*), garantizando coherencia de materiales, grano de película y atmósfera:

```
[KF1: Entrada/Aproximación] ➔ [KF2: Transición] ➔ [KF3: Inflexión] ➔ 
[KF4: Clímax del Plano] ➔ [KF5: Detalle] ➔ [KF6: Pre-Salida] ➔ [KF7: Conector Match-Cut]
```

#### C. El Shotlist Canónico 7D FPV (Sincronizado a 118 BPM)

| Plano | Código Canónico | Ventana Temporal | Duración Real | Compases @ 118 BPM | Ángulo / Trayectoria | Altitud AGL | Velocidad |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **01** | `01_TERMINAL_DIVE` | `0:00 - 0:03s` | $3.05\text{ s}$ | $1.5\text{ compases}$ | Picado vertical $90^\circ$ | $850\text{m} \rightarrow 35\text{m}$ | $140\text{ km/h}$ |
| **02** | `02_CANYON_DRIFT` | `0:03 - 0:10s` | $7.12\text{ s}$ | $3.5\text{ compases}$ | Vuelo rasante en cañón urbano | $1.8\text{m} \rightarrow 15\text{m}$ | $110\text{ km/h}$ |
| **03** | `03_TUNNEL_PIERCE` | `0:10 - 0:18s` | $8.14\text{ s}$ | $4.0\text{ compases}$ | Penetración en arcada (Match-Cut) | $2.5\text{m} \rightarrow 4.0\text{m}$ | $85\text{ km/h}$ |
| **04** | `04_MONUMENT_ORBIT` | `0:18 - 0:25s` | $7.12\text{ s}$ | $3.5\text{ compases}$ | Órbita helicoidal $360^\circ$ | $25\text{m} \rightarrow 85\text{m}$ | $65\text{ km/h}$ |
| **05** | `05_PEDESTRIAN_SWOOP` | `0:25 - 0:32s` | $7.12\text{ s}$ | $3.5\text{ compases}$ | Ras de suelo a escala humana | $1.5\text{m} \rightarrow 12\text{m}$ | $45\text{ km/h}$ |
| **06** | `06_VERTICAL_SURGE` | `0:32 - 0:38s` | $6.10\text{ s}$ | $3.0\text{ compases}$ | Ascenso trepando fachadas | $12\text{m} \rightarrow 300\text{m}$ | $125\text{ km/h}$ |
| **07** | `07_SKYLINE_SUNSET` | `0:38 - 0:45s` | $7.12\text{ s}$ | $3.5\text{ compases}$ | Gran angular panorámico | $300\text{m} \rightarrow 500\text{m}$ | $90\text{ km/h}$ |

#### D. Sintaxis Oficial de Inferencia en Google Flow

```text
[# Sources <FIRST_FRAME>@Keyframe01_Start] [# References <IMAGE_REF_0>@Cam_N <IMAGE_REF_1>@Cam_E <IMAGE_REF_2>@Cam_S <IMAGE_REF_3>@Cam_W <IMAGE_REF_4>@Cam_PitchDown <IMAGE_REF_5>@Cam_PitchUp]

Use Keyframe01_Start as the literal opening frame 0. Use the given reference images as geometric and lighting consistency references for video generation; do not use them as literal initial frames.

A continuous, ultra-smooth 60fps cinematic 5-inch FPV drone flight navigating in 6 degrees of freedom (6-DoF). The camera executes a dynamic terminal dive and canyon drift between architectural structures. Optical parameters: 35mm f/1.8 anamorphic lens, Kodak Vision3 500T grain, ARRI Alexa LF colorimetry, true volumetric lighting and realistic aerodynamic motion blur. No morphing, no distortion artifacts, perfectly stable architectural lines. Audio: high-speed wind shear and binaural carbon-fiber propeller whine.
```

---

### 4. 🎧 Fase 3: Integración de Audio VO-First, Rejilla a 118 BPM & Master EBU R128

#### A. Rejilla Rítmica Exacta a 118 BPM
El diseño sonoro se estructura en torno a una rejilla rítmica inmutable de **118 BPM** en compás de $4/4$:

$$\text{Duración de 1 Beat} = \frac{60\,000\text{ ms}}{118\text{ BPM}} = 508.4746\text{ ms}$$
$$\text{Duración de 1 Compás (4 Beats)} = 4 \times 508.4746\text{ ms} = 2033.898\text{ ms} \approx 2.034\text{ s}$$
$$\text{Frase Canónica (4 Compases / 16 Beats)} = 16 \times 508.4746\text{ ms} = 8135.593\text{ ms} \approx 8.136\text{ s}$$

#### B. Sincronización VO-First con Whisper Stable-TS
La locución manda sobre el montaje visual. Se extraen marcas de tiempo a nivel de palabra para sincronizar los rótulos HUD y los cortes de plano:

```python
# Extracción de timestamps de palabras con Whisper Stable-TS
import stable_whisper

def extract_word_timestamps(audio_path: str):
    model = stable_whisper.load_model('base')
    result = model.transcribe(audio_path)
    return [
        {"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
        for seg in result.segments for w in seg.words
    ]
```

#### C. Dynamic Ducking Inteligente (-18.0 dB)
* **Atenuación bajo Voz/Datos:** **$-18.0\text{ dB}$** (factor lineal de amplitud $0.1258$).
* **Nivel Clímax Instrumental:** **$0.0\text{ dB}$** (en transiciones de vórtice y vuelos rasantes).
* **Parámetros de Envolvente:** $T_{\text{attack}} = 30.0\text{ ms}$, $T_{\text{release}} = 250.0\text{ ms}$, $T_{\text{hold}} = 50.0\text{ ms}$.

```bash
# Filtro FFmpeg Sidechain para Dynamic Ducking a -18dB
ffmpeg -i vo_narration.wav -i bgm_118bpm.wav -filter_complex \
"[1:a]asplit=2[bgm_direct][bgm_sc]; \
 [bgm_sc][0:a]sidechaincompress=threshold=0.08:ratio=6:attack=30:release=250:level_in=1[bgm_ducked]; \
 [0:a]volume=1.0[vo]; \
 [bgm_ducked]volume=0.1258[bgm_attenuated]; \
 [vo][bgm_attenuated]amix=inputs=2:duration=first:dropout_transition=2[out_audio]" \
-map "[out_audio]" audio_ducked_master.wav
```

#### D. Masterización Broadcast EBU R128 (-14.0 LUFS / -1.0 dBTP)
* **Sonoridad Integrada:** **$-14.0\text{ LUFS} \pm 0.5\text{ LUFS}$**.
* **Pico Verdadero Máximo:** **$\le -1.0\text{ dBTP}$** (cero distorsión inter-sample).
* **Rango de Sonoridad (LRA):** **$6.0 - 8.0\text{ LU}$**.

```bash
# Normalización lineal EBU R128 de 2 pasadas en FFmpeg
ffmpeg -i audio_raw_mix.wav -af \
loudnorm=I=-14.0:TP=-1.0:LRA=7.0:measured_I=-18.4:measured_TP=-0.2:measured_LRA=8.1:measured_thresh=-29.1:offset=0.2:linear=true \
-ar 48000 -c:a pcm_s24le audio_master_ebur128.wav
```

#### E. Sound Design Espacial & Foley Doppler 3D
* **Efecto Doppler Arquitectónico:**
  $$\Delta f = f_0 \left( \frac{v_{\text{sonido}}}{v_{\text{sonido}} \mp v_{\text{dron}}} \right)$$
  A $110\text{ km/h}$ ($30.5\text{ m/s}$), el desplazamiento tonal es $+9.8\%$ al aproximarse y $-8.2\%$ al alejarse de fachadas.
* **Capas Diegéticas por Época:**
  - **1626:** Crujidos de madera, cascos de caballos, campanas de bronce históricas, agua en barcas.
  - **2026:** Zumbido de metro subterráneo, fricción de neumáticos sobre asfalto húmedo, sirenas urbanas.
  - **2226:** Propulsores iónicos silenciosos, campos magnéticos, pulsos de datos subacuáticos.
* **Impacto Vórtice Temporal:** Sub-bass braam drop afinado a **$35\text{ Hz}$** con barrido de ruido blanco.

---

### 5. 💻 Fase 4: Composición Remotion 4.x & HUD 3D Vectorial

La interfaz telemétrica se renderiza con aceleración GPU mediante Remotion 4.x en React/TypeScript:

```tsx
// src/components/ChronoDriftHUD.tsx
import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

interface HUDProps {
  currentYear: number;
  altitudeMeters: number;
  speedKmh: number;
  cityCoordinates: string;
  scientificSource: string;
}

export const ChronoDriftHUD: React.FC<HUDProps> = ({
  currentYear,
  altitudeMeters,
  speedKmh,
  cityCoordinates,
  scientificSource
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{
      position: 'absolute',
      inset: 0,
      fontFamily: 'JetBrains Mono, monospace',
      color: '#00e5ff',
      opacity,
      pointerEvents: 'none',
      padding: '48px'
    }}>
      {/* Mira Retícula Central FPV */}
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '120px',
        height: '120px',
        border: '1px solid rgba(0, 229, 255, 0.4)',
        borderRadius: '50%',
        boxShadow: '0 0 20px rgba(0, 229, 255, 0.2)'
      }}>
        <div style={{ position: 'absolute', top: '50%', left: '-15px', width: '30px', height: '1px', background: '#00e5ff' }} />
        <div style={{ position: 'absolute', top: '50%', right: '-15px', width: '30px', height: '1px', background: '#00e5ff' }} />
      </div>

      {/* Caja de Telemetría Superior Izquierda */}
      <div style={{
        position: 'absolute',
        top: '60px',
        left: '60px',
        background: 'rgba(7, 9, 14, 0.85)',
        borderLeft: '4px solid #ffb300',
        padding: '16px 24px',
        borderRadius: '4px',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ fontSize: '14px', color: '#ffb300', letterSpacing: '0.1em' }}>CHRONODRIFT 6-DoF HUD</div>
        <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#ffffff' }}>{currentYear} CE</div>
        <div style={{ fontSize: '13px', color: '#00e5ff' }}>COORDS: {cityCoordinates}</div>
      </div>

      {/* Caja de Altitud & Velocidad Inferior Derecha */}
      <div style={{
        position: 'absolute',
        bottom: '60px',
        right: '60px',
        background: 'rgba(7, 9, 14, 0.85)',
        borderRight: '4px solid #00e5ff',
        padding: '16px 24px',
        borderRadius: '4px',
        textAlign: 'right',
        backdropFilter: 'blur(10px)'
      }}>
        <div style={{ fontSize: '13px', color: '#b388ff' }}>ALT: {altitudeMeters.toFixed(1)} M | SPD: {speedKmh.toFixed(0)} KM/H</div>
        <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.7)', marginTop: '4px' }}>DATA: {scientificSource}</div>
      </div>
    </div>
  );
};
```

---

### 6. 📊 Matriz de Control de Calidad (QA Gates)

| Compuerta de QA | Especificación / Umbral | Herramienta de Verificación | Acción en Fallo |
| :--- | :--- | :--- | :--- |
| **Integridad de Assets** | Todos los archivos $> 5.0\text{ KB}$ | `scripts/verify-assets.py` | Aborto `Exit Code 2` |
| **Resolución de Vídeo** | $3840 \times 2160$ @ $60.0\text{ fps}$ | `ffprobe` | Re-render Remotion |
| **Sonoridad Integrada** | $-14.0\text{ LUFS} \pm 0.5\text{ LUFS}$ | `ffmpeg loudnorm` | Re-masterizado 2 pasadas |
| **Pico Verdadero** | $\le -1.0\text{ dBTP}$ | `ffmpeg loudnorm` | Limitador True-Peak |
| **Ducking de Música** | $-18.0\text{ dB}$ bajo voz | `ffprobe ebur128` | Reajuste de ganancia sidechain |
| **Retención Visual** | 7 planos canónicos por episodio | `scenes.json validator` | Regeneración de shotlist |
| **Consistencia 6-DoF** | Varianza Laplaciana $\ge 100.0$ | `cv2.Laplacian` | Re-scraping / Mosaico 4K |

---

### 7. 🚀 Comandos y Automatización CLI

```bash
# 1. Scraping 6-DoF multi-ángulo de Street View y OSM para las 10 ciudades
python3 scripts/streetview_multitemporal_scraper.py --export-all

# 2. Generación de historias, 7 planos canónicos y prompts Gemini Omni Flash
python3 scripts/tritemporal_urban_story_builder.py --all

# 3. Inferencia de vídeo por lotes en Google Flow (Gemini Omni Flash)
python3 scripts/google_flow_batch_generator.py --manifest data/tritemporal_manifests/tokyo_tritemporal_manifest.json

# 4. Composición final Remotion con HUD 3D y masterización de audio EBU R128
python3 scripts/render_remotion.py --city tokyo --target-lufs -14.0 --resolution 4k
```

---
*CHRONODRIFT Technical Production Specification — VideoPro Studio 2026*
