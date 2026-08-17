#!/usr/bin/env python3
"""
Generator and Validator for 120-second Master Documentary Manifest & Escaleta with 7-Layer DOP Prompts.
"""

import json
import os

manifest_data = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "project_id": "2026-08-17_documental-umbral-cuantico-120s",
    "title": "El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano",
    "english_title": "The Quantum Threshold: The Silent Silicon Revolution and the Fate of Species",
    "slug": "documental-umbral-cuantico-120s",
    "version": "v1.0-Master4K",
    "created_at": "2026-08-17T02:30:00Z",
    "total_duration_seconds": 120.0,
    "total_shots_count": 24,
    "shot_duration_seconds": 5.0,
    "framerate_fps": 24,
    "aspect_ratio": "16:9",
    "resolution": {"width": 3840, "height": 2160, "standard": "4K UHD Cinema"},
    "metadata": {
        "genre": "Premium Factual Science & Deep Tech Documentary",
        "style_influences": ["BBC Earth / Horizon", "Vox / Johnny Harris Deep Dive", "Interstellar Cinematography"],
        "narrative_framework": "BBC 3-Act Exponential Escalation",
        "color_pipeline": "Kodak Vision3 500T 5219 / ARRI Alexa 65 LogC",
        "shutter_angle": "180 degrees (1/48s exposure)",
        "audio_standards": {
            "target_loudness_lufs": -14.0,
            "true_peak_dbtp": -1.0,
            "dynamic_range_dr": 14.5,
            "ducking_depth_db": -18.0,
            "sub_bass_monozygosity_cutoff_hz": 80,
            "crossfeed_model": "Bauer / Meier Binaural HRTF"
        },
        "voiceover": {
            "speaker_engine": "VibeVoice 1.5B Local Neural TTS",
            "voice_profile": "es-emilio (Castilian Spanish / Solemn Factual Tone)",
            "total_word_count": 298,
            "speaking_rate_wpm": 149
        }
    },
    "acts_structure": [
        {
            "act_index": 1,
            "act_title": "Acto I: La Grieta en la Realidad",
            "time_window": "00:00 - 00:30",
            "shots_range": "Tomas 01 a 06",
            "dramatic_function": "Gancho sensorial inmediato (0-3s), ruptura de paradigmas físicos y establecimiento de la premisa de escala global."
        },
        {
            "act_index": 2,
            "act_title": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:30 - 01:30",
            "shots_range": "Tomas 07 a 18",
            "dramatic_function": "Despliegue de ramificaciones geopolíticas, científicas y energéticas; aceleración del montaje e intensificación del conflicto existencial."
        },
        {
            "act_index": 3,
            "act_title": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:30 - 02:00",
            "shots_range": "Tomas 19 a 24",
            "dramatic_function": "Perspectiva planetaria orbital, reconciliación bio-tecnológica, clímax sonoro orquestal y cierre filosófico imborrable."
        }
    ],
    "shots": [
        {
            "shot_index": 1,
            "shot_id": "SHOT_01_QUANTUM_CRYOSTAT_DIVE",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:00 - 00:05",
            "duration_sec": 5.0,
            "hook_category": "Sensory & Conceptual Hook (0-3s Initial Shock)",
            "narration_es": "En este instante, a doscientos setenta y tres grados bajo cero...",
            "narration_word_count": 11,
            "hud_overlay_telemetry": {
                "location": "Laboratorio Subterráneo Gran Sasso, Italia",
                "timestamp_code": "00:00:00:00",
                "telemetry": "TEMP: 10.2 mK | VACUUM: 10^-9 mbar | COHERENCE: 99.98% | LENS: Cooke 25mm Anamorphic T2.3",
                "lower_third": "FÍSICA CUÁNTICA EXPERIMENTAL — DILUCIÓN CRIOGÉNICA"
            },
            "camera_movement_6dof": {
                "type": "Steadicam Z-axis Push-in with Micro-Descent",
                "vector_translation": "Forward +1.2m, Downward -0.3m, Lateral 0.0m",
                "rotation_euler": "Pitch -8deg, Yaw 0deg, Roll 0deg",
                "cadence": "24fps, organic human inertia, 180-degree shutter"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Superconducting quantum processor core suspended inside a gold-plated chandelier dilution cryostat, intricate interwoven coaxial copper and niobium cables with brushed metallic patina, microscopic frost crystal condensation at the outer chamber edges.",
                "layer_2_environment": "Extreme close foreground showing out-of-focus brass support rods; midground housing the glistening gold thermal stages; deep background falling into the dark blue cavernous laboratory with subtle nitrogen mist drifting across the frame.",
                "layer_3_lighting_kelvin": "High-contrast 6:1 Chiaroscuro. 3200K warm halogen rim light grazing the gold and copper coils, contrasted against a 6500K deep cyan fill light illuminating the background vapor.",
                "layer_4_optics_lens": "Cooke Anamorphic /i Full Frame Plus 25mm T2.3 lens at T2.3, extreme shallow depth of field, creamy horizontal oval bokeh, subtle barrel distortion and gentle cyan flare streaks.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219 35mm film emulation, organic fine silver-halide grain in dark tones, warm reddish halation roll-off around metallic specular highlights, ARRI LogC tonal curve.",
                "layer_6_camera_dynamics": "Slow, buttery-smooth forward dolly push at 24fps with organic fluid drag, gliding from 0.8m to 0.2m distance from the golden core.",
                "layer_7_acoustic_foley": "\"Deep resonant low-frequency sub-bass hum at 38Hz, subtle rhythmic pulse of the cryogenic pulse-tube compressor, microscopic metallic ping of thermal contraction\""
            },
            "master_prompt_dop_7layer": "A slow cinematic Steadicam push-in toward the gleaming gold-plated core of a quantum dilution refrigerator at 10 millikelvin. In the midground, intricate bundles of braided copper and superconducting niobium cables descend through circular golden thermal shields, with realistic metallic micro-scratches and delicate cryogenic frost crystals. Out-of-focus foreground brass framing rods create optical depth, while the cavernous deep-blue subterranean lab recedes into darkness with soft nitrogen haze. 6:1 Chiaroscuro lighting with 3200K warm tungsten rim grazing the gold coils against 6500K cold cyan ambient fill. Shot on ARRI Alexa 65 with Cooke Anamorphic /i 25mm T2.3 lens at f/2.0, creamy oval bokeh, subtle horizontal anamorphic flare, Kodak Vision3 500T 5219 film stock, organic chemical grain, rich halation on highlights, natural camera inertia at 24fps. Ambient audio: \"deep resonant 38Hz cryostat drone, rhythmic pulse-tube compression, faint metallic expansion ticks\"."
        },
        {
            "shot_index": 2,
            "shot_id": "SHOT_02_PHYSICIST_EYE_PUPIL_REFLECTION",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:05 - 00:10",
            "duration_sec": 5.0,
            "hook_category": "Human Emotion & Tension Reveal",
            "narration_es": "...la física clásica acaba de romperse para siempre.",
            "narration_word_count": 8,
            "hud_overlay_telemetry": {
                "location": "Puesto de Control Cryo-Q, Gran Sasso",
                "timestamp_code": "00:00:05:00",
                "telemetry": "DECOHERENCE TIME: INFINITE | PHI_CORRELATION: 1.0000 | LENS: Panavision 85mm T1.4",
                "lower_third": "DRA. ELENA VANCE — DIRECTORA DE INVESTIGACIÓN CUÁNTICA"
            },
            "camera_movement_6dof": {
                "type": "Slow Macro Drift with Gentle Focus Pull",
                "vector_translation": "Lateral Track Right +0.15m, Forward +0.3m",
                "rotation_euler": "Pitch 0deg, Yaw -3deg, Roll 0deg",
                "cadence": "24fps, organic human breathing motion"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Macro close-up on the face and intense hazel-green eye of a 38-year-old female quantum physicist, genuine human skin texture with visible micro-pores, fine crow's feet wrinkles, subtle perspiration on the temple, involuntary pupil dilation reflecting green-and-white quantum interference wave functions.",
                "layer_2_environment": "Foreground eye and eyelashes in razor-sharp focus; midground cheekbone and lab coat collar softly falling off; background shows blurred dual-screen telemetry monitors glowing with cascading logarithmic data matrices.",
                "layer_3_lighting_kelvin": "Motivated key light from monitor screens at 5400K daylight-white casting soft specular reflections across the cornea, complemented by a warm 2800K desk lamp rim light on her dark hair.",
                "layer_4_optics_lens": "Panavision Primo 70 85mm T1.4 Macro lens at T1.4, razor-thin depth of field, exquisite circular bokeh on background LED indicator clusters, zero digital edge sharpening.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207 film stock, realistic skin subsurface scattering (SSS) with warm epidermal undertones, rich shadow density without digital noise clipping.",
                "layer_6_camera_dynamics": "Imperceptible handheld floating camera breathing at 24fps, tracking micro-tremor in her gaze as the telemetry confirms the quantum breakthrough.",
                "layer_7_acoustic_foley": "\"Soft human inhalation intake of breath, faint high-frequency data chime on the terminal, distant air filtration whisper\""
            },
            "master_prompt_dop_7layer": "Intimate macro close-up of a female quantum physicist's eye in a dark laboratory, her dilated pupil sharply reflecting green and white quantum telemetry wave graphs. Authentic human skin texture with detailed pores, micro-creases, fine eyelashes, and natural subsurface scattering. Foreground eye in tack-sharp focus with shallow focus falloff across her cheek and hair. Background reveals soft bokeh discs from glowing computer server indicators. Key lighting motivated by 5400K terminal screen glow with 2800K warm tungsten edge light on her hairline. Shot on ARRI Alexa 65 with Panavision Primo 70 85mm T1.4 macro lens, creamy focus falloff, organic Kodak Vision3 250D 35mm grain, gentle highlight halation. Smooth subtle handheld breathing inertia at 24fps. Ambient audio: \"soft caught breath, quiet mechanical keyboard click, gentle hum of cleanroom ventilation\"."
        },
        {
            "shot_index": 3,
            "shot_id": "SHOT_03_UNDERGROUND_CAVERN_WIDE",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:10 - 00:15",
            "duration_sec": 5.0,
            "hook_category": "Monumental Scale & Isolation",
            "narration_es": "A mil cuatrocientos metros bajo roca viva, el silencio oculta la mayor revolución de la historia.",
            "narration_word_count": 16,
            "hud_overlay_telemetry": {
                "location": "Túnel Hall C, Laboratorio Nazionale del Gran Sasso, Italia",
                "timestamp_code": "00:00:10:00",
                "telemetry": "DEPTH: 1,400m ROCK OVERBURDEN | COSMIC RAY SHIELDING: 10^6 | LENS: Arri Master Prime 18mm",
                "lower_third": "ESCUDO GEOLÓGICO CONTRA RADIACIÓN CÓSMICA"
            },
            "camera_movement_6dof": {
                "type": "Wide TechnoCrane Jib Up and Forward Arc",
                "vector_translation": "Vertical Lift +2.5m, Forward +4.0m",
                "rotation_euler": "Pitch -15deg tilting up to -5deg",
                "cadence": "24fps, cinematic fluid crane boom"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A solitary scientist in an anti-static blue cleanroom suit walking on a raised metal grated catwalk, dwarfed by towering 15-meter hemispherical stainless steel cryo-tanks and lead shielding vaults.",
                "layer_2_environment": "Massive vaulted subterranean limestone rock cavern with rough textured rock bolted ceiling; overhead cable bridges, suspended LED industrial lighting gantries, faint atmospheric thermal dust motes caught in light beams.",
                "layer_3_lighting_kelvin": "4500K neutral industrial LED arrays illuminating the catwalk, contrasted with deep 3000K amber sodium safety lights in the perimeter tunnels and intense 6000K xenon floodlights washing the stainless steel vessel.",
                "layer_4_optics_lens": "ARRI Master Prime 18mm T1.3 wide-angle lens, rectilinear geometry with zero fisheye distortion, razor-sharp edge-to-edge definition, immense hyperfocal depth.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, deep rich blacks in unlit cavern crevices, wide 15-stop dynamic range preserving details in gleaming steel highlights and shadowy rock fissures.",
                "layer_6_camera_dynamics": "Sweeping cinematic TechnoCrane boom descending from high cavern ceiling down toward the catwalk at 24fps with majestic architectural parallax.",
                "layer_7_acoustic_foley": "\"Cavernous acoustic reverberation, distant metal footstep clanking on grated floor, deep low-frequency ventilation rumble\""
            },
            "master_prompt_dop_7layer": "Epic wide-angle TechnoCrane shot of a colossal subterranean research cavern 1400 meters under mountain bedrock. A tiny scientist in a navy cleanroom suit walks along an elevated steel catwalk between monolithic stainless steel cryotanks and lead-shielded vessels. Raw limestone cavern walls with steel rock-bolts arc overhead into towering darkness. Industrial lighting mix: 4500K clean white overhead work lights, 3000K warm amber tunnel markers, and cool 6000K floodlights reflecting off brushed cylindrical metal tanks. Volumetric atmospheric haze drifting under light cones. Shot on ARRI Alexa 65 with ARRI Master Prime 18mm T1.3, rectilinear perspective, deep focus, Kodak Vision3 500T 35mm grain, 24fps smooth boom crane arc. Ambient audio: \"massive acoustic cavern reverb, rhythmic distant footsteps echoing on steel mesh, industrial airflow roar\"."
        },
        {
            "shot_index": 4,
            "shot_id": "SHOT_04_EUV_1NM_WAFER_MACRO",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:15 - 00:20",
            "duration_sec": 5.0,
            "hook_category": "Microscopic Alien Precision",
            "narration_es": "Un solo procesador atómico procesa en microsegundos lo que a la humanidad le tomaría milenios.",
            "narration_word_count": 15,
            "hud_overlay_telemetry": {
                "location": "Matriz de Silicio Cuántico Sub-Nanométrica",
                "timestamp_code": "00:00:15:00",
                "telemetry": "SCALE: 0.8nm | GATE SPEED: 1.2 THz | QUBIT DENSITY: 10^7/cm2 | LENS: Laowa 24mm Probe",
                "lower_third": "ARQUITECTURA TOPOLÓGICA DE QÚBITS MONOCRISTALINOS"
            },
            "camera_movement_6dof": {
                "type": "Borescope Probe Lens Glide through Micro-Architecture",
                "vector_translation": "Forward +0.8m at grazing 2mm clearance",
                "rotation_euler": "Roll +12deg slowly leveling, Pitch -5deg",
                "cadence": "24fps, high-precision microscopic motion"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Monocrystalline silicon wafer surface etched with 1-nanometer high-NA EUV lithography patterns, crystalline atomic lattices resembling a futuristic golden cyberpunk metropolis at microscopic scale, quantum dot junctions glowing with faint coherent blue electroluminescence.",
                "layer_2_environment": "Foreground grazing microscopic silicon ridges with iridescent prismatic diffraction; midground topological superconducting bus lanes; background shimmering with repeating fractal circuitry arrays.",
                "layer_3_lighting_kelvin": "Microscopic ring-light illumination at 5600K combined with dramatic 6500K deep ultraviolet side-lighting casting ultra-sharp micro-shadows across atomic trenches.",
                "layer_4_optics_lens": "Laowa 24mm T14 2X Macro Periprobe lens, extreme depth of field through microscopic optics, optical diffraction spikes on laser reflections, zero chromatic fringing.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207, rich golden and iridescent cobalt-blue tones, high micro-contrast across semiconductor metallic layers.",
                "layer_6_camera_dynamics": "Continuous ultra-smooth probe lens tracking shot skimming 2 millimeters above the wafer silicon surface at 24fps.",
                "layer_7_acoustic_foley": "\"Microscopic high-frequency electrical ionization static, oscillating resonant crystal sine tone, rhythmic laser pulse click\""
            },
            "master_prompt_dop_7layer": "Microscopic probe lens flyover skimming 2mm above a 1-nanometer quantum silicon wafer surface. Ultra-detailed etched nanostructures form an intricate golden topological circuit grid resembling a microscopic alien metropolis, with quantum dot nodes emitting faint coherent blue-violet luminescence. Razor-sharp optical refraction and iridescent diffraction grating colors across metallic silicon ridges. 5600K surgical key light with 6500K ultraviolet grazing edge light creating crisp micro-shadows in nanometer trenches. Shot on Laowa 24mm T14 2X Macro Probe on ARRI Alexa 65, deep macro depth, crisp optical micro-contrast, Kodak Vision3 250D color science, photochemical film grain, smooth linear tracking at 24fps. Ambient audio: \"subtle crystalline high-frequency hum, delicate static ionization sizzle, rhythmic micro-laser chirps\"."
        },
        {
            "shot_index": 5,
            "shot_id": "SHOT_05_IMMERSION_DATACENTER_FPV",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:20 - 00:25",
            "duration_sec": 5.0,
            "hook_category": "Technological Power & Fluid Immersion",
            "narration_es": "No es una máquina más rápida. Es una nueva forma de interrogar la realidad.",
            "narration_word_count": 14,
            "hud_overlay_telemetry": {
                "location": "Catedral de Cómputo Cuántico Líquido, Zúrich, Suiza",
                "timestamp_code": "00:00:20:00",
                "telemetry": "FLOW: 450 L/min FLUORINERT | OPTICAL I/O: 800 Tbps | LENS: Cooke Anamorphic 35mm",
                "lower_third": "REFRIGERACIÓN POR INMERSIÓN TOTAL DIELÉCTRICA"
            },
            "camera_movement_6dof": {
                "type": "Low-Angle FPV Glider Track through Server Alley",
                "vector_translation": "Forward +6.0m at 1.2m height, slight lateral weave",
                "rotation_euler": "Roll +4deg banking right, Pitch +2deg",
                "cadence": "24fps, high-speed smooth aerodynamic glide"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Transparent sealed immersion cooling tanks filled with crystal-clear non-conductive dielectric fluid, containing glowing quantum blade accelerators with submerged micro-bubbles rising rhythmically from hot heatsinks.",
                "layer_2_environment": "Endless corridor of industrial computing racks stretching 80 meters into the vanishing point, polished epoxy floor reflecting overhead linear LED lights, suspended stainless steel manifold pipes with insulated valves.",
                "layer_3_lighting_kelvin": "Sleek dual-color scheme: 4000K neutral white linear overhead strip lights contrasting with pulsating 4800K emerald green and deep sapphire blue server activity LEDs refracted through liquid tanks.",
                "layer_4_optics_lens": "Cooke Anamorphic /i Full Frame Plus 35mm T2.3, wide field of view, horizontal anamorphic flare streaks from server LEDs, gentle edge falloff.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich deep liquid refractions, deep saturated cyan-greens and dark shadows with zero digital compression artifacts.",
                "layer_6_camera_dynamics": "High-speed stabilized gimbal tracking shot rushing smoothly down the server aisle at 24fps with realistic physical inertia.",
                "layer_7_acoustic_foley": "\"Muffled bubbling sound of boiling fluorocarbon liquid, heavy low-frequency pump vibration, high-speed optical data whine\""
            },
            "master_prompt_dop_7layer": "Smooth high-speed tracking shot through a massive liquid immersion quantum datacenter aisle in Zurich. Transparent tanks on both sides are filled with boiling dielectric liquid where submerged computing blades glow with emerald and cobalt LED indicators, micro-bubbles rising along metallic copper heat exchangers. Highly polished reflective epoxy floor mirrors endless rows of server cabinets receding into distant darkness. Overhead 4000K architectural strip lighting balanced against vibrant 4800K cyan liquid refraction. Shot on ARRI Alexa 65 with Cooke Anamorphic 35mm T2.3, horizontal streak flares, rich liquid optical distortion, Kodak Vision3 500T 35mm film stock, organic chemical grain at 24fps. Ambient audio: \"submerged liquid bubbling, resonant fluid pump hum, dense rush of optical fiber switching data\"."
        },
        {
            "shot_index": 6,
            "shot_id": "SHOT_06_DUSK_MEGACITY_SUBMARINE_CABLES",
            "act": "Acto I: La Grieta en la Realidad",
            "time_window": "00:25 - 00:30",
            "duration_sec": 5.0,
            "hook_category": "Global Scale & Looming Shift",
            "narration_es": "Y el mundo exterior apenas comienza a percibir el temblor de su despertar.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Bahía de Tokio / Terminal de Enlaces Submarinos",
                "timestamp_code": "00:00:25:00",
                "telemetry": "LAT: 35.6762° N | LON: 139.6503° E | ALT: 250m ➔ 45m | LENS: Panavision 40mm Anamorphic",
                "lower_third": "INTERCONEXIÓN PLANETARIA DE FIBRA ÓPTICA COHERENTE"
            },
            "camera_movement_6dof": {
                "type": "Helicopter Cineflex Descent and Tilt Down",
                "vector_translation": "Descent -200m, Forward +80m across bay water",
                "rotation_euler": "Pitch -25deg tilting down to -60deg toward water surface",
                "cadence": "24fps, majestic cinematic gyro-stabilized flight"
            },
            "seven_layers_dop": {
                "layer_1_subject": "The sprawling nocturnal skyline of Tokyo at blue hour dusk with towering illuminated glass skyscrapers, while in the immediate foreground the dark waters of Tokyo Bay reveal underwater optical fiber landing stations glowing with pulsed laser telemetry.",
                "layer_2_environment": "Distant volcanic silhouette of Mount Fuji against a deep indigo and magenta sunset gradient; dense urban mist drifting between illuminated bridges; cargo container ships navigating illuminated shipping channels.",
                "layer_3_lighting_kelvin": "2700K warm sodium and amber skyline city lights contrasting dramatically against 7500K deep blue dusk sky and 6500K icy cyan underwater fiber beacons.",
                "layer_4_optics_lens": "Panavision C-Series 40mm Anamorphic T2.8 lens, classic anamorphic oval bokeh, gorgeous warm horizontal light flaring from harbor highway lamps.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich deep twilight blues, subtle halation around vehicle headlights and bridge suspension cables, wide dynamic range.",
                "layer_6_camera_dynamics": "Majestic slow gyro-stabilized aerial descent over Tokyo Bay at 24fps, sweeping forward with effortless cinematic scale.",
                "layer_7_acoustic_foley": "\"Distant urban drone of millions of vehicles, deep harbor horn blast, soft lapping of dark ocean waves\""
            },
            "master_prompt_dop_7layer": "Sweeping cinematic aerial descent over Tokyo Bay at twilight blue hour. The illuminated megacity skyline glows with millions of 2700K golden windows, highway arteries, and suspension bridge lights against a deep indigo sky with Mount Fuji's faint silhouette. In the foreground dark harbor waters, submerged optical fiber cable hubs pulse with coherent cyan light beneath the surface. Volumetric coastal mist rolls between skyscrapers. Shot on ARRI Alexa 65 with Panavision C-Series 40mm Anamorphic lens at T2.8, beautiful horizontal lens flares, oval bokeh discs on harbor lights, Kodak Vision3 500T film grain, smooth 24fps helicopter Cineflex motion. Ambient audio: \"distant urban roar, low harbor foghorn reverberation, gentle water lap on sea wall\"."
        },
        {
            "shot_index": 7,
            "shot_id": "SHOT_07_GENEVA_WAR_ROOM_RSA_CRACK",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:30 - 00:35",
            "duration_sec": 5.0,
            "hook_category": "Geopolitical Disruption & Institutional Panic",
            "narration_es": "En minutos, toda la criptografía que protegía el comercio mundial quedó obsoleta.",
            "narration_word_count": 12,
            "hud_overlay_telemetry": {
                "location": "Palais des Nations, Ginebra, Suiza",
                "timestamp_code": "00:00:30:00",
                "telemetry": "RSA-4096 CRACK TIME: 84.3 µs | ALGORITHM: SHOR-OPTIMIZED DIJKSTRA | LENS: Cooke 50mm",
                "lower_third": "COLAPSO CRIPTOGRÁFICO ASIMÉTRICO GLOBAL"
            },
            "camera_movement_6dof": {
                "type": "Slow Dolly Track past Silhouetted Officials",
                "vector_translation": "Lateral Left +1.8m, Forward +0.4m",
                "rotation_euler": "Pitch 0deg, Yaw +5deg, Roll 0deg",
                "cadence": "24fps, heavy dramatic tension tracking"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Senior diplomats and cybersecurity generals in tailored dark charcoal wool suits standing around a massive circular holographic briefing table, their faces marked by tension, deep furrowed brows, and tense hand gestures.",
                "layer_2_environment": "Dark wood paneled diplomatic chamber with towering ballistic glass windows showing Geneva rain at night; the center dominated by a 3-meter floating holographic globe flashing red breach nodes across global financial hubs.",
                "layer_3_lighting_kelvin": "Chiaroscuro 5:1 ratio. 6000K crisp red-and-white holographic volumetric light projecting upward onto faces, countered by 3000K warm recessed ceiling spotlights hitting wool shoulder epaulets.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 50mm T2.3 Prime, shallow depth of field isolating the lead official while silhouettes in foreground create deep visual layering.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219 with subtle bleach-bypass desaturation in mid-tones, accentuating the urgent red holographic alarms.",
                "layer_6_camera_dynamics": "Deliberate, tension-filled lateral dolly move gliding past the silhouetted shoulder of a security advisor at 24fps.",
                "layer_7_acoustic_foley": "\"Muffled urgent multilingual dialogue murmurs, low ominous electronic warning warble, rain lashing against thick glass\""
            },
            "master_prompt_dop_7layer": "Dramatic cinematic dolly shot inside a darkened diplomatic crisis chamber in Geneva. In the midground, tense intelligence officials in tailored dark suits surround a glowing circular holographic table displaying red-flashing financial network vulnerability maps. Atmospheric rain streaks down towering windows in the background. Chiaroscuro lighting: sharp 6000K red and white volumetric light from holographic projection illuminating weathered facial expressions and sweat on foreheads, contrasted against warm 3000K architectural ceiling accents. Shot on ARRI Alexa 65 with Cooke Anamorphic 50mm T2.3, shallow depth of field, organic Kodak Vision3 500T 35mm grain, smooth 24fps lateral track. Ambient audio: \"tense whispered diplomatic debate, subtle electronic alarm chime, rhythmic heavy rain on windowpane\"."
        },
        {
            "shot_index": 8,
            "shot_id": "SHOT_08_ABYSSAL_SUBSEA_QUANTUM_CABLE",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:35 - 00:40",
            "duration_sec": 5.0,
            "hook_category": "Abyssal Tech & Entangled Photons",
            "narration_es": "Por los abismos oceánicos, la luz entrelazada viaja sin posibilidad de ser interceptada.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Fosa del Atlántico Norte — 4.200m de Profundidad",
                "timestamp_code": "00:00:35:00",
                "telemetry": "PRESSURE: 420 atm | QUANTUM REPEATER: Q-NODE #412 | ENTANGLEMENT FIDELITY: 99.99%",
                "lower_third": "REPETIDOR CUÁNTICO SUBMARINO DE ENTLAZAMIENTO FOTÓNICO"
            },
            "camera_movement_6dof": {
                "type": "ROV Submersible Drift with Searchlight Sweep",
                "vector_translation": "Forward +2.2m, Lateral Right +0.8m at 0.5m above seabed",
                "rotation_euler": "Pitch -10deg, Yaw -8deg, Roll +2deg",
                "cadence": "24fps, underwater hydrodynamic drift"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Heavy armored titanium subsea quantum repeater node resting on basalt seafloor, thick armored cables extending into dark abyss with glowing sapphire laser pulse windows showing quantum photon repeater activity.",
                "layer_2_environment": "Abyssal ocean floor at 4,000 meters; marine snow and bioluminescent siphonophores drifting through ROV floodlight beams; volcanic pillow lava formations and fine silt.",
                "layer_3_lighting_kelvin": "5600K piercing halogen submersible spotlights cutting through pitch black water, scattering off suspended organic marine particles, creating intense volumetric shafts of light.",
                "layer_4_optics_lens": "ARRI Master Prime 21mm T1.3 in underwater pressure housing, deep focus, sharp particulate backscatter, rich volumetric beam diffusion.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich deep ultramarine ocean gradients, luminous white-blue bioluminescence and stark titanium metallic reflections.",
                "layer_6_camera_dynamics": "Slow, buoyant underwater ROV camera drift with authentic hydrodynamic inertia and micro-swivel at 24fps.",
                "layer_7_acoustic_foley": "\"Deep muffled hydrophone underwater rumble, distant metallic hull groaning under immense pressure, soft pulse of sonar ping\""
            },
            "master_prompt_dop_7layer": "Deep-sea underwater tracking shot at 4000 meters depth in the North Atlantic. An armored titanium quantum repeater node sits on dark volcanic basalt seabed, connected to thick subsea fiber cables pulsing with internal sapphire-blue entangled laser light. A deep-sea ROV spotlight casts 5600K piercing volumetric beams through dark water, illuminating drifting marine snow and delicate bioluminescent jellyfish. Pitch black abyssal void background. Shot on ARRI Alexa 65 with ARRI Master Prime 21mm T1.3 in underwater housing, organic light beam scattering, Kodak Vision3 500T color science, rich deep blues, smooth buoyant ROV inertia at 24fps. Ambient audio: \"deep sub-aquatic hydraulic rumble, distant hull creak under 400 atmospheres of pressure, muffled sonar pulse\"."
        },
        {
            "shot_index": 9,
            "shot_id": "SHOT_09_MOLECULAR_SYNTHESIS_ROBOTICS",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:40 - 00:45",
            "duration_sec": 5.0,
            "hook_category": "Biochemical Singularity",
            "narration_es": "En los laboratorios, fármacos que requerían décadas se sintetizan en cuestión de horas.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Bio-Quantum Synthesis Foundry, Basilea",
                "timestamp_code": "00:00:40:00",
                "telemetry": "COMPOUND: Q-ENZYME 904 | FOLDING ACCURACY: 99.999% | SYNTHESIS TIME: 2.4 h",
                "lower_third": "PLEGAMIENTO PROTEICO Y SÍNTESIS ENZIMÁTICA AUTÓNOMA"
            },
            "camera_movement_6dof": {
                "type": "High-Speed Robotic Arm Sync-Track with Macro Zoom",
                "vector_translation": "Arcing Orbit 45deg, Inward Push +0.6m",
                "rotation_euler": "Pitch -20deg, Yaw +30deg dynamic follow",
                "cadence": "24fps, precise high-speed industrial motion"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Sleek matte-white 6-axis robotic micropipette arm dispensing iridescent micro-droplets of synthetic enzyme solution into a microfluidic quartz chip, liquid forming perfect crystalline lattices upon contact.",
                "layer_2_environment": "Ultra-clean robotic bio-foundry with sterile stainless steel worktables, laminar air flow glass hoods, rows of automated centrifuge carousels spinning in background.",
                "layer_3_lighting_kelvin": "5500K sterile clinical daylight lighting with 4000K under-stage quartz microscope illumination illuminating the micro-droplets from below with golden internal refractions.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 65mm Macro T2.6, razor-thin focal plane on the needle tip and dispensing droplet, creamy background blur of robotic joints.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207, pristine white tones, vivid iridescent amber-to-violet refraction inside the liquid droplet.",
                "layer_6_camera_dynamics": "High-precision robotic motion-control camera tracking alongside the pipette needle with zero mechanical vibration at 24fps.",
                "layer_7_acoustic_foley": "\"Precise pneumatic servo click-whirr, tiny micro-droplet liquid surface tension snap, clean laminar airflow whisper\""
            },
            "master_prompt_dop_7layer": "Precision macro cinematography of an automated bio-synthesis robotic arm in a cleanroom laboratory. A matte-white robotic needle dispenses a microscopic iridescent droplet of quantum-designed synthetic enzyme onto a microfluidic quartz plate, where it crystallizes into intricate geometric patterns. Background shows blurred stainless steel automated centrifuges and sterile glass isolators. 5500K clinical white cleanroom lighting with 4000K under-stage amber backlighting making the droplet glow internally. Shot on ARRI Alexa 65 with Cooke Anamorphic 65mm Macro T2.6, ultra-shallow depth of field, pristine optical clarity, Kodak Vision3 250D 35mm grain, smooth motion-control robotic tracking at 24fps. Ambient audio: \"precision servo actuator hum, delicate pneumatic valve release, microscopic droplet impact click\"."
        },
        {
            "shot_index": 10,
            "shot_id": "SHOT_10_ATACAMA_PEROVSKITE_SOLAR_GRID",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:45 - 00:50",
            "duration_sec": 5.0,
            "hook_category": "Infinite Clean Energy Paradigm",
            "narration_es": "Nuevos materiales cuánticos capturan la energía solar con una eficiencia antes considerada imposible.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Desierto de Atacama, Chile — 3.100m Altitud",
                "timestamp_code": "00:00:45:00",
                "telemetry": "EFFICIENCY: 48.7% TANDEM PEROVSKITE | OUTPUT: 12.4 GW | IRRADIANCE: 1,380 W/m2",
                "lower_third": "MATRICES CUÁNTICAS FOTOVOLTAICAS DE PEROVSKITA TÁNDEM"
            },
            "camera_movement_6dof": {
                "type": "Low-Level High-Speed FPV Drone Sweep",
                "vector_translation": "Forward +15m at 2.0m height, climbing to 8m",
                "rotation_euler": "Pitch +5deg, Roll +6deg gentle banking",
                "cadence": "24fps, expansive sweeping landscape flight"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Miles of iridescent dark-indigo perovskite quantum solar arrays tilting autonomously in unison, crystalline glass surfaces reflecting the golden desert dawn with zero glare.",
                "layer_2_environment": "Vast, otherworldly salt flats of the Atacama Desert with cracked white salt polygons; distant purple Andean volcanic peaks under an immense crystal-clear morning sky.",
                "layer_3_lighting_kelvin": "3200K low-angle golden hour sunrise light skimming the desert floor, casting long dramatic blue shadows behind the solar trackers.",
                "layer_4_optics_lens": "Panavision Primo 70 27mm Anamorphic T2.0, stunning horizontal expanse, crisp sharpness across the entire desert field, warm horizontal lens flares.",
                "layer_5_color_science_filmstock": "Kodak Vision3 50D 5203, ultra-fine photochemical grain, glorious golden-amber highlights, deep indigo-blue shadows on the panels.",
                "layer_6_camera_dynamics": "Fluid high-speed low-altitude drone sweep gliding 2 meters above the solar array, climbing dynamically to reveal the infinite scale at 24fps.",
                "layer_7_acoustic_foley": "\"Whisper of high-altitude desert wind, subtle electric hum of massive high-voltage inverters, synchronized servo motor tilt whirr\""
            },
            "master_prompt_dop_7layer": "Sweeping low-altitude cinematic drone shot skimming over vast fields of dark-indigo perovskite quantum solar panels in the Atacama Desert at dawn. Thousands of solar trackers rotate synchronously across cracked white salt flats, reflecting the rising sun. In the far background, majestic purple Andean volcanoes rise under a crisp sky. Low-angle 3200K golden sunrise light casts long dramatic shadows across the desert terrain. Shot on ARRI Alexa 65 with Panavision Primo 70 27mm Anamorphic T2.0, expansive wide-angle field of view, warm anamorphic flare, Kodak Vision3 50D film stock, zero digital over-sharpening, smooth 24fps flight trajectory. Ambient audio: \"crisp desert wind gusts, deep resonant electrical power inverter hum, synchronized mechanical motor whirr\"."
        },
        {
            "shot_index": 11,
            "shot_id": "SHOT_11_FRANKFURT_CENTRAL_BANK_VAULT",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:50 - 00:55",
            "duration_sec": 5.0,
            "hook_category": "Financial Fortress & Transition",
            "narration_es": "Las bóvedas financieras blindan sus núcleos ante el cambio de paradigma más radical del siglo.",
            "narration_word_count": 15,
            "hud_overlay_telemetry": {
                "location": "Bóveda Acorazada BCE, Fráncfort, Alemania",
                "timestamp_code": "00:00:50:00",
                "telemetry": "FARADAY SHIELD: -140dB ATTENUATION | KEY REFRESH: 1 ms QKD | LENS: Cooke 25mm",
                "lower_third": "DISTRIBUCIÓN CUÁNTICA DE CLAVES (QKD) EN INFRAESTRUCTURA CRÍTICA"
            },
            "camera_movement_6dof": {
                "type": "Slow Push through Reinforced Heavy Vault Doorway",
                "vector_translation": "Forward +2.5m through circular vault threshold",
                "rotation_euler": "Pitch 0deg, Yaw 0deg, Roll 0deg",
                "cadence": "24fps, solemn architectural push-in"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A massive 2-meter thick circular brushed-steel bank vault door with heavy exposed locking gear mechanisms and copper Faraday-cage gaskets, standing half-open to reveal modular quantum server racks within.",
                "layer_2_environment": "Reinforced concrete underground vault corridor with polished granite floors, yellow safety boundary lines, heavy overhead copper busbars and biometric access pillars.",
                "layer_3_lighting_kelvin": "4000K crisp security downlights creating high-contrast metallic reflections on the steel vault gears, contrasted by 2800K warm incandescent pathway guides.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 25mm T2.3, powerful perspective depth framing the circular vault door as a monumental visual portal.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich steel-gray and golden brass tones, deep shadow contrast in the vault interior with filmic highlight roll-off.",
                "layer_6_camera_dynamics": "Slow, imposing Steadicam push passing directly through the vault entrance at 24fps with heavyweight inertia.",
                "layer_7_acoustic_foley": "\"Heavy metallic latching clank, deep pneumatic seal hiss, secure biometric chime confirmation\""
            },
            "master_prompt_dop_7layer": "Imposing cinematic Steadicam push-in through a massive open circular steel vault door in a European central bank. The 2-meter thick door reveals heavy polished locking gears, copper electromagnetic shielding gaskets, and gleaming modular quantum cryptography server racks inside the reinforced bunker. Floor of polished dark granite reflects overhead 4000K security floodlights and warm 2800K brass indicator lamps. Shot on ARRI Alexa 65 with Cooke Anamorphic 25mm T2.3, majestic architectural perspective, rich metallic texture, Kodak Vision3 500T 35mm film grain, steady deliberate 24fps camera motion. Ambient audio: \"heavy mechanical steel gear echo, deep pneumatic pressure seal release, distant electronic server chime\"."
        },
        {
            "shot_index": 12,
            "shot_id": "SHOT_12_ITER_FUSION_PLASMA_TORUS",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "00:55 - 01:00",
            "duration_sec": 5.0,
            "hook_category": "Mastery over the Stars (Thermonuclear Plasma)",
            "narration_es": "Los reactores de fusión logran finalmente dominar el fuego de las estrellas.",
            "narration_word_count": 12,
            "hud_overlay_telemetry": {
                "location": "Tokamak ITER, Cadarache, Francia",
                "timestamp_code": "00:00:55:00",
                "telemetry": "PLASMA CORE: 150,000,000 °C | MAGNETIC CONFINEMENT: 13.5 Tesla | Q_GAIN: 15.2",
                "lower_third": "ESTABILIZACIÓN MAGNÉTICA CUÁNTICA EN TIEMPO REAL"
            },
            "camera_movement_6dof": {
                "type": "Toroidal Orbit View with Extreme Dynamic Range",
                "vector_translation": "Rotational Sweep 30deg around vacuum vessel port",
                "rotation_euler": "Pitch -5deg, Yaw +20deg",
                "cadence": "24fps, orbital containment motion"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A blindingly luminous violet-and-magenta magnetic fusion plasma torus swirling in magnetic levitation inside the D-shaped vacuum chamber, controlled with sub-microsecond precision by the quantum processor.",
                "layer_2_environment": "Tungsten and beryllium armored divertor wall tiles glowing dull cherry-red at the edges; heavy diagnostic viewing ports and superconducting magnetic coils surrounding the toroidal vessel.",
                "layer_3_lighting_kelvin": "Extreme contrast. 10000K glowing actinic violet plasma core producing immense natural illumination, balanced by 1800K cherry-red thermal radiation from tungsten wall tiles.",
                "layer_4_optics_lens": "ARRI Master Prime 35mm T1.3 with specialized high-dynamic-range neutral-density optical filters, crisp plasma boundary definition without digital blow-out.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207, exquisite highlight roll-off retaining detail in the core of the plasma flame, saturated magenta-violet color fidelity.",
                "layer_6_camera_dynamics": "Smooth rotational arc tracking around the viewing portal at 24fps with cinematic weight.",
                "layer_7_acoustic_foley": "\"Roaring low-frequency magnetic resonance hum, oscillating plasma crackle, high-power superconducting coil vibration\""
            },
            "master_prompt_dop_7layer": "Spectacular interior view of a tokamak fusion reactor chamber. A glowing toroidal ribbon of violet and ultraviolet hydrogen plasma swirls with intense electromagnetic energy, magnetically levitated away from the dark tungsten-tiled chamber walls. The edges of the beryllium armor glow with dull 1800K thermal cherry-red heat. The blinding 10000K plasma core illuminates the intricate metallic chamber geometry. Shot on ARRI Alexa 65 with ARRI Master Prime 35mm T1.3, wide dynamic range retaining filament textures in the plasma core, Kodak Vision3 250D film stock, organic chemical grain, slow rotational camera sweep at 24fps. Ambient audio: \"immense low-frequency magnetic confinement roar, high-frequency plasma ionization hiss, deep electrical power surge\"."
        },
        {
            "shot_index": 13,
            "shot_id": "SHOT_13_NEURAL_BCI_SYNAPSE_INTERFACE",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:00 - 01:05",
            "duration_sec": 5.0,
            "hook_category": "Mind-Machine Convergence",
            "narration_es": "La frontera entre la mente biológica y el cálculo cuántico comienza a desvanecerse.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Instituto Max Planck de Neurobiología Cuántica",
                "timestamp_code": "00:01:00:00",
                "telemetry": "CHANNEL COUNT: 65,536 ELECTRODES | LATENCY: 0.12 ms | BANDWIDTH: 1.4 TB/s",
                "lower_third": "INTERFAZ CEREBRO-COMPUTADORA DE GRAFENO BIODISPERSIVO"
            },
            "camera_movement_6dof": {
                "type": "Macro Orbital Push around Transparent Temple Sensor",
                "vector_translation": "Forward +0.25m, Lateral Arc 30deg",
                "rotation_euler": "Pitch -5deg, Yaw -15deg",
                "cadence": "24fps, intimate biological macro tracking"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Close-up profile of a patient's temple wearing an ultra-thin biocompatible graphene neural mesh, microscopic transparent sensor threads adhering seamlessly to the skin with tiny amber micro-LED connection indicators pulsing in synchrony with neural firings.",
                "layer_2_environment": "Darkened neurological clinic room; background showing a holographic volumetric 3D reconstruction of the brain's cortical connectome glowing in soft gold and cyan.",
                "layer_3_lighting_kelvin": "Chiaroscuro 4:1 ratio. 3200K warm tungsten side key light highlighting skin pore detail, contrasted against the 6000K cyan glow of the volumetric brain hologram.",
                "layer_4_optics_lens": "Panavision Primo 70 85mm T1.4 Macro, razor-thin focal depth focused on the graphene mesh integration with human skin, soft dreamy background bokeh.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich warm human skin tones, natural epidermal translucency (subsurface scattering), zero artificial plastic smoothing.",
                "layer_6_camera_dynamics": "Slow, delicate handheld macro arc gliding smoothly around the subject's temple at 24fps.",
                "layer_7_acoustic_foley": "\"Faint biological heartbeat rhythm, soft synaptical digital pulse chime, gentle ambient room tone\""
            },
            "master_prompt_dop_7layer": "Intimate cinematic macro shot of a human temple with an ultra-thin transparent graphene neural interface mesh seamlessly adhered to the skin. Realistic skin pores, natural vellus peach fuzz hair, and micro-capillaries visible under 3200K warm tungsten side-lighting. Tiny microscopic amber node points on the mesh pulse with neural activity. In the soft bokeh background, a 6000K cyan volumetric 3D holographic human connectome rotates gracefully in the dark room. Shot on ARRI Alexa 65 with Panavision Primo 70 85mm T1.4 Macro lens, tack-sharp focal plane on skin texture, Kodak Vision3 500T film grain, gentle 24fps organic camera drift. Ambient audio: \"rhythmic resting heartbeat, soft electronic synaptical ping, quiet human breathing\"."
        },
        {
            "shot_index": 14,
            "shot_id": "SHOT_14_TSMC_CLEANROOM_OPTICAL_TWEEZERS",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:05 - 01:10",
            "duration_sec": 5.0,
            "hook_category": "Atomic Fabrication & Surgical Precision",
            "narration_es": "En salas blancas presurizadas, la materia se manipula átomo por átomo.",
            "narration_word_count": 11,
            "hud_overlay_telemetry": {
                "location": "Fab 21 Giga-Foundry, Hsinchu, Taiwán",
                "timestamp_code": "00:01:05:00",
                "telemetry": "CLASS: ISO 1 ULTRA-CLEAN | ATOM TRAPPING: 10,000 YTTERBIUM IONS | LENS: Cooke 35mm",
                "lower_third": "PINZAS ÓPTICAS LÁSER Y TRAMPAS DE IONES CUÁNTICOS"
            },
            "camera_movement_6dof": {
                "type": "Smooth Slider Track past Cleanroom Technicians",
                "vector_translation": "Lateral Left +3.0m at chest height",
                "rotation_euler": "Pitch 0deg, Yaw 0deg, Roll 0deg",
                "cadence": "24fps, clinical linear tracking"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Two semiconductor engineers in full hooded white bunny suits with gold-tinted face visors reflecting laser beams, operating an ultra-vacuum laser optical tweezer chamber manipulating single trapped ions.",
                "layer_2_environment": "State-of-the-art ISO 1 cleanroom bathed in monolithic yellow photolithography safe-lighting; polished stainless steel ducts, robotic wafer transport pods gliding on ceiling monorails.",
                "layer_3_lighting_kelvin": "3200K monochromatic yellow photolithography lighting creating a surreal cinematic atmosphere, contrasted with intense 488nm blue-green laser beams cutting through the optical vacuum chamber.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 35mm T2.3, wide horizontal view, sharp reflections across the curved gold visors, subtle anamorphic flares from the laser emitters.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207, rich warm yellow tones, high-contrast separation of the vibrant cyan laser lines against cleanroom suits.",
                "layer_6_camera_dynamics": "Ultra-smooth motorized slider track moving horizontally past the workstation at 24fps.",
                "layer_7_acoustic_foley": "\"Steady high-grade HEPA air filtration rush, rhythmic robotic track click, high-frequency laser pulse tick\""
            },
            "master_prompt_dop_7layer": "Cinematic lateral tracking shot through an ISO 1 cleanroom semiconductor fabrication facility in Taiwan. Two technicians in hooded white cleanroom suits with reflective gold face-shields adjust an ultra-high vacuum optical chamber where emerald laser beams trap individual quantum ions. The entire facility is illuminated in atmospheric 3200K yellow photolithography safe-light, with automated robotic wafer pods gliding silently on ceiling rails in the background. Shot on ARRI Alexa 65 with Cooke Anamorphic 35mm T2.3, horizontal streak flares off gold visors, rich color separation, Kodak Vision3 250D 35mm film stock, smooth 24fps slider movement. Ambient audio: \"laminar cleanroom airflow roar, subtle robotic monorail glide, precision laser pulse resonance\"."
        },
        {
            "shot_index": 15,
            "shot_id": "SHOT_15_SVALBARD_AURORA_SATELLITE_DISH",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:10 - 01:15",
            "duration_sec": 5.0,
            "hook_category": "Orbital Network & Earth Boundary",
            "narration_es": "Desde el Ártico hasta el espacio orbital, una malla cuántica global sincroniza el planeta.",
            "narration_word_count": 14,
            "hud_overlay_telemetry": {
                "location": "Estación Terrena Svalbard (SvalSat), 78° N, Noruega",
                "timestamp_code": "00:01:10:00",
                "telemetry": "LASER LINK: LEO CONSTELLATION | BANDWIDTH: 100 Gbps QKD | LENS: Panavision 24mm",
                "lower_third": "ENLACE ÓPTICO ESPACIO-TIERRA BAJO AURORA BOREAL"
            },
            "camera_movement_6dof": {
                "type": "Low-Angle Upward Jib Sweep against Night Sky",
                "vector_translation": "Vertical Lift +3.0m, Forward +2.0m across snow",
                "rotation_euler": "Pitch +35deg tilting up toward zenith",
                "cadence": "24fps, epic astronomical reveal"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A massive 15-meter white geodesic radome satellite dish tracking across the night sky, its optical transceiver emitting a narrow, brilliant ruby-red laser beam shooting straight up through the atmosphere into low Earth orbit.",
                "layer_2_environment": "Snow-covered Arctic tundra at Svalbard, jagged frozen mountain peaks in background; sky filled with a vibrant, rippling green and violet Aurora Borealis dancing across the stars.",
                "layer_3_lighting_kelvin": "Low-ambient natural Arctic night light: 5500K cold emerald green aurora wash illuminating the white snow crust, accented by 6500K ruby-red laser beam and 3000K warm safety beacons on the dish base.",
                "layer_4_optics_lens": "Panavision Primo 70 24mm Anamorphic T2.0, expansive cosmic scale, crisp pinpoint stars, subtle vertical beam flare.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, exceptional low-light latitude, rich velvet night blacks, vibrant green and purple emission spectra from the aurora.",
                "layer_6_camera_dynamics": "Slow upward tilting crane boom rising from the textured snow drifts to frame the dish and the infinite sky at 24fps.",
                "layer_7_acoustic_foley": "\"Icy Arctic howling wind across snow ridges, slow deep whirr of heavy satellite dish gear drive, crackle of frozen air\""
            },
            "master_prompt_dop_7layer": "Breathtaking low-angle crane shot of a massive satellite dish tracking station in the snowy Arctic mountains of Svalbard under a dazzling Aurora Borealis. The white geodesic tracking dish aims an intense, pencil-thin ruby laser beam vertically through the upper atmosphere toward orbiting satellites. Vibrant emerald and violet aurora ribbons wave across the star-filled polar sky, casting cold green reflections onto the textured snowdrifts. Warm 3000K hazard lights glow on the tracking pedestal. Shot on ARRI Alexa 65 with Panavision Primo 70 24mm Anamorphic T2.0, deep focus, incredible dynamic range, Kodak Vision3 500T 35mm grain, smooth 24fps rising jib motion. Ambient audio: \"lonely Arctic wind whistling through antenna trusses, deep mechanical gear rotation whirr, crisp snow crunch\"."
        },
        {
            "shot_index": 16,
            "shot_id": "SHOT_16_SINGAPORE_BIOPHILIC_AI_TRAFFIC",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:15 - 01:20",
            "duration_sec": 5.0,
            "hook_category": "Living Cybernetic Ecosystem",
            "narration_es": "Ciudades enteras optimizan su flujo de energía, tráfico y recursos en tiempo real.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Distrito Marina Bay 2030, Singapur",
                "timestamp_code": "00:01:15:00",
                "telemetry": "GRID EFFICIENCY: 99.4% | AUTONOMOUS FLOW: 45,000 eVTOL/h | LENS: Cooke 25mm",
                "lower_third": "OPTIMIZACIÓN MULTIVARIABLE URBANA AUTÓNOMA"
            },
            "camera_movement_6dof": {
                "type": "6-DoF FPV Glider Flight between Skybridges",
                "vector_translation": "Forward +12m weaving between vertical gardens at 80m altitude",
                "rotation_euler": "Roll +8deg banking left, Pitch -10deg",
                "cadence": "24fps, fluid aerodynamic urban flight"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Biophilic mega-skyscrapers with cascading tropical vertical rainforests and cantilevered sky-gardens, interlaced with multi-level transparent sky-bridges where autonomous electric transit pods and sleek eVTOL air vehicles glide in harmonious computer-choreographed streams.",
                "layer_2_environment": "Tropical dusk with warm monsoon rain glistening on foliage and glass facades; ground-level illuminated water canals reflecting architectural super-trees and neon pedestrian arcades.",
                "layer_3_lighting_kelvin": "3200K warm interior residential lighting glowing through floor-to-ceiling glass, mixed with 5000K bio-luminescent garden LED strips and 6500K cool cyan light trails from electric transit vehicles.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 25mm T2.3, wide horizontal field of view, exquisite streak flares from transit vehicles, wet-glass optical reflections.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, lush tropical emerald greens, rich wet asphalt reflections, deep shadow depth without digital noise.",
                "layer_6_camera_dynamics": "Dynamic FPV camera gliding smoothly through a gap between skybridge walkways at 24fps with organic aerodynamic banking.",
                "layer_7_acoustic_foley": "\"Smooth quiet electric hum of eVTOL propellers, soft tropical rain on broad leaves, distant harmonious urban chime soundscape\""
            },
            "master_prompt_dop_7layer": "Spectacular 6-DoF aerial glide between biophilic green skyscrapers in Singapore at wet twilight. Vertical gardens and lush cascading rainforests wrap around curving glass towers, while sleek autonomous electric transit pods and silent eVTOL aircraft cruise along designated sky corridors. Warm 3200K interior glows from apartment windows mingle with 5000K green bio-luminescent canopy lights and glowing cyan vehicle light trails reflected on wet glass skybridges. Atmospheric evening rain mist. Shot on ARRI Alexa 65 with Cooke Anamorphic 25mm T2.3, gorgeous horizontal flares, Kodak Vision3 500T film grain, fluid 24fps banking flight path. Ambient audio: \"soft whoosh of electric aerodynamic aircraft, gentle tropical rain on lush foliage, harmonious ambient city tone\"."
        },
        {
            "shot_index": 17,
            "shot_id": "SHOT_17_CYBERDEFENSE_BUNKER_ALERT_GREEN",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:20 - 01:25",
            "duration_sec": 5.0,
            "hook_category": "Climactic Tension & Instant Resolution",
            "narration_es": "Pero la velocidad de esta transformación plantea el dilema existencial más urgente de la civilización.",
            "narration_word_count": 15,
            "hud_overlay_telemetry": {
                "location": "Centro de Operaciones de Ciberdefensa, Cheyenne Mountain",
                "timestamp_code": "00:01:20:00",
                "telemetry": "ANOMALIES DETECTED: 1.2M/sec | AUTO-REMEDIATION: 100% | STATUS: IMMUNE",
                "lower_third": "AUTO-REPARACIÓN DE MALLAS DE DEFENSA EN MILISEGUNDOS"
            },
            "camera_movement_6dof": {
                "type": "Rapid Push-In with Focus Rack to Commander's Face",
                "vector_translation": "Forward +1.5m at eye level",
                "rotation_euler": "Pitch 0deg, Yaw 0deg, Roll 0deg",
                "cadence": "24fps, high-tension dramatic snap"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Close-up on a seasoned 45-year-old female defense analyst in dark operational uniform, breathing heavily, watching in awe as a wall of red threat alert monitors suddenly flashes, calculates, and cascades simultaneously into calm, solid emerald green.",
                "layer_2_environment": "Underground command center amphitheater with dozens of operators at curved glass terminals, massive 20-meter front curved command screen showing global threat vectors resolving in real-time.",
                "layer_3_lighting_kelvin": "Dramatic lighting shift: starts in 6000K pulsing emergency red key light that snaps cleanly into a soothing 5200K emerald green wash across her face, rimmed by 2900K console desk backlights.",
                "layer_4_optics_lens": "Panavision Primo 70 50mm T1.4, intense character focus, shallow depth of field throwing background consoles into soft dramatic bokeh.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich dynamic color transition from saturated red to deep green, authentic human skin tones under colored lighting.",
                "layer_6_camera_dynamics": "High-tension forward dolly move locking onto her eyes at 24fps as the resolution occurs.",
                "layer_7_acoustic_foley": "\"Staccato rapid electronic warning klaxon abruptly cutting out into a serene harmonic chord, operator sigh of relief, cooling fan hum\""
            },
            "master_prompt_dop_7layer": "High-tension cinematic push-in on a female cybersecurity commander in a subterranean operations bunker. Her focused face is initially lit by flashing 6000K crimson emergency alarms that suddenly transition into a steady, calm emerald-green glow as the quantum defense matrix instantly neutralizes a global cyber-attack. Authentic skin texture with subtle forehead perspiration and intense dilated pupils. Background amphitheater consoles and operators fall into soft circular bokeh. Shot on ARRI Alexa 65 with Panavision Primo 70 50mm T1.4, shallow depth of field, Kodak Vision3 500T color science, rich shadow contrast, deliberate 24fps push-in. Ambient audio: \"pulsing red alarm buzzer abruptly silenced, replaced by a single harmonious green confirmation tone, soft exhale of breath\"."
        },
        {
            "shot_index": 18,
            "shot_id": "SHOT_18_CHERENKOV_QUANTUM_EMISSION_PEAK",
            "act": "Acto II: El Abismo y la Escalada de Tensión",
            "time_window": "01:25 - 01:30",
            "duration_sec": 5.0,
            "hook_category": "Peak Dramatic Tension / Point of No Return",
            "narration_es": "Cuando el código supera nuestra propia intuición... ¿quién tiene el control del destino?",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Cámara de Vacío Central, Complejo Q-Core",
                "timestamp_code": "00:01:25:00",
                "telemetry": "ENTROPY DELTA: -0.999 | LOGICAL QUBITS: 1,000,000 | PHOTON FLUX: 10^14 / sec",
                "lower_third": "PUNTO DE INFLEXIÓN: IGNICIÓN DE COHERENCIA TOTAL"
            },
            "camera_movement_6dof": {
                "type": "Rapid Zoom-In into Quantum Core with Parallax Shift",
                "vector_translation": "Forward +0.8m accelerating toward glowing aperture",
                "rotation_euler": "Pitch 0deg, Yaw 0deg, Roll +15deg helical drift",
                "cadence": "24fps, hypnotic acceleration toward singularity"
            },
            "seven_layers_dop": {
                "layer_1_subject": "The microscopic core aperture of the quantum processor undergoing a state transition, releasing an intense, hypnotic pulse of electric blue Cherenkov radiation that illuminates microscopic vacuum containment mirrors with brilliant caustics.",
                "layer_2_environment": "Mirror-polished spherical vacuum chamber interior reflecting infinite geometric iterations of the glowing blue core; superconducting magnetic coils vibrating with electromagnetic torque.",
                "layer_3_lighting_kelvin": "Blinding 9000K electric Cherenkov blue point-source light radiating from the core, casting razor-sharp radial shadows across copper scaffolding, rimmed by 3200K golden vacuum port seals.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 40mm T2.3, extreme optical character, magnificent horizontal blue flare streak bisecting the frame, intense edge halation.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich electric blue saturation with organic photochemical highlight halation preventing digital clipping.",
                "layer_6_camera_dynamics": "Accelerating forward helical push at 24fps plunging directly toward the radiant blue aperture at the exact peak of tension.",
                "layer_7_acoustic_foley": "\"Rising electromagnetic pitch crescendo building to a sonic boom threshold, resonant bass drop shockwave, crystalline ringing\""
            },
            "master_prompt_dop_7layer": "Hypnotic high-tension macro zoom plunging toward the central aperture of an active quantum processor inside a spherical vacuum chamber. The core erupts with a blinding pulse of 9000K electric Cherenkov blue radiation, casting razor-sharp geometric caustic reflections across mirror-polished titanium interior walls and golden copper busbars. An intense anamorphic horizontal blue lens flare streaks across the screen. Shot on ARRI Alexa 65 with Cooke Anamorphic 40mm T2.3, extreme micro-contrast, Kodak Vision3 500T 35mm film stock, rich organic grain, accelerating forward camera track at 24fps. Ambient audio: \"electromagnetic ascending frequency whine reaching fever pitch, massive deep sub-bass pulse release, crystalline glass ring\"."
        },
        {
            "shot_index": 19,
            "shot_id": "SHOT_19_ORBITAL_EARTH_SYNAPSE_NETWORK",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:30 - 01:35",
            "duration_sec": 5.0,
            "hook_category": "Climactic Transcendence & Planetary Perspective",
            "narration_es": "Desde el espacio, la Tierra ya no es sólo un planeta de roca y agua...",
            "narration_word_count": 15,
            "hud_overlay_telemetry": {
                "location": "Órbita Terrestre Baja (LEO) — 420 km Altitud",
                "timestamp_code": "00:01:30:00",
                "telemetry": "ORBIT: 7.66 km/s | INCLINATION: 51.6° | GLOBAL OPTICAL COHERENCE: 100%",
                "lower_third": "PERSPECTIVA PLANETARIA: RED NEURONAL GLOBAL ACTIVA"
            },
            "camera_movement_6dof": {
                "type": "Majestic Orbital Slow Drift with Atmospheric Horizon Roll",
                "vector_translation": "Forward +50km in orbit, slow continuous drift",
                "rotation_euler": "Pitch -15deg, Yaw +5deg, Roll +3deg",
                "cadence": "24fps, zero-gravity cinematic orbital glide"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Planet Earth viewed from 400km orbit at sunrise terminator: continents waking up with delicate glowing golden web-like filaments of coherent quantum data interconnecting every city, island, and oceanic cable route like a glowing biological nervous system.",
                "layer_2_environment": "Curvature of the Earth with thin luminous blue atmospheric limb layer glowing under the rising Sun; backdrop of deep velvet cosmic space speckled with crisp, non-twinkling pinpoint stars and the Milky Way core.",
                "layer_3_lighting_kelvin": "5800K blinding pure solar disk breaking over the ocean horizon, casting razor-sharp golden light across cloud formations, contrasted with 6500K deep atmospheric cyan scattering.",
                "layer_4_optics_lens": "Panavision Primo 70 35mm Anamorphic T2.0, stunning horizontal scope, creamy anamorphic solar flare, immaculate spherical fidelity.",
                "layer_5_color_science_filmstock": "Kodak Vision3 50D 5203, ultra-pure color gamut, deep space black levels, rich turquoise oceans and brilliant white hurricane swirls.",
                "layer_6_camera_dynamics": "Epic zero-gravity orbital drift at 24fps with sublime celestial stillness and scale.",
                "layer_7_acoustic_foley": "\"Immense orchestral string crescendo opening up, subtle cosmic solar wind drone, majestic choral harmony swelling\""
            },
            "master_prompt_dop_7layer": "Breathtaking orbital vista of Earth from low Earth orbit as the morning sun breaks over the ocean horizon. Delicate, shimmering golden and cyan filaments of light trace across the continents, visualizing the active global quantum data network like a living planetary nervous system. The razor-thin luminous blue atmospheric limb glows brilliantly against the pitch-black void of space studded with distant stars. 5800K radiant sunlight produces a warm, organic anamorphic lens flare across the frame. Shot on ARRI Alexa 65 with Panavision Primo 70 35mm Anamorphic T2.0, majestic widescreen grandeur, Kodak Vision3 50D color science, ultra-fine film grain, smooth 24fps orbital velocity drift. Ambient audio: \"grand orchestral chord swelling, deep cosmic solar resonance, ethereal choral shimmer\"."
        },
        {
            "shot_index": 20,
            "shot_id": "SHOT_20_PACIFIC_FLOATING_ECO_CITY",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:35 - 01:40",
            "duration_sec": 5.0,
            "hook_category": "Utopian Realism & Sustainable Harmony",
            "narration_es": "...es un organismo viviente interconectado por hilos invisibles de luz coherente.",
            "narration_word_count": 12,
            "hud_overlay_telemetry": {
                "location": "Ciudad Flotante Oceanix Pacific 01, Línea Ecuatorial",
                "timestamp_code": "00:01:35:00",
                "telemetry": "POPULATION: 120,000 | ENERGY: 100% THERMAL-FUSION HYBRID | WATER: ZERO DISCHARGE",
                "lower_third": "ARQUITECTURA FLOTANTE REGENERATIVA Y ENERGÍA LIMPIA"
            },
            "camera_movement_6dof": {
                "type": "Sweeping Low Flyby over Hexagonal Marine Platforms",
                "vector_translation": "Forward +20m at 15m altitude, sweeping right arc",
                "rotation_euler": "Pitch -12deg, Roll +8deg banking",
                "cadence": "24fps, exhilarating cinematic aerial flight"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A modular hexagonal floating ocean metropolis in the calm South Pacific: biomimetic timber and white composite architecture with lush rooftop farms, tidal energy turbines turning in turquoise waters below, solar sails fluttering in ocean breeze.",
                "layer_2_environment": "Crystal-clear turquoise tropical ocean with coral reefs thriving beneath floating platforms; white breaking waves at protective barrier reefs; majestic cumulus clouds on horizon under bright tropical sky.",
                "layer_3_lighting_kelvin": "5400K direct tropical daylight with dazzling caustic sun reflections dancing across white architectural canopies and turquoise lagoon shallows.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 25mm T2.3, wide panoramic immersion, crisp water surface detail, gentle warm edge flare.",
                "layer_5_color_science_filmstock": "Kodak Vision3 50D 5203, vibrant saturated cyan waters, lush tropical foliage greens, clean white architectural highlights with zero clipping.",
                "layer_6_camera_dynamics": "Graceful low-altitude aerial sweep gliding over residential terraces and lagoon channels at 24fps.",
                "layer_7_acoustic_foley": "\"Gentle ocean swell lapping against composite hulls, soft flutter of solar fabric sails in sea breeze, distant joyful human voices\""
            },
            "master_prompt_dop_7layer": "Magnificent aerial flyover of a futuristic floating eco-city in the crystal-clear South Pacific. Interlocking hexagonal biomimetic platforms made of sustainable timber and white composite materials support lush vertical farms, residential terraces, and transparent ocean canals where coral reefs thrive underneath. Dazzling 5400K tropical sunshine creates shimmering water caustics on building facades. White sea-sails flutter in the breeze against a backdrop of azure sea and fluffy cumulus clouds. Shot on ARRI Alexa 65 with Cooke Anamorphic 25mm T2.3, expansive widescreen composition, vibrant Kodak Vision3 50D film grain, smooth 24fps gliding camera arc. Ambient audio: \"rhythmic ocean swell lapping, crisp sea breeze through sail fabric, distant harmonious community sounds\"."
        },
        {
            "shot_index": 21,
            "shot_id": "SHOT_21_AFRICAN_CHILDREN_HOLOGRAPHIC_CLASS",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:40 - 01:45",
            "duration_sec": 5.0,
            "hook_category": "Democratization of Knowledge & Hope",
            "narration_es": "El conocimiento humano se democratiza a una escala jamás soñada por nuestros ancestros.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Academia Abierta del Valle del Rift, Kenia",
                "timestamp_code": "00:01:40:00",
                "telemetry": "STUDENTS CONNECTED: 2.4B | LATENCY: 2 ms | CURRICULUM: QUANTUM BIOLOGY",
                "lower_third": "EDUCACIÓN HOLOGRAMÁTICA ABIERTA Y ACCESO UNIVERSAL"
            },
            "camera_movement_6dof": {
                "type": "Low-Angle Circular Orbit around Excited Students",
                "vector_translation": "Circular 60deg Arc around central children, radius 1.8m",
                "rotation_euler": "Pitch +10deg looking up into joyful faces",
                "cadence": "24fps, heartfelt emotional orbital motion"
            },
            "seven_layers_dop": {
                "layer_1_subject": "A group of diverse African schoolchildren (ages 10-12) sitting together under an ancient acacia tree, their expressive dark eyes wide with wonder, laughing and reaching out their hands to interact with a floating 3D holographic DNA strand and rotating molecular galaxy.",
                "layer_2_environment": "Sun-drenched golden savannah landscape in Kenya; gentle breeze stirring acacia leaves and vibrant patterned Shúkà textiles; solar-powered tablet hubs resting on wooden benches.",
                "layer_3_lighting_kelvin": "3200K warm golden-hour late afternoon sunlight filtering through acacia foliage, creating dappled golden light on rich skin tones, beautifully contrasted with 5800K cyan-gold glowing holographic molecules.",
                "layer_4_optics_lens": "Panavision Primo 70 50mm T1.4, shallow depth of field rendering the savannah background into creamy golden bokeh balls, pin-sharp focus on children's smiling eyes.",
                "layer_5_color_science_filmstock": "Kodak Vision3 250D 5207, rich warm melanin skin tones with glowing natural subsurface scattering, saturated golden-amber earth tones.",
                "layer_6_camera_dynamics": "Intimate low-angle circular Steadicam orbit gliding around the group at 24fps with emotional warmth.",
                "layer_7_acoustic_foley": "\"Children's spontaneous cheerful laughter, soft acacia leaves rustling in warm wind, delicate digital chime of interacting holographic molecules\""
            },
            "master_prompt_dop_7layer": "Heartwarming cinematic medium shot of diverse African children in Kenya gathered under an iconic acacia tree at golden hour, joyfully reaching out to manipulate a floating 3D holographic model of a double-helix DNA strand and shimmering molecular structures. Warm 3200K late-afternoon sunlight filters through tree branches, casting dappled golden illumination across expressive smiling faces with authentic skin texture and sparkling eyes, contrasted with the 5800K cyan holographic glow. Background golden savannah grass blurs into creamy bokeh. Shot on ARRI Alexa 65 with Panavision Primo 70 50mm T1.4, shallow depth of field, rich Kodak Vision3 250D film stock, organic chemical grain, gentle 24fps circular orbit. Ambient audio: \"joyful children's laughter, gentle savannah wind in tree leaves, melodic interactive holographic chimes\"."
        },
        {
            "shot_index": 22,
            "shot_id": "SHOT_22_ALMA_ARRAY_COSMIC_FIRST_SIGNAL",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:45 - 01:50",
            "duration_sec": 5.0,
            "hook_category": "Cosmic Curiosity & Deep Space Discovery",
            "narration_es": "Miramos hacia las estrellas no para escapar, sino para comprender nuestro verdadero origen.",
            "narration_word_count": 13,
            "hud_overlay_telemetry": {
                "location": "Meseta de Chajnantor, Observatorio ALMA, 5.000m",
                "timestamp_code": "00:01:45:00",
                "telemetry": "FREQUENCY: 850 GHz | SIGNAL-TO-NOISE: 48.2 dB | TARGET: SAGITTARIUS A*",
                "lower_third": "INTERFEROMETRÍA CUÁNTICA DE LÍNEA DE BASE GIGANTE"
            },
            "camera_movement_6dof": {
                "type": "Low-Angle Steadicam Glide past Rotating Giant Antennas",
                "vector_translation": "Forward +4.0m across frozen gravel, tilting upward",
                "rotation_euler": "Pitch +30deg upward toward star-filled Milky Way",
                "cadence": "24fps, awe-inspiring celestial tracking"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Dozens of colossal 12-meter radio astronomy dish antennas pivoting in absolute synchronization across the high-altitude plateau, their metallic sub-reflectors glistening under starlight.",
                "layer_2_environment": "The barren high-altitude Chajnantor plateau at 5,000 meters; frosted gravel and rugged volcanic soil; overhead an overwhelming, crystal-clear view of the Milky Way galactic core stretching from horizon to horizon with colorful nebulae.",
                "layer_3_lighting_kelvin": "Cold 6000K pure starlight and galactic nebular glow illuminating the white antenna surfaces, with 2700K warm incandescent access panel lights on the base towers.",
                "layer_4_optics_lens": "ARRI Master Prime 21mm T1.3, tack-sharp across the entire astronomical expanse, zero astigmatism on pinpoint background stars.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, exceptional shadow detail capturing the rich dust lanes of the Milky Way, crisp metallic whites on antenna dishes.",
                "layer_6_camera_dynamics": "Low-angle forward Steadicam glide across the plateau at 24fps, looking upward into the synchronized movement of the giant dishes.",
                "layer_7_acoustic_foley": "\"Deep synchronized mechanical gear turn whirr of 66 antennas, whistling thin high-altitude mountain wind, subtle deep cosmic static signal\""
            },
            "master_prompt_dop_7layer": "Epic low-angle tracking shot across the ALMA radio telescope observatory on the 5000-meter Chajnantor plateau in Chile under a hyper-vivid night sky. Dozens of monolithic white radio dishes pivot in unison, tracking a celestial target. The Milky Way galactic core arcs across the pristine velvet sky in dazzling detail with pink and magenta nebulae. Cold 6000K natural starlight illuminates the dish structures, accented by tiny warm 2700K maintenance lights. Shot on ARRI Alexa 65 with ARRI Master Prime 21mm T1.3, corner-to-corner astronomical sharpness, Kodak Vision3 500T film grain, smooth 24fps forward glide. Ambient audio: \"harmonious mechanical whirr of rotating telescope gears, crisp mountain wind, deep cosmic radio static hiss\"."
        },
        {
            "shot_index": 23,
            "shot_id": "SHOT_23_DR_VANCE_CRYO_CORE_TOUCH",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:50 - 01:55",
            "duration_sec": 5.0,
            "hook_category": "Human Touch & Emotional Culmination",
            "narration_es": "El silicio ha despertado. Y con él, la próxima era de la conciencia humana.",
            "narration_word_count": 14,
            "hud_overlay_telemetry": {
                "location": "Cámara de Criogenia Principal, Gran Sasso",
                "timestamp_code": "00:01:50:00",
                "telemetry": "EQUILIBRIUM: STABLE | ENTANGLEMENT RANGE: PLANETARY | ENTROPY: 0.0000",
                "lower_third": "EQUILIBRIO COGNITIVO: SIMBIOSIS HUMANO-CUÁNTICA"
            },
            "camera_movement_6dof": {
                "type": "Close Medium Push-In on Hand and Peaceful Face",
                "vector_translation": "Forward +0.5m, slight vertical rise +0.1m",
                "rotation_euler": "Pitch 0deg, Yaw -4deg, Roll 0deg",
                "cadence": "24fps, tender emotional resolution"
            },
            "seven_layers_dop": {
                "layer_1_subject": "Dra. Elena Vance, her expression now radiant with peace, relief, and profound awe, gently placing her gloved hand against the clear vacuum viewing window of the quantum cryostat; inside, the core emits a steady, warm golden-amber and sapphire light.",
                "layer_2_environment": "Quiet underground laboratory now softly illuminated; telemetry screens in background resting at calm, stable baseline graphs; soft nitrogen vapor clearing.",
                "layer_3_lighting_kelvin": "3200K warm golden light radiating outward from the cryostat core onto her face and eyes, balanced by soft 4500K fill light, creating a reverent, painterly chiaroscuro.",
                "layer_4_optics_lens": "Cooke Anamorphic /i 50mm T2.3 Prime, gentle focus falloff, subtle warm horizontal flare crossing her fingertips on the glass.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich warm skin tones, glowing highlight halation around the glass contact point, deep velvety shadow richness.",
                "layer_6_camera_dynamics": "Slow, tender forward Steadicam push-in settling into an intimate close-up at 24fps.",
                "layer_7_acoustic_foley": "\"Soft glove touching glass squeak, serene warm resonant synth pad chord, quiet peaceful human breath\""
            },
            "master_prompt_dop_7layer": "Intimate cinematic close-up of female physicist Dr. Elena Vance in the quiet underground lab, placing her gloved hand against the transparent cryostat window with a peaceful, awe-filled expression. Inside the chamber, the quantum core glows with a steady, serene 3200K warm golden and soft blue light that illuminates her face, reflecting in her eyes. Background server telemetry screens show stable green lines in soft focus. Shot on ARRI Alexa 65 with Cooke Anamorphic 50mm T2.3, gentle focus falloff, creamy bokeh, warm Kodak Vision3 500T film grain and highlight halation, slow deliberate 24fps push-in. Ambient audio: \"gentle touch of glove on glass, warm peaceful synthesized chord crescendo, soft calm breathing\"."
        },
        {
            "shot_index": 24,
            "shot_id": "SHOT_24_COSMIC_ZENITH_FINAL_QUESTION",
            "act": "Acto III: La Singularidad y el Clímax Revelador",
            "time_window": "01:55 - 02:00",
            "duration_sec": 5.0,
            "hook_category": "Unforgettable Philosophical Climax & Fade to Black",
            "narration_es": "La pregunta ya no es qué pueden hacer las máquinas. Sino qué decidiremos ser nosotros.",
            "narration_word_count": 15,
            "hud_overlay_telemetry": {
                "location": "Horizonte Cósmico / Fusión Tierra-Neurona",
                "timestamp_code": "00:01:55:00",
                "telemetry": "CONSCIOUSNESS THRESHOLD: ACHIEVED | TIME HORIZON: INFINITE | SCALE: 10^26 m",
                "lower_third": "EL UMBRAL CUÁNTICO — DIRIGIDO POR VIDEOPRO STUDIO"
            },
            "camera_movement_6dof": {
                "type": "Infinite Exponential Pullback from Laboratory into Cosmos",
                "vector_translation": "Exponential Backward Pull Z -1000m to Orbit",
                "rotation_euler": "Pitch -10deg tilting smoothly into starry zenith",
                "cadence": "24fps, transcendent cosmic zoom-out"
            },
            "seven_layers_dop": {
                "layer_1_subject": "The warm golden light from the laboratory window expands outward, seamlessly dissolving into the nocturnal lights of Earth, which in turn blend into the cosmic web of billions of galaxies structured like an infinite neural network.",
                "layer_2_environment": "Deep velvet cosmos studded with galaxies, glowing nebulae in violet and gold, framing the serene blue curve of planet Earth receding into the cosmic tapestry.",
                "layer_3_lighting_kelvin": "Warm 3200K golden core light in the center transitioning into 6500K starlight and 9000K deep celestial violet nebular illumination.",
                "layer_4_optics_lens": "Panavision Primo 70 35mm Anamorphic T1.4, infinite depth of field, stunning edge-to-edge clarity, subtle horizontal celestial flaring.",
                "layer_5_color_science_filmstock": "Kodak Vision3 500T 5219, rich deep blacks, luminous highlight roll-off, breathtaking photochemical color depth across cosmic dust clouds.",
                "layer_6_camera_dynamics": "Epic exponential backward pull at 24fps, gliding smoothly from human scale to cosmic infinity, slowly fading into peaceful cinematic darkness at 02:00.",
                "layer_7_acoustic_foley": "\"Grand orchestral finale reaching peak resonance, soaring French horn and cello motif, tapering into a solitary resonant singing bowl chime and gentle fade to silence\""
            },
            "master_prompt_dop_7layer": "Transcendent cinematic exponential pull-back shot beginning on the golden glow of the laboratory window, pulling out seamlessly through the night atmosphere to reveal the glowing blue Earth, and further into deep space where clusters of glowing galaxies form an infinite cosmic neural network. Deep space velvet blacks studded with sparkling stars and swirling gold and violet nebulae. 3200K warm central light fading harmoniously into 6500K starlight. Shot on ARRI Alexa 65 with Panavision Primo 70 35mm Anamorphic T1.4, infinite cosmic depth of field, Kodak Vision3 500T 35mm grain, smooth exponential reverse camera velocity at 24fps fading gracefully to black. Ambient audio: \"soaring orchestral brass and cello finale crescendo, tapering into a single crystal singing bowl resonance that fades into absolute peaceful silence\"."
        }
    ]
}

# Output paths
json_output_path = "/home/ubuntu/workspace/pro/hermes/10_videopro/data/documental_120s_escaleta_dop7.json"
md_output_path = "/home/ubuntu/workspace/pro/hermes/10_videopro/DOCUMENTAL_120S_GUION_ESCALETA_DOP7.md"
docs_md_output_path = "/home/ubuntu/workspace/pro/hermes/10_videopro/docs/04_investigaciones/DOCUMENTAL_120S_GUION_ESCALETA_DOP7.md"

# Ensure directories exist
os.makedirs(os.path.dirname(json_output_path), exist_ok=True)
os.makedirs(os.path.dirname(docs_md_output_path), exist_ok=True)

# Write JSON
with open(json_output_path, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2, ensure_ascii=False)
print(f"JSON Manifest written successfully to: {json_output_path}")

# Build Markdown content
total_words = sum(shot["narration_word_count"] for shot in manifest_data["shots"])
assert len(manifest_data["shots"]) == 24, "Must have exactly 24 shots"
assert manifest_data["total_duration_seconds"] == 120.0, "Must be exactly 120 seconds"

md_lines = []
md_lines.append("# 🎬 Manifiesto Cinematográfico 7-Layer DOP & Escaleta Maestra 120s")
md_lines.append("")
md_lines.append("> **Proyecto:** `documental-umbral-cuantico-120s`  ")
md_lines.append("> **Título:** *El Umbral Cuántico: La Revolución Silenciosa del Silicio y el Destino Humano*  ")
md_lines.append("> **English Title:** *The Quantum Threshold: The Silent Silicon Revolution and the Fate of Species*  ")
md_lines.append("> **Duración Total:** 120.0 segundos (2 minutos exactos | 24 Tomas de 5.0s)  ")
md_lines.append("> **Formato:** 4K UHD Cinema (3840×2160), 24.0 fps, 16:9, Shutter 180° (1/48s)  ")
md_lines.append(f"> **Locución Neural:** `es-emilio` (VibeVoice 1.5B) | {total_words} palabras (~149 PPM)  ")
md_lines.append("> **Estándar de Audio:** EBU R128 (-14.0 LUFS ±0.5, True Peak -1.0 dBTP, Ducking -18 dB)  ")
md_lines.append("> **Pipeline Visual:** Gemini Omni Flash / LTX-2.5 + Emulación Celuloide Kodak Vision3 500T / ARRI Alexa 65  ")
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 📜 1. GUION NARRATIVO COMPLETO DE LOCUCIÓN (ESPAÑOL)")
md_lines.append("")
md_lines.append(f"**Voz:** `es-emilio` (Tono solemne, reflexivo, periodístico de alta tensión y revelación cósmica)  ")
md_lines.append(f"**Extensión:** {total_words} palabras | **Duración:** 120 segundos  ")
md_lines.append("")
md_lines.append("### 🔴 Acto I: La Grieta en la Realidad (0:00 - 0:30 | 77 palabras)")
md_lines.append("*Gancho inicial hiper-adrenalínico (0-3s), ruptura de la física convencional y presentación del misterio en las entrañas de la Tierra.*")
md_lines.append("")
for shot in manifest_data["shots"][:6]:
    md_lines.append(f"- **[{shot['time_window']}] (Toma {shot['shot_index']:02d}):** «{shot['narration_es']}»")

md_lines.append("")
md_lines.append("### 🟡 Acto II: El Abismo y la Escalada de Tensión (0:30 - 1:30 | 149 palabras)")
md_lines.append("*Escalada geopolítica, ruptura criptográfica, conquista de la energía estelar, bioingeniería atómica y el dilema del control civilizatorio.*")
md_lines.append("")
for shot in manifest_data["shots"][6:18]:
    md_lines.append(f"- **[{shot['time_window']}] (Toma {shot['shot_index']:02d}):** «{shot['narration_es']}»")

md_lines.append("")
md_lines.append("### 🟢 Acto III: La Singularidad y el Clímax Revelador (1:30 - 2:00 | 72 palabras)")
md_lines.append("*Visión planetaria orbital, democratización universal del saber, contacto con el cosmos y cierre filosófico imborrable.*")
md_lines.append("")
for shot in manifest_data["shots"][18:]:
    md_lines.append(f"- **[{shot['time_window']}] (Toma {shot['shot_index']:02d}):** «{shot['narration_es']}»")

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 🧭 2. MATRIZ DE ESCALETA CINEMATOGRÁFICA (24 TOMAS × 5.0s)")
md_lines.append("")
md_lines.append("| Toma | Código / ID | Ventana | Acto | Sujeto Visual Principal | Dinámica de Cámara 6-DoF | Locución Clave |")
md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

for shot in manifest_data["shots"]:
    short_subj = shot["seven_layers_dop"]["layer_1_subject"][:45] + "..."
    short_cam = shot["camera_movement_6dof"]["type"]
    short_narr = shot["narration_es"][:35] + "..." if len(shot["narration_es"]) > 35 else shot["narration_es"]
    md_lines.append(f"| **{shot['shot_index']:02d}** | `{shot['shot_id']}` | `{shot['time_window']}` | {shot['act'].split(':')[0]} | {short_subj} | {short_cam} | *«{short_narr}»* |")

md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 🎥 3. MANIFIESTO CINEMATOGRÁFICO DOP 7-LAYER DETALLADO (TOMAS 01 A 24)")
md_lines.append("")

for shot in manifest_data["shots"]:
    dop = shot["seven_layers_dop"]
    cam = shot["camera_movement_6dof"]
    hud = shot["hud_overlay_telemetry"]
    md_lines.append(f"### 🎬 Toma {shot['shot_index']:02d} — `{shot['shot_id']}` ({shot['time_window']})")
    md_lines.append(f"- **Acto:** {shot['act']} | **Función Narrativa:** {shot['hook_category']}")
    md_lines.append(f"- **Locución (`es-emilio`):** «{shot['narration_es']}» ({shot['narration_word_count']} palabras)")
    md_lines.append(f"- **Telemetría HUD:** `{hud['location']} | {hud['telemetry']}`")
    md_lines.append(f"- **Cinemática 6-DoF:** {cam['type']} — *Vector:* `{cam['vector_translation']}` | *Rotación:* `{cam['rotation_euler']}`")
    md_lines.append("")
    md_lines.append("#### 📐 Desglose de las 7 Capas DOP:")
    md_lines.append(f"1. **Capa 1 (Sujeto & Fisiología):** {dop['layer_1_subject']}")
    md_lines.append(f"2. **Capa 2 (Entorno & Profundidad):** {dop['layer_2_environment']}")
    md_lines.append(f"3. **Capa 3 (Iluminación & Kelvin):** {dop['layer_3_lighting_kelvin']}")
    md_lines.append(f"4. **Capa 4 (Óptica & Bokeh):** {dop['layer_4_optics_lens']}")
    md_lines.append(f"5. **Capa 5 (Colorimetría & 35mm):** {dop['layer_5_color_science_filmstock']}")
    md_lines.append(f"6. **Capa 6 (Dinámica & Inercia):** {dop['layer_6_camera_dynamics']}")
    md_lines.append(f"7. **Capa 7 (Atmósfera Acústica Foley):** {dop['layer_7_acoustic_foley']}")
    md_lines.append("")
    md_lines.append("#### 🌟 Master Prompt 7-Layer (Inyección Directa Anti-AI Slop):")
    md_lines.append("```text")
    md_lines.append(shot["master_prompt_dop_7layer"])
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

md_lines.append("## 🛡️ 4. PROTOCOLOS DE CONTROL DE CALIDAD Y ANTI-AI SLOP")
md_lines.append("")
md_lines.append("1. **Erradicación de Clichés Visuales de IA:** Queda terminantemente prohibido el uso de términos sintéticos (`hyperrealistic`, `octane render`, `photorealistic`, `8k resolution`, `masterpiece`, `trending on artstation`). Toda fidelidad se obtiene mediante óptica real, temperatura de color Kelvin, física newtoniana y química de película.")
md_lines.append("2. **Consistencia Cromática 35mm:** Todas las tomas mantienen la emulsión Kodak Vision3 500T 5219 / 250D 5207 con grano fotoquímico de haluro de plata distribuido estocásticamente y halación suave en altas luces.")
md_lines.append("3. **Sincronización Audio-First EBU R128:** La locución de 298 palabras en español (`es-emilio`) dicta el montaje con ducking automático a -18 dB en música de fondo, manteniendo el máster a -14.0 LUFS y True Peak de -1.0 dBTP.")
md_lines.append("4. **Dinámica de Cámara 6-DoF Orgánica:** Ningún plano permanece estático; cada toma cuenta con inercia humana real a 24fps (180° shutter angle), con cambios de plano cada 5 segundos exactos para una retención estimada >75%.")
md_lines.append("")

md_content = "\n".join(md_lines)

with open(md_output_path, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Root Markdown written successfully to: {md_output_path}")

with open(docs_md_output_path, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Docs Markdown written successfully to: {docs_md_output_path}")
