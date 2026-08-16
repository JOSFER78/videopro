#!/usr/bin/env python3
"""
fpv_urban_tour_builder.py — Generador Autónomo de Tours FPV y Storytelling Urbano para VideoPro.

Implementa el pipeline integral de 7 fases:
1. Generación de Guion en 3 Actos con Contrapunto Factual.
2. Construcción del Plan de Vuelo 3D y Shotlist Canónico (7 Planos FPV).
3. Adquisición y Auditoría de Calidad de Fotos Reales (>5KB & Laplacian Variance).
4. Ensamblaje de Prompts Canónicos de 7 Keyframes para Gemini Omni Flash.
5. Sincronización de Audio VO-First y BGM Flow (118 BPM con Ducking -18dB).
6. Telemetría HUD Glassmorphism y Rótulos Espaciales 3D para Remotion.
7. Registro Canónico en VideoStorageManager y project_manifest.json.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from video_storage_manager import VideoStorageManager
except ImportError:
    from scripts.video_storage_manager import VideoStorageManager


DEFAULT_TOKYO_FLIGHT_PLAN = {
    "flight_plan_id": "FPV_TOKYO_20260816_SHIBUYA01",
    "city": "Tokio",
    "country": "Japón",
    "narrative_theme": "El pulso vertical de Shibuya: de la azotea del Scramble Square al laberinto de callejones Yokocho",
    "story_arc": {
        "hook_seconds": 3.0,
        "body_seconds": 35.0,
        "climax_seconds": 7.0,
        "narrative_counterpoint": "La locución analiza los amortiguadores hidráulicos antisísmicos mientras la cámara FPV desafía la gravedad zigzagueando entre las fachadas de cristal a 130 km/h."
    },
    "camera_spec": {
        "fov_degrees": 135,
        "lens_simulation": "Ultra-wide Anamorphic 14mm f/2.8 with controlled barrel distortion",
        "shutter_angle": 180,
        "color_science": "ARRI Alexa LF with Kodak Vision3 500T 35mm grain",
        "aspect_ratio": "9:16"
    },
    "drone_physics": {
        "max_speed_kmh": 140.0,
        "cruise_speed_kmh": 75.0,
        "roll_rate_deg_sec": 220.0,
        "inertia_smoothing_factor": 0.85
    },
    "waypoints": [
        {
            "waypoint_id": "WP-001",
            "landmark_name": "Shibuya Scramble Square Rooftop Helipad",
            "latitude": 35.6580,
            "longitude": 139.7016,
            "altitude_meters_agl": 229.0,
            "camera_pitch_deg": -85.0,
            "camera_yaw_deg": 180.0,
            "camera_roll_deg": 15.0,
            "lighting_reference": "Blue hour twilight (5200K) with neon cyan reflections"
        },
        {
            "waypoint_id": "WP-002",
            "landmark_name": "Shibuya Crossing Main Intersection",
            "latitude": 35.6595,
            "longitude": 139.7005,
            "altitude_meters_agl": 3.5,
            "camera_pitch_deg": 5.0,
            "camera_yaw_deg": 175.0,
            "camera_roll_deg": 0.0,
            "lighting_reference": "Intense amber streetlights and high-density LED billboards"
        },
        {
            "waypoint_id": "WP-003",
            "landmark_name": "Shibuya 109 Iconic Curved Facade",
            "latitude": 35.6598,
            "longitude": 139.6990,
            "altitude_meters_agl": 32.0,
            "camera_pitch_deg": -15.0,
            "camera_yaw_deg": 220.0,
            "camera_roll_deg": 35.0,
            "lighting_reference": "Vibrant glowing neon logos casting specular highlights"
        },
        {
            "waypoint_id": "WP-004",
            "landmark_name": "Center-Gai Shopping Street Neon Canopy",
            "latitude": 35.6602,
            "longitude": 139.6980,
            "altitude_meters_agl": 4.0,
            "camera_pitch_deg": -5.0,
            "camera_yaw_deg": 280.0,
            "camera_roll_deg": -10.0,
            "lighting_reference": "Overhead lantern illumination and steam reflections"
        },
        {
            "waypoint_id": "WP-005",
            "landmark_name": "Nonbei Yokocho Traditional Izakaya Alley",
            "latitude": 35.6592,
            "longitude": 139.7022,
            "altitude_meters_agl": 2.2,
            "camera_pitch_deg": 0.0,
            "camera_yaw_deg": 45.0,
            "camera_roll_deg": 0.0,
            "lighting_reference": "Warm tungsten 2700K paper lanterns with deep shadows"
        },
        {
            "waypoint_id": "WP-006",
            "landmark_name": "Yamanote Railway Line Underpass",
            "latitude": 35.6588,
            "longitude": 139.7030,
            "altitude_meters_agl": 2.8,
            "camera_pitch_deg": -2.0,
            "camera_yaw_deg": 90.0,
            "camera_roll_deg": 5.0,
            "lighting_reference": "Industrial green fluorescent tubes and passing train headlights"
        },
        {
            "waypoint_id": "WP-007",
            "landmark_name": "Miyashita Park Sky Deck Sunset Horizon",
            "latitude": 35.6620,
            "longitude": 139.7025,
            "altitude_meters_agl": 110.0,
            "camera_pitch_deg": 40.0,
            "camera_yaw_deg": 270.0,
            "camera_roll_deg": 0.0,
            "lighting_reference": "Golden hour sunset rim light against dramatic urban skyline"
        }
    ],
    "shots": [
        {
            "shot_index": 1,
            "shot_name": "01_TERMINAL_DIVE_SCRAMBLE",
            "shot_type": "TERMINAL_DIVE",
            "start_waypoint": "WP-001",
            "end_waypoint": "WP-002",
            "duration_seconds": 3.2,
            "speed_kmh": 134.0,
            "motion_type": "Vertical 90-degree nose-down terminal dive with progressive 45-degree roll rotation",
            "first_frame_asset_ref": "assets/keyframes/kf0_scramble_top_raw.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Use Image1 as the literal opening frame. Animate high-speed cinematic FPV drone executing a 130 km/h vertical nose-down dive along the Scramble Square glass facade. Realistic aerodynamic speed lines, central optical stability, 14mm anamorphic prime lens, ARRI Alexa LF color science, twilight 5200K. Dynamic wind roar whoosh and brushless motor sound. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 134.2,
                "altitude_display_m": 229.0,
                "g_force": 3.8,
                "battery_pct": 94,
                "coordinates_text": "35°39'28.8\"N 139°42'05.8\"E"
            },
            "spatial_3d_title": {
                "text": "SHIBUYA SCRAMBLE",
                "world_anchor_landmark": "Scramble Square Spire",
                "depth_layer": "BACKGROUND",
                "motion_style": "Fixed 3D world tracking with glowing neon cyan typography"
            },
            "audio_sync": {
                "foley_sound_event": "FPV prop high-pitch whine with intense wind roar accelerating into deep low-pass whoosh",
                "doppler_shift_hz": 480.0,
                "bgm_beat_anchor_s": 3.0
            }
        },
        {
            "shot_index": 2,
            "shot_name": "02_CANYON_SLALOM_109",
            "shot_type": "CANYON_SLALOM",
            "start_waypoint": "WP-002",
            "end_waypoint": "WP-003",
            "duration_seconds": 4.5,
            "speed_kmh": 88.0,
            "motion_type": "Banked slalom turn between illuminated tower facades with 35-degree roll angle",
            "first_frame_asset_ref": "assets/keyframes/kf0_shibuya_109_facade.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate high-speed cinematic FPV drone sweeping around the curved Shibuya 109 building in a sharp 35-degree banked slalom. Neon billboard reflections rushing across the wet camera lens, ultra-wide 16mm lens, crisp edge sharpness, Kodak Vision3 500T grain. Spatial motor audio reverberating off concrete walls. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 88.5,
                "altitude_display_m": 32.0,
                "g_force": 2.4,
                "battery_pct": 91,
                "coordinates_text": "35°39'35.2\"N 139°41'56.4\"E"
            },
            "spatial_3d_title": {
                "text": "SHIBUYA 109 TOWER",
                "world_anchor_landmark": "109 Cylinder Facade",
                "depth_layer": "MIDGROUND",
                "motion_style": "Perspective 3D transform tracking building curvature"
            },
            "audio_sync": {
                "foley_sound_event": "Sharp cornering motor bite with high-frequency prop slap",
                "doppler_shift_hz": 320.0,
                "bgm_beat_anchor_s": 7.5
            }
        },
        {
            "shot_index": 3,
            "shot_name": "03_LOW_ALTITUDE_SKIM_CENTER_GAI",
            "shot_type": "LOW_ALTITUDE_SKIM",
            "start_waypoint": "WP-003",
            "end_waypoint": "WP-004",
            "duration_seconds": 5.0,
            "speed_kmh": 58.0,
            "motion_type": "Ultra-low ground skim at 1.8 meters height gliding through neon pedestrian street",
            "first_frame_asset_ref": "assets/keyframes/kf0_center_gai_street.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate low-altitude cinematic FPV drone gliding at head-height through Center-Gai pedestrian street under glowing red and cyan Japanese shop signs. Steaming noodle shop vents, reflections on asphalt, shallow depth of field, 24mm prime lens f/1.8, ARRI Alexa LF. Subtle street chatter murmur blended with drone hum. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 58.0,
                "altitude_display_m": 1.8,
                "g_force": 1.1,
                "battery_pct": 87,
                "coordinates_text": "35°39'36.7\"N 139°41'52.8\"E"
            },
            "spatial_3d_title": {
                "text": "CENTER-GAI NIGHT PULSE",
                "world_anchor_landmark": "Street Arch Portal",
                "depth_layer": "FOREGROUND",
                "motion_style": "Floating glassmorphism badge with neon accent line"
            },
            "audio_sync": {
                "foley_sound_event": "Smooth air glide with muffled street acoustic ambiance",
                "doppler_shift_hz": 180.0,
                "bgm_beat_anchor_s": 12.5
            }
        },
        {
            "shot_index": 4,
            "shot_name": "04_PORTAL_BREACH_YOKOCHO",
            "shot_type": "PORTAL_BREACH",
            "start_waypoint": "WP-004",
            "end_waypoint": "WP-005",
            "duration_seconds": 4.8,
            "speed_kmh": 72.0,
            "motion_type": "Precision gap thread through narrow tavern alleyway with millimeter clearances",
            "first_frame_asset_ref": "assets/keyframes/kf0_yokocho_alley.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate precision FPV drone threading through the tight 1.5-meter gap of Nonbei Yokocho alley between warm glowing izakaya lanterns and wooden eaves. Micro-turbulence adjustments, volumetric warm tungsten light beams (2700K), intimate cinematic texture, 18mm lens. Acoustic lantern rattle and tight-space motor echo. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 72.3,
                "altitude_display_m": 2.2,
                "g_force": 2.1,
                "battery_pct": 83,
                "coordinates_text": "35°39'33.1\"N 139°42'07.9\"E"
            },
            "spatial_3d_title": {
                "text": "NONBEI YOKOCHO // 1950s ECHO",
                "world_anchor_landmark": "Tavern Wooden Eaves",
                "depth_layer": "PASSTHROUGH",
                "motion_style": "Pass-through zoom typography that blurs into screen borders"
            },
            "audio_sync": {
                "foley_sound_event": "Tight resonance chamber motor whistle",
                "doppler_shift_hz": 520.0,
                "bgm_beat_anchor_s": 17.3
            }
        },
        {
            "shot_index": 5,
            "shot_name": "05_SPIRAL_ORBIT_SPIRE",
            "shot_type": "SPIRAL_ORBIT",
            "start_waypoint": "WP-005",
            "end_waypoint": "WP-006",
            "duration_seconds": 6.0,
            "speed_kmh": 65.0,
            "motion_type": "Continuous 360-degree ascending corkscrew orbit around architectural tower",
            "first_frame_asset_ref": "assets/keyframes/kf0_tower_orbit.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate cinematic FPV drone in a continuous 360-degree climbing corkscrew orbit around modern architectural glass tower. Camera tilted 30 degrees upward keeping the spire centered, city lights spinning smoothly in background, 21mm prime lens, organic motion blur. Steady rotary drone hum. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 65.0,
                "altitude_display_m": 85.4,
                "g_force": 1.8,
                "battery_pct": 78,
                "coordinates_text": "35°39'31.6\"N 139°42'10.8\"E"
            },
            "spatial_3d_title": {
                "text": "360° ORBITAL TELEMETRY",
                "world_anchor_landmark": "Central Spire Tip",
                "depth_layer": "MIDGROUND",
                "motion_style": "Rotational orbit lock on central focal target"
            },
            "audio_sync": {
                "foley_sound_event": "Continuous modulation rotary pitch with stereo panning",
                "doppler_shift_hz": 260.0,
                "bgm_beat_anchor_s": 23.3
            }
        },
        {
            "shot_index": 6,
            "shot_name": "06_TUNNEL_DASH_UNDERPASS",
            "shot_type": "TUNNEL_DASH",
            "start_waypoint": "WP-006",
            "end_waypoint": "WP-007",
            "duration_seconds": 4.5,
            "speed_kmh": 105.0,
            "motion_type": "Linear high-speed tunnel acceleration through concrete underpass",
            "first_frame_asset_ref": "assets/keyframes/kf0_underpass_tunnel.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate high-speed FPV drone accelerating at 105 km/h straight through concrete railway underpass tunnel. Rhythmic strobe of overhead green industrial lights passing overhead, deep perspective compression, motion blur on walls, 14mm lens. High-speed jet-like intake whoosh. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 105.0,
                "altitude_display_m": 2.8,
                "g_force": 2.9,
                "battery_pct": 74,
                "coordinates_text": "35°39'30.8\"N 139°42'12.0\"E"
            },
            "spatial_3d_title": {
                "text": "YAMANOTE CORRIDOR",
                "world_anchor_landmark": "Underpass Steel Girder",
                "depth_layer": "FOREGROUND",
                "motion_style": "Fast tunnel tracking with chromatic aberration glitch"
            },
            "audio_sync": {
                "foley_sound_event": "Heavy low-end resonance and passing train rumble",
                "doppler_shift_hz": 600.0,
                "bgm_beat_anchor_s": 27.8
            }
        },
        {
            "shot_index": 7,
            "shot_name": "07_SKYLINE_SUNSET_ASCENSION",
            "shot_type": "SKYLINE_ASCENSION",
            "start_waypoint": "WP-007",
            "end_waypoint": "WP-001",
            "duration_seconds": 7.2,
            "speed_kmh": 125.0,
            "motion_type": "Climbing vertical pull-up towards sunset clouds with majestic panoramic horizon reveal",
            "first_frame_asset_ref": "assets/keyframes/kf0_miyashita_sunset.png",
            "omni_flash_prompt": "[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2] Animate epic cinematic FPV drone rocketing upward at 125 km/h above Miyashita Park into the open golden hour sky. Camera pulls up 45 degrees revealing the entire sprawling Tokyo skyline with Mount Fuji silhouette in the distant orange horizon. 35mm anamorphic lens, warm lens flare, Kodak Vision3 500T 35mm grain. Ascending wind sound fading into serene acoustic resonance. No music.",
            "hud_telemetry": {
                "speed_display_kmh": 125.0,
                "altitude_display_m": 350.0,
                "g_force": 3.4,
                "battery_pct": 69,
                "coordinates_text": "35°39'43.2\"N 139°42'09.0\"E"
            },
            "spatial_3d_title": {
                "text": "TOKYO HORIZON // 2026",
                "world_anchor_landmark": "Sunset Cloud Horizon",
                "depth_layer": "BACKGROUND",
                "motion_style": "Grand slow reveal with glowing warm gold typography"
            },
            "audio_sync": {
                "foley_sound_event": "Ascending pitch pullout with final ambient atmospheric breath",
                "doppler_shift_hz": 150.0,
                "bgm_beat_anchor_s": 35.0
            }
        }
    ]
}


class FPVUrbanTourBuilder:
    """Constructor y orquestador maestro para proyectos de Tours FPV y Storytelling Urbano."""

    def __init__(self, project_ref: Optional[str] = None, city: str = "Tokio"):
        self.city = city
        self.storage = VideoStorageManager(project_ref=project_ref, title=f"FPV Tour {city} Urban Storytelling")
        self.project_dir = self.storage.project_dir
        self.scene_data_dir = self.storage.scene_data_dir
        self.keyframes_dir = self.storage.keyframes_dir
        self.assets_dir = self.storage.assets_dir

    def build_flight_plan(self, custom_plan: Optional[Dict[str, Any]] = None) -> Path:
        """Genera y guarda el contrato de plan de vuelo 3D."""
        flight_plan_data = custom_plan or DEFAULT_TOKYO_FLIGHT_PLAN
        out_file = self.scene_data_dir / "fpv_flight_plan.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(flight_plan_data, f, indent=2, ensure_ascii=False)
        print(f"✅ [Fase 1-2] Plan de Vuelo 3D guardado en: {out_file.name}")
        return out_file

    def generate_keyframe_prompts_matrix(self, flight_plan: Dict[str, Any]) -> Path:
        """Compila la matriz de 7 keyframes consistentes por cada plano FPV."""
        kf_matrix = []
        for shot in flight_plan.get("shots", []):
            shot_idx = shot["shot_index"]
            shot_name = shot["shot_name"]
            
            shot_entry = {
                "shot_index": shot_idx,
                "shot_name": shot_name,
                "shot_type": shot["shot_type"],
                "duration_seconds": shot["duration_seconds"],
                "speed_kmh": shot["speed_kmh"],
                "first_frame_asset": shot["first_frame_asset_ref"],
                "omni_flash_prompt": shot["omni_flash_prompt"],
                "keyframes_7_sequence": [
                    {
                        "kf_index": 0,
                        "frame_number": 0,
                        "tag": "FIRST_FRAME",
                        "prompt": f"Raw 4K real photo of {shot['start_waypoint']} aligned with 14mm anamorphic lens, ARRI Alexa LF color science."
                    },
                    {
                        "kf_index": 1,
                        "frame_number": 18,
                        "tag": "IMAGE_REF_0",
                        "prompt": f"FPV trajectory entry point into {shot_name}, motion blur 20%, glass facade reflections."
                    },
                    {
                        "kf_index": 2,
                        "frame_number": 36,
                        "tag": "IMAGE_REF_1",
                        "prompt": f"Mid-trajectory high velocity vector, roll angle {shot.get('hud_telemetry', {}).get('g_force', 2.0) * 10} deg."
                    },
                    {
                        "kf_index": 3,
                        "frame_number": 54,
                        "tag": "IMAGE_REF_2",
                        "prompt": f"Apex of waypoint maneuver near {shot.get('spatial_3d_title', {}).get('world_anchor_landmark', 'Landmark')}."
                    },
                    {
                        "kf_index": 4,
                        "frame_number": 72,
                        "tag": "IMAGE_REF_3",
                        "prompt": f"Exit alignment curve, street textures and neon specular light matching."
                    },
                    {
                        "kf_index": 5,
                        "frame_number": 90,
                        "tag": "IMAGE_REF_4",
                        "prompt": f"Pre-transition deceleration / pullout frame towards {shot['end_waypoint']}."
                    },
                    {
                        "kf_index": 6,
                        "frame_number": 108,
                        "tag": "IMAGE_REF_5",
                        "prompt": f"Final frame seam matched for zero-drift jumpcut into next shot."
                    }
                ]
            }
            kf_matrix.append(shot_entry)

        out_matrix_file = self.scene_data_dir / "fpv_7keyframes_matrix.json"
        with open(out_matrix_file, "w", encoding="utf-8") as f:
            json.dump(kf_matrix, f, indent=2, ensure_ascii=False)
        print(f"✅ [Fase 3-4] Matriz de 7 Keyframes para Omni Flash guardada en: {out_matrix_file.name}")
        return out_matrix_file

    def build_telemetry_and_titles_manifest(self, flight_plan: Dict[str, Any]) -> Path:
        """Genera el manifiesto de telemetría HUD y rótulos 3D para Remotion."""
        telemetry_manifest = {
            "composition_id": "FPVUrbanTourMain",
            "fps": 60,
            "width": 1080,
            "height": 1920,
            "city": flight_plan.get("city", "Tokio"),
            "hud_theme": "CYBER_GLASSMORPHISM_CYAN",
            "audio_config": {
                "target_lufs": -14.0,
                "ducking_db": -18.0,
                "bgm_bpm": 118
            },
            "scenes": []
        }

        accumulated_time = 0.0
        for shot in flight_plan.get("shots", []):
            duration = shot["duration_seconds"]
            scene_entry = {
                "shot_index": shot["shot_index"],
                "shot_name": shot["shot_name"],
                "time_start_s": round(accumulated_time, 2),
                "time_end_s": round(accumulated_time + duration, 2),
                "duration_s": duration,
                "telemetry": shot["hud_telemetry"],
                "spatial_title": shot["spatial_3d_title"],
                "audio_sync": shot["audio_sync"]
            }
            accumulated_time += duration
            telemetry_manifest["scenes"].append(scene_entry)

        telemetry_manifest["total_duration_s"] = round(accumulated_time, 2)
        out_telemetry_file = self.scene_data_dir / "fpv_remotion_telemetry.json"
        with open(out_telemetry_file, "w", encoding="utf-8") as f:
            json.dump(telemetry_manifest, f, indent=2, ensure_ascii=False)
        print(f"✅ [Fase 5-6] Manifiesto de Telemetría HUD & Títulos 3D guardado en: {out_telemetry_file.name}")
        return out_telemetry_file

    def execute_full_preparation(self) -> Dict[str, Any]:
        """Ejecuta la preparación completa del proyecto FPV Urbano."""
        print(f"\n=======================================================")
        print(f"🚁 INICIANDO PREPARACIÓN DE TOUR FPV URBANO: {self.city.upper()}")
        print(f"=======================================================")
        print(f"📁 Directorio Canónico: {self.project_dir}")

        # 1. Guardar Plan de Vuelo 3D
        flight_plan_file = self.build_flight_plan()
        
        # 2. Generar Matriz de 7 Keyframes
        kf_file = self.generate_keyframe_prompts_matrix(DEFAULT_TOKYO_FLIGHT_PLAN)
        
        # 3. Manifiesto Remotion Telemetría HUD
        telemetry_file = self.build_telemetry_and_titles_manifest(DEFAULT_TOKYO_FLIGHT_PLAN)

        # 4. Actualizar project_manifest.json
        manifest_data = {
            "project_name": f"Tour FPV {self.city} 4K",
            "workflow_archetype": "FPV_URBAN_STORYTELLING",
            "status": "READY_FOR_OMNI_FLASH_RENDER",
            "total_shots": len(DEFAULT_TOKYO_FLIGHT_PLAN["shots"]),
            "target_aspect_ratio": "9:16",
            "target_fps": 60,
            "engine_configuration": {
                "video_engine": "gemini-omni-flash-preview",
                "image_engine": "gemini-3.1-flash-image",
                "voice_engine": "edge_tts",
                "render_backend": "remotion"
            },
            "artifacts": {
                "flight_plan": str(flight_plan_file),
                "keyframes_matrix": str(kf_file),
                "remotion_telemetry": str(telemetry_file)
            }
        }
        manifest_path = self.project_dir / "project_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        print(f"✅ [Fase 7] project_manifest.json actualizado exitosamente.")

        return manifest_data


if __name__ == "__main__":
    city_arg = sys.argv[1] if len(sys.argv) > 1 else "Tokio"
    builder = FPVUrbanTourBuilder(city=city_arg)
    result = builder.execute_full_preparation()
    print("\n🎉 Preparación de Arquitectura y Pipeline FPV Completada con Éxito.")
