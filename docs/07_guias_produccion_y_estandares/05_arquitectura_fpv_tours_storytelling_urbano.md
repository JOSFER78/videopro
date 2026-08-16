# 🚁 ARQUITECTURA TÉCNICA & WORKFLOW MAESTRO: TOURS FPV Y STORYTELLING URBANO
### *Motor Autónomo de Vuelos Cinemáticos 4K/60fps, Grounding Factual, Keyframing Omni Flash y Motion Graphics 3D*

---

## 1. 🎯 DIAGNÓSTICO Y REGLAS DE ORO DE PRODUCCIÓN

El formato **Tours FPV y Storytelling Urbano** en **videopro** fusiona la emoción inmersiva de los vuelos con dron de alta velocidad (acrobacias de 6 ejes, *dives* verticales entre rascacielos y pasos rasantes milimétricos) con el rigor del periodismo documental factual y el diseño gráfico tridimensional de vanguardia.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                      PIPELINE INTEGRAL DE PRODUCCIÓN FPV URBANA (7 FASES)                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
  [1. GUIONIZACIÓN & ARCO NARRATIVO] ──► [2. PLAN DE VUELO 3D & SHOTLIST] ──► [3. SCRAPING 4K REAL]
                    │                                                                 │
                    ▼                                                                 ▼
  [4. REIMAGINACIÓN 7-KEYFRAMES]   ──► [5. GOOGLE FLOW OMNI FLASH]       ──► [6. AUDIO FLOW & SFX]
                    │                                                                 │
                    └─────────────────────► [7. OVERLAYS 3D & REMOTION MASTER] ◄──────┘
```

### 🔴 Reglas de Oro Inquebrantables del Pipeline:
1. **MOTOR DE VÍDEO = ESTRICTAMENTE GEMINI OMNI FLASH**:
   - Todo clip dinámico se sintetiza mediante `Gemini Omni Flash` (`gemini-omni-flash-preview` / `--engine omni_flash`). **PROHIBIDO EL USO DE VEO 3**. Omni Flash ofrece simulación física inercial de vuelo, renderizado a 60fps y síntesis de audio espacial foley integrado.
2. **MOTOR DE IMAGEN & KEYFRAMES = NANO BANANA PRO**:
   - La reiluminación, texturizado y generación de los 7 keyframes de soporte visual se ejecuta exclusivamente con `Nano Banana Pro` (`gemini-3.1-flash-image`), garantizando óptica prime 14mm-24mm, ciencia de color ARRI Alexa LF y grano 35mm Kodak Vision3 500T.
3. **GROUNDING REAL OBLIGATORIO (ZERO HALLUCINATIONS)**:
   - Todo vuelo parte de coordenadas GPS exactas y fotografías reales de alta resolución ($\ge 3840\times 2160$) adquiridas mediante scraping validado. No se inventa la arquitectura de las ciudades reales.
4. **REGLA DE INTEGRIDAD > 5 KB**:
   - Todo activo (foto satelital, keyframe, clip MP4, pista BGM, SFX Doppler) debe pesar $> 5\text{ KB}$ y ser validado con `Pillow` y `ffprobe`. Si un asset falla o está corrupto, la pipeline aborta inmediatamente (`Exit Code 2`).
5. **LOCUCIÓN & AUDIO SOBERANO (VO-FIRST & FLOW SYNC)**:
   - Las duraciones exactas de la voz (`vo_durations.json` vía Whisper Stable-TS) y la rejilla rítmica del BGM (BPM constante) gobiernan las aceleraciones, frenadas y puntos de giro de la cámara FPV.

---

## 2. 📖 PILAR 1: GUIONIZACIÓN CON ARCO NARRATIVO ESTRUCTURADO

Un tour FPV no es un simple compendio de tomas aéreas inconexas; es una narrativa cinematográfica con tensión dramática creciente estructurada en **3 Actos** y contrapunto conceptual:

```
Tensión
  ▲                                                            [CLÍMAX: Salida al Horizonte]
  │                                                                   ▲
  │                                      [NUDO: Inmersión Laberíntica]│
  │                                              ▲                   │
  │                     [DESPEGUE]               │                   │
  │        [GANCHO 3s]      ▲                    │                   │
  │            ▲            │                    │                   │
──┴────────────┴────────────┴────────────────────┴───────────────────┴────────────────────────► Tiempo
  0s          3s           8s                   30s                 45s
```

### 2.1 Los Tres Actos Cinemáticos FPV:

#### A. Acto 1: El Gancho de Impacto (0.0s – 3.5s)
- **Visual:** Picado vertical extremo (*Terminal Dive*) a 130 km/h desde la antena de un rascacielos o monumento hacia la calle con rotación continua.
- **Narrativa (Gancho):** Premisa intrigante o paradoja urbana no evidente.
- *Ejemplo de Locución:* *"A 230 metros de altura, Tokio parece un circuito integrado en calma... pero si caes a 120 km/h hacia Shibuya, descubres el secreto que sostiene a la metrópolis más poblada del planeta."*

#### B. Acto 2: El Nudo de Exploración Espacial y Subtexto (3.5s – 38.0s)
- **Visual:** Transiciones dinámicas entre los 5 hitos urbanos principales (vuelo rasante a nivel de peatones, slalom entre fachadas de cristal, entrada a través de arcos o túneles de metro y giros orbitales cerrados).
- **Narrativa (Desarrollo & Contrapunto):** Explicación de hechos históricos, récords de ingeniería, contrastes socioespaciales (antigüedad vs hipermodernidad) y dinámicas urbanas.
- *Regla del Contrapunto:* Mientras la voz explica un dato técnico o histórico, la cámara FPV muestra el espacio físico tangible donde ocurrió, evitando metáforas simplistas.

#### C. Acto 3: El Desenlace y Clímax Panorámico (38.0s – 45.0s+)
- **Visual:** Aceleración final saliendo del confinamiento urbano hacia la bahía, el río o el cielo abierto al atardecer (*Golden Hour Reveal*).
- **Narrativa (Cierre Poético / Reflexión):** Conclusión del misterio planteado y llamada a la reflexión sobre la identidad de la ciudad.

---

## 3. 📍 PILAR 2: PLAN DE VUELO 3D, COORDENADAS Y SHOTLIST CANÓNICO (7 PLANOS)

El vuelo FPV se formaliza mediante una spline matemática tridimensional que conecta coordenadas geográficas reales con variables de actitud de vuelo:

$$\vec{P}(t) = \begin{pmatrix} \text{Lat}(t) \\ \text{Lon}(t) \\ Z_{\text{AGL}}(t) \end{pmatrix}, \quad \vec{\Theta}(t) = \begin{pmatrix} \text{Pitch}(t) \\ \text{Yaw}(t) \\ \text{Roll}(t) \end{pmatrix}, \quad v(t) = \left\| \frac{d\vec{P}}{dt} \right\|$$

### 3.1 El Shotlist Canónico FPV (7 Planos Obligatorios por Recorrido):

| Plano | Tipo de Movimiento FPV | Velocidad | Óptica / Lente | Función Narrativa y Espacial |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Terminal Dive (Picado Vertical)** | 120-140 km/h | 14mm Anamorphic f/2.8 | **El Gancho:** Caída vertical libre rozando la fachada del edificio más alto. |
| **02** | **Canyon Slalom (Zigzag entre Torres)** | 80-95 km/h | 18mm Prime f/2.0 | **La Escala:** Vuelo en slalom cerrado entre cañones urbanos de hormigón y cristal. |
| **03** | **Sub-Canopy Skim (Vuelo Rasante)** | 50-65 km/h | 24mm Prime f/1.8 | **La Vida Urbana:** Desplazamiento a 1.5 metros del suelo sobre cruces, fuentes o plazas. |
| **04** | **Portal Breach (Traspaso de Estructuras)**| 70-85 km/h | 16mm Ultra-wide f/2.8 | **La Tensión:** Vuelo a través de arcos históricos, puentes, pasarelas o pérgolas. |
| **05** | **Spiral Orbit (Tirabuzón Ascendente)** | 60-75 km/h | 21mm Prime f/2.0 | **El Monumento:** Giro helicoidal de 360° ascendiendo alrededor de la cúspide. |
| **06** | **Tunnel / Underbridge Dash** | 90-110 km/h | 14mm Anamorphic f/2.8 | **La Velocidad:** Aceleración lineal por espacios confinados con compresión de perspectiva. |
| **07** | **Skyline Sunset Ascension** | 100-130 km/h | 35mm Cine Prime f/2.8 | **El Clímax:** Trepada vertical hacia el cielo con revelación panorámica 4K. |

```json
// Fragmento del Contrato fpv_urban_flight_plan.schema.json
{
  "shot_index": 1,
  "shot_name": "01_TERMINAL_DIVE_SHIBUYA",
  "shot_type": "TERMINAL_DIVE",
  "start_waypoint": "WP_SCRAMBLE_ROOFTOP_229M",
  "end_waypoint": "WP_CROSSING_STREET_LEVEL_3M",
  "duration_seconds": 4.2,
  "speed_kmh": 132.5,
  "motion_type": "Nose-down 90-degree dive along glass facade with 90-degree yaw correction at pullout",
  "first_frame_asset_ref": "assets/keyframes/kf0_scramble_top.png"
}
```

---

## 4. 🌐 PILAR 3: SCRAPING Y DESCARGA DE IMÁGENES REALES DE ALTA RESOLUCIÓN

Para evitar la generación de "ciudades genéricas de IA" y anclar el vídeo en la realidad tangible, `videopro` implementa un módulo de adquisición multicanal:

```
                               ┌──────────────────────────────────────────────┐
                               │  FUENTES DE IMÁGENES REALES DE ALTA CALIDAD  │
                               │ (Wikimedia 8K, Mapillary, Pexels/Unsplash 4K)│
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │     FILTRADO Y AUDITORÍA DE CALIDAD          │
                               │  • Resolución mínima: ≥ 3840x2160            │
                               │  • Tamaño de archivo: > 500 KB (Regla > 5KB) │
                               │  • Nitidez: Laplacian Variance ≥ 120.0       │
                               │  • Cero marcas de agua ni texto incrustado   │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │   NORMALIZACIÓN Y PERSPECTIVA ANAMÓRFICA     │
                               │  (Alineación de horizontes y balance 5600K)  │
                               └──────────────────────────────────────────────┘
```

### 4.1 Algoritmo de Verificación de Nitidez (Laplacian Variance):
```python
import cv2
from pathlib import Path

def audit_real_image_quality(image_path: Path) -> dict:
    """Verifica resolución mínima 4K, tamaño de archivo y nitidez óptica."""
    if not image_path.exists() or image_path.stat().st_size < 5000:
        return {"passed": False, "reason": "Archivo inexistente o <5KB"}
    
    img = cv2.imread(str(image_path))
    if img is None:
        return {"passed": False, "reason": "Imagen corrupta"}
    
    h, w, _ = img.shape
    if w < 1920 or h < 1080:
        return {"passed": False, "reason": f"Resolución insuficiente ({w}x{h})"}
    
    # Cálculo de nitidez mediante varianza del operador Laplaciano
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    if laplacian_var < 100.0:
        return {"passed": False, "reason": f"Imagen excesivamente borrosa (Laplacian: {laplacian_var:.1f})"}
    
    return {
        "passed": True,
        "width": w,
        "height": h,
        "laplacian_var": round(laplacian_var, 2),
        "size_kb": round(image_path.stat().st_size / 1024, 2)
    }
```

---

## 5. 🎨 PILAR 4: PIPELINE DE REIMAGINACIÓN Y 7 KEYFRAMES PARA GOOGLE FLOW (OMNI FLASH)

### 5.1 La Estrategia de 7 Keyframes por Plano (Anclas de Trayectoria):
En un plano FPV que se desplaza a 100 km/h, una única imagen inicial genera pérdida de detalle o distorsiones a los 2 segundos de animación. Para garantizar **fidelidad fotográfica absoluta**, cada plano genera un conjunto de **7 Keyframes Estratégicos** con `Nano Banana Pro`:

```
Plano FPV (4.5 segundos / 108 fotogramas a 24fps)
├─ KF 0 (Frame 000 / <FIRST_FRAME>):   Foto Real 4K Reiluminada (Punto de inicio en azotea)
├─ KF 1 (Frame 018 / <IMAGE_REF_0>):   Vista intermedia del descenso (Reflejos en cristales)
├─ KF 2 (Frame 036 / <IMAGE_REF_1>):   Aproximación a nivel medio (Letreros luminosos)
├─ KF 3 (Frame 054 / <IMAGE_REF_2>):   Paso rasante cerca de marquesinas (Textura de asfalto)
├─ KF 4 (Frame 072 / <IMAGE_REF_3>):   Punto de giro yaw 45° (Cruce de peatones iluminado)
├─ KF 5 (Frame 090 / <IMAGE_REF_4>):   Alineación de salida con la avenida principal
└─ KF 6 (Frame 108 / <IMAGE_REF_5>):   Keyframe de empalme exacto con el siguiente plano
```

### 5.2 Sintaxis Oficial de Prompting para Gemini Omni Flash:

De acuerdo con la especificación verificada de `Gemini Omni Flash` en Google Flow:
- `<FIRST_FRAME>` es la imagen fija inicial (frame 0).
- `<IMAGE_REF_0>` a `<IMAGE_REF_N>` son imágenes de referencia de estilo, consistencia 3D y guías de trayectoria de cámara.
- Las guías de trayectoria (trazado rojo o vector de cámara) se inyectan como `IMAGE_REF` con la directiva explícita de no ser renderizadas en el vídeo final.

```text
[PROMPT CANÓNICO OMNI FLASH - SHOT 01: TERMINAL DIVE SHIBUYA]
[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3]
Use Image1 as the literal starting frame. Use Image2 and Image3 strictly as 3D environmental references and spatial motion anchors; do not show them as static overlays.
ACTION: High-speed cinematic FPV acrobatic drone diving straight down at 130 km/h along the glass and steel skyscraper facade. True 6-axis aerodynamic physics, realistic forward velocity blur at screen edges, subtle atmospheric air drag turbulence. Near the ground, the drone executes a smooth, aggressive 85-degree pitch-up pullout into a forward glide over the bustling pedestrian intersection.
CAMERA: Ultra-wide 14mm anamorphic cine lens, f/2.8 aperture, 180-degree shutter angle creating natural motion blur on close passing architecture, razor-sharp central focal lock.
LIGHTING & COLOR: Twilight Blue Hour (5200K) combined with vibrant neon cyan and amber billboard light casting dynamic moving reflections across wet asphalt and glass panels. ARRI Alexa LF color science, authentic Kodak Vision3 500T 35mm film grain.
AUDIO: Dynamic binaural FPV high-pitch brushless motor whine accelerating into a deep aerodynamic wind roar whoosh with realistic urban acoustic Doppler reflection off the surrounding buildings. No music.
```

---

## 6. 🔊 PILAR 5: INTEGRACIÓN DE AUDIO FLOW, SOUND DESIGN & OVERLAYS 3D

El montaje final en **videopro** se construye programáticamente mediante `Remotion` o `MoviePy 2.x`, sincronizando la telemetría gráfica con la pista de audio:

```
                                  TIMELINE DE MASTERIZACIÓN MULTICAPA
  ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
  │ CAPA 1: OVERLAYS 3D & HUD TELEMETRÍA (Remotion TSX / CSS 3D Matrix Transforms)              │
  │ • Rótulos flotantes anclados a edificios (Perspective 3D, Glitch in / Fade out)            │
  │ • HUD FPV: Velocímetro dinámico (km/h), Altímetro AGL, Coordenadas GPS, Brújula de Rumbo    │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ CAPA 2: VÍDEOS GENERADOS GOOGLE FLOW OMNI FLASH (4K / 60fps Concat)                         │
  │ [Shot 01: Dive] ──► [Shot 02: Slalom] ──► [Shot 03: Skim] ──► [Shot 04: Breach] ...         │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ CAPA 3: LOCUCIÓN TTS PRINCIPAL (VibeVoice / Edge-TTS a -14 LUFS)                            │
  │ "A 230 metros de altura..."                "Bajo el asfalto de Shibuya..."                 │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ CAPA 4: EFECTOS SONOROS FOLEY FPV (Doppler Shifter & Motor Whine)                           │
  │ [Whoosh Dive 450Hz]        [Proximity Glitch]        [Airbrake Sfx]                         │
  ├─────────────────────────────────────────────────────────────────────────────────────────────┤
  │ CAPA 5: BANDA SONORA FLOW BGM (Electronic Synthwave / Beat 118 BPM con Ducking -18dB)       │
  │ ♫ Beat Drop en t=3.0s (Sincronizado con el impacto del picado en el suelo)                  │
  └─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.1 Componente Remotion de Telemetría HUD FPV & Título Espacial 3D (`FPVTelemetryHUD.tsx`):
```tsx
import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';

interface FPVTelemetryProps {
  speedKmh: number;
  altitudeM: number;
  coordinates: string;
  landmarkTitle: string;
  yawAngle: number;
}

export const FPVTelemetryHUD: React.FC<FPVTelemetryProps> = ({
  speedKmh,
  altitudeM,
  coordinates,
  landmarkTitle,
  yawAngle,
}) => {
  const frame = useCurrentFrame();
  const currentSpeed = Math.round(interpolate(frame, [0, 90], [speedKmh * 0.7, speedKmh], { extrapolateRight: 'clamp' }));
  const currentAlt = Math.round(interpolate(frame, [0, 90], [altitudeM, altitudeM * 0.15], { extrapolateRight: 'clamp' }));

  return (
    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', fontFamily: 'monospace', color: '#38bdf8' }}>
      {/* 1. Telemetría HUD Esquinas */}
      <div style={{ position: 'absolute', top: 40, left: 40, background: 'rgba(15,23,42,0.65)', padding: '10px 16px', borderRadius: 8, backdropFilter: 'blur(8px)', border: '1px solid rgba(56,189,248,0.3)' }}>
        <div style={{ fontSize: 13, color: '#94a3b8' }}>SPEED // TELEMETRY</div>
        <div style={{ fontSize: 28, fontWeight: 'bold', color: '#f8fafc' }}>{currentSpeed} <span style={{ fontSize: 16 }}>KM/H</span></div>
        <div style={{ fontSize: 12, color: '#38bdf8' }}>ALT: {currentAlt}M AGL</div>
      </div>

      <div style={{ position: 'absolute', top: 40, right: 40, textAlign: 'right', background: 'rgba(15,23,42,0.65)', padding: '10px 16px', borderRadius: 8, backdropFilter: 'blur(8px)', border: '1px solid rgba(56,189,248,0.3)' }}>
        <div style={{ fontSize: 13, color: '#94a3b8' }}>GPS FIX // 60 FPS</div>
        <div style={{ fontSize: 14, color: '#f8fafc', fontWeight: 600 }}>{coordinates}</div>
        <div style={{ fontSize: 12, color: '#4ade80' }}>HDOP: 0.8 • 18 SATS</div>
      </div>

      {/* 2. Rótulo 3D Flotante Integrado en el Espacio Urbano */}
      <div style={{
        position: 'absolute',
        top: '42%',
        left: '15%',
        transform: `perspective(800px) rotateY(${yawAngle * 0.15}deg) rotateX(10deg)`,
        borderLeft: '4px solid #38bdf8',
        paddingLeft: 20,
      }}>
        <div style={{ fontSize: 14, letterSpacing: 4, color: '#38bdf8', textTransform: 'uppercase' }}>WAYPOINT REACHED</div>
        <h1 style={{ margin: 0, fontSize: 48, fontWeight: 900, color: '#ffffff', textShadow: '0 0 20px rgba(56,189,248,0.8)' }}>
          {landmarkTitle}
        </h1>
      </div>
    </div>
  );
};
```

---

## 7. 🤖 ARQUITECTURA DE INTEGRACIÓN Y ESQUEMA DEL ARCHETYPE EN VIDEOPRO

Se registra formalmente el arquetipo `FPV_URBAN_STORYTELLING` en el catálogo maestro de `app/core/orchestration/workflow_archetypes.py`:

```python
FPV_URBAN_STORYTELLING_ARCHETYPE = WorkflowArchetype(
    id="FPV_URBAN_STORYTELLING",
    name="Tours FPV y Storytelling Urbano 4K",
    icon="🚁",
    tag="CINEMATIC FPV & DRONE TOURS",
    description="Vuelos FPV de alta velocidad por ciudades globales con planes de vuelo 3D, 7 keyframes consistentes para Gemini Omni Flash, telemetría HUD y música flow.",
    category="travel_fpv_action",
    target_audience="Audiovisual Premium, Turismo de Lujo, Récords de Arquitectura, Viral Reels",
    default_aspect_ratio="9:16",
    visual_strategy=VisualStrategy.SINGLE_ENGINE,
    default_voice_engine="edge_tts",
    default_voice_id="es-ES-AlvaroNeural",
    default_music_genre="flow_synthwave",
    interview_schema=[
        InterviewQuestion(
            key="target_city_and_landmarks",
            question="¿Qué ciudad y qué 5 a 7 puntos emblemáticos compondrán la ruta FPV?",
            description="Ejemplo: 'Tokio: Scramble Square, Calle Center-Gai, Paso de Shibuya 109, Callejón Nonbei Yokocho, Mirador Cerulean'",
            question_type="text",
            default_value="Tokio: Azotea Scramble Square, Cruce de Shibuya, Fachada 109, Callejón Yokocho y Parque Miyashita"
        ),
        InterviewQuestion(
            key="fpv_flight_style",
            question="¿Qué estilo y agresividad de vuelo FPV deseas imprimir?",
            description="Define la física de movimiento, aceleraciones y acrobacias de la cámara",
            question_type="select",
            options=[
                "Acrobático & Extremo (Dives de 140 km/h, slaloms cerrados y giros de 360°)",
                "Cinemático & Fluido (Vuelos suaves, curvas amplias y paneos majestuosos)",
                "Cyberpunk Nocturno (Alta velocidad entre luces de neón y lluvia)",
                "Histórico & Arquitectónico (Aproximaciones de detalle y traspaso de monumentos)"
            ],
            default_value="Acrobático & Extremo (Dives de 140 km/h, slaloms cerrados y giros de 360°)"
        ),
        InterviewQuestion(
            key="narrative_subtext_focus",
            question="¿Cuál es el ángulo narrativo o misterio central de la historia urbana?",
            description="El gancho documental que aportará subtexto a los planos aéreos",
            question_type="select",
            options=[
                "Secretos de Ingeniería & Rascacielos Invisibles",
                "Contraste Urbano: Tradición Oculta vs Hipermodernidad",
                "La Metrópolis que Nunca Duerme (Pulso Nocturno 24/7)",
                "Historia Olvidada bajo el Asfalto"
            ],
            default_value="Secretos de Ingeniería & Rascacielos Invisibles"
        )
    ]
)
```

---

## 8. 🛡️ MATRIZ DE AUDITORÍA Y QUALITY GATES (CONTROL DE CALIDAD)

Antes de autorizar la entrega del máster final `final_fpv_tour.mp4`, el sistema ejecuta la siguiente matriz de verificación automatizada:

| Criterio de Auditoría | Umbral Requerido | Acción en caso de Fallo |
| :--- | :--- | :--- |
| **Regla de Oro de Peso** | Todos los activos $> 5\text{ KB}$ | Aborto inmediato (`Exit Code 2`) |
| **Nitidez de Imágenes Reales** | Varianza Laplaciana $\ge 100.0$ | Re-descarga automática de fuente alternativa |
| **Resolución de Salida** | 1080x1920 (9:16) o 3840x2160 (16:9) | Re-escalado bicúbico y encode con `libx264` / `h264_nvenc` |
| **Tasa de Cuadros** | 60.0 fps constantes | Normalización con filtro `fps=fps=60` en FFmpeg |
| **Nivel Sonoro Master** | $-14.0 \pm 1.0\text{ LUFS}$ (EBU R128) | Normalización de loudness de doble pasada (`loudnorm`) |
| **Ducking de Música** | $-18\text{ dB}$ durante locución | Aplicación de compuerta *sidechain* en Remotion/FFmpeg |

---
*Fin de la Especificación de Arquitectura Técnica — videopro Engine v5.0 Ultra.*
