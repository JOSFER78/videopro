"""
test_workflow_registry.py
=========================
Batería de Pruebas Unitarias y de Integración para el Registro Persistente,
Versionado Semántico y Sellado Criptográfico SHA-256 de Workflows (WorkflowRegistry).

Valida:
  1. Catálogo de los 8 Arquetipos Canónicos y resolución de alias.
  2. Integridad y consistencia del Manifiesto 7D de Prompts y Óptica.
  3. Especificaciones de Audio Broadcast (-18dB Ducking, EBU R128 -14 LUFS, BPM).
  4. Reglas de Subtitulado Levenshtein (>= 0.85) y Ritmo de Montaje (2-3s o 3-5s).
  5. Configuración de Renderizado (16:9 / 9:16, 60fps, Shaders, Anti-Blackdetect).
  6. Sellado Criptográfico SHA-256 determinista y detección de alteraciones.
  7. Versionado Semántico (SemVer: patch, minor, major), linaje y rollback.
  8. Persistencia Dual en Disco (JSON y YAML) y generación del Catálogo Maestro.
  9. Cumplimiento del 100% en la Auditoría de las 10 Reglas de Oro (R01 a R10).
 10. Compatibilidad y migración de formatos legacy.
"""

import sys
import json
import yaml
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.workflow_registry import (
    WorkflowRegistry, StructuredWorkflow,
    Prompt7DManifest, CameraOpticsSpec, AudioSpec,
    SubtitlesPacingSpec, RenderConfigSpec, WorkflowVersionInfo,
    CANONICAL_ARCHETYPES_DEFS, ARCHETYPE_ALIASES
)


class TestWorkflowRegistry(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="videopro_registry_test_")
        self.storage_dir = Path(self.temp_dir) / "storage"
        self.workflows_dir = self.storage_dir / "workflows"

        self.registry = WorkflowRegistry(
            storage_dir=self.storage_dir,
            workflows_dir=self.workflows_dir
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_canonical_archetypes_catalog_integrity(self):
        """Verifica que existan exactamente los 8 arquetipos canónicos requeridos."""
        canonical_keys = self.registry.get_canonical_archetypes()
        self.assertEqual(len(canonical_keys), 8)

        expected_archetypes = [
            "CHRONODRIFT_6DOF",
            "FPV_URBAN",
            "VOX_EXPLAINER",
            "VIRAL_SHORTS_916",
            "DOCUMENTAL_35MM",
            "NANOVERSE",
            "LIVING_CANVAS",
            "ASTRODRIFT"
        ]
        for exp in expected_archetypes:
            self.assertIn(exp, canonical_keys)

    def test_alias_resolution(self):
        """Verifica que los alias y variantes se resuelvan al arquetipo canónico correspondiente."""
        test_cases = [
            ("CHRONODRIFT_TRITEMPORAL", "CHRONODRIFT_6DOF"),
            ("01_CHRONODRIFT", "CHRONODRIFT_6DOF"),
            ("FPV_URBAN_REAL_FLOW", "FPV_URBAN"),
            ("CITY_ROUTES_BEATS", "FPV_URBAN"),
            ("VOX_INVESTIGATIVE_DOC", "VOX_EXPLAINER"),
            ("DEEP_EXPLAINER_ESSAY", "VOX_EXPLAINER"),
            ("VIRAL_SHORTS_HOOK", "VIRAL_SHORTS_916"),
            ("TIKTOK_REELS_916", "VIRAL_SHORTS_916"),
            ("DOCUMENTARY_MASTER", "DOCUMENTAL_35MM"),
            ("HISTORICAL_SCRAPING", "DOCUMENTAL_35MM"),
            ("NANOVERSE_MACRO", "NANOVERSE"),
            ("03_NANOVERSE", "NANOVERSE"),
            ("LIVING_CANVAS_ART", "LIVING_CANVAS"),
            ("PIXAR_3D_ANIMATION", "LIVING_CANVAS"),
            ("ASTRODRIFT_DEEP_SPACE", "ASTRODRIFT"),
            ("05_ASTRODRIFT", "ASTRODRIFT"),
        ]
        for alias_input, expected_canon in test_cases:
            resolved = self.registry.resolve_archetype_id(alias_input)
            self.assertEqual(resolved, expected_canon, f"Fallo al resolver '{alias_input}'")

    def test_sha256_cryptographic_sealing(self):
        """Valida que el sellado criptográfico SHA-256 sea determinista y detecte alteraciones."""
        wf = self.registry.create_canonical_workflow("CHRONODRIFT_6DOF")
        self.assertTrue(len(wf.version_info.sha256_hash) == 64)

        # Verificación en vivo
        valid, msg = self.registry.verify_workflow_integrity(wf)
        self.assertTrue(valid, msg)

        # Alterar un parámetro interno y comprobar fallo de integridad
        wf_tampered = wf.model_copy(deep=True) if hasattr(wf, "model_copy") else wf.copy(deep=True)
        wf_tampered.audio_spec.ducking_db = -10.0  # Cambio no sellado
        valid_tampered, msg_tampered = self.registry.verify_workflow_integrity(wf_tampered)
        self.assertFalse(valid_tampered)
        self.assertIn("Hash SHA-256 corrupto o alterado", msg_tampered)

    def test_dual_persistence_json_and_yaml(self):
        """Verifica que los workflows se persistan y lean idénticamente en JSON y YAML."""
        self.registry.init_all_canonical_workflows(force=True)

        for canon_id in self.registry.get_canonical_archetypes():
            json_file = self.workflows_dir / f"{canon_id}_v1.0.0.json"
            yaml_file = self.workflows_dir / f"{canon_id}_v1.0.0.yaml"
            latest_json = self.workflows_dir / f"{canon_id}_latest.json"
            latest_yaml = self.workflows_dir / f"{canon_id}_latest.yaml"

            self.assertTrue(json_file.exists(), f"Falta archivo {json_file.name}")
            self.assertTrue(yaml_file.exists(), f"Falta archivo {yaml_file.name}")
            self.assertTrue(latest_json.exists(), f"Falta archivo {latest_json.name}")
            self.assertTrue(latest_yaml.exists(), f"Falta archivo {latest_yaml.name}")

            # Cargar desde JSON
            wf_from_json = self.registry.load_workflow_from_disk(json_file)
            # Cargar desde YAML
            wf_from_yaml = self.registry.load_workflow_from_disk(yaml_file)

            self.assertEqual(wf_from_json.version_info.sha256_hash, wf_from_yaml.version_info.sha256_hash)
            self.assertEqual(wf_from_json.archetype_id, wf_from_yaml.archetype_id)
            self.assertEqual(wf_from_json.audio_spec.bpm, wf_from_yaml.audio_spec.bpm)
            self.assertEqual(wf_from_json.render_config.fps, wf_from_yaml.render_config.fps)

    def test_semantic_versioning_and_bump(self):
        """Valida incrementos SemVer (patch, minor, major), historial y trazabilidad de hashes padre."""
        self.registry.init_all_canonical_workflows(force=True)
        base_wf = self.registry.get_workflow("VOX_EXPLAINER")
        self.assertEqual(base_wf.version_info.semver, "v1.0.0")
        parent_hash = base_wf.version_info.sha256_hash

        # 1. Bump Patch
        wf_patch = self.registry.create_version(
            archetype_id="VOX_EXPLAINER",
            patch_data={"audio_spec": {"ducking_db": -22.0}},
            bump_type="patch",
            changelog="Ajuste fino de ducking a -22dB"
        )
        self.assertEqual(wf_patch.version_info.semver, "v1.0.1")
        self.assertEqual(wf_patch.version_info.version_int, 2)
        self.assertEqual(wf_patch.version_info.parent_hash, parent_hash)
        self.assertEqual(wf_patch.audio_spec.ducking_db, -22.0)

        # 2. Bump Minor
        wf_minor = self.registry.create_version(
            archetype_id="VOX_EXPLAINER",
            patch_data={"render_config": {"crf": 17}},
            bump_type="minor",
            changelog="Mejora de nitidez en compresión CRF 17"
        )
        self.assertEqual(wf_minor.version_info.semver, "v1.1.0")
        self.assertEqual(wf_minor.version_info.version_int, 3)
        self.assertEqual(wf_minor.version_info.parent_hash, wf_patch.version_info.sha256_hash)

        # 3. Bump Major
        wf_major = self.registry.create_version(
            archetype_id="VOX_EXPLAINER",
            patch_data={"subtitles_pacing": {"style": "vox_glow_boxless_v2"}},
            bump_type="major",
            changelog="Nueva generación v2.0.0 de subtítulos cinemáticos"
        )
        self.assertEqual(wf_major.version_info.semver, "v2.0.0")
        self.assertEqual(wf_major.version_info.version_int, 4)

        # Verificar lista de versiones
        history = self.registry.list_versions("VOX_EXPLAINER")
        self.assertEqual(len(history), 4)
        self.assertEqual([h.semver for h in history], ["v1.0.0", "v1.0.1", "v1.1.0", "v2.0.0"])

    def test_rollback_functionality(self):
        """Valida que se pueda revertir a una versión previa y actualizar los punteros en disco."""
        self.registry.init_all_canonical_workflows(force=True)
        self.registry.create_version(
            archetype_id="VIRAL_SHORTS_916",
            patch_data={"audio_spec": {"bpm": 145}},
            bump_type="minor",
            changelog="Aceleración de BPM a 145"
        )
        self.assertEqual(self.registry.get_latest_version("VIRAL_SHORTS_916"), "v1.1.0")

        # Rollback a v1.0.0
        rolled_back = self.registry.rollback_to_version("VIRAL_SHORTS_916", "v1.0.0")
        self.assertEqual(rolled_back.version_info.semver, "v1.0.0")
        self.assertEqual(self.registry.get_latest_version("VIRAL_SHORTS_916"), "v1.0.0")
        self.assertEqual(rolled_back.audio_spec.bpm, 138)

    def test_diff_between_versions(self):
        """Valida el cálculo de diferencias clave a clave entre dos versiones."""
        self.registry.init_all_canonical_workflows(force=True)
        self.registry.create_version(
            archetype_id="FPV_URBAN",
            patch_data={
                "audio_spec": {"ducking_db": -20.0, "bpm": 132},
                "camera_optics": {"focal_length_mm": 10.0}
            },
            bump_type="minor",
            changelog="Lente ultra-wide 10mm y BPM 132"
        )
        diff_result = self.registry.diff_versions("FPV_URBAN", "v1.0.0", "v1.1.0")
        self.assertEqual(diff_result["archetype_id"], "FPV_URBAN")
        self.assertEqual(diff_result["v1"], "v1.0.0")
        self.assertEqual(diff_result["v2"], "v1.1.0")
        self.assertEqual(diff_result["total_differences"], 3)

        fields_changed = [d["field"] for d in diff_result["differences"]]
        self.assertIn("audio_spec.ducking_db", fields_changed)
        self.assertIn("audio_spec.bpm", fields_changed)
        self.assertIn("camera_optics.focal_length_mm", fields_changed)

    def test_10_golden_rules_audit_compliance(self):
        """Verifica que todos los 8 workflows canónicos cumplan 100/100 en la auditoría de Reglas de Oro."""
        self.registry.init_all_canonical_workflows(force=True)
        for canon_id in self.registry.get_canonical_archetypes():
            wf = self.registry.get_workflow(canon_id)
            audit = self.registry.validate_against_golden_rules(wf)
            self.assertTrue(audit["passed"], f"Fallo en auditoría de {canon_id}: {audit['violations']}")
            self.assertEqual(audit["score"], 100.0, f"Puntaje inferior a 100 en {canon_id}")
            self.assertEqual(audit["violations_count"], 0)

    def test_catalog_manifest_files(self):
        """Valida que `workflow_catalog.json` y `workflow_catalog.yaml` contengan los 8 arquetipos."""
        self.registry.init_all_canonical_workflows(force=True)

        cat_json = self.workflows_dir / "workflow_catalog.json"
        cat_yaml = self.workflows_dir / "workflow_catalog.yaml"

        self.assertTrue(cat_json.exists())
        self.assertTrue(cat_yaml.exists())

        with open(cat_json, "r", encoding="utf-8") as f:
            data_json = json.load(f)
        with open(cat_yaml, "r", encoding="utf-8") as f:
            data_yaml = yaml.safe_load(f)

        self.assertEqual(data_json["total_canonical_archetypes"], 8)
        self.assertEqual(data_yaml["total_canonical_archetypes"], 8)
        self.assertEqual(len(data_json["archetypes"]), 8)
        self.assertEqual(len(data_yaml["archetypes"]), 8)

    def test_legacy_workflow_conversion(self):
        """Verifica la conversión de un workflow legacy a StructuredWorkflow con sellado SHA-256."""
        legacy_data = {
            "id": "LEGACY_SAMPLE",
            "name": "Legacy Workflow Test",
            "description": "Workflow antiguo para prueba de migración",
            "archetype_id": "HISTORICAL_SCRAPING",
            "nodes": [{"id": "n1", "title": "Scraping"}],
            "connections": []
        }
        structured = self.registry._convert_legacy_to_structured(legacy_data)
        self.assertEqual(structured.archetype_id, "DOCUMENTAL_35MM")
        self.assertEqual(structured.name, "Legacy Workflow Test")
        self.assertTrue(len(structured.version_info.sha256_hash) == 64)
        valid, msg = self.registry.verify_workflow_integrity(structured)
        self.assertTrue(valid, msg)


if __name__ == "__main__":
    unittest.main()
