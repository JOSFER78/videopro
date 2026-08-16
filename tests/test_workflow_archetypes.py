"""
Batería de Pruebas Unitarias y de Integración — Specialized Workflow Archetypes & ComfyUI Pipelines
Valida los 5 Arquetipos de Producción, sus Entrevistas Adaptativas, sus Grafos ComfyUI y el Bucle de Versionado.
"""

import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.orchestration.workflow_archetypes import get_all_archetypes, get_archetype, ARCHETYPES_CATALOG
from app.core.orchestration.workflows import get_all_workflows, get_workflow, get_workflow_by_archetype
from app.core.orchestration.planner import RequestPlanner
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.job import JobStatus, JobStepStatus
from app.core.orchestration.repository import StudioRepository


class TestWorkflowArchetypes(unittest.TestCase):

    def test_archetypes_catalog_integrity(self):
        """Verifica que existan los 5 arquetipos de producción especializados."""
        archetypes = get_all_archetypes()
        self.assertEqual(len(archetypes), 5)
        
        expected_ids = ["PIXAR_3D_ANIMATION", "HISTORICAL_SCRAPING", "CITY_ROUTES_BEATS", "VIRAL_SHORTS_HOOK", "DEEP_EXPLAINER_ESSAY"]
        for eid in expected_ids:
            arch = get_archetype(eid)
            self.assertIsNotNone(arch, f"Arquetipo {eid} no encontrado")
            self.assertGreater(len(arch.interview_schema), 1)
            self.assertIn("nodes", arch.pipeline_graph)
            self.assertGreaterEqual(len(arch.pipeline_graph["nodes"]), 4)

    def test_pixar_3d_interview_and_plan(self):
        """Verifica que la entrevista de Pixar 3D genere un plan con personajes y estilo animado."""
        answers = {
            "character_name": "Toby el osito astronauta",
            "story_conflict": "Reparar la linterna lunar antes de que anochezca",
            "emotional_tone": "Tierno y Conmovedor",
            "visual_environment": "Superficie Lunar Brillante"
        }
        plan = RequestPlanner.plan_from_interview("PIXAR_3D_ANIMATION", answers, project_id="test_pixar_01")
        self.assertEqual(plan.metadata.get("archetype_id"), "PIXAR_3D_ANIMATION")
        self.assertGreaterEqual(len(plan.scenes), 3)
        self.assertTrue(any("Toby el osito astronauta" in sc.prompt for sc in plan.scenes))
        self.assertEqual(plan.estimated_total_cost, 0.0)

    def test_city_routes_interview_and_plan(self):
        """Verifica que la entrevista de Rutas Urbanas genere planos de Google Flow y música Synthwave."""
        answers = {
            "city_and_spots": "Tokio: Shibuya, Shinjuku y Torre de Tokio",
            "music_beat_style": "Electronic City Synthwave (118 BPM)",
            "facts_focus": "Secretos Arquitectónicos & Récords"
        }
        plan = RequestPlanner.plan_from_interview("CITY_ROUTES_BEATS", answers, project_id="test_tokyo_01")
        self.assertEqual(plan.metadata.get("archetype_id"), "CITY_ROUTES_BEATS")
        self.assertGreaterEqual(len(plan.scenes), 3)
        # Debe haber planos con Google Flow para vistas orbitales
        self.assertTrue(any(sc.recommended_engine == "google_flow" for sc in plan.scenes))

    def test_historical_scraping_plan_and_execution(self):
        """Verifica la ejecución completa de un Job de Documental Histórico con Scraping."""
        answers = {
            "historical_subject": "La Expedición Balmis de la Vacuna en 1803",
            "scraping_depth": "Exhaustiva (Wikipedia + Commons + Hemerotecas)",
            "gap_filling_policy": "Híbrido Restauración + Recreación 35mm"
        }
        plan = RequestPlanner.plan_from_interview("HISTORICAL_SCRAPING", answers, project_id="test_balmis_01")
        job = RequestPlanner.create_job_from_plan(plan)
        
        executor = WorkflowExecutor()
        completed_job = executor.execute_job(job)
        
        self.assertEqual(completed_job.status, JobStatus.COMPLETED)
        self.assertEqual(len(completed_job.steps), len(plan.steps))
        for s in completed_job.steps:
            self.assertEqual(s.status, JobStepStatus.COMPLETED)

    def test_workflow_versioning_loop(self):
        """Verifica el bucle de perfeccionamiento continuo y versionado de workflows."""
        wf = get_workflow_by_archetype("CITY_ROUTES_BEATS")
        self.assertIsNotNone(wf)
        
        # Clonar y versionar
        new_wf = wf.copy(deep=True)
        new_wf.version = 2
        new_wf.version_label = "v2.0-tuned-beats"
        StudioRepository.save_workflow(new_wf)
        
        retrieved = get_workflow("CITY_ROUTES_BEATS")
        self.assertEqual(retrieved.version, 2)
        self.assertEqual(retrieved.version_label, "v2.0-tuned-beats")


if __name__ == "__main__":
    unittest.main()
