#!/usr/bin/env python3
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from video_storage_manager import (
    VideoStorageManager,
    VideoProject,
    init_project,
    get_project,
    create_version,
    list_projects,
    resolve_canonical_path,
    slugify,
    normalize_version,
    MIN_ASSET_SIZE_BYTES,
    STANDARD_SUBDIRECTORIES,
)


class TestVideoStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_video_storage_"))
        self.mgr = VideoStorageManager(storage_root=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_slugify_and_version_normalization(self):
        self.assertEqual(
            slugify("Marte 2200: El Salto Multiplanetario!"),
            "marte-2200-el-salto-multiplanetario"
        )
        self.assertEqual(
            slugify("Apple M4 Pro vs Snapdragon X Elite"),
            "apple-m4-pro-vs-snapdragon-x-elite"
        )
        self.assertEqual(
            slugify("¡Hola! ¿Cómo estás? 100%"),
            "hola-como-estas-100"
        )
        
        self.assertEqual(normalize_version(1), "v1")
        self.assertEqual(normalize_version("1"), "v1")
        self.assertEqual(normalize_version("v1"), "v1")
        self.assertEqual(normalize_version("V2"), "v2")
        self.assertEqual(normalize_version("v10"), "v10")

    def test_project_initialization_hierarchy(self):
        proj = self.mgr.init_project(
            title="Documental Marte 2200",
            slug="marte-2200",
            date="2026-08-14",
            version="v1"
        )

        # Check strict path: <STORAGE_ROOT>/<YYYY>/<MM>/<YYYY-MM-DD>_<slug>/v<version>/
        expected_path = self.temp_dir / "2026" / "08" / "2026-08-14_marte-2200" / "v1"
        self.assertEqual(proj.version_dir, expected_path)
        self.assertTrue(expected_path.exists())
        self.assertTrue(expected_path.is_dir())

        # Check all standard subdirectories
        for subdir in STANDARD_SUBDIRECTORIES:
            p = expected_path / subdir
            self.assertTrue(p.exists() and p.is_dir(), f"Missing standard directory: {subdir}")

        # Check organization subfolders
        self.assertTrue((expected_path / "raw_clips" / "flow").exists())
        self.assertTrue((expected_path / "assets" / "photos").exists())
        self.assertTrue((expected_path / "assets" / "keyframes").exists())
        self.assertTrue((expected_path / "audio" / "vo").exists())
        self.assertTrue((expected_path / "renders" / "scenes").exists())
        self.assertTrue((expected_path / "exports" / "telegram").exists())
        self.assertTrue((expected_path / "manifests" / "logs").exists())

        # Check manifest.json
        manifest_file = expected_path / "manifest.json"
        self.assertTrue(manifest_file.exists())
        
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["project_id"], "2026-08-14_marte-2200")
        self.assertEqual(data["slug"], "marte-2200")
        self.assertEqual(data["version"], "v1")
        self.assertEqual(data["status"], "initialized")
        self.assertIn("directory_structure", data)
        self.assertIn("pipeline_lifecycle", data)
        self.assertEqual(data["pipeline_lifecycle"]["phase_1_bootstrap"]["status"], "completed")

    def test_asset_registration_and_5kb_gate(self):
        proj = self.mgr.init_project(title="Test Project", slug="test-proj", date="2026-08-14")

        # 1. Test asset below 5KB (should fail with ValueError)
        small_asset = proj.assets_dir / "photos" / "tiny.jpg"
        with open(small_asset, "wb") as f:
            f.write(b"x" * 1024)  # 1 KB

        with self.assertRaises(ValueError):
            proj.register_asset(small_asset, category="photos")

        # 2. Test valid asset (>= 5KB)
        valid_asset = proj.assets_dir / "photos" / "photo_4k.jpg"
        with open(valid_asset, "wb") as f:
            f.write(b"x" * 6000)  # 6 KB

        record = proj.register_asset(valid_asset, category="photos", source_engine="nanobanana")
        self.assertTrue(record["verified"])
        self.assertEqual(record["filesize_bytes"], 6000)
        self.assertEqual(len(record["sha256"]), 64)

        # Check that manifest has it
        manifest = proj.load_manifest()
        self.assertEqual(len(manifest["assets_manifest"]), 1)
        self.assertEqual(manifest["assets_manifest"][0]["name"], "photo_4k.jpg")

    def test_clip_and_export_registration(self):
        proj = self.mgr.init_project(title="Clip Test", slug="clip-test", date="2026-08-14")

        # Create dummy clip
        clip_path = proj.raw_clips_dir / "flow" / "scene_01.mp4"
        with open(clip_path, "wb") as f:
            f.write(b"0" * 10000)

        clip_rec = proj.register_clip(
            clip_path,
            prompt="Establishing shot of Olympus Mons",
            node_id=1,
            duration_s=10.0,
            engine="gemini-omni-flash-preview"
        )
        self.assertEqual(clip_rec["node_id"], 1)
        self.assertEqual(clip_rec["duration_s"], 10.0)

        # Create dummy export
        export_path = proj.exports_dir / "master" / "final.mp4"
        with open(export_path, "wb") as f:
            f.write(b"0" * 2000000)  # ~2MB

        exp_rec = proj.register_export(export_path, export_type="master", platform="telegram")
        self.assertTrue(exp_rec["telegram_under_50mb"])

        manifest = proj.load_manifest()
        self.assertEqual(len(manifest["clips_registry"]), 1)
        self.assertEqual(len(manifest["exports_registry"]), 1)
        self.assertTrue(manifest["qa_checks"]["telegram_under_50mb_passed"])

    def test_version_lifecycle_and_branching(self):
        proj_v1 = self.mgr.init_project(title="Version Test", slug="version-test", date="2026-08-14", version="v1")

        # Put an asset in v1
        v1_asset = proj_v1.assets_dir / "photos" / "hero.png"
        with open(v1_asset, "wb") as f:
            f.write(b"1" * 8000)
        proj_v1.register_asset(v1_asset)

        # Check version listing
        self.assertEqual(self.mgr.list_versions("version-test", date="2026-08-14"), ["v1"])
        self.assertEqual(self.mgr.get_next_version("version-test", date="2026-08-14"), "v2")

        # Create v2 with asset copying
        proj_v2 = self.mgr.create_new_version(
            slug="version-test",
            date="2026-08-14",
            base_version="v1",
            copy_assets=True
        )

        self.assertEqual(proj_v2.version, "v2")
        self.assertTrue(proj_v2.version_dir.exists())
        self.assertTrue((proj_v2.assets_dir / "photos" / "hero.png").exists())

        v2_manifest = proj_v2.load_manifest()
        self.assertEqual(v2_manifest["version"], "v2")
        self.assertEqual(v2_manifest.get("parent_version"), "v1")
        self.assertEqual(len(v2_manifest.get("assets_manifest", [])), 1)

        # Check latest version query
        self.assertEqual(self.mgr.get_latest_version("version-test", date="2026-08-14"), "v2")
        self.assertEqual(self.mgr.list_versions("version-test", date="2026-08-14"), ["v1", "v2"])

    def test_path_resolvers(self):
        proj = init_project(title="Resolver Test", slug="res-test", date="2026-08-14", base_dir=self.temp_dir)

        self.assertEqual(
            proj.resolve_path("raw_clips", "clip1.mp4", subcategory="flow"),
            proj.raw_clips_dir / "flow" / "clip1.mp4"
        )
        self.assertEqual(
            proj.resolve_asset_path("logo.svg", subcategory="logos"),
            proj.assets_dir / "logos" / "logo.svg"
        )
        self.assertEqual(
            proj.resolve_audio_path("voice.mp3", subcategory="vo"),
            proj.audio_dir / "vo" / "voice.mp3"
        )
        self.assertEqual(
            proj.resolve_render_path("chunk_01.mp4"),
            proj.renders_dir / "scenes" / "chunk_01.mp4"
        )
        self.assertEqual(
            proj.resolve_export_path("final.mp4"),
            proj.exports_dir / "master" / "final.mp4"
        )
        self.assertEqual(
            proj.resolve_manifest_path("scenes.json"),
            proj.manifests_dir / "scenes.json"
        )

        # Convenience functional helper
        resolved = resolve_canonical_path(
            slug="res-test",
            category="exports",
            filename="telegram_clip.mp4",
            subcategory="telegram",
            date="2026-08-14",
            base_dir=self.temp_dir
        )
        self.assertEqual(resolved, proj.exports_dir / "telegram" / "telegram_clip.mp4")

    def test_flow_and_videomastery_integrations(self):
        proj = init_project(title="Integration Test", slug="integ-test", date="2026-08-14", base_dir=self.temp_dir)

        # Google Flow
        flow_info = proj.get_flow_paths()
        self.assertIn("<FIRST_FRAME>", flow_info["consistency_pins"])
        self.assertIn("<IMAGE_REF_0>", flow_info["consistency_pins"])
        self.assertIn("<IMAGE_REF_5>", flow_info["consistency_pins"])
        self.assertIn("keyframes", flow_info["keyframes_dir"])

        # Videomastery
        vm_info = proj.get_videomastery_integration_info(api_base_url="http://127.0.0.1:9130")
        self.assertEqual(vm_info["project_id"], "2026-08-14_integ-test")
        self.assertEqual(vm_info["api_endpoints"]["render"], "http://127.0.0.1:9130/api/render")
        self.assertIn("/pro/videomastery-api/projects/", vm_info["static_proxy_path"])

    def test_project_listing_and_discovery(self):
        self.mgr.init_project(title="AI Documental", slug="ai-doc", date="2026-08-10")
        self.mgr.init_project(title="Quantum Computing", slug="quantum-comp", date="2026-08-12")
        self.mgr.init_project(title="Superconductors", slug="super-conductors", date="2026-07-20")

        all_projs = self.mgr.list_all_projects()
        self.assertEqual(len(all_projs), 3)

        aug_projs = self.mgr.list_all_projects(year=2026, month=8)
        self.assertEqual(len(aug_projs), 2)

        jul_projs = self.mgr.list_all_projects(year=2026, month=7)
        self.assertEqual(len(jul_projs), 1)

        search_res = self.mgr.find_projects("quantum")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["slug"], "quantum-comp")

    def test_integrity_verification(self):
        proj = self.mgr.init_project(title="Integrity Test", slug="integ-chk", date="2026-08-14")

        # Add valid asset
        valid_file = proj.assets_dir / "photos" / "pic.png"
        with open(valid_file, "wb") as f:
            f.write(b"a" * 7000)
        proj.register_asset(valid_file)

        report = proj.verify_integrity()
        self.assertTrue(report["valid"])
        self.assertEqual(report["verified_assets"], 1)
        self.assertEqual(len(report["issues"]), 0)


if __name__ == "__main__":
    unittest.main()
