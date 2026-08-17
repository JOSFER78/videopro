"""
test_firebase_and_learning_ui.py
================================
Suite de Pruebas de Integración y Validación para:
1. Sincronización y persistencia dual de Workflows y Memoria de Aprendizaje en Firestore y Local.
2. Carga y renderizado seguro de datos en la WebUI de Aprendizaje (Streamlit).
3. Ciclo de vida completo: Simulación de producción -> Detección QA -> Auto-mejora (v+1) -> Actualización en Firebase y WebUI.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.config import config
from app.models.learning_experience import (
    LearnedLesson, LessonCategory, LessonSeverity,
    ProjectCritiqueFeedback, ProviderExecutionMetric, ProviderExecutionMode
)
from app.services.learning_memory_engine import (
    LearningMemoryEngine, DEFAULT_LESSONS, DEFAULT_METRICS
)
from app.services import firebase_sync
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_archetype, get_all_archetypes
from app.core.orchestration.workflows import (
    WorkflowDefinition, WorkflowNode, WorkflowConnection,
    get_workflow, get_all_workflows, get_workflow_by_archetype
)
from app.core.orchestration.videopro_system_registry import sync_entire_ontology_to_firebase
from scripts.workflow_learner import (
    WorkflowLearner, GOLDEN_RULES_CATALOG, LearningEventType,
    compute_levenshtein_distance, compute_text_similarity
)
from scripts.workflow_registry import (
    WorkflowRegistry, StructuredWorkflow, CANONICAL_ARCHETYPES_DEFS
)


class MockStreamlitSession(dict):
    def __getattr__(self, key):
        return self.get(key)
    def __setattr__(self, key, value):
        self[key] = value


class StreamlitContextMock:
    """Mock completo del framework Streamlit para probar el renderizado de la WebUI sin browser."""
    def __init__(self):
        self.session_state = MockStreamlitSession()
        self.markdown_calls = []
        self.metric_calls = []
        self.expander_calls = []
        self.button_calls = []
        self.selectbox_calls = []
        self.multiselect_calls = []
        self.text_input_calls = []
        self.text_area_calls = []
        self.success_calls = []
        self.warning_calls = []
        self.error_calls = []
        self.info_calls = []

    def markdown(self, body, unsafe_allow_html=False, **kwargs):
        self.markdown_calls.append(str(body))

    def metric(self, label, value, delta=None, help=None, **kwargs):
        self.metric_calls.append({"label": label, "value": value, "delta": delta, "help": help})

    def dialog(self, title):
        return self

    def caption(self, body, **kwargs):
        self.markdown_calls.append(f"CAPTION: {body}")

    def columns(self, spec, **kwargs):
        count = len(spec) if isinstance(spec, (list, tuple)) else int(spec)
        return [self for _ in range(count)]

    def tabs(self, tabs_list):
        return [self for _ in range(len(tabs_list))]

    def expander(self, label, expanded=False):
        self.expander_calls.append({"label": label, "expanded": expanded})
        return self

    def form(self, key, **kwargs):
        return self

    def form_submit_button(self, label, **kwargs):
        return False

    def button(self, label, key=None, **kwargs):
        self.button_calls.append({"label": label, "key": key})
        return False

    def selectbox(self, label, options, index=0, format_func=None, key=None, **kwargs):
        self.selectbox_calls.append({"label": label, "options": options, "key": key})
        if options:
            idx = min(index, len(options) - 1) if index >= 0 else 0
            return options[idx]
        return None

    def multiselect(self, label, options, default=None, key=None, **kwargs):
        self.multiselect_calls.append({"label": label, "options": options, "default": default, "key": key})
        return default or []

    def text_input(self, label, value="", key=None, **kwargs):
        self.text_input_calls.append({"label": label, "value": value, "key": key})
        return value

    def text_area(self, label, value="", key=None, **kwargs):
        self.text_area_calls.append({"label": label, "value": value, "key": key})
        return value

    def success(self, body, **kwargs):
        self.success_calls.append(str(body))

    def warning(self, body, **kwargs):
        self.warning_calls.append(str(body))

    def error(self, body, **kwargs):
        self.error_calls.append(str(body))

    def info(self, body, **kwargs):
        self.info_calls.append(str(body))

    def checkbox(self, label, value=False, key=None, **kwargs):
        return value

    def slider(self, label, min_value=None, max_value=None, value=None, step=None, key=None, **kwargs):
        return value if value is not None else min_value

    def json(self, body, expanded=True, **kwargs):
        self.markdown_calls.append(str(body))

    def code(self, body, language=None, **kwargs):
        self.markdown_calls.append(str(body))

    def dataframe(self, data, **kwargs):
        self.markdown_calls.append(str(data))

    def download_button(self, label, data=None, file_name=None, mime=None, key=None, **kwargs):
        return False

    def divider(self):
        pass

    def spinner(self, text=""):
        return self

    def rerun(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __call__(self, *args, **kwargs):
        return self


import types

# Registrar mock de paquete streamlit en sys.modules para permitir imports de vistas sin dependencia de UI
st_mod = types.ModuleType("streamlit")
st_mod.__path__ = []


class _StreamlitDecorators:
    def cache_data(self, *args, **kwargs):
        def wrapper(func):
            return func
        if args and callable(args[0]):
            return wrapper(args[0])
        return wrapper

    def cache_resource(self, *args, **kwargs):
        def wrapper(func):
            return func
        if args and callable(args[0]):
            return wrapper(args[0])
        return wrapper

    def experimental_memo(self, *args, **kwargs):
        def wrapper(func):
            return func
        if args and callable(args[0]):
            return wrapper(args[0])
        return wrapper

    def experimental_singleton(self, *args, **kwargs):
        def wrapper(func):
            return func
        if args and callable(args[0]):
            return wrapper(args[0])
        return wrapper


mock_decorators = _StreamlitDecorators()
mock_instance = StreamlitContextMock()
for attr in dir(mock_instance):
    if not attr.startswith("__"):
        setattr(st_mod, attr, getattr(mock_instance, attr))
for attr in dir(mock_decorators):
    if not attr.startswith("__"):
        setattr(st_mod, attr, getattr(mock_decorators, attr))

# Asegurar atributos UI que usan decoradores/context managers en webui/views sin depender de __getattr__ del módulo.
class _StubModule(types.ModuleType):
    def __getattr__(self, name):
        return mock_instance

st_mod.__class__ = _StubModule

st_comp = types.ModuleType("streamlit.components")
st_comp.__path__ = []
st_comp_v1 = types.ModuleType("streamlit.components.v1")
st_comp_v1.html = MagicMock()
st_comp_v1.declare_component = MagicMock()
st_comp.v1 = st_comp_v1
st_mod.components = st_comp

sys.modules["streamlit"] = st_mod
sys.modules["streamlit.components"] = st_comp
sys.modules["streamlit.components.v1"] = st_comp_v1




class TestFirebaseSyncAndPersistence(unittest.TestCase):
    """
    Bloque 1: Pruebas unitarias y de integración para la persistencia
    y sincronización con Firebase Firestore y almacenamiento local.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="videopro_fb_test_")
        self.storage_dir = Path(self.temp_dir) / "storage"
        self.workflows_dir = self.storage_dir / "workflows"
        self.learning_dir = self.storage_dir / "learning_memory"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        self.sample_workflow = {
            "id": "VOX_INVESTIGATIVE_DOC",
            "name": "VOX Investigative Documentary 4K",
            "description": "Workflow optimizado para documentales estilo VOX",
            "version": 2,
            "version_label": "v2.0-optimized",
            "archetype_id": "VOX_EXPLAINER",
            "required_capabilities": ["script", "voice_generation", "rendering"],
            "pipeline_graph": {
                "nodes": [
                    {"id": "node_01", "name": "Investigación", "category": "script"}
                ],
                "connections": []
            },
            "policies": {"retry_limit": 3, "auto_fallback": True},
            "created_at": "2026-08-16T12:00:00",
            "updated_at": "2026-08-17T02:00:00"
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.get")
    def test_firebase_status_connected_and_disconnected(self, mock_get, mock_auth):
        """Verifica la comprobación de estado de conexión con Firebase."""
        # 1. Sin token
        mock_auth.return_value = None
        st_no_tok = firebase_sync.get_firebase_status()
        self.assertFalse(st_no_tok["connected"])
        self.assertIn("no disponible", st_no_tok["message"])

        # 2. Con token y respuesta exitosa
        mock_auth.return_value = "fake_test_token_12345"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        st_ok = firebase_sync.get_firebase_status()
        self.assertTrue(st_ok["connected"])
        self.assertIn("Conectado con Firestore", st_ok["message"])

        # 3. Con token pero respuesta de error HTTP 500
        mock_resp.status_code = 500
        st_err = firebase_sync.get_firebase_status()
        self.assertFalse(st_err["connected"])
        self.assertIn("HTTP 500", st_err["message"])

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    @patch("requests.get")
    def test_workflow_backup_and_fetch_firestore(self, mock_get, mock_patch, mock_auth):
        """Valida el respaldo de un workflow individual en Firestore y su posterior recuperación."""
        mock_auth.return_value = "test_bearer_token"

        # 1. Respaldo exitoso
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        ok, msg = firebase_sync.backup_workflow_to_firebase(self.sample_workflow)
        self.assertTrue(ok)
        self.assertIn("respaldado en Firebase Firestore", msg)
        mock_patch.assert_called_once()
        patch_args, patch_kwargs = mock_patch.call_args
        self.assertIn("videopro_workflows/VOX_INVESTIGATIVE_DOC", patch_args[0])
        fields_sent = patch_kwargs["json"]["fields"]
        self.assertEqual(fields_sent["workflow_id"]["stringValue"], "VOX_INVESTIGATIVE_DOC")
        self.assertEqual(fields_sent["version"]["integerValue"], "2")

        # 2. Recuperación exitosa
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "fields": {
                "workflow_id": {"stringValue": "VOX_INVESTIGATIVE_DOC"},
                "workflow_json": {"stringValue": json.dumps(self.sample_workflow)},
                "version": {"integerValue": "2"}
            }
        }
        mock_get.return_value = mock_get_resp

        fetched_wf = firebase_sync.fetch_single_workflow_from_firebase("VOX_INVESTIGATIVE_DOC")
        self.assertIsNotNone(fetched_wf)
        self.assertEqual(fetched_wf["id"], "VOX_INVESTIGATIVE_DOC")
        self.assertEqual(fetched_wf["version"], 2)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.get")
    def test_fetch_all_workflows_from_firestore(self, mock_get, mock_auth):
        """Valida la descarga de la colección completa de workflows de Firestore."""
        mock_auth.return_value = "test_bearer_token"

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "documents": [
                {
                    "fields": {
                        "workflow_id": {"stringValue": "VOX_INVESTIGATIVE_DOC"},
                        "workflow_json": {"stringValue": json.dumps(self.sample_workflow)}
                    }
                },
                {
                    "fields": {
                        "workflow_id": {"stringValue": "CHRONODRIFT_TRITEMPORAL"},
                        "workflow_json": {"stringValue": json.dumps({"id": "CHRONODRIFT_TRITEMPORAL", "version": 1})}
                    }
                }
            ]
        }
        mock_get.return_value = mock_get_resp

        workflows = firebase_sync.fetch_all_workflows_from_firebase()
        self.assertEqual(len(workflows), 2)
        self.assertEqual(workflows[0]["id"], "VOX_INVESTIGATIVE_DOC")
        self.assertEqual(workflows[1]["id"], "CHRONODRIFT_TRITEMPORAL")

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    def test_sync_all_workflows_to_firestore(self, mock_patch, mock_auth):
        """Verifica la sincronización en lote de todos los workflows JSON locales a Firestore."""
        mock_auth.return_value = "test_bearer_token"
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        # Crear 3 archivos de prueba
        wf1 = {"id": "WF_01", "name": "Workflow 1", "version": 1}
        wf2 = {"id": "WF_02", "name": "Workflow 2", "version": 1}
        wf3 = {"id": "WF_03", "name": "Workflow 3", "version": 2}

        with open(self.workflows_dir / "wf1.json", "w") as f:
            json.dump(wf1, f)
        with open(self.workflows_dir / "wf2.json", "w") as f:
            json.dump(wf2, f)
        with open(self.workflows_dir / "wf3.json", "w") as f:
            json.dump(wf3, f)

        ok, msg = firebase_sync.sync_all_workflows_to_firebase(str(self.workflows_dir))
        self.assertTrue(ok)
        self.assertIn("Sincronizados 3 workflows", msg)
        self.assertGreaterEqual(mock_patch.call_count, 3)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    @patch("requests.get")
    def test_learning_memory_engine_firestore_sync_and_load(self, mock_get, mock_patch, mock_auth):
        """Valida que LearningMemoryEngine sincronice lecciones, críticas y métricas bidireccionalmente con Firestore."""
        mock_auth.return_value = "test_bearer_token"

        with patch("app.services.learning_memory_engine.STORAGE_DIR", self.learning_dir), \
             patch("app.services.learning_memory_engine.LESSONS_FILE", self.learning_dir / "lessons_catalog.json"), \
             patch("app.services.learning_memory_engine.CRITIQUES_FILE", self.learning_dir / "project_critiques.json"), \
             patch("app.services.learning_memory_engine.METRICS_FILE", self.learning_dir / "provider_metrics.json"):

            engine = LearningMemoryEngine()

            # 1. Registrar una nueva lección
            new_lesson = LearnedLesson(
                id="rule_test_cinematic_zoom",
                title="Zoom Suave Ken-Burns 4K",
                category=LessonCategory.VISUAL_PACING,
                severity=LessonSeverity.CRITICAL,
                what_failed="Tomas fijas estáticas aburridas",
                golden_rule="Aplicar zoompan suave en cada clip",
                applicable_nodes=["node_03_ingesta_multimedia_4k"],
                applicable_workflows=["ALL"]
            )
            saved = engine.register_lesson(new_lesson)
            self.assertTrue(saved)

            # 2. Sincronizar en Firestore
            mock_patch_resp = MagicMock()
            mock_patch_resp.status_code = 200
            mock_patch.return_value = mock_patch_resp

            ok, msg = engine.sync_to_firebase()
            self.assertTrue(ok)
            self.assertIn("sincronizada con éxito en Firestore", msg)
            self.assertGreaterEqual(mock_patch.call_count, 1)

            # 3. Descargar desde Firestore
            firestore_payload = {
                "lessons": [new_lesson.model_dump()],
                "critiques": [
                    {
                        "critique_id": "critique_test_01",
                        "project_id": "proj_madrid_120s",
                        "workflow_id": "VOX_INVESTIGATIVE_DOC",
                        "overall_score": 95,
                        "user_feedback_raw": "Excelente ritmo y tipografía",
                        "critique_breakdown": {"visual_pacing": 98, "audio_rhythm": 95},
                        "lessons_extracted": ["rule_test_cinematic_zoom"]
                    }
                ],
                "metrics": DEFAULT_METRICS
            }

            mock_get_resp = MagicMock()
            mock_get_resp.status_code = 200
            mock_get_resp.json.return_value = {
                "fields": {
                    "learning_memory_json": {"stringValue": json.dumps(firestore_payload)}
                }
            }
            mock_get.return_value = mock_get_resp

            load_ok, load_msg = engine.load_from_firebase()
            self.assertTrue(load_ok)
            self.assertIn("restaurada desde Firebase Firestore", load_msg)

            # Verificar que el estado local se actualizó
            critiques = engine.get_all_critiques()
            self.assertEqual(len(critiques), 1)
            self.assertEqual(critiques[0].project_id, "proj_madrid_120s")
            self.assertEqual(critiques[0].overall_score, 95)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    @patch("requests.get")
    def test_learning_events_emission_and_retrieval(self, mock_get, mock_patch, mock_auth):
        """Verifica la emisión de eventos en tiempo real y su descarga desde Firestore."""
        mock_auth.return_value = "test_bearer_token"

        # 1. Emisión de evento
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        event_data = {
            "event_id": "evt_test_qa_violation_01",
            "event_type": LearningEventType.VIOLATION_DETECTED,
            "session_id": "sess_test_100",
            "project_id": "proj_madrid_doc",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "message": "Violación de regla R04: Plano estático de 7.5s detectado.",
            "severity": "CRITICAL",
            "timestamp": datetime.now().isoformat(),
            "payload": {"duration": 7.5, "shot_id": "shot_03"}
        }

        ok, msg = firebase_sync.emit_learning_event_to_firebase(event_data)
        self.assertTrue(ok)
        self.assertIn("emitido a Firestore con éxito", msg)
        self.assertEqual(mock_patch.call_count, 2)  # live + events collection

        # 2. Descarga de eventos
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {
            "documents": [
                {
                    "fields": {
                        "event_id": {"stringValue": "evt_test_qa_violation_01"},
                        "event_type": {"stringValue": "VIOLATION_DETECTED"},
                        "project_id": {"stringValue": "proj_madrid_doc"},
                        "archetype_id": {"stringValue": "VOX_INVESTIGATIVE_DOC"},
                        "message": {"stringValue": "Violación R04"},
                        "severity": {"stringValue": "CRITICAL"},
                        "payload_json": {"stringValue": json.dumps({"duration": 7.5})}
                    }
                }
            ]
        }
        mock_get.return_value = mock_get_resp

        events = firebase_sync.fetch_learning_events_from_firebase(limit=10)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_id"], "evt_test_qa_violation_01")
        self.assertEqual(events[0]["event_type"], "VIOLATION_DETECTED")
        self.assertEqual(events[0]["payload"]["duration"], 7.5)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    def test_audit_report_and_improvements_firestore_sync(self, mock_patch, mock_auth):
        """Verifica la persistencia de auditorías QA e historial de mejoras en Firestore."""
        mock_auth.return_value = "test_bearer_token"
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        # 1. Auditoría
        sample_audit_report = {
            "project_id": "proj_madrid_curiosities",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "audit": {
                "overall_score": 85.0,
                "passed": False,
                "violations": [{"rule_id": "R04_RHYTHM_3_5S_CUT", "penalty": 15.0}]
            },
            "completed_at": datetime.now().isoformat()
        }
        ok_a, msg_a = firebase_sync.save_audit_report_to_firebase(sample_audit_report)
        self.assertTrue(ok_a)
        self.assertIn("guardado en Firestore", msg_a)

        # 2. Historial de mejoras
        improvements = [
            {
                "archetype_id": "VOX_INVESTIGATIVE_DOC",
                "previous_version": 1,
                "new_version": 2,
                "patches_applied": {"pacing": {"max_shot_duration_sec": 4.0}}
            }
        ]
        ok_i, msg_i = firebase_sync.sync_workflow_improvements_to_firebase(improvements)
        self.assertTrue(ok_i)
        self.assertIn("sincronizado en Firestore", msg_i)

        # 3. Métricas de arquetipo
        perf = {
            "VOX_INVESTIGATIVE_DOC": {
                "total_runs": 5,
                "passed_runs": 4,
                "avg_score": 93.4,
                "current_version": 2
            }
        }
        ok_p, msg_p = firebase_sync.sync_archetype_performance_to_firebase(perf)
        self.assertTrue(ok_p)
        self.assertIn("sincronizadas en Firestore", msg_p)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    def test_ontology_firestore_sync(self, mock_patch, mock_auth):
        """Verifica la persistencia de la ontología arquitectónica global."""
        mock_auth.return_value = "test_bearer_token"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_patch.return_value = mock_resp

        ok = sync_entire_ontology_to_firebase()
        self.assertTrue(ok)
        mock_patch.assert_called()


class TestLearningWebUIRendering(unittest.TestCase):
    """
    Bloque 2: Pruebas unitarias para validar que los paneles web de aprendizaje
    (view_learning_workflows y view_comfy_pipeline tab 5) carguen sin errores de renderizado.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="videopro_webui_test_")
        self.storage_dir = Path(self.temp_dir) / "storage"
        self.workflows_dir = self.storage_dir / "workflows"
        self.learning_dir = self.storage_dir / "learning_memory"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        self.registry = WorkflowRegistry(storage_dir=self.storage_dir, workflows_dir=self.workflows_dir)
        self.learner = WorkflowLearner(storage_dir=self.storage_dir, workflows_dir=self.workflows_dir, learning_dir=self.learning_dir)
        self.engine = LearningMemoryEngine()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_comfy_pipeline_learning_tab_rendering(self):
        """Valida que _render_learning_memory_tab en view_comfy_pipeline se ejecute sin excepciones."""
        from webui.views.view_comfy_pipeline import _render_learning_memory_tab

        st_mock = StreamlitContextMock()
        with patch("webui.views.view_comfy_pipeline.st", st_mock):
            # Ejecutar renderizado
            _render_learning_memory_tab()

            # Verificaciones de que se renderizaron los elementos esperados
            self.assertGreater(len(st_mock.metric_calls), 0)
            metric_labels = [m["label"] for m in st_mock.metric_calls]
            self.assertIn("Lecciones & Reglas", metric_labels)
            self.assertIn("Reglas Críticas", metric_labels)
            self.assertIn("Críticas Post-Rodaje", metric_labels)
            self.assertIn("Rutas Multi-Proveedor", metric_labels)

            # Verificar botones de sincronización
            button_labels = [b["label"] for b in st_mock.button_calls]
            self.assertTrue(any("Sincronizar Memoria" in bl for bl in button_labels))
            self.assertTrue(any("Descargar Memoria" in bl for bl in button_labels))

    def test_comfy_pipeline_learning_tab_register_lesson(self):
        """Verifica que el formulario de nueva lección en view_comfy_pipeline use register_lesson de forma correcta."""
        from webui.views.view_comfy_pipeline import _render_learning_memory_tab

        st_mock = StreamlitContextMock()
        with patch("webui.views.view_comfy_pipeline.st", st_mock), \
             patch("app.services.learning_memory_engine.learning_engine.register_lesson") as mock_reg:

            mock_reg.return_value = True
            # Simular submit del formulario
            st_mock.form_submit_button = MagicMock(return_value=True)

            _render_learning_memory_tab()
            self.assertTrue(mock_reg.called)
            lesson_arg = mock_reg.call_args[0][0]
            self.assertIsInstance(lesson_arg, LearnedLesson)
            self.assertEqual(lesson_arg.severity, LessonSeverity.STRICT)

    def test_view_learning_workflows_full_rendering(self):
        """Valida que render_learning_workflows_view se ejecute sin errores en todos sus componentes."""
        from webui.views import view_learning_workflows

        st_mock = StreamlitContextMock()
        with patch("webui.views.view_learning_workflows.st", st_mock), \
             patch("webui.views.view_learning_workflows._get_services", return_value=(self.registry, self.learner, MagicMock())):

            view_learning_workflows.render_learning_workflows_view()

            # Verificar renderizado de métricas y cards
            markdown_content = "\n".join(st_mock.markdown_calls)
            self.assertIn("Aprendizaje Continuo & Control de Workflows", markdown_content)
            self.assertIn("ARQUETIPOS ACTIVOS", markdown_content)
            self.assertIn("REGLAS DE ORO QA", markdown_content)
            self.assertIn("LECCIONES APRENDIDAS", markdown_content)

    def test_view_learning_workflows_subtabs_rendering(self):
        """Valida el renderizado individual de cada una de las 4 pestañas de view_learning_workflows."""
        from webui.views.view_learning_workflows import (
            _render_archetype_viewer_tab,
            _render_version_diffs_tab,
            _render_qa_audit_tab,
            _render_control_panel_tab
        )

        st_mock = StreamlitContextMock()
        dispatcher_mock = MagicMock()

        # Tab 1: Visor de Arquetipos
        with patch("webui.views.view_learning_workflows.st", st_mock):
            _render_archetype_viewer_tab(self.registry)
            self.assertTrue(any("Arquetipo" in s["label"] for s in st_mock.selectbox_calls))

        # Tab 2: Diffs de Versiones
        with patch("webui.views.view_learning_workflows.st", st_mock):
            _render_version_diffs_tab(self.registry, self.learner)

        # Tab 3: Tablero QA R01-R10
        with patch("webui.views.view_learning_workflows.st", st_mock):
            _render_qa_audit_tab(self.learner, dispatcher_mock)

        # Tab 4: Panel de Control y Auto-Mejora
        with patch("webui.views.view_learning_workflows.st", st_mock):
            _render_control_panel_tab(self.registry, self.learner, dispatcher_mock)

        self.assertEqual(len(st_mock.error_calls), 0)

    def test_view_learning_workflows_sample_manifest_generation(self):
        """Valida que los manifiestos de prueba generados por la UI sean válidos para auditoría."""
        from webui.views.view_learning_workflows import _build_sample_manifest

        # 1. Manifiesto con fallos intencionales
        flawed = _build_sample_manifest("test_flawed_project_demo")
        self.assertEqual(flawed["project_id"], "test_flawed_project_demo")
        self.assertEqual(flawed["background_color"], "#000000")
        self.assertLess(flawed["assets_manifest"][0]["filesize_bytes"], 5120)

        # 2. Manifiesto canónico de alta calidad
        clean = _build_sample_manifest("test_clean_project")
        self.assertEqual(clean["project_id"], "test_clean_project")
        self.assertEqual(clean["background_color"], "#243048")
        self.assertGreater(clean["assets_manifest"][0]["filesize_bytes"], 5120)


class TestCompleteAutoImprovementCycle(unittest.TestCase):
    """
    Bloque 3: Validación del ciclo completo:
    Simulación de vídeo defectuoso -> Detección de Reglas QA -> Auto-mejora a v+1 -> Persistencia y Actualización en Firebase y WebUI.
    """

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="videopro_lifecycle_test_")
        self.storage_dir = Path(self.temp_dir) / "storage"
        self.workflows_dir = self.storage_dir / "workflows"
        self.learning_dir = self.storage_dir / "learning_memory"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        self.learner = WorkflowLearner(
            storage_dir=self.storage_dir,
            workflows_dir=self.workflows_dir,
            learning_dir=self.learning_dir
        )
        self.registry = WorkflowRegistry(
            storage_dir=self.storage_dir,
            workflows_dir=self.workflows_dir
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("app.services.firebase_sync._get_firebase_auth_token")
    @patch("requests.patch")
    def test_full_lifecycle_simulation_flawed_video_to_vplus1_and_firebase_update(self, mock_patch, mock_auth):
        """
        Ciclo completo:
        1. Simula un montaje con 5 violaciones de QA críticas (R01 desync, R04 plano largo, R05 blackdetect, R07 ducking débil, R10 generic UA).
        2. WorkflowLearner audita el proyecto, calcula penalizaciones y emite eventos en tiempo real.
        3. Genera y guarda las lecciones aprendidas en LearningMemoryEngine.
        4. Auto-parchea los parámetros del arquetipo VOX_INVESTIGATIVE_DOC y genera la versión v2 optimizada.
        5. Sincroniza el resultado con Firebase Firestore.
        6. Verifica que la nueva versión v2 y las lecciones queden reflejadas en la WebUI.
        """
        mock_auth.return_value = "test_bearer_token"
        mock_patch_resp = MagicMock()
        mock_patch_resp.status_code = 200
        mock_patch.return_value = mock_patch_resp

        # 1. Manifiesto con múltiples violaciones de calidad
        flawed_project_manifest = {
            "project_id": "simulated_vox_flawed_01",
            "archetype_id": "VOX_INVESTIGATIVE_DOC",
            "metadata": {
                "topic": "La Conspiración del Oro de Moscú",
                "target_duration_seconds": 120.0,
                "actual_duration_seconds": 95.0  # Desfase 25s (>5s => R01 FAILED)
            },
            "script": "En 1936, las reservas de oro del Banco de España fueron trasladadas en secreto a Cartagena.",
            "subtitles_text": "En 1936, las reservas de oro del Banco de España fueron trasladadas en secreto a Cartagena.",
            "scenes": [
                {
                    "id": "scene_01",
                    "duration_sec": 8.0,  # Plano estático de 8s (>5s => R04 FAILED)
                    "ken_burns": False,
                    "prompt": "ARRI Alexa 35mm, secret vault loading crates"
                }
            ],
            "audio_dsp": {
                "ducking_db": -6.0,  # Ducking insuficiente (-6dB > -18dB => R07 FAILED)
                "target_lufs": -14.0
            },
            "thumbnail": {
                "microcopy": "EL ORO DE MOSCU"
            },
            "background_color": "#000000",  # Negro puro digital (=> R05 FAILED)
            "scraping_config": {
                "user_agent": "python-requests/2.31.0"  # User-Agent genérico (=> R10 FAILED)
            },
            "assets_manifest": [
                {
                    "name": "asset_doc_01.jpg",
                    "filesize_bytes": 102400
                }
            ]
        }

        # Monitorear eventos en tiempo real emitidos durante el ciclo
        emitted_events = []
        self.learner.add_event_listener(lambda evt: emitted_events.append(evt))

        # 2. Ejecutar auditoría y auto-mejora
        result = self.learner.audit_and_optimize_post_execution(
            project_path_or_manifest=flawed_project_manifest,
            archetype_id="VOX_INVESTIGATIVE_DOC",
            auto_patch=True
        )

        # Verificaciones del resultado de auditoría
        self.assertEqual(result["status"], "SUCCESS")
        audit = result["audit"]
        self.assertFalse(audit["passed"])
        self.assertLess(audit["overall_score"], 60.0)  # Múltiples penalizaciones aplicadas
        self.assertGreaterEqual(audit["violations_count"], 4)

        violation_rule_ids = [v["rule_id"] for v in audit["violations"]]
        self.assertIn("R01_AUDIO_FIRST_LIFECYCLE", violation_rule_ids)
        self.assertIn("R04_RHYTHM_3_5S_CUT", violation_rule_ids)
        self.assertIn("R05_ANTI_BLACKDETECT", violation_rule_ids)
        self.assertIn("R07_EBU_R128_MASTERING", violation_rule_ids)
        self.assertIn("R10_USER_AGENT_INSTITUTIONAL", violation_rule_ids)

        # 3. Verificación de Auto-parcheo y generación de workflow v+1
        patch_info = result["workflow_patch"]
        self.assertIsNotNone(patch_info)
        self.assertEqual(patch_info["status"], "OPTIMIZED")
        self.assertEqual(patch_info["previous_version"], 1)
        self.assertEqual(patch_info["new_version"], 2)

        # Verificar archivo físico del nuevo workflow v2
        new_wf_file = Path(patch_info["workflow_file"])
        self.assertTrue(new_wf_file.exists())

        with open(new_wf_file, "r", encoding="utf-8") as f:
            new_wf_data = json.load(f)

        self.assertEqual(new_wf_data["version"], 2)
        bg_val = new_wf_data.get("background_color", new_wf_data.get("canvas_color", {}).get("background_color"))
        self.assertEqual(bg_val, "#243048")  # Parche R05 aplicado
        ducking_val = new_wf_data.get("ducking_db", new_wf_data.get("audio_dsp", {}).get("ducking_db"))
        self.assertEqual(ducking_val, -20.0)  # Parche R07 aplicado
        ua_val = new_wf_data.get("user_agent", new_wf_data.get("scraping_config", {}).get("user_agent"))
        self.assertEqual(ua_val, "VideoProHermesBot/1.0 (https://videopro.app; contact@videopro.app)")  # Parche R10 aplicado
        pacing_val = new_wf_data.get("ken_burns_zoompan", new_wf_data.get("pacing", {}).get("ken_burns_zoompan"))
        self.assertTrue(pacing_val)  # Parche R04 aplicado

        # 4. Verificación de eventos emitidos
        event_types = [e["event_type"] for e in emitted_events]
        self.assertIn(LearningEventType.AUDIT_STARTED, event_types)
        self.assertIn(LearningEventType.VIOLATION_DETECTED, event_types)
        self.assertIn(LearningEventType.AUTO_PATCH_STARTED, event_types)
        self.assertIn(LearningEventType.VERSION_INCREMENTED, event_types)

        # 5. Verificación de sincronización con Firestore
        # Se debe haber emitido la actualización de auditoría, mejoras y eventos
        self.assertGreater(mock_patch.call_count, 0)

        # 6. Verificación de renderizado en WebUI con los nuevos datos
        from webui.views.view_learning_workflows import _render_version_diffs_tab, _render_control_panel_tab

        st_mock = StreamlitContextMock()
        with patch("webui.views.view_learning_workflows.st", st_mock):
            _render_version_diffs_tab(self.registry, self.learner)
            _render_control_panel_tab(self.registry, self.learner, MagicMock())

        # No debe haber errores de renderizado
        self.assertEqual(len(st_mock.error_calls), 0)

    def test_full_lifecycle_clean_project_no_patch_needed(self):
        """Verifica que un proyecto que cumple todas las reglas obtenga 100/100 y no genere parche innecesario."""
        perfect_manifest = {
            "project_id": "simulated_perfect_doc",
            "archetype_id": "VOX_EXPLAINER",
            "metadata": {
                "topic": "La Bóveda Acorazada",
                "target_duration_seconds": 3.0,
                "actual_duration_seconds": 3.0
            },
            "script": "Cámara subterránea protegida por agua.",
            "subtitles_text": "Cámara subterránea protegida por agua.",
            "scenes": [
                {
                    "id": "s1",
                    "duration_sec": 3.0,
                    "ken_burns": True,
                    "prompt": "ARRI Alexa 35mm, subterranean vault"
                }
            ],
            "audio_dsp": {
                "ducking_db": -20.0,
                "target_lufs": -14.0
            },
            "thumbnail": {
                "microcopy": "BOVEDA ACORAZADA"
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
                    "filesize_bytes": 500000
                }
            ]
        }

        result = self.learner.audit_and_optimize_post_execution(
            project_path_or_manifest=perfect_manifest,
            archetype_id="VOX_EXPLAINER",
            auto_patch=True
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertTrue(result["audit"]["passed"])
        self.assertEqual(result["audit"]["overall_score"], 100.0)
        self.assertIsNone(result["workflow_patch"])

    def test_multi_version_incremental_patching_and_diffs(self):
        """Valida que múltiples optimizaciones sucesivas incrementen v1 -> v2 -> v3 correctamente."""
        # 1. Primera optimización v1 -> v2
        flawed_1 = {
            "project_id": "p1",
            "archetype_id": "CITY_ROUTES_BEATS",
            "background_color": "#000000",
            "scenes": [{"duration_sec": 7.0, "ken_burns": False}],
            "audio_dsp": {"ducking_db": -5.0},
            "scraping_config": {"user_agent": "python-requests/2.31.0"},
            "metadata": {"target_duration_seconds": 60, "actual_duration_seconds": 40},
            "assets_manifest": [{"name": "a.mp4", "filesize_bytes": 100000}]
        }
        res1 = self.learner.audit_and_optimize_post_execution(flawed_1, auto_patch=True)
        self.assertEqual(res1["workflow_patch"]["new_version"], 2)

        # 2. Segunda optimización v2 -> v3
        flawed_2 = {
            "project_id": "p2",
            "archetype_id": "CITY_ROUTES_BEATS",
            "background_color": "#000000",
            "scenes": [{"duration_sec": 8.0, "ken_burns": False}],
            "audio_dsp": {"ducking_db": -2.0},
            "scraping_config": {"user_agent": "curl/7.68.0"},
            "metadata": {"target_duration_seconds": 60, "actual_duration_seconds": 30},
            "assets_manifest": [{"name": "b.mp4", "filesize_bytes": 100000}]
        }
        res2 = self.learner.audit_and_optimize_post_execution(flawed_2, auto_patch=True)
        self.assertEqual(res2["workflow_patch"]["new_version"], 3)

        # Verificar historial de mejoras
        metrics = self.learner.get_performance_metrics("CITY_ROUTES_BEATS")
        self.assertEqual(len(metrics["improvements"]), 2)
        self.assertEqual(metrics["archetype_performance"]["current_version"], 3)


if __name__ == "__main__":
    unittest.main()
