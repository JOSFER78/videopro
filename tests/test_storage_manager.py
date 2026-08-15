#!/usr/bin/env python3
"""
test_storage_manager.py — Test suite for unified VideoStorageManager.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from video_storage_manager import VideoStorageManager, VideoProject, MIN_ASSET_SIZE_BYTES


class TestVideoStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_root = tempfile.mkdtemp(prefix="videopro_test_storage_")
        self.mgr = VideoStorageManager(storage_root=self.temp_root)

    def tearDown(self):
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_project_initialization_and_hierarchy(self):
        proj = self.mgr.init_project("Test Neural Documentary", slug="neural-doc")
        self.assertTrue(proj.version_dir.exists())
        self.assertTrue(proj.assets_dir.exists())
        self.assertTrue(proj.photos_dir.exists())
        self.assertTrue(proj.audio_dir.exists())
        self.assertTrue(proj.renders_dir.exists())
        self.assertTrue(proj.exports_dir.exists())
        self.assertTrue(proj.temp_dir.exists())
        self.assertTrue(proj.screenshots_dir.exists())
        self.assertTrue(proj.manifest_path.exists())

        # Backwards-compatible aliases
        self.assertTrue((proj.version_dir / "out").exists())
        self.assertTrue((proj.version_dir / "project_manifest.json").exists())

    def test_asset_registration_and_5kb_gate(self):
        proj = self.mgr.init_project("Quantum Computing 2026", slug="quantum-2026")
        
        # 1. Reject < 5KB asset
        tiny_data = b"tiny asset file under 5kb"
        tiny_file = proj.temp_dir / "tiny.png"
        tiny_file.write_bytes(tiny_data)
        
        with self.assertRaises(ValueError) as ctx:
            proj.register_asset(tiny_file, category="photos")
        self.assertIn("5KB", str(ctx.exception))

        # 2. Accept valid > 5KB asset
        valid_data = b"X" * (MIN_ASSET_SIZE_BYTES + 500)
        valid_file = proj.temp_dir / "valid_image.png"
        valid_file.write_bytes(valid_data)

        registered = proj.register_asset(
            file_path=valid_file,
            category="photos",
            source_engine="nanobanana",
            extra={"prompt": "Quantum chip in ultra high resolution"}
        )
        self.assertIsNotNone(registered)
        
        # Verify asset in manifest
        manifest = proj.load_manifest()
        self.assertEqual(len(manifest.get("assets_manifest", [])), 1)
        asset_entry = manifest["assets_manifest"][0]
        self.assertEqual(asset_entry["source_engine"], "nanobanana")
        self.assertGreaterEqual(asset_entry["filesize_bytes"], MIN_ASSET_SIZE_BYTES)
        self.assertTrue(len(asset_entry["sha256"]) == 64)

    def test_lifecycle_phase_updates(self):
        proj = self.mgr.init_project("Mars Odyssey 2200", slug="mars-2200")
        proj.update_phase("phase_2_research_and_dossier", "completed", notes="BBC style dossier verified")
        
        manifest = proj.load_manifest()
        p2 = manifest["pipeline_lifecycle"]["phase_2_research_and_dossier"]
        self.assertEqual(p2["status"], "completed")
        self.assertEqual(p2["notes"], "BBC style dossier verified")
        self.assertIsNotNone(p2["timestamp"])

    def test_version_management(self):
        proj_v1 = self.mgr.init_project("Robotics Evolution", slug="robotics-evo")
        self.assertEqual(proj_v1.version, "v1")

        # Create v2
        proj_v2 = self.mgr.create_new_version("robotics-evo", copy_assets=True)
        self.assertEqual(proj_v2.version, "v2")
        self.assertTrue(proj_v2.version_dir.exists())

        versions = self.mgr.list_versions("robotics-evo")
        self.assertEqual(versions, ["v1", "v2"])

    def test_isolated_temp_and_screenshot_path(self):
        proj = self.mgr.init_project("AI Film", slug="ai-film")
        ss_path = proj.get_screenshot_path("browser_state.png")
        self.assertTrue(str(ss_path).startswith(str(proj.screenshots_dir)))
        self.assertFalse(str(ss_path).startswith("/tmp/browser_state.png"))

        # Write temp and clean
        temp_f = proj.get_temp_path("scratch.txt")
        temp_f.write_text("temporary scratch data")
        self.assertTrue(temp_f.exists())
        proj.cleanup_temp()
        self.assertFalse(temp_f.exists())

    def test_integrity_validation(self):
        proj = self.mgr.init_project("Integrity Demo", slug="integrity-demo")
        
        # Valid asset creation
        valid_img = proj.photos_dir / "hero.png"
        valid_img.write_bytes(b"A" * 6000)
        proj.register_asset(valid_img, category="photos")

        passed, errors = proj.validate_all_assets()
        self.assertTrue(passed)
        self.assertEqual(len(errors), 0)

        report = proj.verify_integrity()
        self.assertTrue(report["valid"])
        self.assertEqual(report["verified_assets"], 1)


if __name__ == "__main__":
    unittest.main()
