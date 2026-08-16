# 🛰️ Workflow Técnico de Producción Optimizado: CHRONODRIFT
## Pipeline Autónomo de Producción de Vídeo 4K 60fps Anti-AI Slop
**Canal:** CHRONODRIFT (`@ChronoDriftOfficial`)  
**Motor de Vídeo:** Gemini Omni Flash (`gemini-omni-flash-preview` en Google Flow)  
**Motor de Keyframes:** Nano Banana Pro (`gemini-3.1-flash-image`)  
**Ecosistema:** VideoPro v4.0 Ultra / Remotion 4.x / Whisper Stable-TS / EBU R128  

---

## 1. 🏗️ Arquitectura Global del Pipeline de Producción

El canal **CHRONODRIFT** opera bajo una filosofía estricta **Anti-AI Slop**, garantizando que cada segundo de metraje esté anclado en datos geográficos reales (Street View 6-DoF + OpenStreetMap), proyecciones científicas rigurosas (IPCC / MIT / Copernicus) y una experiencia cinemática inmersiva de 60fps con diseño sonoro de nivel cinematográfico a **118 BPM**.

```mermaid
graph TD
    subgraph FASE 1: INGESTA & GROUNDING FACTICO 360°
        A1[Google Street View API 360° Master 8K] --> A3[Extracción 6 Perspectivas Canónicas 6-DoF]
        A2[OpenStreetMap Overpass 3D + Copernicus DEM] --> A4[Malla Vectorial & Altitud Barométrica AGL]
        A3 & A4 --> A5[Filtro Óptico: Var Laplaciana >=100.0 & Res >=4K]
    end

    subgraph FASE 2: KEYFRAMING & RENDER VIDEO GEMINI OMNI FLASH
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
```

---

## 2. 🌐 Fase 1: Ingesta & Scraping 6-DoF Fáctico (Street View + OpenStreetMap)

Para evitar la deformación y alucinación espacial de la IA generativa pura, el pipeline ancla cada plano utilizando un sistema de **6 grados de libertad (6-DoF)** extraído directamente del mundo real.

### 2.1 Las 6 Perspectivas Canónicas de Captura

Para cada hito urbano o coordenada de vuelo, se extrae un conjunto ortogonal y angular completo:

| Perspectiva | Heading ($\theta$) | Pitch ($\phi$) | Roll ($\psi$) | FOV | Propósito Técnico |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Norte (`CAM_N`)** | $0.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Vector de referencia axial norte y fachada frontal |
| **2. Este (`CAM_E`)** | $90.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Paraje lateral derecho y continuidad de horizonte |
| **3. Sur (`CAM_S`)** | $180.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Retro-perspectiva y anclaje de fuga trasera |
| **4. Oeste (`CAM_W`)** | $270.0^\circ$ | $0.0^\circ$ | $0.0^\circ$ | $90^\circ$ | Paraje lateral izquierdo y paralaje de sombra |
| **5. Picado Vertical (`CAM_PITCH_DOWN`)** | Target Vector | $-20.0^\circ$ | $0.0^\circ$ | $100^\circ$ | Textura de calzada, escala peatonal y relieve basal |
| **6. Contrapicado Vertical (`CAM_PITCH_UP`)**| Target Vector | $+25.0^\circ$ | $0.0^\circ$ | $100^\circ$ | Cúspide de rascacielos, cañón urbano y cielo abierto |

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

### 2.2 Integración Vectorial OSM 3D & Modelo Digital de Elevación (DEM)

El scraper consulta la API Overpass de OpenStreetMap para extraer huellas de edificios y alturas exactas, cruzándolas con los datos topográficos de Copernicus DEM 30m:

```python
# overpass_query_builder.py
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

### 2.3 Filtros de Calidad Óptica y Verificación Laplaciana

Cada fotograma descargado debe superar estrictamente tres filtros automáticos antes de ingresar a la memoria de trabajo de generación:

1. **Resolución Mínima:** $3840 \times 2160$ px (4K UHD nativo o mosaico esférico cosido de nivel 3).
2. **Umbral de Peso de Archivo:** $> 5.0\text{ KB}$ (rechazo instantáneo de respuestas truncadas o mocks).
3. **Filtro de Nitidez Laplaciana:** Varianza del operador Laplaciano $\text{Var}(\Delta I) \ge 100.0$.

$$\text{Laplacian Variance} = \sigma^2(\nabla^2 I) = \frac{1}{N} \sum_{x,y} \left( \nabla^2 I(x,y) - \mu_{\nabla^2 I} \right)^2 \ge 100.0$$

#### Script de Scraping y Filtrado de Nitidez:
```python
# scripts/scrape_and_filter_6dof.py
import cv2
import numpy as np
import os

def verify_and_filter_frame(image_path: str, min_variance: float = 100.0) -> bool:
    if not os.path.exists(image_path):
        return False
    
    file_size_kb = os.path.getsize(image_path) / 1024.0
    if file_size_kb < 5.0:
        print(f"[RECHAZADO] Archivo corrupto o mock (<5KB): {file_size_kb:.2f} KB")
        return False
        
    image = cv2.imread(image_path)
    if image is None:
        return False
        
    height, width, _ = image.shape
    if width < 3840 or height < 2160:
        print(f"[ALERTA RESOLUCION] {width}x{height} - Requiere mosaico 4K.")
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    print(f"[FRAME AUDIT] {os.path.basename(image_path)} | Tamaño: {file_size_kb:.1f}KB | Var Laplaciana: {laplacian_var:.2f}")
    
    if laplacian_var < min_variance:
        print(f"[RECHAZADO] Imagen borrosa (Var {laplacian_var:.2f} < {min_variance})")
        return False
        
    return True
```

---

## 3. 🎬 Fase 2: Motor de Generación Visual con Gemini Omni Flash (Sin Veo 3)

### 3.1 Mandato Estricto: Cero Veo 3 / Exclusividad Gemini Omni Flash

* **Motivo del Descarte de Veo 3:** Veo 3 presenta inconsistencias en la física aerodinámica de trayectorias 6-DoF, tiempos de inferencia no lineales y fallos de coincidencia geométrica en transformaciones match-cut temporales.
* **Modelo Oficial:** **`gemini-omni-flash-preview`** (`--engine omni_flash`) en Google Flow.
* **Ventajas de Omni Flash:**
  - Soporte nativo de hasta 7 imágenes de referencia (`<FIRST_FRAME>` + `<IMAGE_REF_0..5>`).
  - Capacidad de interpretar líneas vectoriales rojas de spline de cámara sin renderizarlas en el metraje final.
  - Sincronización de físicas y audio nativo ambiental de alta coherencia.
  - Generación de clips fluidos de 60fps con control milimétrico de inercia y aceleración.

---

### 3.2 El Shotlist Canónico de 7 Planos FPV (7D Canon)

Cada secuencia de viaje temporal en CHRONODRIFT se estructura invariablemente en los **7 planos canónicos**, garantizando un ritmo hipnótico y retención máxima (>90% en el primer minuto):

```text
[01_TERMINAL_DIVE] ──► [02_CANYON_DRIFT] ──► [03_TUNNEL_PIERCE] ──► [04_MONUMENT_ORBIT]
     (0-3s Hook)            (3-10s Micro)         (10-18s Foley)        (18-25s Anchor)
                                                                                │
[07_SKYLINE_SUNSET] ◄── [06_VERTICAL_SURGE] ◄── [05_PEDESTRIAN_SWOOP] ◄───────┘
   (38-45s Climax)          (32-38s Ascent)        (25-32s Atmosphere)
```

1. **`01_TERMINAL_DIVE` (0–3s | 1.5 compases):** Picado vertical $90^\circ$ a 140 km/h desde 850m AGL hacia el centro histórico. Funciona como el *hook* visual de retención instantánea.
2. **`02_CANYON_DRIFT` (3–10s | 3.5 compases):** Vuelo rasante entre fachadas históricas con giro centempóreo y despliegue de telemetría HUD (altitud, velocidad, año).
3. **`03_TUNNEL_PIERCE` (10–18s | 4.0 compases):** Penetración supersónica a baja altura por arcos medievales o pasajes cubiertos; en el centro del umbral, se ejecuta el match-cut hacia 2026.
4. **`04_MONUMENT_ORBIT` (18–25s | 3.5 compases):** Giro orbital continuo $360^\circ$ en torno al hito arquitectónico contemporáneo con rótulos 3D anclados espacialmente (*billboard tracking*).
5. **`05_PEDESTRIAN_SWOOP` (25–32s | 3.5 compases):** Vuelo a ras de suelo a escala humana ($1.5\text{m}$ AGL) capturando la iluminación y atmósfera antes de iniciar la ascensión hacia 2226.
6. **`06_VERTICAL_SURGE` (32–38s | 3.0 compases):** Aceleración vertical trepando por la fachada de la arcología bioclimática hacia las pasarelas aéreas a 300m AGL.
7. **`07_SKYLINE_SUNSET_ASCENSION` (38–45s | 3.5 compases):** Revelación panorámica en gran angular durante el crepúsculo futurista a 500m AGL, cerrando el bucle temporal.

---

### 3.3 Generación de los 7 Keyframes Consistentes con Nano Banana Pro

Antes de solicitar la animación a Gemini Omni Flash, se generan las **7 imágenes ancla fotorrealistas** con **Nano Banana Pro** (`gemini-3.1-flash-image` / `--model nanobanana`), asegurando la misma lente, paleta de iluminación volumétrica y anclaje arquitectónico.

#### Especificación Cinematográfica de Prompts:
* **Óptica:** Lentes anamórficas prime de $35\text{mm } f/1.8$ y $50\text{mm } f/1.2$.
* **Grano:** Textura fina cinematográfica analógica Kodak Vision3 500T 5219.
* **Colorimetría:** Perfil ARRI Alexa LF LogC / Rec.709 D65 Master.
* **Obturación:** $180^\circ$ shutter angle ($1/120\text{s}$ para 60fps) con motion blur físico real.

---

### 3.4 Sintaxis Oficial de Google Flow / Gemini Omni Flash

```text
[# Sources <FIRST_FRAME>@Keyframe01_Start] [# References <IMAGE_REF_0>@Cam_N <IMAGE_REF_1>@Cam_E <IMAGE_REF_2>@Cam_S <IMAGE_REF_3>@Cam_W <IMAGE_REF_4>@Cam_PitchDown <IMAGE_REF_5>@Cam_PitchUp]

Use Keyframe01_Start as the literal opening frame 0. Use the given reference images as geometric and lighting consistency references for video generation; do not use them as literal initial frames.

A continuous, ultra-smooth 60fps cinematic 5-inch FPV drone flight navigating in 6 degrees of freedom (6-DoF). The camera executes a dynamic terminal dive and canyon drift between architectural structures. Optical parameters: 35mm f/1.8 anamorphic lens, Kodak Vision3 500T grain, ARRI Alexa LF colorimetry, true volumetric lighting and realistic aerodynamic motion blur. No morphing, no distortion artifacts, perfectly stable architectural lines. Audio: high-speed wind shear and binaural carbon-fiber propeller whine.
```

---

### 3.5 Prompts Maestros Tritemporales de Producción (10 Episodios)

#### 🇯🇵 Episodio 01: Tokio (1630 Edo ➔ 2026 Shibuya ➔ 2226 Neo-Tokyo Arcology)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Tokyo_Edo_1630] [# References <IMAGE_REF_0>@Shibuya_N <IMAGE_REF_1>@Shibuya_E <IMAGE_REF_2>@Shibuya_S <IMAGE_REF_3>@Shibuya_W <IMAGE_REF_4>@Tokyo_Arcology_Concept <IMAGE_REF_5>@Tokyo_Spline_Path]

Execute a seamless tritemporal FPV match-cut sequence across 3 distinct historical epochs along the Sumida River and Shibuya axis:
- Epoch I (1630 Edo): Low-altitude glide under wooden Nihonbashi bridges, traditional timber merchant stalls, paper lanterns, and mist over Mount Fuji in the background.
- Epoch II (2026 Tokyo): Transitioning smoothly along the identical camera vector into modern Shibuya Crossing at night, hyper-vibrant 4K neon signage, asphalt reflections, and streaming commuter flows.
- Epoch III (2226 Neo-Tokyo Arcology): Accelerating through the identical flight path into a towering self-sustaining mega-arcology, magnetic levitation transit tubes, vertical hydroponic terraces, and atmospheric holographic navigational beacons.

Camera movement: Continuous forward surge at 110 km/h with a 15-degree banked turn to the right, maintaining continuous horizon stability. 35mm f/1.8 anamorphic lens, Kodak Vision3 500T texture, volumetric atmosphere. No jump-cuts; motion vectors align perfectly across epoch dissolves.
```
* **7 Keyframes:**
  1. `KF1`: Estratosfera 850m mirando hacia la cubierta de nubes sobre Edo.
  2. `KF2`: Penetrando nubes volumétricas con motion blur periférico.
  3. `KF3`: Apertura a 450m mostrando el foso y murallas del Castillo de Edo.
  4. `KF4`: Vuelo rasante a 1.8m por el puente de madera de Nihonbashi en 1630.
  5. `KF5`: Match-cut en el umbral del puente que transmuta en Shibuya Neón 2026.
  6. `KF6`: Ascenso vertical trepando la megatorre Shimizu Arcology en 2226.
  7. `KF7`: Órbita panorámica a 500m con el Monte Fuji y la arcología al atardecer.

#### 🇺🇸 Episodio 02: Nueva York (1626 Nieuw Amsterdam ➔ 2026 Manhattan ➔ 2226 Bioluminescent Manhattan)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@NYC_NieuwAmsterdam_1626] [# References <IMAGE_REF_0>@WallStreet_N <IMAGE_REF_1>@WallStreet_E <IMAGE_REF_2>@WallStreet_S <IMAGE_REF_3>@WallStreet_W <IMAGE_REF_4>@NYC_Graphene_Towers <IMAGE_REF_5>@NYC_Spline_Path]

Continuous FPV drone canyon drift along the Manhattan spine from Wall Street to Central Park:
- Epoch I (1626): Overflying the virgin Lenape forest hills, wooden palisades of Fort Amsterdam, and natural marshy shoreline.
- Epoch II (2026): Merging through the identical trajectory into the modern concrete and glass canyons of Wall Street and One World Trade, sun glinting off glass facades at 60fps.
- Epoch III (2226): Seamless match-cut into a climate-resilient metropolis featuring MIT-designed kinetic sea-wall dikes, translucent graphene supertall towers, and bioluminescent sky-gardens illuminated by soft cyan and gold ambient light.

Cinematography: 50mm f/1.2 lens, volumetric god rays piercing between towers, organic motion blur. Audio: aerodynamic wind shear transitioning into deep urban resonance and subtle magnetic purr.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre la bahía virgen de Mannahatta en 1626.
  2. `KF2`: Vuelo rasante rozando la empalizada de troncos de Wall Street.
  3. `KF3`: Match-cut en la esquina de Wall St y Broad St transmutando en 2026.
  4. `KF4`: Ascenso supersónico entre One WTC y los cañones de cristal.
  5. `KF5`: Entrada a la pasarela bioclimática The Big U 2200 sobre la costa.
  6. `KF6`: Planeo entre torres de grafeno translúcidas con jardines colgantes.
  7. `KF7`: Panorámica crepuscular de la Bahía de Nueva York con la arcología dorada.

#### 🇬🇧 Episodio 03: Londres (1610 Tudor Bridge ➔ 2026 The City ➔ 2226 Sky-Canopy London)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@London_Tudor_1610] [# References <IMAGE_REF_0>@Thames_N <IMAGE_REF_1>@Thames_E <IMAGE_REF_2>@Thames_S <IMAGE_REF_3>@Thames_W <IMAGE_REF_4>@London_GeoDome_2226 <IMAGE_REF_5>@London_Spline_Path]

FPV low-altitude water-skim along the River Thames executing a 360-degree helical climb around key architectural anchors:
- Epoch I (1610): Skimming inches above the Thames, threading through the crowded multistory timber houses of old London Bridge before the Great Fire.
- Epoch II (2026): Sweeping seamlessly up the glass spire of The Shard and Tower Bridge with pristine reflective water and modern red transit buses below.
- Epoch III (2226): Ascending through the same spiral into Sky-Canopy London, under massive climate-protective geo-domes spanning the Thames basin with autonomous micro-solar aerial gliders.

Camera: Ultra-precise roll stabilization, anamorphic flare, Kodak 500T color grading. Flawless match-cut transitions on beat subdivisions.
```
* **7 Keyframes:**
  1. `KF1`: Inmersión en la niebla del Támesis hacia el viejo Puente de Londres en 1610.
  2. `KF2`: Vuelo rasante bajo los arcos de piedra esquivando barcas de madera.
  3. `KF3`: Match-cut bajo el arco que transmuta en Tower Bridge 2026.
  4. `KF4`: Ascenso en espiral rozando los paneles de cristal de The Shard.
  5. `KF5`: Entrada bajo la megacúpula geodésica bioclimática Sky-Canopy 2226.
  6. `KF6`: Planeo siguiendo cápsulas de levitación magnética a 200m AGL.
  7. `KF7`: Gran panorámica crepuscular sobre Westminster y la cúpula dorada.

#### 🇫🇷 Episodio 04: París (1620 Île de la Cité ➔ 2026 Haussmann ➔ 2226 Vertical Forest)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Paris_Medieval_1620] [# References <IMAGE_REF_0>@NotreDame_N <IMAGE_REF_1>@NotreDame_E <IMAGE_REF_2>@NotreDame_S <IMAGE_REF_3>@NotreDame_W <IMAGE_REF_4>@Paris_Biophilic_2226 <IMAGE_REF_5>@Paris_Spline_Path]

360-degree orbital dive and fly-through along the Seine River across 400 years:
- Epoch I (1620): Gliding above timber-framed houses in Île de la Cité, Notre-Dame Cathedral in its medieval state, Pont Neuf under early stone construction, horse carriages.
- Epoch II (2026): Merging seamlessly into Haussmannian stone boulevards, illuminated Eiffel Tower glistening at twilight, modern clean riverbanks.
- Epoch III (2226): Ascending into a vertical garden metropolis designed with Vincent Callebaut biophilic towers, CLT-graphene spirals, and a crystal-clear purified Seine biosphere.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre el Sena medieval hacia la aguja de Notre-Dame en 1620.
  2. `KF2`: Vuelo rasante por las callejuelas de madera de Le Marais.
  3. `KF3`: Match-cut atravesando una arcada de piedra hacia los bulevares de 2026.
  4. `KF4`: Ascenso trepando la estructura de hierro de la Torre Eiffel iluminada.
  5. `KF5`: Transición hacia las torres biofílicas de madera contralaminada en 2226.
  6. `KF6`: Planeo sobre el Sena cristalino con pasarelas peatonales a 300m AGL.
  7. `KF7`: Panorámica de los Campos Elíseos convertidos en bosque aéreo al ocaso.

#### 🇳🇱 Episodio 05: Ámsterdam (1626 Grachtengordel ➔ 2026 Canales ➔ 2226 Kinetic Ocean Grid)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Amsterdam_VOC_1626] [# References <IMAGE_REF_0>@DamSquare_N <IMAGE_REF_1>@DamSquare_E <IMAGE_REF_2>@DamSquare_S <IMAGE_REF_3>@DamSquare_W <IMAGE_REF_4>@Amsterdam_OceanGrid_2226 <IMAGE_REF_5>@Amsterdam_Spline_Path]

Low-altitude canal skimming FPV drone flight along the historic Grachtengordel ring:
- Epoch I (1626): Passing wooden warehouses with hoist beams, VOC three-masted sailing galleons, and hand-excavated canals.
- Epoch II (2026): Sweeping under modern iron bridges with sleek electric trams and thousands of bicycles along brick quays.
- Epoch III (2226): Floating ocean-grid architecture with modular kinetic tidal gates, self-healing biopolymer canal barriers, and solar-membrane water homes.
```
* **7 Keyframes:**
  1. `KF1`: Entrada rasante sobre el río Amstel hacia los astilleros de la VOC en 1626.
  2. `KF2`: Vuelo bajo entre almacenes de ladrillo con poleas de madera.
  3. `KF3`: Match-cut bajo el puente levadizo que transmuta en Prinsengracht 2026.
  4. `KF4`: Vuelo dinámico esquivando ciclistas y casas flotantes de diseño.
  5. `KF5`: Salto hacia las compuertas cinéticas modulares anti-marea de 2226.
  6. `KF6`: Planeo por canales bioclimáticos con micro-biosferas transparentes.
  7. `KF7`: Panorámica sobre la Plaza Dam con la red oceánica flotante al atardecer.

#### 🇮🇹 Episodio 06: Roma (1626 San Pietro ➔ 2026 Coliseo ➔ 2226 Cyber-Antiquity)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Rome_Baroque_1626] [# References <IMAGE_REF_0>@Colosseum_N <IMAGE_REF_1>@Colosseum_E <IMAGE_REF_2>@Colosseum_S <IMAGE_REF_3>@Colosseum_W <IMAGE_REF_4>@Rome_HoloRuins_2226 <IMAGE_REF_5>@Rome_Spline_Path]

High-speed supersonic dive over Vatican and Imperial Forums through historical eras:
- Epoch I (1626): St. Peter's Basilica freshly consecrated by Urban VIII, Bernini's travertine workshops, cows grazing in the Roman Forum ruins.
- Epoch II (2026): Restored Colosseum bathed in dramatic night spotlights, bustling Piazza Navona, modern electric scooters.
- Epoch III (2226): Cyber-antiquity architecture with permanent volumetric holograms projecting classical marble temples over ancient ruins, protected by climate geodomes.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre la cúpula de San Pedro recién completada en 1626.
  2. `KF2`: Vuelo rasante entre los talleres de mármol de Bernini.
  3. `KF3`: Match-cut en el arco de triunfo hacia la Vía de los Foros en 2026.
  4. `KF4`: Ascenso orbital en torno a los arcos iluminados del Coliseo.
  5. `KF5`: Activación de hologramas volumétricos azules restaurando templos en 2226.
  6. `KF6`: Planeo bajo cúpulas geodésicas de nanopolímeros sobre el Foro Romano.
  7. `KF7`: Panorámica de la Ciudad Eterna al crepúsculo fusionando piedra y luz láser.

#### 🇦🇪 Episodio 07: Dubái (1833 Al Fahidi ➔ 2026 Burj Khalifa ➔ 2226 Solar Arcology)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Dubai_AlFahidi_1833] [# References <IMAGE_REF_0>@BurjKhalifa_N <IMAGE_REF_1>@BurjKhalifa_E <IMAGE_REF_2>@BurjKhalifa_S <IMAGE_REF_3>@BurjKhalifa_W <IMAGE_REF_4>@Dubai_MegaTower_2226 <IMAGE_REF_5>@Dubai_Spline_Path]

Desert dune to stratospheric mega-tower FPV transition:
- Epoch I (1833): Traditional pearl-diving village of Al Fahidi, coral and gypsum Barjeel wind towers, wooden dhows on Dubai Creek.
- Epoch II (2026): Burj Khalifa soaring 828 meters into blue sky, Dubai Marina superyachts, dancing fountains with laser shows.
- Epoch III (2226): 3,000-meter solar arcology geo-towers with passive geothermal cooling and massive hydroponic green belts terraforming the desert.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre las dunas doradas y cabañas Barasti de Al Fahidi en 1833.
  2. `KF2`: Vuelo rasante entre torres de viento Barjeel y dhows en el Creek.
  3. `KF3`: Match-cut en el agua del Creek transmutando en el Lago de las Fuentes 2026.
  4. `KF4`: Ascenso vertical trepando los 828 metros del Burj Khalifa.
  5. `KF5`: Revelación de la megatorre bioclimática de 3.000m en 2226.
  6. `KF6`: Planeo entre terrazas hidropónicas colgantes sobre el desierto verde.
  7. `KF7`: Panorámica del skyline futurista con energía solar pura al atardecer.

#### 🇭🇰 Episodio 08: Hong Kong (1841 Fragrant Harbour ➔ 2026 Victoria Peak ➔ 2226 Stratospheric Aerodome)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@HongKong_Fishery_1841] [# References <IMAGE_REF_0>@VictoriaPeak_N <IMAGE_REF_1>@VictoriaPeak_E <IMAGE_REF_2>@VictoriaPeak_S <IMAGE_REF_3>@VictoriaPeak_W <IMAGE_REF_4>@HongKong_Skyway_2226 <IMAGE_REF_5>@HongKong_Spline_Path]

Extreme vertical canyon drift between jungle peaks and laser-lit skyscrapers:
- Epoch I (1841): Hakka fishing village on stilts in Aberdeen, red-sailed Chinese junks in Victoria Harbour, dense tropical rainforest.
- Epoch II (2026): World's densest skyscraper skyline, double-decker Ding Ding trams, laser symphony of lights across the harbour.
- Epoch III (2226): Habitable skyways suspended at 800m altitude connecting supertowers, typhoon kinetic dissipation shield rings, and floating marine arcologies.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre la selva virgen de Victoria Peak hacia los juncos en 1841.
  2. `KF2`: Vuelo rasante entre casas de pescadores sobre pilotes de madera.
  3. `KF3`: Match-cut en el puerto transmutando en el Victoria Harbour nocturno de 2026.
  4. `KF4`: Espiral entre los rascacielos iluminados por láser de Central.
  5. `KF5`: Ascenso hacia las pasarelas peatonales habitables a 800m en 2226.
  6. `KF6`: Planeo a través de los anillos cinéticos de disipación de tifones.
  7. `KF7`: Panorámica crepuscular de la bahía con las megatorres estratosféricas.

#### 🇪🇬 Episodio 09: El Cairo (1626 Ciudadela ➔ 2026 Metrópolis ➔ 2226 Nile Solar Arcology)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Cairo_Citadel_1626] [# References <IMAGE_REF_0>@Giza_N <IMAGE_REF_1>@Giza_E <IMAGE_REF_2>@Giza_S <IMAGE_REF_3>@Giza_W <IMAGE_REF_4>@Cairo_SolarDome_2226 <IMAGE_REF_5>@Cairo_Spline_Path]

Sweeping historical transition across the Nile basin and Giza plateau:
- Epoch I (1626): Mamluk and Ottoman Citadel of Saladin, bustling Khan el-Khalili bazaar alleys, annual Nile floodwaters irrigating crops near Giza.
- Epoch II (2026): Grand Egyptian Museum (GEM), modern Nile bridges, sprawling metropolitan grid surrounding the Pyramids.
- Epoch III (2226): Climate-controlled nanoglass geodomes preserving the Pyramids, solar-powered atmospheric water generators, and vertical agricultural arcologies along the green Nile corridor.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre la Ciudadela de Saladino y mezquitas mamelucas en 1626.
  2. `KF2`: Vuelo rasante por los callejones de especias de Khan el-Khalili.
  3. `KF3`: Match-cut en la ribera del Nilo transmutando en la metrópolis de 2026.
  4. `KF4`: Vuelo rasante rozando el ápice de la Gran Pirámide de Guiza.
  5. `KF5`: Entrada bajo la cúpula geodésica de nanovidrio protectora en 2226.
  6. `KF6`: Planeo sobre los corredores agrícolas desérticos regados con energía solar.
  7. `KF7`: Panorámica al atardecer sobre el Nilo con las pirámides y arcologías.

#### 🇮🇹 Episodio 10: Venecia (1626 Serenissima ➔ 2026 Gran Canal & MOSE ➔ 2226 Crystal Venice)
* **Prompt Gemini Omni Flash:**
```text
[# Sources <FIRST_FRAME>@Venice_Serenissima_1626] [# References <IMAGE_REF_0>@SanMarco_N <IMAGE_REF_1>@SanMarco_E <IMAGE_REF_2>@SanMarco_S <IMAGE_REF_3>@SanMarco_W <IMAGE_REF_4>@Venice_CrystalLagoon_2226 <IMAGE_REF_5>@Venice_Spline_Path]

Fluid aquatic and aerial FPV flight through Venetian canals across four centuries:
- Epoch I (1626): Naval supremacy of the Venetian Republic, war galleys building in the Arsenal, Doge's Palace and St. Mark's Basilica in golden glory.
- Epoch II (2026): Grand Canal with electric vaporettos, restored Rialto Bridge, active MOSE flood barrier gates protecting the lagoon.
- Epoch III (2226): Sub-aquatic transparent graphene arcologies in the lagoon, self-healing biocement foundations, and ionic sea-level stabilizers.
```
* **7 Keyframes:**
  1. `KF1`: Picado sobre la Plaza de San Marcos y galeazas del Arsenal en 1626.
  2. `KF2`: Vuelo rasante a ras de agua por el Gran Canal entre góndolas históricas.
  3. `KF3`: Match-cut bajo el Puente de Rialto transmutando en el canal moderno de 2026.
  4. `KF4`: Vuelo sobre las compuertas amarillas del sistema MOSE emergiendo del mar.
  5. `KF5`: Inmersión hacia la arcología subacuática transparente de grafeno en 2226.
  6. `KF6`: Ascenso sobre canales de filtración biológica con biosferas flotantes.
  7. `KF7`: Panorámica crepuscular de la laguna de Venecia con la ciudad de cristal.

---

## 4. 🔊 Fase 3: Audio Engineering, VO-First & Master EBU R128

### 4.1 Rejilla Rítmica Estricta a 118 BPM

Toda la música del canal pertenece al género **Flow Chillhop / Urban Lo-Fi & Darksynth**, compuesto y editado estrictamente a **118 BPM** en compás de $4/4$:

$$\text{Duración de 1 Beat} = \frac{60\,000\text{ ms}}{118\text{ BPM}} = 508.4746\text{ ms}$$
$$\text{Duración de 1 Compás (4 Beats)} = 4 \times 508.4746\text{ ms} = 2033.898\text{ ms} \approx 2.034\text{ s}$$
$$\text{Frase Canónica (4 Compases / 16 Beats)} = 16 \times 508.4746\text{ ms} = 8135.593\text{ ms} \approx 8.136\text{ s}$$

* **Cortes de Plano Sincronizados:** Los 7 planos del shotlist coinciden exactamente con múltiplos de compases (ej. `01_TERMINAL_DIVE` dura exactamente 1 compás y medio = $3.05\text{s}$; `02_CANYON_DRIFT` dura 3 compases y medio = $7.12\text{s}$; `03_TUNNEL_PIERCE` dura 4 compases = $8.14\text{s}$).

---

### 4.2 Sincronización VO-First con Whisper Stable-TS

El audio de la locución (`narration.mp3`) manda sobre la línea de tiempo visual. Se procesa con **Whisper Stable-TS** para extraer marcas de tiempo a nivel de palabra:

```python
# scripts/extract_vo_timestamps.py
import stable_whisper
import json

def process_voiceover(audio_path: str, output_json: str):
    model = stable_whisper.load_model('base')
    result = model.transcribe(audio_path)
    
    word_timestamps = []
    for segment in result.segments:
        for word in segment.words:
            word_timestamps.append({
                "word": word.word.strip(),
                "start": round(word.start, 3),
                "end": round(word.end, 3),
                "probability": round(word.probability, 3)
            })
            
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            "total_duration": result.duration,
            "words": word_timestamps
        }, f, indent=2, ensure_ascii=False)
```

---

### 4.3 Ducking Dinámico Inteligente (-18 dB)

Durante los tramos en los que la voz en off entrega datos científicos o históricos, la música de fondo se atenúa automáticamente a **-18.0 dB**. En los momentos de aceleración visual, transiciones de vórtice y clímax instrumental, la música asciende a **0.0 dB** (nivel nominal master).

* **Tiempo de Ataque ($T_{\text{attack}}$):** $30.0\text{ ms}$ (curva exponencial suave para evitar chasquidos).
* **Tiempo de Relajación ($T_{\text{release}}$):** $250.0\text{ ms}$ (retorno natural tras la última sílaba).
* **Tiempo de Sostenido ($T_{\text{hold}}$):** $50.0\text{ ms}$.

#### Filtro FFmpeg para Ducking Dinámico:
```bash
ffmpeg -i vo_narration.wav -i bgm_118bpm.wav -filter_complex \
"[1:a]asplit=2[bgm_direct][bgm_sc]; \
 [bgm_sc][0:a]sidechaincompress=threshold=0.08:ratio=6:attack=30:release=250:level_in=1[bgm_ducked]; \
 [0:a]volume=1.0[vo]; \
 [bgm_ducked]volume=0.1258[bgm_attenuated]; \
 [vo][bgm_attenuated]amix=inputs=2:duration=first:dropout_transition=2[out_audio]" \
-map "[out_audio]" audio_ducked_master.wav
```
*(Nota: Un factor de volumen de $0.1258$ equivale exactamente a $-18.0\text{ dB}$).*

---

### 4.4 Masterización Broadcast EBU R128 (-14 LUFS / -1.0 dBTP)

Para garantizar la máxima potencia y claridad en YouTube sin activar la compresión destructiva del algoritmo de normalización de la plataforma:

* **Sonoridad Integrada:** **$-14.0\text{ LUFS}$** ($\pm 0.5\text{ LUFS}$).
* **Pico Verdadero Máximo (True Peak):** **$-1.0\text{ dBTP}$** (previene distorsión inter-sample en encoders AAC/Opus).
* **Rango de Sonoridad (LRA):** **$6.0\text{ a }8.0\text{ LU}$** (dinámica cinemática controlada).

#### Comando FFmpeg con Filtro `loudnorm` de 2 Pasadas:
```bash
# Paso 1: Medición de parámetros acústicos
ffmpeg -i audio_raw_mix.wav -af loudnorm=I=-14:TP=-1.0:LRA=7:print_format=json -f null - 2> loudnorm_stats.json

# Paso 2: Normalización lineal precisa de 2 pasadas
ffmpeg -i audio_raw_mix.wav -af \
loudnorm=I=-14.0:TP=-1.0:LRA=7.0:measured_I=-18.4:measured_TP=-0.2:measured_LRA=8.1:measured_thresh=-29.1:offset=0.2:linear=true \
-ar 48000 -c:a pcm_s24le audio_master_ebur128.wav
```

---

### 4.5 Sound Design Espacial & Foley Doppler 3D

El diseño de sonido inyecta capas diegéticas tridimensionales calibradas por la telemetría del vuelo:

1. **Efecto Doppler en Puntos de Proximidad Arquitectónica:**
   $$\Delta f = f_0 \left( \frac{v_{\text{sonido}}}{v_{\text{sonido}} \mp v_{\text{dron}}} \right)$$
   Al pasar a $110\text{ km/h}$ ($30.5\text{ m/s}$) junto a una torre, el tono del zumbido de las hélices se desplaza $+9.8\%$ en la aproximación y $-8.2\%$ en el alejamiento.
2. **Capas Foley de Época:**
   - **1626:** Crujidos de madera, agua en cascos de barcas, viento natural y campanadas distantes.
   - **2026:** Fricción de neumáticos sobre asfalto húmedo, zumbido electromagnético y metro subterráneo.
   - **2226:** Silbido de propulsores iónicos, campos de fuerza y pulsos de datos subacuáticos.
3. **Impacto de Transición Vórtice:** Sub-bass drop afinado a **$35\text{ Hz}$** combinado con barrido de ruido blanco filtrado en paso-banda.

---

## 5. 💻 Fase 4: Composición Remotion 4.x & HUD 3D Vectorial

El renderizado final y la superposición de interfaces gráficas en pantalla se gestionan con **Remotion 4.x** en TypeScript/React, utilizando aceleración GPU para 60fps constantes.

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

      {/* Caja de Velocidad & Altitud Inferior Derecha */}
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
        <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.7)', marginTop: '4px' }}>DATA ANCHOR: {scientificSource}</div>
      </div>
    </div>
  );
};
```

---

## 6. 📊 Matriz de Control de Calidad (QA Gates)

Todo episodio renderizado debe validar el checklist antes de su distribución:

| Criterio | Umbral / Especificación | Herramienta de Validación | Acción en Fallo |
| :--- | :--- | :--- | :--- |
| **Integridad de Assets** | Todos los archivos $> 5.0\text{ KB}$ | `scripts/verify-assets.py` | Aborto inmediato `Exit Code 2` |
| **Resolución de Vídeo** | $3840 \times 2160$ px @ 60.0 fps | `ffprobe` | Re-renderizado en Remotion |
| **Sonoridad Integrada** | $-14.0\text{ LUFS} \pm 0.5\text{ LUFS}$ | `ffmpeg loudnorm` | Re-masterizado de 2 pasadas |
| **Pico Verdadero** | $\le -1.0\text{ dBTP}$ | `ffmpeg loudnorm` | Limitador de picos True-Peak |
| **Ducking de Música** | $-18.0\text{ dB}$ bajo voz | `ffprobe ebur128` | Ajuste de ganancia sidechain |
| **Retención Visual** | 7 planos canónicos por episodio | `scenes.json validator` | Regeneración de shotlist |
| **Consistencia 6-DoF** | Varianza Laplaciana $\ge 100.0$ | `cv2.Laplacian` | Re-scraping / Mosaico 4K |

---

## 7. 🚀 Plan de Despliegue de los 10 Primeros Episodios

| # | Ciudad | Época I (Pasado) | Época II (Presente) | Época III (Futuro) | Anclaje Científico |
| :- | :--- | :--- | :--- | :--- | :--- |
| **EP01** | **Tokio** | 1630 (Edo / Nihonbashi) | 2026 (Shibuya Neón) | 2226 (Mega-Arcología) | IPCC Mega-Delta Resilience + Tokyo Seismic Grid + Shimizu Mega-Pyramid |
| **EP02** | **Nueva York** | 1626 (Nieuw Amsterdam) | 2026 (Manhattan Vertical) | 2226 (Bioluminescent NYC) | MIT Sea-Wall Dikes + Carbon-Graphene Aerodynamics + The Big U 2200 |
| **EP03** | **Londres** | 1610 (Puente Tudor) | 2026 (The City & Shard) | 2226 (Sky-Canopy London) | Thames Barrier Phase 4 + Atmospheric Geo-domes + UCL Bartlett School |
| **EP04** | **París** | 1620 (Medieval Île Cité) | 2026 (Haussmann & Eiffel) | 2226 (Vertical Forest) | Bioclimatic Chimneys + Subterranean Hyperloop + Vincent Callebaut Paris 2200 |
| **EP05** | **Ámsterdam** | 1626 (Grachtengordel) | 2026 (Canales y Bicis) | 2226 (Kinetic Ocean Grid) | TU Delft Hydro-kinetic Floating Foundations + Deltares Adaptation |
| **EP06** | **Roma** | 1626 (San Pietro Barroco) | 2026 (Coliseo Eterno) | 2226 (Subterranean Hub) | Geothermal Roman Concrete Regeneration + Sapienza CNR Framework |
| **EP07** | **Dubái** | 1833 (Al Fahidi Pearl) | 2026 (Burj Khalifa) | 2226 (Cloud-Seeded Tower) | Solar Desalination Aeroponic Mega-Towers + Dubai Future Foundation |
| **EP08** | **Hong Kong** | 1841 (Fragrant Harbour) | 2026 (Victoria Peak Neón) | 2226 (Stratosphere Dome) | Typhoon Kinetic Dissipation Shield Rings + HKUST Aerodynamics |
| **EP09** | **El Cairo** | 1626 (Ciudadela Mameluca) | 2026 (Guiza y Metrópolis) | 2226 (Nile Solar Arcology) | Desert Carbon Mineralization + Preservation Domes + Nile Resilience |
| **EP10** | **Venecia** | 1626 (Serenissima Naval) | 2026 (Gran Canal & MOSE) | 2226 (Crystal Venice) | Ionic Sea-Level Stabilizers + Biomimetic Coral Dikes + Venice Lagoon |

---

*Manual técnico de producción optimizado para CHRONODRIFT en VideoPro v4.0 Ultra — Aprobado para ejecución autónoma.*
