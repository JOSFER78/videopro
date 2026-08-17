"""
Suite de Tests del Sistema de Workflows Canónicos — VideoPro Studio
Verifica la persistencia, integridad topológica, planificación, ejecución y compatibilidad API
de los 8 workflows canónicos iniciales (v1.0.0) en storage/workflows/:
1. chronodrift_tritemporal.json
2. fpv_urban_6dof.json
3. vox_investigative_doc.json
4. viral_shorts_hook_916.json
5. hollywood_documentary_35mm.json
6. nanoverse_macro_physics.json
7. living_canvas_3d.json
8. astrodrift_deep_space.json
"""

import sys
import os
import json
import unittest
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.workflows import router as workflows_router

from app.core.orchestration.capabilities import Capability
from app.core.orchestration.workflows import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowConnection,
    get_workflow,
    get_all_workflows,
    get_workflow_by_archetype,
    WORKFLOW_TEMPLATES
)
from app.core.orchestration.workflow_archetypes import (
    get_archetype,
    get_all_archetypes,
    ARCHETYPES_CATALOG,
    WorkflowArchetype
)
from app.core.orchestration.repository import StudioRepository
from app.core.orchestration.planner import RequestPlanner, ExecutionPlan
from app.core.orchestration.job import ExecutionJob, JobStatus
from app.core.orchestration.executor import WorkflowExecutor


class TestCanonicalWorkflowsSystem(unittest.TestCase):
    """Pruebas exhaustivas para los 8 workflows canónicos iniciales de VideoPro Studio."""

    CANONICAL_FILES = [
        "chronodrift_tritemporal.json",
        "fpv_urban_6dof.json",
        "vox_investigative_doc.json",
        "viral_shorts_hook_916.json",
        "hollywood_documentary_35mm.json",
        "nanoverse_macro_physics.json",
        "living_canvas_3d.json",
        "astrodrift_deep_space.json"
    ]

    CANONICAL_IDS = [
        "CHRONODRIFT_TRITEMPORAL",
        "FPV_URBAN_6DOF",
        "VOX_INVESTIGATIVE_DOC",
        "VIRAL_SHORTS_HOOK_916",
        "HOLLYWOOD_DOCUMENTARY_35MM",
        "NANOVERSE_MACRO_PHYSICS",
        "LIVING_CANVAS_3D",
        "ASTRODRIFT_DEEP_SPACE"
    ]

    @classmethod
    def setUpClass(cls):
        app = FastAPI(title="VideoPro Test API")
        app.include_router(workflows_router)
        cls.client = TestClient(app)
        cls.base_dir = Path(__file__).resolve().parent.parent
        cls.workflows_dir = cls.base_dir / "storage" / "workflows"

    # =========================================================================
    # 1. PRUEBAS DE EXISTENCIA E INTEGRIDAD DE ARCHIVOS
    # =========================================================================

    def test_canonical_files_exist_on_disk(self):
        """Verifica que los 8 archivos JSON canónicos existen físicamente en storage/workflows/."""
        for filename in self.CANONICAL_FILES:
            file_path = self.workflows_dir / filename
            self.assertTrue(
                file_path.is_file(),
                f"El archivo canónico {filename} debe existir en {self.workflows_dir}"
            )

    def test_canonical_files_valid_json_and_pydantic_schema(self):
        """Verifica que cada uno de los 8 archivos es un JSON válido y se deserializa en WorkflowDefinition."""
        for filename in self.CANONICAL_FILES:
            file_path = self.workflows_dir / filename
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validación Pydantic
            wf = WorkflowDefinition(**data)
            self.assertIsInstance(wf, WorkflowDefinition)
            self.assertEqual(wf.version, 1)
            self.assertEqual(wf.version_label, "v1.0.0")
            self.assertTrue(len(wf.id) > 0)
            self.assertTrue(len(wf.name) > 0)
            self.assertTrue(len(wf.description) > 0)
            self.assertGreaterEqual(len(wf.nodes), 4, f"{filename} debe contener al menos 4 nodos")
            self.assertGreaterEqual(len(wf.connections), 3, f"{filename} debe contener al menos 3 conexiones")
            self.assertGreaterEqual(len(wf.required_capabilities), 4, f"{filename} debe requerir capacidades de producción")
            self.assertIn("nodes", wf.pipeline_graph, f"{filename} debe contener pipeline_graph con nodos")

    def test_graph_topology_integrity_no_dangling_connections(self):
        """Verifica que todas las conexiones entre nodos referencian nodos existentes en el grafo."""
        for filename in self.CANONICAL_FILES:
            file_path = self.workflows_dir / filename
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            wf = WorkflowDefinition(**data)

            node_ids = {n.id for n in wf.nodes}
            for conn in wf.connections:
                self.assertIn(
                    conn.from_node, node_ids,
                    f"[{wf.id}] from_node '{conn.from_node}' de la conexión '{conn.id}' no existe en nodes"
                )
                self.assertIn(
                    conn.to_node, node_ids,
                    f"[{wf.id}] to_node '{conn.to_node}' de la conexión '{conn.id}' no existe en nodes"
                )

    # =========================================================================
    # 2. PRUEBAS DE RESOLUCIÓN Y REPOSITORIO
    # =========================================================================

    def test_repository_load_canonical_workflows(self):
        """Verifica que StudioRepository puede cargar individual y masivamente los workflows canónicos."""
        for filename in self.CANONICAL_FILES:
            file_path = str(self.workflows_dir / filename)
            wf = StudioRepository.load_workflow_from_file(file_path)
            self.assertIsNotNone(wf, f"StudioRepository falló al cargar {filename}")
            self.assertIsInstance(wf, WorkflowDefinition)

        all_stored = StudioRepository.load_all_workflows_from_storage()
        self.assertGreaterEqual(len(all_stored), 8)

        files = StudioRepository.list_stored_workflow_files()
        self.assertGreaterEqual(len(files), 8)

    def test_get_workflow_resolution_variations(self):
        """Verifica que get_workflow resuelve por ID exacto, minúsculas, mayúsculas y nombre de archivo."""
        for wf_id in self.CANONICAL_IDS:
            # 1. ID Exacto
            wf_exact = get_workflow(wf_id)
            self.assertIsNotNone(wf_exact, f"get_workflow({wf_id}) falló")
            self.assertEqual(wf_exact.id, wf_id)

            # 2. ID en minúsculas
            wf_lower = get_workflow(wf_id.lower())
            self.assertIsNotNone(wf_lower, f"get_workflow({wf_id.lower()}) falló")

            # 3. Filename stem
            stem = wf_id.lower()
            wf_stem = get_workflow(stem)
            self.assertIsNotNone(wf_stem, f"get_workflow({stem}) falló")

    def test_repository_save_and_version_bumping(self):
        """Verifica el guardado y versionado de un workflow canónico."""
        wf = get_workflow("CHRONODRIFT_TRITEMPORAL")
        self.assertIsNotNone(wf)

        # Clonar e incrementar versión
        data = wf.model_dump() if hasattr(wf, "model_dump") else wf.dict()
        data["version"] = 2
        data["version_label"] = "v2.0.0"
        data["description"] += " [Updated by Unit Test]"
        
        wf_v2 = WorkflowDefinition(**data)
        saved = StudioRepository.save_workflow(wf_v2)
        self.assertTrue(saved, "StudioRepository.save_workflow debe retornar True")

        # Verificar archivo generado en disco
        v2_path = self.workflows_dir / f"{wf_v2.id}_v2.json"
        self.assertTrue(v2_path.is_file(), f"El archivo {v2_path} debe haberse creado")

        # Cargar y verificar
        loaded_v2 = StudioRepository.load_workflow_from_file(str(v2_path))
        self.assertIsNotNone(loaded_v2)
        self.assertEqual(loaded_v2.version, 2)
        self.assertEqual(loaded_v2.version_label, "v2.0.0")

        # Limpiar archivo temporal de test v2
        if v2_path.is_file():
            os.remove(v2_path)

    # =========================================================================
    # 3. PRUEBAS DE ARQUETIPOS Y ENTREVISTA ADAPTATIVA
    # =========================================================================

    def test_all_canonical_archetypes_exist_in_catalog(self):
        """Verifica que todos los arquetipos canónicos están registrados en ARCHETYPES_CATALOG."""
        for arch_id in self.CANONICAL_IDS:
            arch = get_archetype(arch_id)
            self.assertIsNotNone(arch, f"Arquetipo {arch_id} no encontrado en ARCHETYPES_CATALOG")
            self.assertIsInstance(arch, WorkflowArchetype)
            self.assertGreater(len(arch.interview_schema), 0, f"El arquetipo {arch_id} debe tener preguntas de entrevista")
            self.assertIn("nodes", arch.pipeline_graph, f"El arquetipo {arch_id} debe tener pipeline_graph")

    def test_plan_from_interview_all_archetypes(self):
        """Verifica que RequestPlanner.plan_from_interview genera un ExecutionPlan válido para cada arquetipo."""
        for arch_id in self.CANONICAL_IDS:
            arch = get_archetype(arch_id)
            self.assertIsNotNone(arch)

            # Generar respuestas por defecto a partir del schema
            answers = {q.key: q.default_value for q in arch.interview_schema}

            plan = RequestPlanner.plan_from_interview(
                archetype_id=arch.id,
                interview_answers=answers,
                project_id=f"test_proj_{arch.id.lower()}"
            )

            self.assertIsInstance(plan, ExecutionPlan)
            self.assertEqual(plan.project_id, f"test_proj_{arch.id.lower()}")
            self.assertGreater(len(plan.steps), 0, f"El plan para {arch.id} debe contener pasos")
            self.assertGreater(len(plan.scenes), 0, f"El plan para {arch.id} debe contener escenas generadas")
            self.assertGreater(plan.estimated_total_duration_seconds, 0.0)

    # =========================================================================
    # 4. PRUEBAS DE PLANIFICACIÓN Y EJECUCIÓN (PLANNER & EXECUTOR)
    # =========================================================================

    def test_plan_request_all_canonical_workflows(self):
        """Verifica que RequestPlanner.plan_request resuelve capabilities y motores para cada workflow."""
        for wf_id in self.CANONICAL_IDS:
            plan = RequestPlanner.plan_request(
                project_id=f"plan_test_{wf_id.lower()}",
                user_prompt="Demostración de producción 4K de alta fidelidad",
                target_duration=60,
                workflow_id=wf_id
            )

            self.assertIsInstance(plan, ExecutionPlan)
            self.assertEqual(plan.workflow_id, wf_id)
            self.assertGreater(len(plan.steps), 0)

            # Validar que cada paso tiene engine y provider resueltos
            for step in plan.steps:
                self.assertTrue(len(step.engine_id) > 0, f"El paso {step.step_id} debe tener engine_id")
                self.assertTrue(len(step.provider_id) > 0, f"El paso {step.step_id} debe tener provider_id")

    def test_create_and_execute_job_simulation(self):
        """Verifica que un ExecutionJob se crea y completa exitosamente con WorkflowExecutor."""
        for wf_id in self.CANONICAL_IDS:
            plan = RequestPlanner.plan_request(
                project_id=f"job_sim_{wf_id.lower()}",
                user_prompt="Simulación de ejecución de test",
                target_duration=30,
                workflow_id=wf_id
            )

            job = RequestPlanner.create_job_from_plan(plan)
            self.assertIsInstance(job, ExecutionJob)
            self.assertEqual(job.status, JobStatus.QUEUED)
            self.assertEqual(len(job.steps), len(plan.steps))

            # Ejecución síncrona
            completed_job = WorkflowExecutor.execute_job_sync(job)
            self.assertEqual(
                completed_job.status, JobStatus.COMPLETED,
                f"El job para {wf_id} debe terminar en COMPLETED"
            )
            self.assertIsNotNone(completed_job.completed_at)
            for step in completed_job.steps:
                self.assertEqual(step.status, JobStatus.COMPLETED)

    # =========================================================================
    # 5. PRUEBAS DE ENDPOINTS REST API
    # =========================================================================

    def test_api_list_workflows_includes_canonical(self):
        """Verifica que GET /api/v1/workflows devuelve todos los workflows canónicos."""
        response = self.client.get("/api/v1/workflows")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("workflows", data)

        returned_ids = {w["id"] for w in data["workflows"]}
        for canonical_id in self.CANONICAL_IDS:
            self.assertIn(
                canonical_id, returned_ids,
                f"Workflow {canonical_id} debe aparecer en la lista de /api/v1/workflows"
            )

    def test_api_get_workflow_by_id_endpoints(self):
        """Verifica que GET /api/v1/workflows/{id} retorna detalles y pipeline_graph para cada workflow canónico."""
        for wf_id in self.CANONICAL_IDS:
            response = self.client.get(f"/api/v1/workflows/{wf_id}")
            self.assertEqual(
                response.status_code, 200,
                f"GET /api/v1/workflows/{wf_id} devolvió {response.status_code}: {response.text}"
            )
            payload = response.json()
            self.assertEqual(payload["status"], "ok")
            self.assertIn("workflow", payload)
            wf_data = payload["workflow"]
            self.assertEqual(wf_data["id"], wf_id)
            self.assertIn("pipeline_graph", wf_data)
            self.assertIn("nodes", wf_data["pipeline_graph"])
            self.assertGreater(len(wf_data["pipeline_graph"]["nodes"]), 0)

    def test_api_run_workflow_headless(self):
        """Verifica que POST /api/v1/workflows/{id}/run inicia misiones headless para los workflows canónicos."""
        for test_wf in ["CHRONODRIFT_TRITEMPORAL", "VOX_INVESTIGATIVE_DOC", "VIRAL_SHORTS_HOOK_916"]:
            req_body = {
                "user_prompt": f"Test Headless Runner para {test_wf}",
                "target_duration": 30,
                "aspect_ratio": "16:9"
            }
            response = self.client.post(f"/api/v1/workflows/{test_wf}/run", json=req_body)
            self.assertEqual(
                response.status_code, 200,
                f"POST /api/v1/workflows/{test_wf}/run devolvió {response.status_code}: {response.text}"
            )
            res_data = response.json()
            self.assertIn(res_data.get("status"), ("dispatched", "success", "ok"))
            self.assertIn("job_id", res_data)
            self.assertIn("mission_id", res_data)

    def test_api_save_custom_variant(self):
        """Verifica que POST /api/v1/workflows/{id}/save guarda variantes personalizadas correctamente."""
        variant_id = "WF_TEST_CHRONODRIFT_VARIANT_99"
        wf_original = get_workflow("CHRONODRIFT_TRITEMPORAL")
        self.assertIsNotNone(wf_original)

        req_body = {
            "name": "ChronoDrift Variante Personalizada Test",
            "pipeline_graph": wf_original.pipeline_graph,
            "new_variant_id": variant_id
        }

        response = self.client.post("/api/v1/workflows/CHRONODRIFT_TRITEMPORAL/save", json=req_body)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertIn(res_json.get("status"), ("ok", "success"))
        self.assertIn("workflow", res_json)
        self.assertEqual(res_json["workflow"]["id"], variant_id)

        # Verificar que la nueva variante se puede consultar por API
        get_res = self.client.get(f"/api/v1/workflows/{variant_id}")
        self.assertEqual(get_res.status_code, 200)

        # Limpiar archivo generado
        variant_path = self.workflows_dir / f"{variant_id}_v1.json"
        if variant_path.is_file():
            os.remove(variant_path)


if __name__ == "__main__":
    unittest.main()

