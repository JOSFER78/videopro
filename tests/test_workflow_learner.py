"""
test_workflow_learner.py
========================
Batería de Pruebas Unitarias y de Integración para el Motor de Auto-Mejora y Aprendizaje Continuo (WorkflowLearner).
Valida:
  1. Catálogo de 10 Reglas de Oro (R01 a R10) y cálculo de penalizaciones.
  2. Detección automática de errores en montaje (desincronización VO, caídas de ritmo, blackdetect, bitrate).
  3. Auto-parcheo determinista de parámetros y generación de workflow versión v+1.
  4. Preservación del historial de mejoras (improvement_history) y métricas de rendimiento por arquetipo.
  5. Cálculo de Levenshtein y alineación determinista de subtítulos.
"""

import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.workflow_learner import (
    WorkflowLearner, GOLDEN_RULES_CATALOG,
    compute_levenshtein_distance, compute_text_similarity
)
from scripts.learning_memory_tool import LearningMemoryTool


class TestWorkflowLearner(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="videopro_learner_test_")
        self.storage_dir = Path(self.temp_dir) / "storage"
        self.workflows_dir = self.storage_dir / "workflows"
        self.learning_dir = self.storage_dir / "learning_memory"

        self.learner = WorkflowLearner(
            storage_dir=self.storage_dir,
            workflows_dir=self.workflows_dir,
            learning_dir=self.learning_dir
        )
        self.memory_tool = LearningMemoryTool(storage_dir=str(self.learning_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_golden_rules_catalog_integrity(self):
        """Verifica que el catálogo contenga exactamente las 10 Reglas de Oro con sus atributos."""
        self.assertEqual(len(GOLDEN_RULES_CATALOG), 10)
        expected_ids = [
            "R01_AUDIO_FIRST_LIFECYCLE",
            "R02_STRICT_5KB_GATE",
            "R03_LEVENSHTEIN_CAPTIONS",
            "R04_RHYTHM_3_5S_CUT",
            "R05_ANTI_BLACKDETECT",
            "R06_DOP_7LAYER_PROMPT",
            "R07_EBU_R128_MASTERING",
            "R08_THUMBNAIL_SAFE_ZONE",
            "R09_DUAL_PERSISTENCE",
            "R10_USER_AGENT_INSTITUTIONAL"
        ]
        rule_ids = [r["id"] for r in GOLDEN_RULES_CATALOG]
        for eid in expected_ids:
            self.assertIn(eid, rule_ids)

        for r in GOLDEN_RULES_CATALOG:
            self.assertIn("penalty", r)
            self.assertGreater(r["penalty"], 0)
            self.assertIn("category", r)
            self.assertIn("severity", r)
            self.assertIn("recommended_patch", r)

    def test_levenshtein_and_similarity(self):
        """Valida el cálculo de distancia de Levenshtein y ratio de similitud."""
        dist = compute_levenshtein_distance("Madrid Secreto", "Madrid Secreto")
        self.assertEqual(dist, 0)
        sim = compute_text_similarity("Madrid Secreto", "Madrid Secreto")
        self.assertAlmostEqual(sim, 1.0, places=2)

        # Prueba con diferencias leves
        sim_close = compute_text_similarity("El gran misterio del banco", "El gran misterio del banco de espana")
        self.assertGreater(sim_close, 0.70)

        # Prueba con alucinación total
        sim_far = compute_text_similarity("Cámara acorazada subterránea", "Suscríbete y dale like al vídeo")
        self.assertLess(sim_far, 0.40)

    def test_audit_perfect_project(self):
        """Verifica que un proyecto perfecto obtenga 100/100 y pase todas las reglas."""
        manifest = {
            "project_id": "test_perfect_project",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "metadata": {
                "topic": "La Cámara Acorazada de Cibeles",
                "style": "vox_documentary",
                "target_duration_seconds": 30,
                "actual_duration_seconds": 30.0
            },
            "script": "Bajo la fuente de Cibeles se oculta la cámara acorazada del Banco de España.",
            "subtitles_text": "Bajo la fuente de Cibeles se oculta la cámara acorazada del Banco de España.",
            "scenes": [
                {
                    "id": "shot_01",
                    "duration_sec": 3.5,
                    "ken_burns": True,
                    "prompt": "ARRI Alexa 35mm, f/1.8, subterranean vault mechanism with tungsten practical lights"
                },
                {
                    "id": "shot_02",
                    "duration_sec": 4.0,
                    "ken_burns": True,
                    "prompt": "35mm anamorphic prime lens, hydraulic floodgate system, 24fps cinema grading"
                }
            ],
            "audio_dsp": {
                "ducking_db": -20.0,
                "target_lufs": -14.0
            },
            "thumbnail": {
                "microcopy": "EL GRAN SECRETO"
            },
            "background_color": "#243048",
            "scraping_config": {
                "user_agent": "VideoProHermesBot/1.0 (https://videopro.app; contact@videopro.app)"
            },
            "pipeline_lifecycle": {
                "phase_1_bootstrap": {"status": "completed"}
            },
            "assets_manifest": [
                {
                    "name": "clip_01.mp4",
                    "filesize_bytes": 102400
                }
            ]
        }

        audit_res = self.learner.audit_project(manifest)
        self.assertTrue(audit_res["passed"])
        self.assertEqual(audit_res["overall_score"], 100.0)
        self.assertEqual(audit_res["violations_count"], 0)
        self.assertEqual(audit_res["total_penalties"], 0.0)

    def test_audit_violations_detection_and_penalties(self):
        """Verifica la detección precisa de violaciones múltiples y cálculo de penalizaciones."""
        flawed_manifest = {
            "project_id": "test_flawed_project",
            "archetype_id": "CITY_ROUTES_BEATS",
            "metadata": {
                "topic": "Rutas Urbanas por Madrid",
                "target_duration_seconds": 60,
                "actual_duration_seconds": 35.0  # Desfase R01
            },
            "script": "Caminando por la Gran Vía madrileña.",
            "subtitles_text": "Texto completamente inventado por alucinación de STT.",  # R03
            "scenes": [
                {
                    "id": "shot_01",
                    "duration_sec": 8.0,  # R04: Plano estático >5s
                    "ken_burns": False,
                    "prompt": "hyper-realistic 8k octane render glowing city"  # R06: Slop
                }
            ],
            "audio_dsp": {
                "ducking_db": -5.0  # R07: Ducking insuficiente
            },
            "thumbnail": {
                "microcopy": "ESTA ES LA RUTA MÁS INCREÍBLE Y LARGA DE TODA LA HISTORIA"  # R08: >3 palabras
            },
            "background_color": "#000000",  # R05: Blackdetect puro
            "scraping_config": {
                "user_agent": "python-requests/2.31.0"  # R10: Generic UA
            },
            "assets_manifest": [
                {
                    "name": "bad_clip.mp4",
                    "filesize_bytes": 1024  # R02: <5KB gate
                }
            ]
        }

        audit_res = self.learner.audit_project(flawed_manifest)
        self.assertFalse(audit_res["passed"])
        self.assertLess(audit_res["overall_score"], 50.0)
        self.assertGreater(audit_res["violations_count"], 5)

        violation_rule_ids = [v["rule_id"] for v in audit_res["violations"]]
        self.assertIn("R01_AUDIO_FIRST_LIFECYCLE", violation_rule_ids)
        self.assertIn("R02_STRICT_5KB_GATE", violation_rule_ids)
        self.assertIn("R03_LEVENSHTEIN_CAPTIONS", violation_rule_ids)
        self.assertIn("R04_RHYTHM_3_5S_CUT", violation_rule_ids)
        self.assertIn("R05_ANTI_BLACKDETECT", violation_rule_ids)
        self.assertIn("R06_DOP_7LAYER_PROMPT", violation_rule_ids)
        self.assertIn("R07_EBU_R128_MASTERING", violation_rule_ids)
        self.assertIn("R08_THUMBNAIL_SAFE_ZONE", violation_rule_ids)
        self.assertIn("R10_USER_AGENT_INSTITUTIONAL", violation_rule_ids)

    def test_montage_anomaly_detection(self):
        """Verifica la detección automática de errores específicos del montaje."""
        manifest = {
            "metadata": {"actual_duration_seconds": 20.0},
            "scenes": [
                {"id": "s1", "duration_sec": 3.0, "ken_burns": True},
                {"id": "s2", "duration_sec": 7.5, "ken_burns": False}  # Pacing drop
            ],
            "background_color": "#000000",  # Blackdetect risk
            "engine_specifications": {
                "video_encoder": {
                    "codec": "libx264",
                    "crf": 30,  # High CRF
                    "audio_bitrate": "64k"  # Low audio bitrate
                }
            }
        }

        anomalies_res = self.learner.detect_montage_anomalies(manifest)
        self.assertGreaterEqual(anomalies_res["total_anomalies"], 3)
        types = [a["type"] for a in anomalies_res["anomalies"]]
        self.assertIn("PACING_DROP", types)
        self.assertIn("BLACKDETECT_RISK", types)
        self.assertIn("BITRATE_ENCODING_DEGRADATION", types)
        self.assertIn("LOW_AUDIO_BITRATE", types)

    def test_auto_patch_workflow_version_increment(self):
        """Verifica que el auto-parcheo incremente la versión (v+1) y guarde el historial de mejoras."""
        # 1. Crear versión inicial v1 en el storage de prueba
        v1_data = {
            "id": "CITY_ROUTES_BEATS",
            "name": "City Routes & Music Beats",
            "version": 1,
            "version_label": "v1.0",
            "archetype_id": "CITY_ROUTES_BEATS",
            "background_color": "#000000",
            "ducking_db": -5.0,
            "max_shot_duration_sec": 8.0,
            "pipeline_graph": {"nodes": [], "connections": []}
        }
        v1_path = self.workflows_dir / "CITY_ROUTES_BEATS_v1.json"
        with open(v1_path, "w", encoding="utf-8") as f:
            json.dump(v1_data, f, indent=2)

        # 2. Auditar y auto-parchear
        audit_res = {
            "overall_score": 65.0,
            "passed": False,
            "violations": [
                {
                    "rule_id": "R05_ANTI_BLACKDETECT",
                    "name": "Paleta Anti-Blackdetect",
                    "recommended_patch": {"background_color": "#243048"}
                },
                {
                    "rule_id": "R07_EBU_R128_MASTERING",
                    "name": "Mastering EBU R128",
                    "recommended_patch": {"ducking_db": -20.0}
                },
                {
                    "rule_id": "R04_RHYTHM_3_5S_CUT",
                    "name": "Ritmo Cinemático",
                    "recommended_patch": {"max_shot_duration_sec": 4.0, "ken_burns_zoompan": True}
                }
            ]
        }

        patch_res = self.learner.auto_patch_workflow("CITY_ROUTES_BEATS", audit_res, "test_proj_001")
        self.assertEqual(patch_res["previous_version"], 1)
        self.assertEqual(patch_res["new_version"], 2)

        # 3. Verificar que se haya creado el archivo v2
        v2_path = self.workflows_dir / "CITY_ROUTES_BEATS_v2.json"
        self.assertTrue(v2_path.exists())

        with open(v2_path, "r", encoding="utf-8") as f:
            v2_data = json.load(f)

        self.assertEqual(v2_data["version"], 2)
        self.assertEqual(v2_data["background_color"], "#243048")
        self.assertEqual(v2_data["ducking_db"], -20.0)
        self.assertEqual(v2_data["max_shot_duration_sec"], 4.0)
        self.assertTrue(v2_data.get("ken_burns_zoompan"))
        self.assertGreater(len(v2_data.get("improvement_history", [])), 0)
        self.assertEqual(v2_data["improvement_history"][0]["from_version"], 1)
        self.assertEqual(v2_data["improvement_history"][0]["to_version"], 2)

    def test_full_audit_and_optimize_post_execution(self):
        """Verifica el flujo maestro integral de post-ejecución."""
        project_manifest = {
            "project_id": "2026-08-17_documental_test_run",
            "archetype_id": "HISTORICAL_SCRAPING",
            "metadata": {
                "topic": "La Expedición Balmis 1803",
                "target_duration_seconds": 45,
                "actual_duration_seconds": 45.0
            },
            "script": "En 1803 zarpó la expedición marítima filantrópica de la vacuna.",
            "subtitles_text": "En 1803 zarpó la expedición marítima filantrópica de la vacuna.",
            "scenes": [
                {"id": "sc1", "duration_sec": 6.5, "ken_burns": False}  # Pacing violation
            ],
            "background_color": "#000000",  # Blackdetect violation
            "audio_dsp": {"ducking_db": -8.0}  # Ducking violation
        }

        full_res = self.learner.audit_and_optimize_post_execution(
            project_manifest,
            archetype_id="HISTORICAL_SCRAPING",
            auto_patch=True
        )

        self.assertEqual(full_res["status"], "SUCCESS")
        self.assertEqual(full_res["project_id"], "2026-08-17_documental_test_run")
        self.assertFalse(full_res["audit"]["passed"])
        self.assertIsNotNone(full_res["workflow_patch"])
        self.assertEqual(full_res["workflow_patch"]["archetype_id"], "HISTORICAL_SCRAPING")
        self.assertGreaterEqual(full_res["workflow_patch"]["new_version"], 2)

        # Verificar reporte Markdown
        md_report = self.learner.export_report_markdown(full_res)
        self.assertIn("INFORME DE AUDITORÍA QA FORENSE", md_report)
        self.assertIn("R04_RHYTHM_3_5S_CUT", md_report)
        self.assertIn("R05_ANTI_BLACKDETECT", md_report)

    def test_performance_metrics_tracking(self):
        """Verifica la preservación de métricas de rendimiento por arquetipo."""
        # Registrar una ejecución
        manifest = {
            "project_id": "perf_test_01",
            "archetype_id": "PIXAR_3D_ANIMATION",
            "scenes": [{"id": "s1", "duration_sec": 3.0, "ken_burns": True}],
            "audio_dsp": {"ducking_db": -20.0},
            "background_color": "#243048"
        }
        self.learner.audit_and_optimize_post_execution(manifest, archetype_id="PIXAR_3D_ANIMATION", auto_patch=True)

        metrics = self.learner.get_performance_metrics("PIXAR_3D_ANIMATION")
        self.assertIn("archetype_performance", metrics)
        arch_perf = metrics["archetype_performance"]
        self.assertEqual(arch_perf["archetype_id"], "PIXAR_3D_ANIMATION")
        self.assertGreaterEqual(arch_perf["total_runs"], 1)
        self.assertGreater(arch_perf["avg_score"], 0.0)

    def test_learning_memory_tool_wrapper(self):
        """Verifica la interfaz de LearningMemoryTool."""
        manifest = {
            "project_id": "tool_test_01",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "scenes": [{"id": "s1", "duration_sec": 3.0, "ken_burns": True}],
            "audio_dsp": {"ducking_db": -20.0},
            "background_color": "#243048"
        }
        audit_output = self.memory_tool.audit_project(manifest)
        self.assertIn("score", audit_output)
        self.assertIn("passed", audit_output)
        self.assertIn("rules_checked", audit_output)
        self.assertEqual(audit_output["rules_checked"], 10)

    def test_realtime_event_emission_and_listener_callbacks(self):
        """Verifica la emisión de eventos en tiempo real, registro de callbacks y persistencia local."""
        received_events = []

        def sample_listener(event):
            received_events.append(event)

        self.learner.add_event_listener(sample_listener)

        ev = self.learner.emit_event(
            event_type="RULE_PASSED",
            message="Regla de prueba validada",
            payload={"test_key": "test_val"},
            session_id="session_test_123",
            project_id="proj_test_123",
            archetype_id="VOX_INVESTIGATIVE_DOC",
            severity="INFO",
            sync_firebase=False
        )

        self.assertIsNotNone(ev)
        self.assertEqual(ev["event_type"], "RULE_PASSED")
        self.assertEqual(ev["project_id"], "proj_test_123")
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0]["message"], "Regla de prueba validada")

        # Verificar persistencia en archivo local
        recent = self.learner.get_recent_events(limit=10)
        self.assertGreaterEqual(len(recent), 1)
        self.assertEqual(recent[0]["event_id"], ev["event_id"])

        # Verificar última sesión
        last_sess = self.learner.get_latest_session_events()
        self.assertEqual(last_sess["session_id"], "session_test_123")
        self.assertEqual(last_sess["project_id"], "proj_test_123")

        # Remover listener
        self.learner.remove_event_listener(sample_listener)
        self.learner.emit_event("INFO_EVENT", "Segundo evento", sync_firebase=False)
        self.assertEqual(len(received_events), 1)

    def test_event_types_coverage_in_audit_lifecycle(self):
        """Verifica que el ciclo completo emita la secuencia canónica de eventos."""
        captured_types = []

        def type_tracker(event):
            captured_types.append(event["event_type"])

        self.learner.add_event_listener(type_tracker)

        manifest = {
            "project_id": "lifecycle_event_test_project",
            "archetype_id": "FPV_URBAN_REAL_FLOW",
            "metadata": {"actual_duration_seconds": 15.0},
            "script": "Paseo en dron FPV por Tokio.",
            "subtitles_text": "Paseo en dron FPV por Tokio.",
            "scenes": [
                {"id": "sc1", "duration_sec": 7.0, "ken_burns": False}  # Pacing drop & violation
            ],
            "background_color": "#000000",  # Blackdetect violation
            "audio_dsp": {"ducking_db": -5.0}  # Ducking violation
        }

        res = self.learner.audit_and_optimize_post_execution(manifest, auto_patch=True)

        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("SESSION_STARTED", captured_types)
        self.assertIn("AUDIT_STARTED", captured_types)
        self.assertIn("EVALUATION_STARTED", captured_types)
        self.assertIn("VIOLATION_DETECTED", captured_types)
        self.assertIn("ANOMALY_DETECTED", captured_types)
        self.assertIn("AUDIT_COMPLETED", captured_types)
        self.assertIn("LESSON_RECORDED", captured_types)
        self.assertIn("CRITIQUE_RECORDED", captured_types)
        self.assertIn("AUTO_PATCH_STARTED", captured_types)
        self.assertIn("CORRECTION_APPLIED", captured_types)
        self.assertIn("VERSION_INCREMENTED", captured_types)
        self.assertIn("PERFORMANCE_UPDATED", captured_types)
        self.assertIn("SESSION_COMPLETED", captured_types)

        self.learner.remove_event_listener(type_tracker)

    def test_firebase_sync_methods_graceful_handling(self):
        """Verifica que los métodos de sincronización con Firebase Firestore degraden limpiamente."""
        from app.services import firebase_sync

        event_sample = {
            "event_id": "evt_test_firebase",
            "event_type": "RULE_PASSED",
            "timestamp": "2026-08-17T00:00:00",
            "project_id": "proj_fb_test",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "message": "Prueba de evento a Firebase",
            "severity": "INFO",
            "payload": {"score": 100}
        }

        # Comprobar que no lanza excepciones no controladas incluso sin red
        ok, msg = firebase_sync.emit_learning_event_to_firebase(event_sample)
        self.assertIsInstance(ok, bool)
        self.assertIsInstance(msg, str)

        improvements = [{"archetype_id": "VOX_INVESTIGATIVE_DOC", "from_version": 1, "to_version": 2}]
        ok_imp, msg_imp = firebase_sync.sync_workflow_improvements_to_firebase(improvements)
        self.assertIsInstance(ok_imp, bool)

        perf = {"VOX_INVESTIGATIVE_DOC": {"total_runs": 5, "avg_score": 95.0}}
        ok_perf, msg_perf = firebase_sync.sync_archetype_performance_to_firebase(perf)
        self.assertIsInstance(ok_perf, bool)


if __name__ == "__main__":
    unittest.main()

