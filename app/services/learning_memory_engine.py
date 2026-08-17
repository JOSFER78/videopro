"""
learning_memory_engine.py
Motor de Aprendizaje Continuo y Memoria de Experiencia — VideoPro Studio & Hermes.
Gestiona el catálogo de lecciones aprendidas, estándares de calidad, evaluaciones post-producción
y métricas de proveedores multi-cloud con persistencia dual en Firebase Firestore y JSON local.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.learning_experience import (
    LearnedLesson, LessonCategory, LessonSeverity,
    ProjectCritiqueFeedback, ProviderExecutionMetric, ProviderExecutionMode
)
from app.config import config

logger = logging.getLogger("videopro.learning_memory")

STORAGE_DIR = BASE_DIR / "storage" / "learning_memory"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

LESSONS_FILE = STORAGE_DIR / "lessons_catalog.json"
CRITIQUES_FILE = STORAGE_DIR / "project_critiques.json"
METRICS_FILE = STORAGE_DIR / "provider_metrics.json"


# ============================================================================
# SEMILLERO CANÓNICO DE LECCIONES APRENDIDAS Y ESTÁNDARES ÁUREOS
# ============================================================================
DEFAULT_LESSONS: List[Dict[str, Any]] = [
    {
        "id": "rule_dynamic_visual_cutaways_3s",
        "title": "Ritmo Cinemático: Cortes y Variación Visual Dinámica cada 3-5s",
        "category": "VISUAL_PACING",
        "severity": "CRITICAL",
        "what_failed": "Planos fijos o estáticos prolongados (>6-10s) mientras la voz avanza, provocando pérdida de retención y sensación de vídeo aficionado aburrido.",
        "golden_rule": "Cambiar de ángulo, aplicar movimiento Ken-Burns (zoompan) o alternar B-Roll/fotogramas de detalle cada 3 a 5 segundos como máximo.",
        "applicable_nodes": ["node_03_ingesta_multimedia_4k", "node_04_composicion_motion_graphics"],
        "applicable_workflows": ["ALL"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 12,
        "success_rating": 0.98
    },
    {
        "id": "rule_sleek_broadcast_typography",
        "title": "Tipografía Broadcast: Tercios Inferiores Limpios y Sin Cajas Invasivas",
        "category": "TYPOGRAPHY_DESIGN",
        "severity": "CRITICAL",
        "what_failed": "Uso de recuadros oscuros toscos con texto invasivo y leyendas explícitas como 'FUENTE: ...' que tapan la belleza visual.",
        "golden_rule": "Diseño tipográfico sutil y moderno (Inter / Outfit), sombras suaves en texto, lower-thirds de alta gama con márgenes elegantes y sin enlaces crudos.",
        "applicable_nodes": ["node_04_composicion_motion_graphics"],
        "applicable_workflows": ["ALL"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 8,
        "success_rating": 0.95
    },
    {
        "id": "rule_exact_thematic_correspondence",
        "title": "Correspondencia Semántica Exacta: Imagen Específica por Cada Frase",
        "category": "ASSET_MATCHING",
        "severity": "CRITICAL",
        "what_failed": "Mostrar planos exteriores genéricos de un edificio cuando la locución describe la cámara acorazada subterránea, túneles o mecanismos internos.",
        "golden_rule": "Cada frase o concepto clave debe ilustrarse con el activo visual específico del elemento mencionado (cámara, maquinaria, frescos, documentos).",
        "applicable_nodes": ["node_01_investigacion_y_narrativa", "node_03_ingesta_multimedia_4k"],
        "applicable_workflows": ["ALL"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 15,
        "success_rating": 0.99
    },
    {
        "id": "rule_wikimedia_institutional_headers",
        "title": "Ingesta Wikimedia: Headers Institucionales Anti-403 Forbidden",
        "category": "INVESTIGATION_RESEARCH",
        "severity": "STRICT",
        "what_failed": "Descargas de archivos históricos de Wikimedia Commons rechazadas con HTTP 403 Forbidden por User-Agent genérico de Python.",
        "golden_rule": "Utilizar siempre cabecera User-Agent institucional obligatoria (ej: VideoProHermesBot/1.0) para garantizar tasa de descarga del 100%.",
        "applicable_nodes": ["node_03_ingesta_multimedia_4k"],
        "applicable_workflows": ["ALL"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 24,
        "success_rating": 1.0
    },
    {
        "id": "rule_audio_first_cadence_ducking",
        "title": "Audio-First: Montaje Sincronizado al Ritmo y Ducking Musical -18dB",
        "category": "AUDIO_RHYTHM",
        "severity": "STRICT",
        "what_failed": "Música de fondo compitiendo con la voz del narrador o tiempos de plano desfasados de las frases habladas.",
        "golden_rule": "Audio-First absoluto: la duración de cada toma se calcula a partir de los timestamps del audio locutado con ducking musical suave a 0.12-0.18 de volumen.",
        "applicable_nodes": ["node_02_audio_first_y_ritmo", "node_05_masterizacion_audio_foley"],
        "applicable_workflows": ["ALL"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 18,
        "success_rating": 0.96
    },
    {
        "id": "rule_flux3_multi_provider_routing",
        "title": "Ruteo Multi-Proveedor FLUX.3: Free ZeroGPU ➔ Replicate API ➔ RunPod GPU",
        "category": "PROVIDER_DISPATCH",
        "severity": "STRICT",
        "what_failed": "Dependencia rígida de un solo endpoint de IA que incrementa costes o falla cuando el servicio serverless tiene colas.",
        "golden_rule": "Desacoplamiento total: 1º Intentar Serverless Free ZeroGPU / Local VPS ($0), 2º Conmutar a Replicate API para SLA garantizado, 3º RunPod ComfyUI para lotes pesados.",
        "applicable_nodes": ["node_03_ingesta_multimedia_4k"],
        "applicable_workflows": ["workflow_pixar_3d_animation", "workflow_chronodrift_tritemporal", "workflow_vox_investigative_doc"],
        "experience_source_project": "2026_08_16_workflow_madrid_curiosities_3min",
        "applied_count": 9,
        "success_rating": 0.94
    },
    {
        "id": "rule_stagger_entry_3frames",
        "title": "Pacing Psicoacústico: Desfase Temporal Stagger (3-5 Frames) para Retención >70%",
        "category": "VISUAL_PACING",
        "severity": "CRITICAL",
        "what_failed": "Introducir todos los elementos visuales (documento, titular, marcador) en el mismo fotograma exacto, reduciendo el interés del cerebro del espectador.",
        "golden_rule": "Desfasar la entrada 3-5 fotogramas entre el documento (Frame 0), el titular (Frame 3) y el resaltador amarillo (Frame 6) para mantener el reflejo de orientación activo.",
        "applicable_nodes": ["node_04_composicion_motion_graphics", "node_07_cartografia_y_paralaje_3d"],
        "applicable_workflows": ["workflow_vox_investigative_doc", "workflow_geopolitical_historical_maps"],
        "experience_source_project": "vox_documentary_tutorial_benchmarks",
        "applied_count": 6,
        "success_rating": 0.99
    },
    {
        "id": "rule_paper_texture_tint",
        "title": "Tratamiento Físico: Textura Papel Prensa, Tint y Bordes Roughen Edges",
        "category": "TYPOGRAPHY_DESIGN",
        "severity": "STRICT",
        "what_failed": "Mostrar documentos con blancos sintéticos 100% RGB planos y bordes vectoriales hiper-perfectos que lucen digitales y artificiales.",
        "golden_rule": "Aplicar textura de papel analógico (25% opacidad), filtro Tint para atenuar la saturación y Roughen Edges para simular desgaste físico de celulosa.",
        "applicable_nodes": ["node_04_composicion_motion_graphics", "node_07_cartografia_y_paralaje_3d"],
        "applicable_workflows": ["workflow_vox_investigative_doc", "workflow_geopolitical_historical_maps"],
        "experience_source_project": "vox_documentary_tutorial_benchmarks",
        "applied_count": 5,
        "success_rating": 0.98
    },
    {
        "id": "rule_map_dashed_route_78",
        "title": "Cartografía Cinemática: Rutas Vectoriales con Dash=78 y Trim Paths Síncrono",
        "category": "INVESTIGATION_RESEARCH",
        "severity": "STRICT",
        "what_failed": "Líneas de ruta continuas y toscas sobre mapas sin movimiento de pluma progresivo ni separación de capas.",
        "golden_rule": "Configurar el trazo de pluma con parámetro Dashes exactamente a 78 y animar la escritura síncrona mediante Trim Paths con curvas de aceleración Bezier suaves.",
        "applicable_nodes": ["node_07_cartografia_y_paralaje_3d"],
        "applicable_workflows": ["workflow_vox_investigative_doc", "workflow_geopolitical_historical_maps"],
        "experience_source_project": "vox_documentary_tutorial_benchmarks",
        "applied_count": 4,
        "success_rating": 0.97
    },
    {
        "id": "rule_z_axis_offset_0001",
        "title": "Composición 3D: Offset Z de +0.001 en Máscaras para Eliminar Z-Fighting",
        "category": "ASSET_MATCHING",
        "severity": "BEST_PRACTICE",
        "what_failed": "Parpadeos y artefactos visuales de renderizado cuando dos capas 3D comparten exactamente la misma coordenada Z.",
        "golden_rule": "Desplazar siempre la capa superior +0.001 en el eje Z de la cámara para garantizar renderizado limpio y libre de artefactos en GPU.",
        "applicable_nodes": ["node_04_composicion_motion_graphics", "node_07_cartografia_y_paralaje_3d"],
        "applicable_workflows": ["workflow_vox_investigative_doc", "workflow_geopolitical_historical_maps"],
        "experience_source_project": "vox_documentary_tutorial_benchmarks",
        "applied_count": 8,
        "success_rating": 1.0
    }
]

DEFAULT_METRICS: List[Dict[str, Any]] = [
    {
        "provider_id": "serverless_zerogpu_flux",
        "capability_id": "cap_flux3_image_lora",
        "provider_name": "FLUX.3 Video / LoRA (HuggingFace ZeroGPU Pool $0)",
        "mode": "FREE_SERVERLESS",
        "latency_avg_sec": 8.5,
        "success_rate": 0.92,
        "cost_per_generation": 0.0,
        "total_calls": 45,
        "notes": "Gratuito sin coste de API. Puede presentar colas en horas punta."
    },
    {
        "provider_id": "serverless_replicate_flux",
        "capability_id": "cap_flux3_image_lora",
        "provider_name": "FLUX.3 Pro / Schnell (Serverless Replicate API)",
        "mode": "REPLICATE_API",
        "latency_avg_sec": 3.2,
        "success_rate": 0.99,
        "cost_per_generation": 0.03,
        "total_calls": 120,
        "notes": "Máxima fiabilidad y velocidad de entrega inmediata."
    },
    {
        "provider_id": "comfyui_runpod_flux",
        "capability_id": "cap_flux3_comfyui_local",
        "provider_name": "FLUX.3 ComfyUI Dedicated (RunPod / Modal GPU)",
        "mode": "RUNPOD_GPU",
        "latency_avg_sec": 4.1,
        "success_rate": 0.97,
        "cost_per_generation": 0.015,
        "total_calls": 30,
        "notes": "Óptimo para generación de lotes con LoRAs personalizadas en ComfyUI."
    },
    {
        "provider_id": "local_antigravity_bridge_8742",
        "capability_id": "cap_flux3_comfyui_local",
        "provider_name": "NanoBanana Pro 2 (Antigravity Bridge $0)",
        "mode": "LOCAL_VPS",
        "latency_avg_sec": 2.8,
        "success_rate": 1.0,
        "cost_per_generation": 0.0,
        "total_calls": 80,
        "notes": "Procesamiento local ultrarrápido sin coste por consulta."
    }
]


# ============================================================================
# CLASE PRINCIPAL: LearningMemoryEngine
# ============================================================================
class LearningMemoryEngine:
    """Motor de gestión de memoria de aprendizaje, experiencia acumulada y reglas de calidad."""

    def __init__(self):
        self._ensure_storage()

    def _ensure_storage(self):
        """Inicializa los archivos JSON locales si no existen con el semillero canónico."""
        if not LESSONS_FILE.exists():
            with open(LESSONS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_LESSONS, f, indent=2, ensure_ascii=False)
        if not CRITIQUES_FILE.exists():
            with open(CRITIQUES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        if not METRICS_FILE.exists():
            with open(METRICS_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_METRICS, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------------
    # LECCIONES Y REGLAS DE CALIDAD
    # ------------------------------------------------------------------------
    def get_all_lessons(
        self,
        category: Optional[LessonCategory] = None,
        node_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> List[LearnedLesson]:
        """Obtiene las lecciones aprendidas con filtrado opcional."""
        try:
            with open(LESSONS_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            lessons = [LearnedLesson(**item) for item in raw_data]

            if category:
                lessons = [l for l in lessons if l.category == category]
            if node_id:
                lessons = [l for l in lessons if not l.applicable_nodes or node_id in l.applicable_nodes or "ALL" in l.applicable_nodes]
            if workflow_id:
                lessons = [l for l in lessons if "ALL" in l.applicable_workflows or workflow_id in l.applicable_workflows]

            return lessons
        except Exception as ex:
            logger.error(f"Error al cargar lecciones aprendidas: {ex}")
            return [LearnedLesson(**item) for item in DEFAULT_LESSONS]

    def get_lesson(self, lesson_id: str) -> Optional[LearnedLesson]:
        lessons = self.get_all_lessons()
        for l in lessons:
            if l.id == lesson_id:
                return l
        return None

    def save_lesson(self, lesson: LearnedLesson) -> bool:
        """Guarda o actualiza una lección aprendida en el catálogo local y encola para Firebase."""
        try:
            lessons = self.get_all_lessons()
            found = False
            for i, l in enumerate(lessons):
                if l.id == lesson.id:
                    lesson.updated_at = datetime.now().isoformat()
                    lessons[i] = lesson
                    found = True
                    break
            if not found:
                lessons.append(lesson)

            with open(LESSONS_FILE, "w", encoding="utf-8") as f:
                json.dump([l.model_dump() for l in lessons], f, indent=2, ensure_ascii=False)
            
            # Auto-backup asíncrono
            self.sync_to_firebase_async()
            return True
        except Exception as ex:
            logger.error(f"Error al guardar lección: {ex}")
            return False

    def register_lesson(self, lesson: LearnedLesson) -> bool:
        """Registra o actualiza una lección aprendida en el catálogo (usado en WebUI)."""
        return self.save_lesson(lesson)

    def delete_lesson(self, lesson_id: str) -> bool:
        """Elimina una lección aprendida."""
        try:
            lessons = self.get_all_lessons()
            lessons = [l for l in lessons if l.id != lesson_id]
            with open(LESSONS_FILE, "w", encoding="utf-8") as f:
                json.dump([l.model_dump() for l in lessons], f, indent=2, ensure_ascii=False)
            self.sync_to_firebase_async()
            return True
        except Exception as ex:
            logger.error(f"Error al eliminar lección: {ex}")
            return False

    # ------------------------------------------------------------------------
    # EVALUACIONES Y CRÍTICAS DE PROYECTOS
    # ------------------------------------------------------------------------
    def record_project_critique(
        self,
        project_id: str,
        workflow_id: str,
        overall_score: int,
        user_feedback_raw: str,
        critique_breakdown: Optional[Dict[str, Any]] = None,
        lessons_extracted: Optional[List[str]] = None
    ) -> ProjectCritiqueFeedback:
        """Registra una evaluación post-producción con sus lecciones asociadas."""
        critique = ProjectCritiqueFeedback(
            critique_id=f"critique_{int(datetime.now().timestamp())}_{project_id[:8]}",
            project_id=project_id,
            workflow_id=workflow_id,
            overall_score=overall_score,
            user_feedback_raw=user_feedback_raw,
            critique_breakdown=critique_breakdown or {},
            lessons_extracted=lessons_extracted or []
        )

        try:
            critiques = self.get_all_critiques()
            critiques.insert(0, critique)
            with open(CRITIQUES_FILE, "w", encoding="utf-8") as f:
                json.dump([c.model_dump() for c in critiques], f, indent=2, ensure_ascii=False)
            self.sync_to_firebase_async()
        except Exception as ex:
            logger.error(f"Error al registrar crítica de proyecto: {ex}")

        return critique

    def get_all_critiques(self) -> List[ProjectCritiqueFeedback]:
        try:
            if not CRITIQUES_FILE.exists():
                return []
            with open(CRITIQUES_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [ProjectCritiqueFeedback(**item) for item in raw]
        except Exception as ex:
            logger.error(f"Error al cargar críticas: {ex}")
            return []

    # ------------------------------------------------------------------------
    # MÉTRICAS MULTI-PROVEEDOR
    # ------------------------------------------------------------------------
    def get_provider_metrics(self) -> List[ProviderExecutionMetric]:
        try:
            if not METRICS_FILE.exists():
                return [ProviderExecutionMetric(**item) for item in DEFAULT_METRICS]
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return [ProviderExecutionMetric(**item) for item in raw]
        except Exception as ex:
            logger.error(f"Error al cargar métricas: {ex}")
            return [ProviderExecutionMetric(**item) for item in DEFAULT_METRICS]

    def record_provider_metric(
        self,
        provider_id: str,
        capability_id: str,
        provider_name: str,
        mode: ProviderExecutionMode,
        latency_sec: float,
        success: bool,
        cost: float = 0.0,
        notes: str = ""
    ):
        metrics = self.get_provider_metrics()
        found = False
        for m in metrics:
            if m.provider_id == provider_id and m.capability_id == capability_id:
                m.total_calls += 1
                m.latency_avg_sec = round((m.latency_avg_sec * (m.total_calls - 1) + latency_sec) / m.total_calls, 2)
                successes = (m.success_rate * (m.total_calls - 1)) + (1.0 if success else 0.0)
                m.success_rate = round(successes / m.total_calls, 3)
                m.cost_per_generation = cost
                if notes:
                    m.notes = notes
                m.updated_at = datetime.now().isoformat()
                found = True
                break
        if not found:
            metrics.append(ProviderExecutionMetric(
                provider_id=provider_id,
                capability_id=capability_id,
                provider_name=provider_name,
                mode=mode,
                latency_avg_sec=latency_sec,
                success_rate=1.0 if success else 0.0,
                cost_per_generation=cost,
                total_calls=1,
                notes=notes
            ))
        try:
            with open(METRICS_FILE, "w", encoding="utf-8") as f:
                json.dump([m.model_dump() for m in metrics], f, indent=2, ensure_ascii=False)
            self.sync_to_firebase_async()
        except Exception as ex:
            logger.error(f"Error guardando métricas de proveedor: {ex}")

    # ------------------------------------------------------------------------
    # CONSULTA DE DIRECTRICES PRE-EJECUCIÓN
    # ------------------------------------------------------------------------
    def get_active_guidelines(
        self,
        workflow_id: str = "ALL",
        node_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retorna las directrices y reglas obligatorias que deben regir
        la generación de un proyecto o etapa de montaje.
        """
        lessons = self.get_all_lessons(workflow_id=workflow_id)
        if node_ids:
            filtered = []
            for l in lessons:
                if not l.applicable_nodes or any(n in l.applicable_nodes for n in node_ids) or "ALL" in l.applicable_nodes:
                    filtered.append(l)
            lessons = filtered

        # Agrupar por categoría
        grouped = {}
        for l in lessons:
            cat_name = l.category.value
            if cat_name not in grouped:
                grouped[cat_name] = []
            grouped[cat_name].append({
                "id": l.id,
                "title": l.title,
                "severity": l.severity.value,
                "golden_rule": l.golden_rule,
                "what_failed": l.what_failed
            })

        rules_list = [
            {
                "id": l.id,
                "title": l.title,
                "category": l.category.value,
                "severity": l.severity.value,
                "golden_rule": l.golden_rule,
                "golden_standard": l.golden_rule,
                "what_failed": l.what_failed
            }
            for l in lessons
        ]

        return {
            "workflow_id": workflow_id,
            "total_rules": len(lessons),
            "critical_rules_count": sum(1 for l in lessons if l.severity == LessonSeverity.CRITICAL),
            "guidelines_by_category": grouped,
            "rules": rules_list
        }

    # ------------------------------------------------------------------------
    # CONSULTA DE EVENTOS, MEJORAS Y DESEMPEÑO DE WORKFLOWS
    # ------------------------------------------------------------------------
    def get_learning_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene los eventos recientes de auto-aprendizaje en tiempo real."""
        events_file = STORAGE_DIR / "learning_events.json"
        if not events_file.exists():
            return []
        try:
            with open(events_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            if not isinstance(events, list):
                return []
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]
            return events[:limit]
        except Exception as ex:
            logger.error(f"Error al leer learning_events.json: {ex}")
            return []

    def get_latest_session_events(self) -> Dict[str, Any]:
        """Obtiene los datos de la última sesión de auditoría/aprendizaje."""
        session_file = STORAGE_DIR / "latest_session_events.json"
        if not session_file.exists():
            return {}
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            logger.error(f"Error al leer latest_session_events.json: {ex}")
            return {}

    def get_workflow_improvements(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de auto-parcheo y versiones v+1 de workflows."""
        imp_file = STORAGE_DIR / "workflow_improvements.json"
        if not imp_file.exists():
            return []
        try:
            with open(imp_file, "r", encoding="utf-8") as f:
                improvements = json.load(f)
            return improvements if isinstance(improvements, list) else []
        except Exception as ex:
            logger.error(f"Error al leer workflow_improvements.json: {ex}")
            return []

    def get_archetype_performance(self) -> Dict[str, Any]:
        """Obtiene las métricas de rendimiento y calidad por tipo de vídeo/arquetipo."""
        perf_file = STORAGE_DIR / "archetype_performance.json"
        if not perf_file.exists():
            return {}
        try:
            with open(perf_file, "r", encoding="utf-8") as f:
                perf = json.load(f)
            return perf if isinstance(perf, dict) else {}
        except Exception as ex:
            logger.error(f"Error al leer archetype_performance.json: {ex}")
            return {}

    # ------------------------------------------------------------------------
    # SINCRONIZACIÓN FIREBASE FIRESTORE
    # ------------------------------------------------------------------------
    def sync_to_firebase(self) -> (bool, str):
        """Sincroniza la memoria de aprendizaje completa en Firestore."""
        from app.services import firebase_sync
        token = firebase_sync._get_firebase_auth_token()
        if not token:
            return False, "Token de autenticación Firebase no disponible."

        project_id = config.app.get("firebase_project_id") or "ayuda-emilio-83261"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        payload = {
            "lessons": [l.model_dump() for l in self.get_all_lessons()],
            "critiques": [c.model_dump() for c in self.get_all_critiques()],
            "metrics": [m.model_dump() for m in self.get_provider_metrics()],
            "improvements": self.get_workflow_improvements(),
            "archetype_performance": self.get_archetype_performance(),
            "recent_events": self.get_learning_events(limit=30),
            "synced_at": datetime.now().isoformat()
        }

        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/learning_memory"
        fields = {
            "learning_memory_json": {"stringValue": json.dumps(payload, ensure_ascii=False)},
            "updated_at": {"stringValue": datetime.now().isoformat()},
            "total_lessons": {"integerValue": str(len(payload["lessons"]))},
            "total_critiques": {"integerValue": str(len(payload["critiques"]))},
            "total_improvements": {"integerValue": str(len(payload["improvements"]))}
        }

        try:
            import requests
            resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=12)
            if resp.status_code in (200, 201):
                return True, f"Memoria de aprendizaje sincronizada con éxito en Firestore ({len(payload['lessons'])} lecciones, {len(payload['critiques'])} críticas, {len(payload['improvements'])} mejoras v+1)."
            return False, f"Firestore respondió con código HTTP {resp.status_code}: {resp.text}"
        except Exception as ex:
            return False, f"Error al conectar con Firestore: {ex}"

    def sync_to_firebase_async(self):
        """Sincronización en segundo plano no bloqueante."""
        import threading
        t = threading.Thread(target=self.sync_to_firebase, daemon=True)
        t.start()

    def load_from_firebase(self) -> (bool, str):
        """Descarga la memoria de aprendizaje desde Firestore y actualiza el caché local."""
        from app.services import firebase_sync
        token = firebase_sync._get_firebase_auth_token()
        if not token:
            return False, "Token de autenticación Firebase no disponible."

        project_id = config.app.get("firebase_project_id") or "ayuda-emilio-83261"
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/learning_memory"

        try:
            import requests
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code != 200:
                return False, f"No se encontró memoria de aprendizaje previa en Firestore (HTTP {resp.status_code})."

            doc = resp.json()
            fields = doc.get("fields", {})
            raw_str = fields.get("learning_memory_json", {}).get("stringValue", "{}")
            payload = json.loads(raw_str)

            if "lessons" in payload and isinstance(payload["lessons"], list):
                with open(LESSONS_FILE, "w", encoding="utf-8") as f:
                    json.dump(payload["lessons"], f, indent=2, ensure_ascii=False)
            if "critiques" in payload and isinstance(payload["critiques"], list):
                with open(CRITIQUES_FILE, "w", encoding="utf-8") as f:
                    json.dump(payload["critiques"], f, indent=2, ensure_ascii=False)
            if "metrics" in payload and isinstance(payload["metrics"], list):
                with open(METRICS_FILE, "w", encoding="utf-8") as f:
                    json.dump(payload["metrics"], f, indent=2, ensure_ascii=False)
            if "improvements" in payload and isinstance(payload["improvements"], list):
                with open(STORAGE_DIR / "workflow_improvements.json", "w", encoding="utf-8") as f:
                    json.dump(payload["improvements"], f, indent=2, ensure_ascii=False)
            if "archetype_performance" in payload and isinstance(payload["archetype_performance"], dict):
                with open(STORAGE_DIR / "archetype_performance.json", "w", encoding="utf-8") as f:
                    json.dump(payload["archetype_performance"], f, indent=2, ensure_ascii=False)

            return True, "Memoria de aprendizaje restaurada desde Firebase Firestore."
        except Exception as ex:
            return False, f"Error al descargar de Firestore: {ex}"


# Instancia singleton accesible globalmente
learning_engine = LearningMemoryEngine()

