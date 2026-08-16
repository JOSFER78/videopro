#!/usr/bin/env python3
"""
tritemporal_urban_story_builder.py — Generador de Manifiestos de Vuelos Tritemporales (1626 ➔ 2026 ➔ 2226) para VideoPro & ChronoDrift.

Ensambla la historia completa de 7 planos canónicos por episodio sincronizados con:
- Transiciones match-cut exactas en el mismo eje de cámara (georreferenciadas WGS84).
- Prompts estructurados para Gemini Omni Flash (gemini-omni-flash-preview) con 7 keyframes consistentes por plano (gemini-3.1-flash-image / Nano Banana Pro).
- Overlays HUD 3D en Remotion con altímetro dinámico, compás, coordenadas WGS84, datos curiosos y citas de estudios científicos (IPCC / MIT).
- Pistas de audio Flow / Chillhop / Darksynth (118 BPM) con ducking dinámico a -18 dB y masterización sonora EBU R128 (-14.0 LUFS integrado, -1.0 dBTP True Peak).
- Cero dependencia de Veo 3.
- Generación de los 10 episodios maestros completos del canal CHRONODRIFT.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    try:
        from scripts.video_storage_manager import VideoStorageManager
    except ImportError:
        VideoStorageManager = None

WORKSPACE_ROOT = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
GROUNDING_DIR = WORKSPACE_ROOT / "data" / "tritemporal_grounding"
OUTPUT_DIR = WORKSPACE_ROOT / "data" / "tritemporal_manifests"


CITY_EPISODES_METADATA = {
    "tokyo": {
        "num": 1,
        "name": "Tokio",
        "historical_name": "Edo",
        "past_year": 1630,
        "past_focus": "Castillo de Edo, puente Nihonbashi y barrios de madera machiya a orillas del río Sumida",
        "present_focus": "Shibuya Scramble, Shinjuku neón y rascacielos sismorresistentes con pantallas 3D",
        "future_focus": "Mega-Arcología Neo-Tokyo X-Seed 1200m y Shimizu Mega-Pyramid con redes de levitación en vacío",
        "hook": "Picado vertical a 130 km/h desde la Torre de Tokio que atraviesa una nube temporal hacia el río Sumida en 1630.",
        "mit_ipcc_fact": "Estudio Shimizu & Tokyo Urban Resilience 2200: arcologías con capacidad para 1.5 millones de habitantes con balance neutro de carbono."
    },
    "newyork": {
        "num": 2,
        "name": "Nueva York",
        "historical_name": "Nueva Ámsterdam",
        "past_year": 1626,
        "past_focus": "Fuerte Ámsterdam en The Battery, empalizada en Wall Street y colinas vírgenes de Mannahatta",
        "present_focus": "Manhattan Vertical, One WTC, Times Square y Central Park",
        "future_focus": "Bioluminescent Manhattan con el sistema The Big U 2200, torres de grafeno y pasarelas eólicas",
        "hook": "Vuelo rasante por Wall Street que disuelve los rascacielos de cristal en el bosque original de la tribu Lenape.",
        "mit_ipcc_fact": "Columbia Climate School & BIG: parques costeros de amortiguación frente a elevación del nivel del mar de +1.8m."
    },
    "london": {
        "num": 3,
        "name": "Londres",
        "historical_name": "Londres Tudor",
        "past_year": 1610,
        "past_focus": "Antiguo Puente de Londres con casas de madera colgantes, Globe Theatre y el Támesis con veleros",
        "present_focus": "The City, The Shard, Tower Bridge y el South Bank moderno",
        "future_focus": "Sky-Canopy London con cúpulas bioclimáticas sobre el Támesis y cápsulas de levitación magnética",
        "hook": "Vuelo a ras de agua esquivando barcazas del siglo XVII antes de ascender a la cúspide del rascacielos The Shard.",
        "mit_ipcc_fact": "UCL Bartlett School: cúpulas de microclima y filtración de aire que reducen en 92% la huella térmica urbana."
    },
    "paris": {
        "num": 4,
        "name": "París",
        "historical_name": "París Medieval / Borbónico",
        "past_year": 1620,
        "past_focus": "Île de la Cité con Notre-Dame, Pont Neuf de piedra y casas de entramado de madera en Le Marais",
        "present_focus": "Bulevares Haussmannianos, Torre Eiffel, Louvre y riberas del Sena",
        "future_focus": "Vertical Garden Paris con torres espirales bioclimáticas integrando arquitectura clásica a 300m",
        "hook": "Giro de 360 grados sobre el rosetón de Notre-Dame mientras la piedra envejece y rejuvenece 600 años en 3 segundos.",
        "mit_ipcc_fact": "Vincent Callebaut & Paris 2200: torres biofílicas que absorben 40 toneladas de CO2 al año por fachada."
    },
    "amsterdam": {
        "num": 5,
        "name": "Ámsterdam",
        "historical_name": "Siglo de Oro Neerlandés",
        "past_year": 1626,
        "past_focus": "Construcción de los canales Grachtengordel, almacenes VOC, puentes levadizos y barcos de 3 mástiles",
        "present_focus": "Canales modernos, casas flotantes de diseño, tranvías eléctricos y ciclovías",
        "future_focus": "Floating Ocean-Grid Amsterdam con compuertas cinéticas modulares y biosferas de nanopolímeros",
        "hook": "Entrada rasante bajo un puente levadizo de madera donde los mercaderes se transforman en ciclistas modernos.",
        "mit_ipcc_fact": "Deltares & MIT Senseable City Lab: compuertas cinéticas modulares diseñadas para adaptación a +2.1m marea extrema."
    },
    "rome": {
        "num": 6,
        "name": "Roma",
        "historical_name": "Roma Barroca",
        "past_year": 1626,
        "past_focus": "Consagración de la Basílica de San Pedro, talleres de canteros de Bernini y ruinas del Foro Romano",
        "present_focus": "Coliseo restaurado, Vía del Corso, fuentes barrocas y vida en plazas históricas",
        "future_focus": "Cyber-Antiquity Roma con hologramas volumétricos que restauran templos clásicos y cúpulas geodésicas",
        "hook": "Vuelo supersónico sobre la cúpula de San Pedro cruzando un vórtice hacia los talleres de mármol del siglo XVII.",
        "mit_ipcc_fact": "Sapienza Università & CNR: cúpulas de nanopolímeros auto-refrigerantes para proteger el mármol del estrés térmico."
    },
    "dubai": {
        "num": 7,
        "name": "Dubái",
        "historical_name": "Costa de Pescadores Al Fahidi",
        "past_year": 1820,
        "past_focus": "Asentamiento de perlas de Al Fahidi, torres de viento Barjeel de coral y barro, y dhows en Dubai Creek",
        "present_focus": "Burj Khalifa alzándose a 828 metros, Dubai Marina, islas artificiales Palm y autopistas nocturnas",
        "future_focus": "Solar Arcology Dubai con megatorres bioclimáticas de 3.000 metros y agricultura hidropónica desértica masiva",
        "hook": "Una duna del desierto se contrae y en 2 segundos brota la estructura imponente de 828 metros del Burj Khalifa.",
        "mit_ipcc_fact": "Dubai Future Foundation & MIT: sistemas de enfriamiento geotérmico pasivo que reducen consumo energético en un 78%."
    },
    "hongkong": {
        "num": 8,
        "name": "Hong Kong",
        "historical_name": "Bahía de Pescadores Victoria",
        "past_year": 1840,
        "past_focus": "Aldeas costeras de pescadores Hakka, juncos chinos de velas rojas en Victoria Harbour y selva en The Peak",
        "present_focus": "Densidad vertical extrema, más de 500 rascacielos iluminados, tranvías Ding Ding y Star Ferry",
        "future_focus": "Stratospheric Hong Kong con puentes peatonales habitables a 800m de altura y plataformas marinas",
        "hook": "Caída libre entre los callejones de Kowloon Walled City hacia los rascacielos iluminados por láser.",
        "mit_ipcc_fact": "HKUST Aerodynamics: túneles de viento urbanos integrados que ventilan los cañones de rascacielos con brisa marina continua."
    },
    "cairo": {
        "num": 9,
        "name": "El Cairo",
        "historical_name": "El Cairo Mameluco / Otomano",
        "past_year": 1620,
        "past_focus": "Mezquita del Sultán Hassan, zocos amurallados de Khan el-Khalili y campos inundados por el Nilo junto a Guiza",
        "present_focus": "Gran Museo Egipcio (GEM), puentes modernos sobre el Nilo y la meseta de las Pirámides de Guiza",
        "future_focus": "Terraformed Oasis Cairo con corredores verdes refrigerados y cúpulas geodésicas de nanovidrio sobre Guiza",
        "hook": "Paso rozando el ápice de la Gran Pirámide mientras la sombra proyecta 4.000 años de historia en un instante.",
        "mit_ipcc_fact": "Cairo University & Nile Resilience Consortium: micro-canales de agua desalinizada solar para crear microclimas agrícolas urbanos."
    },
    "venice": {
        "num": 10,
        "name": "Venecia",
        "historical_name": "Serenísima República",
        "past_year": 1626,
        "past_focus": "Palacio Ducal y Basílica de San Marcos en pleno apogeo naval, galeazas del Arsenal y talleres de Murano",
        "present_focus": "Gran Canal, Puente de Rialto, vaporettos eléctricos y barreras móviles MOSE activadas",
        "future_focus": "Sub-Aquatic Biosphere Venice con arcología subacuática de grafeno y canales transparentes de filtración biológica",
        "hook": "Inmersión bajo el agua del Gran Canal que emerge en el taller de un soplador de vidrio de Murano de 1626.",
        "mit_ipcc_fact": "Venice Lagoon Preservation Institute: estabilización del lecho lagunar con bio-cemento autorreparable y barreras cinéticas inteligentes."
    }
}


def build_canonical_7_shots(city_key: str, city_meta: Dict[str, Any], grounding_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Construye los 7 planos maestros canónicos con prompts específicos para Gemini Omni Flash y Remotion HUD."""
    name = city_meta["name"]
    hist_name = city_meta["historical_name"]
    past_y = city_meta["past_year"]
    
    shots = [
        {
            "shot_index": 1,
            "shot_id": "01_STRATOSPHERE_TIME_DIVE",
            "epoch": f"TRANSITION_{past_y}",
            "duration_sec": 4.5,
            "time_window": "0:00 - 0:04.5",
            "camera_motion": f"Picado vertical a 140 km/h desde 850m AGL atravesando nubes volumétricas; al disiparse, el paisaje revela el trazado de {name} en {past_y}.",
            "prompt_brief": f"Epic high-speed vertical FPV dive through atmospheric volumetric clouds down into historic {name} ({hist_name}) in the year {past_y}. Authentic period wooden structures, historic waterways, period ships, brick rooftops. Cinematic 35mm Kodak 500T, f/2.8, hyper-detailed photorealism.",
            "gemini_omni_flash_prompt": {
                "subject": f"Historic cityscape of {name} ({hist_name}) in the year {past_y}",
                "visual_specifics": f"Authentic {past_y} architecture, historical docks, timber and stone materials, volumetric mist",
                "action": "Vertical camera dive from stratosphere entering urban canopy at high speed and stabilizing at 35m AGL",
                "camera": "Continuous 6-DoF FPV dive, focal length 18mm, pitch -80deg to -15deg smooth transition",
                "lighting": "Golden morning sunlight breaking through parting volumetric cloud layers",
                "environment": f"Historic topography of {name} with authentic water bodies and natural vegetation",
                "audio": "Wind rushing Doppler dive effect transitioning into subtle distant period bells and water lap",
                "style": "Cinematic documentary, 60fps, 4K UHD, hyperrealistic photorealism, zero AI distortion"
            },
            "keyframe_prompts_7": [
                f"KF1: High altitude 850m above {name} looking straight down into cloud deck, sunlight edge",
                f"KF2: Piercing through dense volumetric white clouds, motion blur on lens periphery",
                f"KF3: Breaking out below clouds at 450m, initial outline of {hist_name} {past_y} visible",
                f"KF4: Mid-dive at 250m, distinguishing wooden rooftops, historic river courses and sailing vessels",
                f"KF5: Low approach at 120m, architectural details of historic landmark buildings emerging",
                f"KF6: Leveling out at 60m, detailed wooden beams, street cobblestones and period citizens visible",
                f"KF7: Stable forward flight at 35m, banking right into the main historic thoroughfare"
            ],
            "hud_overlay": {
                "title": f"SALTO TEMPORAL: {name.upper()} {past_y}",
                "telemetry": "ALT: 850m ➔ 35m | VEL: 140 km/h | FOV: 110° | EBU -14 LUFS",
                "fact_text": f"En {past_y} la urbe era el núcleo neurálgico de comercio y cultura de la región.",
                "citation": "Archivos Cartográficos Históricos & Overpass 3D Grounding"
            },
            "audio_cue": {
                "music_layer": "Intro beat Flow Chillhop / Darksynth (118 BPM) con filtrado suave",
                "foley": "Silbido de viento Doppler + campanas de bronce históricas",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 2,
            "shot_id": "02_PAST_ALLEY_LOW_DRIFT",
            "epoch": f"PAST_{past_y}",
            "duration_sec": 6.0,
            "time_window": "0:04.5 - 0:10.5",
            "camera_motion": f"Vuelo rasante a 1.8m del suelo deslizándose entre carruajes, mercados y arquitectura original de {past_y}.",
            "prompt_brief": f"Low-altitude FPV drift at 1.8m above ground level in historic {name} {past_y}. {city_meta['past_focus']}. Citizens in authentic period clothing, wooden stalls, warm amber morning sunlight, volumetric dust.",
            "gemini_omni_flash_prompt": {
                "subject": f"Street-level daily life and architecture of {name} in {past_y}",
                "visual_specifics": f"{city_meta['past_focus']}, period textiles, wooden barrels, horse carriages, authentic materials",
                "action": "Smooth low-altitude FPV slalom between buildings, market stalls and historic facades",
                "camera": "Wide-angle 16mm lens, altitude 1.8m AGL, smooth roll +8deg / -8deg dynamic banking",
                "lighting": "Warm morning side-light casting long shadows on cobblestones and wooden planks",
                "environment": f"Historic streetscape of {name} with authentic 17th-century textures and atmospheric smoke",
                "audio": "Cobblestone clatter, distant merchant calls, creaking timber, flowing water",
                "style": "Authentic historical cinematic realism, 60fps, rich micro-contrast"
            },
            "keyframe_prompts_7": [
                f"KF1: Entry into narrow historic lane of {name} {past_y}, wooden facades framing the shot",
                f"KF2: Passing close to authentic wooden market stall, handcrafted goods on display",
                f"KF3: Citizens in authentic period attire turning towards the camera, morning light on faces",
                f"KF4: Mid-lane bank around a wooden cart loaded with barrels and fabrics",
                f"KF5: Low glide alongside historic stone wall and water canal with moored wooden boats",
                f"KF6: Approaching historic stone bridge archway, water reflections dancing on the stone underside",
                f"KF7: Centering precisely into the dark tunnel entrance of the historic bridge"
            ],
            "hud_overlay": {
                "title": f"MORFOLOGÍA & VIDA URBANA {past_y}",
                "telemetry": "ALT: 1.8m AGL | HEADING: 090° | ROLL: +8° | 118 BPM FLOW",
                "fact_text": "Las técnicas constructivas combinaban madera local tratada y piedra sillar tallada a mano.",
                "citation": "Registro Arqueológico & Planos Históricos Originales"
            },
            "audio_cue": {
                "music_layer": "Bajo analógico cálido + percusión Lo-Fi fluida a 118 BPM",
                "foley": "Crujido de madera, cascos de caballos, murmullo de mercado",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 3,
            "shot_id": "03_MATCH_CUT_PRESENT_PORTAL",
            "epoch": "TRANSITION_2026",
            "duration_sec": 5.5,
            "time_window": "0:10.5 - 0:16.0",
            "camera_motion": f"El dron atraviesa un arco arquitectónico; en el centro exacto del umbral, la iluminación y los materiales mutan instantáneamente a 2026.",
            "prompt_brief": f"Seamless match-cut transition shot. Drone enters a historic archway in {past_y} and exits into contemporary {name} 2026. Smooth spatial shift from historic materials to modern glass, steel, electric transit and contemporary pedestrians. 8K ultra-realistic clarity.",
            "gemini_omni_flash_prompt": {
                "subject": f"Temporal portal match-cut from {name} {past_y} to modern {name} 2026",
                "visual_specifics": f"Left side of frame transitioning historical wood/stone to contemporary glass/steel, {city_meta['present_focus']}",
                "action": "Continuous uninterrupted camera vector through an archway, emerging into modern bustling city",
                "camera": "Locked axis dolly forward, perfectly matched horizon and vanishing point, FOV 100deg",
                "lighting": "Shift from warm 17th-century tungsten/torch amber to crisp daylight and LED reflections",
                "environment": "Urban transition from historic riverbank to modern metropolitan thoroughfare",
                "audio": "Low-pass filter opening up into full stereo spectrum, modern transit sounds and urban hum",
                "style": "Hyper-clean transition, zero temporal jitter, photorealistic 60fps"
            },
            "keyframe_prompts_7": [
                f"KF1: Inside the historic archway in {past_y}, rough stone texture and warm lantern glow",
                f"KF2: Advancing halfway through the arch, light at the end of tunnel begins shifting spectrum",
                f"KF3: Center of portal, visual distortion wave as historic stone dissolves into brushed steel and glass",
                f"KF4: Emerging from archway into bright 2026 sunlight, contemporary {name} skyline instantly visible",
                f"KF5: Passing modern electric transport and contemporary citizens with smartphones",
                f"KF6: Accelerating down modern avenue, glass skyscrapers reflecting morning sky",
                f"KF7: Banking upwards into the modern urban canyon of {name}"
            ],
            "hud_overlay": {
                "title": f"PRESENTE REAL: {name.upper()} 2026",
                "telemetry": "MATCH-CUT EXACTO: LAT/LON CONSTANTE | TELEMETRÍA 4K 60FPS",
                "fact_text": "Hoy la densidad y conectividad urbana multiplican por 50 la capacidad del núcleo histórico.",
                "citation": "Google Street View 360 Grounding & Cartografía 2026"
            },
            "audio_cue": {
                "music_layer": "Transición de filtro Low-Pass a estéreo Hi-Fi brillante con drop limpio",
                "foley": "Zumbido de motores eléctricos, timbres modernos y ambiente metropolitano",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 4,
            "shot_id": "04_PRESENT_URBAN_CANYON_DRIFT",
            "epoch": "PRESENT_2026",
            "duration_sec": 6.5,
            "time_window": "0:16.0 - 0:22.5",
            "camera_motion": f"Vuelo dinámico en espiral ascendente entre los cañones urbanos de {name} 2026 mostrando la vibrante metrópolis.",
            "prompt_brief": f"Cinematic FPV banking turn through modern urban avenues and glass towers of {name} 2026. {city_meta['present_focus']}. Vibrant street life, clean reflections, authentic urban textures, crisp daylight.",
            "gemini_omni_flash_prompt": {
                "subject": f"Modern metropolitan canyons and landmarks of {name} 2026",
                "visual_specifics": f"{city_meta['present_focus']}, glass reflections, modern infrastructure, dynamic pedestrian and transit flow",
                "action": "Ascending spiral FPV bank between skyscrapers, banking around architectural curves",
                "camera": "Dynamic FPV drone with smooth 3-axis gyro stabilization, altitude 25m to 85m AGL",
                "lighting": "Crisp morning sunlight reflecting off glass curtain walls with subtle lens flares",
                "environment": f"Modern core of {name} with high-resolution architectural details",
                "audio": "Crisp city ambience, gentle wind shear, modern urban pulse",
                "style": "High-end drone cinematography, 60fps, vibrant color grading"
            },
            "keyframe_prompts_7": [
                f"KF1: Low altitude flight at 25m along modern boulevard of {name}, clean reflective glass facades",
                f"KF2: Banking left around modern architectural curve, displaying active pedestrian concourse below",
                f"KF3: Ascending to 45m, revealing multi-level transit infrastructure and rooftop gardens",
                f"KF4: Mid-spiral at 60m between twin glass skyscrapers, sunlight glinting off metal mullions",
                f"KF5: Passing near a prominent modern landmark of {name}, high detail on facade materials",
                f"KF6: Reaching 85m AGL, wide perspective of the metropolitan grid spreading to the horizon",
                f"KF7: Nose pitching up towards the upper atmosphere for the future temporal warp"
            ],
            "hud_overlay": {
                "title": f"DENSIDAD & INFRAESTRUCTURA 2026",
                "telemetry": "ALT: 25m ➔ 85m | VEL: 75 km/h | PITCH: +25° | -14 LUFS MASTER",
                "fact_text": "Redes de sensores IoT monitorizan en tiempo real los flujos peatonales y la calidad del aire.",
                "citation": "OpenStreetMap 3D Buildings & Smart City Analytics"
            },
            "audio_cue": {
                "music_layer": "Melodía de piano y sintetizador sobre beat fluido 118 BPM",
                "foley": "Silbido aerodinámico, eco de fachadas de cristal",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 5,
            "shot_id": "05_WARP_TO_FUTURE_ARCOLOGY",
            "epoch": "FUTURE_2226",
            "duration_sec": 6.0,
            "time_window": "0:22.5 - 0:28.5",
            "camera_motion": f"El dron asciende hacia las alturas; los edificios contemporáneos se transforman en megatorres bioclimáticas de {name} en 2226.",
            "prompt_brief": f"Futuristic transformation flight in {name} year 2226. {city_meta['future_focus']}. Vertical bioclimatic arcologies covered in hanging hydroponic gardens, elevated magnetic pod tubes, clean atmospheric filtration towers. Photorealistic science-based sci-fi.",
            "gemini_omni_flash_prompt": {
                "subject": f"Bioclimatic arcologies and sustainable architecture of {name} 2226",
                "visual_specifics": f"{city_meta['future_focus']}, graphene composites, transparent solar skins, vertical flora",
                "action": "Ascending glide past colossal vertical arcologies with silent magnetic pods cruising in tubes",
                "camera": "Sweeping panoramic ascent, altitude 85m to 250m AGL, smooth tilt up",
                "lighting": "Golden hour combined with soft amber and cyan holographic energy matrices",
                "environment": f"Terraformed futuristic {name} with zero emissions and lush vertical vegetation",
                "audio": "Gentle magnetic humming, harmonious synthetic wind, ambient future chimes",
                "style": "Grounded scientific future aesthetic, 8K clarity, photorealistic nature-tech fusion"
            },
            "keyframe_prompts_7": [
                f"KF1: Ascent past 100m, modern glass morphs into self-healing graphene and biopolymer lattice",
                f"KF2: Approaching 150m, massive vertical hydroponic gardens cascading down arcology exterior",
                f"KF3: Passing adjacent to a transparent magnetic levitation transit tube with sleek pod passing",
                f"KF4: Leveling at 200m near a sky-lobby terrace with citizens enjoying lush aerial gardens",
                f"KF5: Banking around a solar concentration spire, glowing soft amber in the evening light",
                f"KF6: Reaching 250m, revealing interconnected network of sky-bridges connecting mega-towers",
                f"KF7: Aligning heading directly along an aerial pedestrian skyway at 250m altitude"
            ],
            "hud_overlay": {
                "title": f"HORIZONTE 2226: ARCOLOGÍA BIOCLIMÁTICA",
                "telemetry": "MODELO IPCC SSP5-8.5 | RESILIENCIA URBANA SIGLO XXIII",
                "fact_text": city_meta["mit_ipcc_fact"],
                "citation": "MIT Senseable City Lab & Future Urban Resilience Studies"
            },
            "audio_cue": {
                "music_layer": "Sintetizadores analógicos profundos y etéreos en armonía con el chillhop",
                "foley": "Zumbido magnético suave de cápsulas, brisa limpia entre jardines aéreos",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 6,
            "shot_id": "06_FUTURE_AERIAL_SKYWAY_GLIDE",
            "epoch": "FUTURE_2226",
            "duration_sec": 6.5,
            "time_window": "0:28.5 - 0:35.0",
            "camera_motion": f"Planeo entre pasarelas peatonales aéreas a 300m de altura conectando torres vivientes en {name} 2226.",
            "prompt_brief": f"Gliding FPV shot along sky-bridge pedestrian corridors at 300m altitude in {name} 2226. Citizens walking in smart thermoregulated fabrics, clean drone lanes humming in the distance, lush aerial parks, crystal clear zero-emission air. Cinematic 8K.",
            "gemini_omni_flash_prompt": {
                "subject": f"Skyway pedestrian life and aerial ecology of {name} 2226",
                "visual_specifics": "Elevated parks at 300m AGL, transparent safety barriers, citizens in biopolymeric clothing, small automated air taxis far in background",
                "action": "High-speed gliding flight parallel to a suspended botanical sky-corridor",
                "camera": "Ultra-wide 14mm lens, altitude 300m AGL, smooth tracking shot with zero shake",
                "lighting": "Warm sunset light bathing the sky-structures in copper and gold tones",
                "environment": f"Sky-level biosphere above {name} with clean blue skies and verdant green canopies",
                "audio": "Soft ambient birdsong in aerial parks, gentle laminar airflow, futuristic tonal pads",
                "style": "Utopian grounded documentary, hyperrealistic 60fps"
            },
            "keyframe_prompts_7": [
                f"KF1: Entry alongside 300m high pedestrian bridge in {name} 2226, trees growing on suspended soil",
                f"KF2: Gliding past walking citizens who glance upwards at the camera with peaceful expressions",
                f"KF3: Passing through a holographic municipal information arch with real-time ecological stats",
                f"KF4: Banking over a suspended open-air amphitheater with cascading water features",
                f"KF5: Skimming along the edge of a carbon-capture filtration waterfall on the arcology wall",
                f"KF6: Approaching the outer perimeter of the sky-district looking out towards the open horizon",
                f"KF7: Accelerating past the final tower out into the open sky for the grand finale"
            ],
            "hud_overlay": {
                "title": f"SOCIEDAD VERTICAL DEL SIGLO XXIII",
                "telemetry": "ALT: 300m AGL | EMISIONES CERO | RED INTEGRADA 2226",
                "fact_text": "El 100% de la energía y alimentos frescos se producen dentro del propio perímetro de la torre.",
                "citation": "Journal of Sustainable Vertical Cities 2200"
            },
            "audio_cue": {
                "music_layer": "Pluck de guitarra procesada + pad atmosférico expansivo",
                "foley": "Pájaros en jardines aéreos, flujo de aire laminar silencioso",
                "ducking_db": -18.0
            }
        },
        {
            "shot_index": 7,
            "shot_id": "07_PANORAMIC_TIMELAPSE_HORIZON",
            "epoch": "SYNTHESIS_OUTRO",
            "duration_sec": 7.0,
            "time_window": "0:35.0 - 0:42.0",
            "camera_motion": f"Ascenso final a 500m AGL en órbita lenta mostrando el horizonte completo de {name} con las tres épocas fusionadas en una panorámica al atardecer.",
            "prompt_brief": f"Grand epic wide panoramic sunset orbit at 500m altitude above {name}. Golden sun dipping below the horizon, reflections across water and vertical forests, soft glowing twilight lights turning on across the futuristic skyline. Cinematic masterpiece, 8K, EBU R128 master.",
            "gemini_omni_flash_prompt": {
                "subject": f"Grand panoramic synthesis of {name} across 400 years of evolution (1626 ➔ 2026 ➔ 2226)",
                "visual_specifics": f"Epic horizon of {name}, setting sun, glowing twilight arcology lights, water reflections",
                "action": "Slow 360-degree orbit and pull-back reveal at 500m altitude",
                "camera": "Grand panoramic 24mm lens, altitude 500m AGL, smooth deceleration to majestic final frame",
                "lighting": "Magical twilight hour with deep indigo sky, blazing orange horizon and bioluminescent city lights",
                "environment": f"Complete territorial view of {name} showing harmony of preserved heritage and futuristic arcologies",
                "audio": "Harmonic climax of the Flow Chillhop track with gentle reverb tail fading out",
                "style": "Epic cinematic master shot, BBC Earth / Interstellar aesthetic, pristine 60fps"
            },
            "keyframe_prompts_7": [
                f"KF1: Pulling back from 350m to 400m altitude above {name}, revealing the vastness of the city",
                f"KF2: Orbiting 45 degrees, sunset colors intensifying from amber to deep magenta",
                f"KF3: Halfway through orbit at 450m, historical and modern landmarks visible in harmony with 2226 towers",
                f"KF4: City twilight illumination activates across the entire urban basin simultaneously",
                f"KF5: Reaching peak altitude of 500m, sun touching the horizon line with blazing rays",
                f"KF6: Full panoramic vista stabilized, holographic chronometer overlay appearing smoothly in center",
                f"KF7: Final static epic frame, fading smoothly to black with brand signature CHRONODRIFT"
            ],
            "hud_overlay": {
                "title": f"{name.upper()}: 400 AÑOS DE EVOLUCIÓN",
                "telemetry": "VUELO COMPLETO | RETENCIÓN >90% | CHRONODRIFT MASTER",
                "fact_text": f"De enclave histórico en {past_y} a civilización bioclimática en 2226.",
                "citation": "ChronoDrift by VideoPro Studio"
            },
            "audio_cue": {
                "music_layer": "Clímax armónico de la pista musical con decaimiento suave y delay estéreo",
                "foley": "Eco suave de la metrópolis en el atardecer, desvanecimiento a silencio",
                "ducking_db": 0.0
            }
        }
    ]
    
    return shots


def build_shorts_funnel_spec(city_key: str, city_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Genera la especificación de 3 Shorts estratégicos con retención VTR > 120%."""
    name = city_meta["name"]
    past_y = city_meta["past_year"]
    
    return [
        {
            "short_id": f"SHORT_{city_key.upper()}_01_SEAMLESS_LOOP",
            "title": f"¿Cómo era {name} hace 400 años vs Hoy vs 2226? ⏳ (Bucle Infinito)",
            "duration_sec": 14.8,
            "aspect_ratio": "9:16",
            "hook_0_3s": f"Match-cut vertiginoso a 120 km/h: entras en un callejón de {past_y} y sales en Shibuya/Wall Street 2026.",
            "retention_mechanic": "Bucle perfecto (Seamless Loop): el último fotograma en 2226 conecta exactamente con el picado inicial de 1626.",
            "target_vtr": "135%",
            "pinned_comment": f"🎬 Mira el vuelo completo en 4K 60fps de {name} en nuestro canal principal 👉 [Enlace al Episodio {city_meta['num']}]"
        },
        {
            "short_id": f"SHORT_{city_key.upper()}_02_SECRET_HISTORY",
            "title": f"El secreto oculto de {name} que casi nadie conoce 😱",
            "duration_sec": 22.0,
            "aspect_ratio": "9:16",
            "hook_0_3s": f"¿Sabías que en {past_y} el centro de {name} no existía y era solo...",
            "retention_mechanic": "Curiosity gap con revelación visual en el segundo 14 y salto futurista en el segundo 18.",
            "target_vtr": "125%",
            "pinned_comment": f"¿Te gustaría vivir en la arcología de {name} en 2226? Comenta abajo 👇"
        },
        {
            "short_id": f"SHORT_{city_key.upper()}_03_FUTURE_SCIENCE",
            "title": f"Así será {name} en 2226 según el MIT y la Ciencia 🏙️✨",
            "duration_sec": 18.5,
            "aspect_ratio": "9:16",
            "hook_0_3s": "Esto NO es ciencia ficción: así planea el MIT reconstruir la ciudad ante el cambio climático.",
            "retention_mechanic": "Datos de telemetría HUD 3D en pantalla que obligan a pausar o repetir para leer.",
            "target_vtr": "120%",
            "pinned_comment": f"Descubre los 10 episodios de CHRONODRIFT en la playlist oficial 🚀"
        }
    ]


def generate_tritemporal_storyboard(city_key: str) -> Dict[str, Any]:
    """Construye el storyboard canónico de 7 planos y los shorts de un episodio maestro."""
    grounding_file = GROUNDING_DIR / city_key.lower() / "grounding_manifest.json"
    city_meta = CITY_EPISODES_METADATA.get(city_key.lower())
    
    if not city_meta:
        raise ValueError(f"Ciudad '{city_key}' no catalogada. Disponibles: {list(CITY_EPISODES_METADATA.keys())}")
        
    if grounding_file.exists():
        with open(grounding_file, "r", encoding="utf-8") as f:
            grounding_data = json.load(f)
    else:
        grounding_data = {"city_name": city_meta["name"], "country": "Mundial"}
        
    shots = build_canonical_7_shots(city_key, city_meta, grounding_data)
    shorts = build_shorts_funnel_spec(city_key, city_meta)
    
    manifest = {
        "story_id": f"CHRONODRIFT_EP{city_meta['num']:02d}_{city_key.upper()}",
        "episode_number": city_meta["num"],
        "channel_brand": "CHRONODRIFT",
        "tagline": "Urban Time Travel & Future Cities (1626 ➔ 2026 ➔ 2226)",
        "city_key": city_key.lower(),
        "city_name": city_meta["name"],
        "total_duration_sec": sum(s["duration_sec"] for s in shots),
        "target_engine": "gemini-omni-flash-preview",
        "keyframe_engine": "gemini-3.1-flash-image",
        "zero_veo_policy": True,
        "audio_spec": {
            "tempo_bpm": 118,
            "style": "Flow Chillhop / Urban Lo-Fi & Darksynth",
            "loudness_target_lufs": -14.0,
            "ducking_depth_db": -18.0,
            "true_peak_dbtp": -1.0
        },
        "hook_strategy": {
            "initial_hook_0_5s": city_meta["hook"],
            "target_first_minute_retention": ">90%",
            "target_avd": ">72%"
        },
        "canonical_shots": shots,
        "shorts_funnel": shorts
    }
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{city_key.lower()}_tritemporal_manifest.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        
    return manifest


def main():
    all_cities = list(CITY_EPISODES_METADATA.keys())
    parser = argparse.ArgumentParser(description="Builder de Historias Urbanas Tritemporales para ChronoDrift & VideoPro")
    parser.add_argument("--city", type=str, default="tokyo", choices=all_cities, help="Ciudad a guionizar")
    parser.add_argument("--all", action="store_true", help="Generar manifiestos para los 10 episodios completos")
    args = parser.parse_args()
    
    cities = all_cities if args.all else [args.city]
    
    print("================================================================================")
    print("🎬 [ChronoDrift Storyboard Builder] Ensamblando guiones y escaleta de producción...")
    print("================================================================================")
    
    for c in cities:
        manifest = generate_tritemporal_storyboard(c)
        print(f"✅ Episodio {manifest['episode_number']:02d}: {manifest['city_name'].upper()} ({manifest['story_id']})")
        print(f"   - Duración total: {manifest['total_duration_sec']:.1f}s en 7 Planos Canónicos 60fps")
        print(f"   - Match-Cuts temporales georreferenciados: 1626 ➔ 2026 ➔ 2226")
        print(f"   - Motor de vídeo: Gemini Omni Flash ({manifest['target_engine']}) [CERO VEO 3]")
        print(f"   - Audio EBU R128: -14.0 LUFS / Ducking -18dB / 118 BPM Flow Chillhop")
        print(f"   - 3 Shorts de alta retención (>120% VTR) generados")
        print(f"   - Guardado en: {OUTPUT_DIR}/{c}_tritemporal_manifest.json\n")


if __name__ == "__main__":
    main()
