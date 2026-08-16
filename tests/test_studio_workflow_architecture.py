"""
Batería de Pruebas Unitarias y de Integración — VideoPro Studio Workflow Architecture
Valida Capabilities, Engines, Providers, Workflows, Scene Routing, Request Planner, Adapters y Executor.
"""

import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.orchestration.capabilities import Capability, get_all_capabilities, get_capability
from app.core.orchestration.engines import get_all_engines, get_engine, get_engines_by_capability
from app.core.orchestration.providers import get_providers_for_engine, get_primary_provider
from app.core.orchestration.workflows import get_all_workflows, get_workflow, WORKFLOW_TEMPLATES
from app.core.orchestration.scene_router import SceneEngineRouter, VisualStrategy
from app.core.orchestration.planner import RequestPlanner
from app.core.orchestration.job import JobStatus, JobStepStatus
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.repository import StudioRepository


class TestStudioWorkflowArchitecture(unittest.TestCase):

    def test_capabilities_catalog(self):
        """Verifica que todas las capacidades esenciales del Studio estén registradas."""
        caps = get_all_capabilities()
        self.assertGreaterEqual(len(caps), 10)
        
        script_cap = get_capability(Capability.SCRIPT)
        self.assertIsNotNone(script_cap)
        self.assertEqual(script_cap.id, Capability.SCRIPT)
        self.assertTrue(script_cap.is_required_for_video)

        voice_cap = get_capability(Capability.VOICE_GENERATION)
        self.assertIsNotNone(voice_cap)

    def test_engines_catalog_and_capabilities(self):
        """Verifica que los motores declaren sus capacidades y fallbacks."""
        engines = get_all_engines()
        self.assertGreaterEqual(len(engines), 10)

        # Google Flow debe soportar VIDEO_GENERATION
        flow = get_engine("google_flow")
        self.assertIsNotNone(flow)
        self.assertIn(Capability.VIDEO_GENERATION, flow.capabilities)
        self.assertIn("flux_video", flow.fallbacks)

        # VibeVoice debe soportar VOICE_GENERATION
        vibe = get_engine("vibevoice")
        self.assertIsNotNone(vibe)
        self.assertIn(Capability.VOICE_GENERATION, vibe.capabilities)

        # Resolución de motores por capacidad
        video_engines = get_engines_by_capability(Capability.VIDEO_GENERATION)
        self.assertGreaterEqual(len(video_engines), 3)

    def test_providers_separation_from_engines(self):
        """Verifica la separación completa entre Engine ('CÓMO') y Provider ('DÓNDE')."""
        flux_provs = get_providers_for_engine("flux_video")
        self.assertGreaterEqual(len(flux_provs), 1)
        
        primary_flux = get_primary_provider("flux_video")
        self.assertIsNotNone(primary_flux)
        self.assertEqual(primary_flux.engine_id, "flux_video")

        vibe_provs = get_providers_for_engine("vibevoice")
        self.assertGreaterEqual(len(vibe_provs), 1)

    def test_workflow_templates(self):
        """Verifica que los workflows oficiales tengan grafos válidos y requerimientos consistentes."""
        workflows = get_all_workflows()
        self.assertGreaterEqual(len(workflows), 5)

        master = get_workflow("DOCUMENTARY_MASTER")
        self.assertIsNotNone(master)
        self.assertGreaterEqual(len(master.nodes), 8)
        self.assertGreaterEqual(len(master.connections), 8)

    def test_scene_level_engine_routing(self):
        """Verifica que el SceneEngineRouter distribuya motores según el contenido de la toma."""
        scenes = [
            {"id": "s1", "prompt": "Vuelo de dron aéreo sobre el skyline de la ciudad", "duration": 4.0},
            {"id": "s2", "prompt": "Primer plano de un arquitecto hablando sobre los planos", "duration": 5.0},
            {"id": "s3", "prompt": "Fotografía fotorrealista de la fachada de la Gran Vía de Madrid", "duration": 4.0},
        ]
        
        # Estrategia Automática / Híbrida
        planned = SceneEngineRouter.route_scenes(scenes, strategy=VisualStrategy.AUTOMATIC)
        self.assertEqual(len(planned), 3)
        
        # Escena aérea debe ir a google_flow
        self.assertEqual(planned[0].recommended_engine, "google_flow")
        # Escena personaje debe ir a flux_video
        self.assertEqual(planned[1].recommended_engine, "flux_video")
        # Escena lugar real debe ir a nanobanana
        self.assertEqual(planned[2].recommended_engine, "nanobanana")

    def test_request_planner_and_execution_plan(self):
        """Verifica la transformación de una petición de producción en un ExecutionPlan."""
        plan = RequestPlanner.plan_request(
            project_id="test_proj_001",
            user_prompt="Documental de prueba sobre la evolución espacial",
            target_duration=30,
            workflow_id="DOCUMENTARY_MASTER",
            visual_strategy=VisualStrategy.HYBRID
        )
        self.assertEqual(plan.project_id, "test_proj_001")
        self.assertEqual(plan.workflow_id, "DOCUMENTARY_MASTER")
        self.assertGreaterEqual(len(plan.steps), 8)
        self.assertGreaterEqual(len(plan.scenes), 3)

    def test_workflow_executor_end_to_end(self):
        """Verifica la ejecución de un Job completo a través de adaptadores con trazabilidad."""
        plan = RequestPlanner.plan_request(
            project_id="test_exec_001",
            user_prompt="Mini documental de prueba",
            target_duration=20,
            workflow_id="DOCUMENTARY_MASTER"
        )
        job = RequestPlanner.create_job_from_plan(plan)
        self.assertEqual(job.status, JobStatus.QUEUED)

        executor = WorkflowExecutor()
        completed_job = executor.execute_job(job)

        self.assertEqual(completed_job.status, JobStatus.COMPLETED)
        self.assertEqual(len(completed_job.steps), len(plan.steps))
        for step in completed_job.steps:
            self.assertEqual(step.status, JobStepStatus.COMPLETED)
            self.assertGreaterEqual(len(step.logs), 1)

        # Guardar en repositorio y recuperar
        StudioRepository.save_job(completed_job)
        retrieved = StudioRepository.get_job(completed_job.job_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.job_id, completed_job.job_id)


if __name__ == "__main__":
    unittest.main()
