#!/usr/bin/env python3
"""
test_storage_empirical_battery.py
=================================
Rigorous empirical test battery for videopro storage management, CLI,
directory hierarchies, semantic versioning, 5KB gate, manifest schemas,
integrity verification, and stress/tamper resilience.
"""

import os
import sys
import json
import shutil
import tempfile
import hashlib
import subprocess
import unittest
from pathlib import Path

# Add paths
SKILL_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))

import video_storage_manager
from video_storage_manager import (
    VideoStorageManager,
    VideoProject,
    MIN_ASSET_SIZE_BYTES,
    STANDARD_SUBDIRECTORIES,
    ORGANIZATION_SUBDIRECTORIES,
    slugify,
    normalize_version,
    resolve_canonical_path,
    init_project,
    get_project,
    create_version,
    list_projects,
)


class TestVideoproEmpiricalBattery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_temp_root = Path(tempfile.mkdtemp(prefix="videopro_empirical_root_"))
        cls.cli_scripts = [
            SCRIPTS_DIR / "video_storage_manager.py",
            SCRIPTS_DIR / "project_manager.py",
        ]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_temp_root, ignore_errors=True)

    def setUp(self):
        self.run_dir = Path(tempfile.mkdtemp(dir=self.test_temp_root, prefix="case_"))
        self.mgr = VideoStorageManager(storage_root=self.run_dir)

    def tearDown(self):
        shutil.rmtree(self.run_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. HIERARCHY & DIRECTORY STRUCTURE TESTS
    # -------------------------------------------------------------------------
    def test_strict_date_slug_version_hierarchy(self):
        """Verify strict <STORAGE_ROOT>/YYYY/MM/YYYY-MM-DD_<slug>/v<version>/ hierarchy."""
        date_str = "2026-08-14"
        slug_str = "quantum-hyperdrive"
        proj = self.mgr.init_project(
            title="Quantum Hyperdrive Propulsion",
            slug=slug_str,
            date=date_str,
            version="v1"
        )

        expected_version_dir = self.run_dir / "2026" / "08" / f"{date_str}_{slug_str}" / "v1"
        self.assertEqual(proj.version_dir.resolve(), expected_version_dir.resolve())
        self.assertTrue(expected_version_dir.exists())
        self.assertTrue(expected_version_dir.is_dir())

        # All standard subdirectories must exist
        for subdir in STANDARD_SUBDIRECTORIES:
            target = expected_version_dir / subdir
            self.assertTrue(target.exists() and target.is_dir(), f"Missing standard dir: {subdir}")

        # Organization subdirectories
        for parent, subs in ORGANIZATION_SUBDIRECTORIES.items():
            for sub in subs:
                target = expected_version_dir / parent / sub
                self.assertTrue(target.exists() and target.is_dir(), f"Missing subfolder: {parent}/{sub}")

        # Check legacy compatibility aliases
        self.assertTrue((expected_version_dir / "out").is_symlink() or (expected_version_dir / "out").exists())
        self.assertTrue((expected_version_dir / "project_manifest.json").exists())

    def test_leap_year_and_custom_dates(self):
        """Test leap year date (2024-02-29) and boundary year dates."""
        proj_leap = self.mgr.init_project("Leap Year Tech", date="2024-02-29", slug="leap-tech")
        expected_leap = self.run_dir / "2024" / "02" / "2024-02-29_leap-tech" / "v1"
        self.assertEqual(proj_leap.version_dir.resolve(), expected_leap.resolve())
        self.assertTrue(expected_leap.exists())

        proj_future = self.mgr.init_project("Future Vision 2030", date="2030-12-31", slug="future-2030")
        expected_future = self.run_dir / "2030" / "12" / "2030-12-31_future-2030" / "v1"
        self.assertEqual(proj_future.version_dir.resolve(), expected_future.resolve())
        self.assertTrue(expected_future.exists())

    # -------------------------------------------------------------------------
    # 2. SLUGIFICATION & SPECIAL CHARACTERS
    # -------------------------------------------------------------------------
    def test_slugify_unicode_and_symbols(self):
        """Test slugification of complex Unicode, accents, emojis, and punctuation."""
        cases = [
            ("¡Supervivencia en Marte 2200! 🚀🛰️", "supervivencia-en-marte-2200"),
            ("El Niño & La Niña: Climatología Avanzada (2026)", "el-nino-la-nina-climatologia-avanzada-2026"),
            ("   ---Espacios   y   guiones---   ", "espacios-y-guiones"),
            ("100% Ciberseguridad: ¿Estás Protegido?", "100-ciberseguridad-estas-protegido"),
            ("$$$ Bitcoin, Ethereum & Web3 $$$", "bitcoin-ethereum-web3"),
            ("中文 商业 计划", "video-project"),  # non-ascii strips to default fallback
        ]
        for title, expected_slug in cases:
            self.assertEqual(slugify(title), expected_slug)

    # -------------------------------------------------------------------------
    # 3. SEMANTIC VERSIONING & BRANCHING
    # -------------------------------------------------------------------------
    def test_semantic_version_progression_and_branching(self):
        """Test v1 -> v2 -> v3 progression, asset copying, parent version tracking."""
        proj_v1 = self.mgr.init_project("Neural Cinema", slug="neural-cinema", date="2026-08-14", version="v1")
        
        # Add assets to v1
        hero_img = proj_v1.assets_dir / "photos" / "hero_render.png"
        hero_img.write_bytes(b"A" * 8192)
        proj_v1.register_asset(hero_img, category="photos", source_engine="nanobanana")

        # Create v2 with copy_assets=True
        proj_v2 = self.mgr.create_new_version("neural-cinema", date="2026-08-14", base_version="v1", copy_assets=True)
        self.assertEqual(proj_v2.version, "v2")
        self.assertTrue((proj_v2.assets_dir / "photos" / "hero_render.png").exists())
        self.assertEqual((proj_v2.assets_dir / "photos" / "hero_render.png").stat().st_size, 8192)

        v2_manifest = proj_v2.load_manifest()
        self.assertEqual(v2_manifest["version"], "v2")
        self.assertEqual(v2_manifest["parent_version"], "v1")
        self.assertEqual(len(v2_manifest["assets_manifest"]), 1)

        # Create v3 with copy_assets=False
        proj_v3 = self.mgr.create_new_version("neural-cinema", date="2026-08-14", base_version="v2", copy_assets=False)
        self.assertEqual(proj_v3.version, "v3")
        self.assertFalse((proj_v3.assets_dir / "photos" / "hero_render.png").exists())

        v3_manifest = proj_v3.load_manifest()
        self.assertEqual(v3_manifest["version"], "v3")
        self.assertEqual(v3_manifest["parent_version"], "v2")
        self.assertEqual(len(v3_manifest["assets_manifest"]), 0)

        # Version query methods
        versions = self.mgr.list_versions("neural-cinema", date="2026-08-14")
        self.assertEqual(versions, ["v1", "v2", "v3"])
        self.assertEqual(self.mgr.get_latest_version("neural-cinema", date="2026-08-14"), "v3")
        self.assertEqual(self.mgr.get_next_version("neural-cinema", date="2026-08-14"), "v4")

    # -------------------------------------------------------------------------
    # 4. 5KB GATE & CHECKSUM VERIFICATION
    # -------------------------------------------------------------------------
    def test_strict_5kb_gate_enforcement(self):
        """Test boundary conditions for 5KB (5120 bytes) gate."""
        proj = self.mgr.init_project("Gate Keeper", slug="gate-keeper", date="2026-08-14")

        # Case A: 0 bytes
        f_0 = proj.temp_dir / "empty.png"
        f_0.write_bytes(b"")
        with self.assertRaises(ValueError) as ctx:
            proj.register_asset(f_0)
        self.assertIn("5KB", str(ctx.exception))

        # Case B: 5119 bytes (1 byte below gate)
        f_5119 = proj.temp_dir / "almost.png"
        f_5119.write_bytes(b"B" * 5119)
        with self.assertRaises(ValueError) as ctx:
            proj.register_asset(f_5119)
        self.assertIn("5KB", str(ctx.exception))

        # Case C: 5120 bytes (exact boundary threshold)
        f_5120 = proj.temp_dir / "exact.png"
        exact_bytes = b"C" * 5120
        f_5120.write_bytes(exact_bytes)
        rec = proj.register_asset(f_5120, category="photos")
        self.assertEqual(rec["filesize_bytes"], 5120)
        self.assertEqual(rec["sha256"], hashlib.sha256(exact_bytes).hexdigest())

        # Case D: 100 KB
        f_large = proj.temp_dir / "large.jpg"
        large_bytes = b"D" * 102400
        f_large.write_bytes(large_bytes)
        rec_large = proj.register_asset(f_large, category="photos")
        self.assertEqual(rec_large["filesize_bytes"], 102400)
        self.assertEqual(rec_large["sha256"], hashlib.sha256(large_bytes).hexdigest())

    # -------------------------------------------------------------------------
    # 5. ASSET CATEGORIES, CLIPS, EXPORTS & RESOLVERS
    # -------------------------------------------------------------------------
    def test_multicategory_assets_clips_exports_resolution(self):
        """Register assets across all categories and test path resolution."""
        proj = self.mgr.init_project("Full Spectrum Project", slug="full-spectrum", date="2026-08-14")

        # 1. Keyframe asset
        kf_file = proj.assets_dir / "keyframes" / "kf_01.png"
        kf_file.write_bytes(b"K" * 6000)
        proj.register_asset(kf_file, category="keyframes")

        # 2. Audio voiceover
        vo_file = proj.audio_dir / "vo" / "narration.mp3"
        vo_file.write_bytes(b"V" * 15000)
        proj.register_asset(vo_file, category="audio")

        # 3. Raw clip
        clip_file = proj.raw_clips_dir / "flow" / "scene_01.mp4"
        clip_file.write_bytes(b"F" * 50000)
        proj.register_clip(clip_file, prompt="Sci-fi lab interior", node_id=101, duration_s=6.5)

        # 4. Render
        render_file = proj.renders_dir / "scenes" / "scene_01_rendered.mp4"
        render_file.write_bytes(b"R" * 60000)

        # 5. Export
        export_file = proj.exports_dir / "telegram" / "telegram_preview.mp4"
        export_file.write_bytes(b"E" * 1000000)
        proj.register_export(export_file, export_type="telegram", platform="telegram")

        # Test canonical path resolutions
        self.assertEqual(
            proj.resolve_asset_path("kf_01.png", subcategory="keyframes"),
            kf_file
        )
        self.assertEqual(
            proj.resolve_audio_path("narration.mp3", subcategory="vo"),
            vo_file
        )
        self.assertEqual(
            proj.resolve_clip_path("scene_01.mp4", subcategory="flow"),
            clip_file
        )
        self.assertEqual(
            proj.resolve_render_path("scene_01_rendered.mp4", subcategory="scenes"),
            render_file
        )
        self.assertEqual(
            proj.resolve_export_path("telegram_preview.mp4", subcategory="telegram"),
            export_file
        )

    # -------------------------------------------------------------------------
    # 6. MANIFEST INTEGRITY, LIFECYCLE & TAMPER DETECTION
    # -------------------------------------------------------------------------
    def test_pipeline_lifecycle_transitions(self):
        """Test transitions across all 7 pipeline phases in manifest."""
        proj = self.mgr.init_project("Lifecycle Test", slug="lifecycle-test", date="2026-08-14")

        phases = [
            ("phase_1_bootstrap", "completed", "Project initialized"),
            ("phase_2_research_and_dossier", "completed", "Dossier synthesized from Deep Research"),
            ("phase_3_script_and_storyboard", "completed", "Audio-visual nodes generated"),
            ("phase_4_asset_generation", "completed", "All keyframes generated via Google Flow"),
            ("phase_5_audio_production", "completed", "TTS VO and BGM mixed"),
            ("phase_6_timeline_assembly", "completed", "Remotion React timeline aligned"),
            ("phase_7_qa_and_deliverables", "completed", "QA verified, telegram export < 50MB"),
        ]

        for phase, status, notes in phases:
            proj.update_phase(phase, status, notes=notes)

        manifest = proj.load_manifest()
        for phase, status, notes in phases:
            p_data = manifest["pipeline_lifecycle"][phase]
            self.assertEqual(p_data["status"], status)
            self.assertEqual(p_data["notes"], notes)
            self.assertIsNotNone(p_data["timestamp"])

    def test_tamper_detection_and_integrity_verification(self):
        """Test that modified checksums, deleted files, or shrunk files trigger integrity errors."""
        proj = self.mgr.init_project("Tamper Check", slug="tamper-check", date="2026-08-14")

        # Register valid asset
        img = proj.assets_dir / "photos" / "photo1.png"
        img.write_bytes(b"ORIGINAL_DATA" * 500)
        proj.register_asset(img, category="photos")

        # Initial check must pass
        report = proj.verify_integrity()
        self.assertTrue(report["valid"])
        self.assertEqual(len(report["issues"]), 0)

        # 1. Tamper content (modify bytes -> SHA256 mismatch)
        img.write_bytes(b"TAMPERED_DATA" * 500)
        report_tampered = proj.verify_integrity()
        self.assertFalse(report_tampered["valid"])
        self.assertTrue(any("mismatch" in issue.lower() for issue in report_tampered["issues"]))

        # Restore
        img.write_bytes(b"ORIGINAL_DATA" * 500)
        self.assertTrue(proj.verify_integrity()["valid"])

        # 2. Tamper size below 5KB
        img.write_bytes(b"TINY")
        report_shrunk = proj.verify_integrity()
        self.assertFalse(report_shrunk["valid"])
        self.assertTrue(any("5kb" in issue.lower() or "bytes" in issue.lower() for issue in report_shrunk["issues"]))

        # 3. Tamper deleted file
        img.unlink()
        report_missing = proj.verify_integrity()
        self.assertFalse(report_missing["valid"])
        self.assertTrue(any("missing" in issue.lower() or "not found" in issue.lower() for issue in report_missing["issues"]))

    # -------------------------------------------------------------------------
    # 7. CLI EQUIVALENCE & SUBCOMMANDS (Testing both scripts)
    # -------------------------------------------------------------------------
    def test_cli_subcommands_on_both_entrypoints(self):
        """Empirically execute all CLI subcommands via subprocess on both entrypoints."""
        for script_path in self.cli_scripts:
            with self.subTest(script=script_path.name):
                # A. init
                slug = f"cli-test-{script_path.stem}"
                cmd_init = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "init", "CLI Automation Test",
                    "--slug", slug,
                    "--date", "2026-08-14",
                    "--version", "v1",
                    "--style", "vox_documentary",
                    "--duration", "60",
                ]
                res_init = subprocess.run(cmd_init, capture_output=True, text=True)
                self.assertEqual(res_init.returncode, 0, f"Failed init: {res_init.stderr}")
                self.assertIn("Project initialized successfully", res_init.stdout)

                # B. info
                cmd_info = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "info", slug,
                    "--date", "2026-08-14",
                    "--json",
                ]
                res_info = subprocess.run(cmd_info, capture_output=True, text=True)
                self.assertEqual(res_info.returncode, 0, f"Failed info: {res_info.stderr}")
                manifest = json.loads(res_info.stdout)
                self.assertEqual(manifest["slug"], slug)
                self.assertEqual(manifest["version"], "v1")

                # C. register-asset
                temp_asset = self.run_dir / f"test_asset_{script_path.stem}.png"
                temp_asset.write_bytes(b"CLI_ASSET_CONTENT" * 500)
                cmd_reg = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "register-asset", slug, str(temp_asset),
                    "--category", "photos",
                    "--engine", "nanobanana",
                    "--version", "v1",
                ]
                res_reg = subprocess.run(cmd_reg, capture_output=True, text=True)
                self.assertEqual(res_reg.returncode, 0, f"Failed register-asset: {res_reg.stderr}")
                self.assertIn("Asset registered successfully", res_reg.stdout)

                # D. resolve
                cmd_res = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "resolve", slug, "exports", "final_render.mp4",
                    "--subcategory", "master",
                    "--version", "v1",
                ]
                res_res = subprocess.run(cmd_res, capture_output=True, text=True)
                self.assertEqual(res_res.returncode, 0, f"Failed resolve: {res_res.stderr}")
                self.assertTrue(res_res.stdout.strip().endswith("exports/master/final_render.mp4"))

                # E. new-version
                cmd_new_ver = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "new-version", slug,
                    "--date", "2026-08-14",
                    "--copy-assets",
                ]
                res_new_ver = subprocess.run(cmd_new_ver, capture_output=True, text=True)
                self.assertEqual(res_new_ver.returncode, 0, f"Failed new-version: {res_new_ver.stderr}")
                self.assertIn("v2", res_new_ver.stdout)

                # F. export-flow
                cmd_flow = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "export-flow", slug,
                    "--version", "v2",
                ]
                res_flow = subprocess.run(cmd_flow, capture_output=True, text=True)
                self.assertEqual(res_flow.returncode, 0, f"Failed export-flow: {res_flow.stderr}")
                flow_data = json.loads(res_flow.stdout)
                self.assertIn("consistency_pins", flow_data)

                # G. export-videomastery
                cmd_vm = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "export-videomastery", slug,
                    "--version", "v2",
                    "--api-url", "http://127.0.0.1:9130",
                ]
                res_vm = subprocess.run(cmd_vm, capture_output=True, text=True)
                self.assertEqual(res_vm.returncode, 0, f"Failed export-videomastery: {res_vm.stderr}")
                vm_data = json.loads(res_vm.stdout)
                self.assertEqual(vm_data["project_id"], f"2026-08-14_{slug}")

                # H. verify / validate
                cmd_verify = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "verify", slug,
                    "--date", "2026-08-14",
                    "--version", "v2",
                ]
                res_verify = subprocess.run(cmd_verify, capture_output=True, text=True)
                self.assertEqual(res_verify.returncode, 0, f"Failed verify: {res_verify.stderr}")
                self.assertIn("Integrity Report", res_verify.stdout)
                self.assertIn("100% PASS", res_verify.stdout)

                # I. list
                cmd_list = [
                    sys.executable, str(script_path),
                    "--storage-root", str(self.run_dir),
                    "list",
                    "--json",
                ]
                res_list = subprocess.run(cmd_list, capture_output=True, text=True)
                self.assertEqual(res_list.returncode, 0, f"Failed list: {res_list.stderr}")
                list_data = json.loads(res_list.stdout)
                self.assertTrue(any(p["slug"] == slug for p in list_data))

    # -------------------------------------------------------------------------
    # 8. STRESS TESTING (High volume, deep versioning, asset batches)
    # -------------------------------------------------------------------------
    def test_stress_multi_project_and_high_volume_assets(self):
        """Stress test: 10 projects across dates, multi-version progression to v5, 20 assets each."""
        num_projects = 10
        assets_per_proj = 20

        created_projects = []
        for i in range(num_projects):
            slug = f"stress-proj-{i:03d}"
            date = f"2026-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}"
            p = self.mgr.init_project(f"Stress Project {i}", slug=slug, date=date, version="v1")
            created_projects.append((slug, date, p))

        # Register assets batch
        for slug, date, p in created_projects:
            for a_idx in range(assets_per_proj):
                asset_file = p.assets_dir / "photos" / f"img_{a_idx:03d}.png"
                content = f"STRESS_DATA_PROJ_{slug}_ASSET_{a_idx}".encode() * 200
                asset_file.write_bytes(content)
                p.register_asset(asset_file, category="photos", source_engine="nanobanana")

            # Verify integrity
            rep = p.verify_integrity()
            self.assertTrue(rep["valid"])
            self.assertEqual(rep["verified_assets"], assets_per_proj)

        # Multi-version cascade up to v5 for first project
        s0, d0, p0 = created_projects[0]
        cur_slug = s0
        for v in range(2, 6):
            ver_tag = f"v{v}"
            base_tag = f"v{v-1}"
            pv = self.mgr.create_new_version(cur_slug, date=d0, base_version=base_tag, copy_assets=True)
            self.assertEqual(pv.version, ver_tag)
            rep_v = pv.verify_integrity()
            self.assertTrue(rep_v["valid"])
            self.assertEqual(rep_v["verified_assets"], assets_per_proj)

        self.assertEqual(self.mgr.list_versions(s0, date=d0), ["v1", "v2", "v3", "v4", "v5"])


if __name__ == "__main__":
    unittest.main()
