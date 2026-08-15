#!/usr/bin/env python3
"""
test_unified_scripts.py — Batería de Pruebas Unitarias para Scripts Unificados con VideoStorageManager.
===================================================================================================
Skill: videopro (Hermes Autonomous Video Engine)
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from video_storage_manager import VideoStorageManager


class TestUnifiedScripts(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="test_videopro_unified_")
        self.storage_root = Path(self.tmp_dir) / "projects"
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.manager = VideoStorageManager(
            storage_root=self.storage_root,
            title="Test Unified Project",
            version="v1",
        )
        self.project = self.manager._get_active()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_download_clips_integration(self):
        """Verifica que download_clips guarde y registre activos correctamente en el proyecto."""
        from scripts.download_clips import download_clip

        # Crear activo de prueba de >5KB
        source_file = Path(self.tmp_dir) / "sample_clip.mp4"
        source_file.write_bytes(b"0" * 8192)

        res = download_clip(
            source=str(source_file),
            project_ref=str(self.project.version_dir),
            filename="test_broll_clip.mp4",
            category="broll",
            engine="gemini-omni-flash-preview",
            prompt="A test cinematic shot",
        )

        self.assertEqual(res["filename"], "test_broll_clip.mp4")
        self.assertTrue(Path(res["path"]).exists())
        self.assertGreaterEqual(Path(res["path"]).stat().st_size, 5120)

        # Verificar que el activo esté registrado en manifest.json
        manifest = self.project.load_manifest()
        clips = manifest.get("clips_registry", [])
        registered_paths = [c.get("path") for c in clips]
        self.assertIn(str(res["path"]), registered_paths)

    def test_render_vertical_video_integration(self):
        """Verifica render_vertical_video con imágenes y audio de prueba sintéticos."""
        from scripts.render_vertical_video import render_vertical_video

        # Crear imágenes de escena de >5KB
        flow_dir = self.project.flow_images_dir
        flow_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, 3):
            img_path = flow_dir / f"flow_scene_{i}.png"
            cmd = f'ffmpeg -y -loglevel error -f lavfi -i color=c=red:s=1080x1920:d=1 -vframes 1 "{img_path}"'
            subprocess.run(cmd, shell=True, check=True)

        # Crear audio de prueba de 2 segundos
        audio_dir = self.project.audio_dir
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / "narration.wav"
        cmd_audio = f'ffmpeg -y -loglevel error -f lavfi -i sine=frequency=440:duration=2 "{audio_path}"'
        subprocess.run(cmd_audio, shell=True, check=True)

        res = render_vertical_video(
            project_ref=str(self.project.version_dir),
            output_filename="test_vertical.mp4",
        )

        self.assertEqual(res["filename"], "test_vertical.mp4")
        self.assertTrue(Path(res["path"]).exists())
        self.assertGreaterEqual(Path(res["path"]).stat().st_size, 5120)

        manifest = self.project.load_manifest()
        exports = manifest.get("exports_registry", [])
        self.assertTrue(any(e.get("path") == str(res["path"]) for e in exports))

    def test_render_from_plan_integration(self):
        """Verifica render_from_plan con scenes.json sintético."""
        from scripts.render_from_plan import render_project_from_plan

        # Escribir scenes.json
        scenes_data = {
            "scenes": [
                {
                    "id": 1,
                    "title": "Escena de prueba 1",
                    "duration_seconds": 1.5,
                    "image": "flow_scene_1.png",
                    "audio": "vo_scene_1.wav"
                }
            ]
        }
        with open(self.project.scenes_path, "w", encoding="utf-8") as f:
            json.dump(scenes_data, f, indent=2)

        # Crear imagen y audio de escena
        img_path = self.project.flow_images_dir / "flow_scene_1.png"
        cmd_img = f'ffmpeg -y -loglevel error -f lavfi -i color=c=blue:s=1920x1080:d=1 -vframes 1 "{img_path}"'
        subprocess.run(cmd_img, shell=True, check=True)

        audio_path = self.project.audio_dir / "vo_scene_1.wav"
        cmd_aud = f'ffmpeg -y -loglevel error -f lavfi -i sine=frequency=880:duration=1.5 "{audio_path}"'
        subprocess.run(cmd_aud, shell=True, check=True)

        res = render_project_from_plan(
            plan_path_or_slug=str(self.project.version_dir),
            output_filename="master_from_plan.mp4"
        )

        self.assertEqual(res["filename"], "master_from_plan.mp4")
        self.assertTrue(Path(res["path"]).exists())
        self.assertGreaterEqual(Path(res["path"]).stat().st_size, 5120)

        manifest = self.project.load_manifest()
        self.assertEqual(manifest["pipeline_lifecycle"]["phase_5_render_and_composition"]["status"], "completed")

    def test_render_remotion_tsconfig_configuration(self):
        """Verifica que configure_remotion_tsconfig configure tsconfig.json correctamente."""
        from scripts.render_remotion import configure_remotion_tsconfig

        tsconfig_path = configure_remotion_tsconfig(self.project.src_dir)
        self.assertTrue(tsconfig_path.exists())
        with open(tsconfig_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("compilerOptions", {}).get("jsx"), "react-jsx")


if __name__ == "__main__":
    unittest.main()
