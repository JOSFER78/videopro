"""
tests/test_workflows_api.py
Batería de Pruebas Unitarias y de Integración para los Endpoints de Workflows:
- GET  /api/v1/workflows
- GET  /api/v1/workflows/{id}
- POST /api/v1/workflows/{id}/run
- POST /api/v1/workflows/{id}/save
"""

import sys
import unittest
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.workflows import router as workflows_router
from app.core.orchestration.workflows import WORKFLOW_TEMPLATES


class TestWorkflowsAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = FastAPI(title="VideoPro Test API")
        app.include_router(workflows_router)
        cls.client = TestClient(app)

    def test_list_all_workflows_endpoint(self):
        """GET /api/v1/workflows lista todos los workflows disponibles y sus versiones."""
        response = self.client.get("/api/v1/workflows")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["total"], 5)
        self.assertIsInstance(data["workflows"], list)
        
        wf_ids = [w["id"] for w in data["workflows"]]
        self.assertIn("DOCUMENTARY_MASTER", wf_ids)
        self.assertIn("PIXAR_3D", wf_ids)

        # Validar estructura de un elemento
        first = data["workflows"][0]
        self.assertIn("id", first)
        self.assertIn("name", first)
        self.assertIn("version", first)
        self.assertIn("version_label", first)
        self.assertIn("required_capabilities", first)
        self.assertIn("recent_improvements", first)

    def test_list_workflows_filter_category(self):
        """GET /api/v1/workflows?category=storytelling filtra por categoría."""
        response = self.client.get("/api/v1/workflows?category=storytelling")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        for wf in data["workflows"]:
            self.assertEqual(wf["category"], "storytelling")

    def test_get_workflow_detail_endpoint(self):
        """GET /api/v1/workflows/{id} consulta detalles, parámetros y mejoras recientes."""
        response = self.client.get("/api/v1/workflows/DOCUMENTARY_MASTER")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "ok")
        self.assertIn("workflow", data)
        self.assertIn("archetype", data)
        self.assertIn("parameters", data)
        self.assertIn("recent_improvements", data)
        self.assertIn("versions", data)

        wf = data["workflow"]
        self.assertEqual(wf["id"], "DOCUMENTARY_MASTER")
        self.assertGreaterEqual(len(wf["nodes"]), 5)
        self.assertGreaterEqual(len(data["recent_improvements"]), 1)

    def test_get_workflow_detail_not_found(self):
        """GET /api/v1/workflows/{id} devuelve 404 para ID inexistente."""
        response = self.client.get("/api/v1/workflows/INEXISTENT_WF_999")
        self.assertEqual(response.status_code, 404)

    def test_run_workflow_headless_sync(self):
        """POST /api/v1/workflows/{id}/run ejecuta headless síncronamente."""
        payload = {
            "title": "Documental Test API Headless",
            "topic": "Historia y evolución de las telecomunicaciones",
            "duration_target_sec": 30.0,
            "async_execution": False,
            "interview_answers": {
                "historical_subject": "Telecomunicaciones",
                "narrative_focus": "Evolución tecnológica"
            }
        }
        response = self.client.post("/api/v1/workflows/DOCUMENTARY_MASTER/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "completed")
        self.assertIn("mission_id", data)
        self.assertIn("job_id", data)
        self.assertIn("mission", data)
        self.assertEqual(data["workflow_id"], "DOCUMENTARY_MASTER")

    def test_run_workflow_headless_async(self):
        """POST /api/v1/workflows/{id}/run despacha headless asíncronamente."""
        payload = {
            "title": "Shorts Viral API Test",
            "topic": "Top 3 inventos más sorprendentes",
            "duration_target_sec": 15.0,
            "async_execution": True,
            "preferences": {
                "aspect_ratio": "9:16",
                "voice_engine": "vibevoice"
            }
        }
        response = self.client.post("/api/v1/workflows/VIRAL_SHORTS_HOOK/run", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "dispatched")
        self.assertEqual(data["execution_mode"], "headless_async")
        self.assertIn("mission_id", data)
        self.assertIn("job_id", data)
        self.assertIn("plan", data)

    def test_save_workflow_new_version(self):
        """POST /api/v1/workflows/{id}/save guarda una nueva versión congelada."""
        payload = {
            "name": "Documental Maestro Mejorado v5",
            "description": "Nueva versión con optimización de ducking y nuevos nodos",
            "version_label": "v5.0"
        }
        response = self.client.post("/api/v1/workflows/DOCUMENTARY_MASTER/save", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "ok")
        self.assertIn("workflow", data)
        self.assertEqual(data["workflow"]["version_label"], "v5.0")

    def test_save_workflow_new_variant(self):
        """POST /api/v1/workflows/{id}/save guarda una nueva variante independiente."""
        variant_id = "WF_TEST_VARIANT_CUSTOM_01"
        payload = {
            "is_new_variant": True,
            "new_variant_id": variant_id,
            "name": "Variante Especializada de Prueba",
            "description": "Variante con ruteo experimental",
            "version_label": "v1.0-test"
        }
        response = self.client.post("/api/v1/workflows/DOCUMENTARY_MASTER/save", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["workflow"]["id"], variant_id)
        
        # Verificar que la nueva variante ahora es accesible
        get_res = self.client.get(f"/api/v1/workflows/{variant_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["workflow"]["id"], variant_id)


if __name__ == "__main__":
    unittest.main()
