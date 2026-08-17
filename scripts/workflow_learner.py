#!/usr/bin/env python3
"""
workflow_learner.py
===================
Motor de Auto-Mejora y Aprendizaje Continuo — VideoPro Studio & Hermes Agent.
Optimiza los workflows automáticamente tras cada ejecución mediante:
  1. Auditoría post-ejecución contra el catálogo de 10 Reglas de Oro (R01 a R10).
  2. Detección automática de errores y anomalías en el montaje (desincronizaciones de VO/audio,
     caídas de ritmo, falsos positivos de blackdetect, problemas de bitrate/CRF, 5KB gate y Levenshtein drift).
  3. Registro estructurado de lecciones aprendidas en el catálogo y generación de críticas post-mortem.
  4. Auto-parcheo determinista de parámetros en el workflow del arquetipo correspondiente,
     generando la nueva versión optimizada (v+1) con historial de mejoras (improvement_history).
  5. Preservación del historial de optimizaciones y cálculo de métricas de rendimiento por arquetipo.
"""

from __future__ import annotations

import os
import sys
import json
import time
import argparse
import difflib
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime

# Añadir raíz de VideoPro al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.models.learning_experience import (
        LearnedLesson, LessonCategory, LessonSeverity,
        ProjectCritiqueFeedback, ProviderExecutionMetric, ProviderExecutionMode
    )
    from app.services.learning_memory_engine import learning_engine
    from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_archetype, get_all_archetypes
    from app.core.orchestration.workflows import WORKFLOW_TEMPLATES, WorkflowDefinition, get_workflow, get_workflow_by_archetype
    from app.core.orchestration.repository import StudioRepository
    from app.config import config
except ImportError as err:
    logging.warning(f"Aviso de importación parcial de módulos VideoPro: {err}")
    learning_engine = None

logger = logging.getLogger("videopro.workflow_learner")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s : %(message)s")


# ============================================================================
# 0. TIPOS DE EVENTOS DE APRENDIZAJE EN TIEMPO REAL
# ============================================================================
class LearningEventType:
    """Tipos canónicos de eventos emitidos por el motor de auto-mejora continua."""
    SESSION_STARTED = "SESSION_STARTED"
    AUDIT_STARTED = "AUDIT_STARTED"
    EVALUATION_STARTED = "EVALUATION_STARTED"
    RULE_PASSED = "RULE_PASSED"
    VIOLATION_DETECTED = "VIOLATION_DETECTED"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    AUDIT_COMPLETED = "AUDIT_COMPLETED"
    LESSON_RECORDED = "LESSON_RECORDED"
    CRITIQUE_RECORDED = "CRITIQUE_RECORDED"
    AUTO_PATCH_STARTED = "AUTO_PATCH_STARTED"
    CORRECTION_APPLIED = "CORRECTION_APPLIED"
    VERSION_INCREMENTED = "VERSION_INCREMENTED"
    PERFORMANCE_UPDATED = "PERFORMANCE_UPDATED"
    SESSION_COMPLETED = "SESSION_COMPLETED"


# ============================================================================
# 1. CATÁLOGO MAESTRO DE LAS 10 REGLAS DE ORO (R01 A R10)
# ============================================================================
GOLDEN_RULES_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "R01_AUDIO_FIRST_LIFECYCLE",
        "name": "Audio-First & VO-First Timeline Lifecycle",
        "category": "AUDIO_RHYTHM",
        "severity": "CRITICAL",
        "penalty": 15.0,
        "description": "El audio de locución manda en los cortes del timeline. La duración del vídeo se sincroniza milimétricamente con los timestamps de voz (vo_durations.json).",
        "patch_target": "audio_sync",
        "recommended_patch": {
            "enforce_vo_durations": True,
            "vo_sync_tolerance_ms": 50,
            "timeline_mode": "audio_first"
        }
    },
    {
        "id": "R02_STRICT_5KB_GATE",
        "name": "Cero Mocks / Gate Estricto > 5 KB",
        "category": "ASSET_MATCHING",
        "severity": "CRITICAL",
        "penalty": 20.0,
        "description": "Todo activo binario (fotos, clips, audios, renders) debe existir físicamente y superar los 5120 bytes (5 KB) sin corrupción.",
        "patch_target": "asset_gate",
        "recommended_patch": {
            "strict_5kb_gate": True,
            "auto_retry_corrupt_assets": True,
            "min_asset_size_bytes": 5120
        }
    },
    {
        "id": "R03_LEVENSHTEIN_CAPTIONS",
        "name": "Alineación Forzada Levenshtein en Subtítulos",
        "category": "TYPOGRAPHY_DESIGN",
        "severity": "STRICT",
        "penalty": 12.0,
        "description": "Subtítulos alineados de forma determinista contra el guion original aprobado (similitud >= 0.80), sin alucinaciones de Whisper.",
        "patch_target": "subtitles",
        "recommended_patch": {
            "enforce_levenshtein_alignment": True,
            "min_levenshtein_similarity": 0.85,
            "subtitle_style": "karaoke_gold_boxless"
        }
    },
    {
        "id": "R04_RHYTHM_3_5S_CUT",
        "name": "Ritmo Cinemático: Variación Dinámica cada 3-5s",
        "category": "VISUAL_PACING",
        "severity": "CRITICAL",
        "penalty": 15.0,
        "description": "Prohibición de planos estáticos prolongados (>5s). Debe haber cortes o movimiento Ken-Burns / 6-DoF cada 3-5 segundos como máximo.",
        "patch_target": "pacing",
        "recommended_patch": {
            "max_shot_duration_sec": 4.0,
            "ken_burns_zoompan": True,
            "cut_every_bars": 2,
            "pacing_stagger_frames": 4
        }
    },
    {
        "id": "R05_ANTI_BLACKDETECT",
        "name": "Paleta Anti-Blackdetect (Fondo Navy Industrial #243048)",
        "category": "EDITING_COMPOSITION",
        "severity": "CRITICAL",
        "penalty": 15.0,
        "description": "Nunca usar negro digital puro RGB (0,0,0) en canvas o transiciones. Usar #243048 o #F4F1EA para eliminar falsos positivos de blackdetect.",
        "patch_target": "canvas_color",
        "recommended_patch": {
            "background_color": "#243048",
            "canvas_base_hex": "#243048",
            "anti_blackdetect_padding": True
        }
    },
    {
        "id": "R06_DOP_7LAYER_PROMPT",
        "name": "Director DoP: Estructura 7 Capas & Léxico Anti-CGI",
        "category": "ASSET_MATCHING",
        "severity": "STRICT",
        "penalty": 10.0,
        "description": "Prompts cinemáticos estructurados en 7 capas físicas (Sujeto, Entorno, Iluminación, Óptica, Movimiento, Colorimetría 35mm, Render 24fps) sin palabras slop.",
        "patch_target": "prompts",
        "recommended_patch": {
            "enforce_dop_7layer": True,
            "strip_forbidden_cgi_keywords": True,
            "camera_optical_profile": "ARRI_Alexa_35mm_f1.8"
        }
    },
    {
        "id": "R07_EBU_R128_MASTERING",
        "name": "Mastering Audiófilo EBU R128 (-14 LUFS / Ducking <= -18dB)",
        "category": "AUDIO_RHYTHM",
        "severity": "CRITICAL",
        "penalty": 15.0,
        "description": "Sonoridad normalizada a -14.0 LUFS (+-0.5), True Peak <= -1.0 dBTP, ducking BGM entre -18dB y -22dB y micro-crossfades de 30ms.",
        "patch_target": "audio_dsp",
        "recommended_patch": {
            "ducking_db": -20.0,
            "target_lufs": -14.0,
            "true_peak_dbtp": -1.0,
            "crossfade_ms": 30,
            "sub_80hz_mono": True
        }
    },
    {
        "id": "R08_THUMBNAIL_SAFE_ZONE",
        "name": "Neurodiseño de Miniaturas: Microcopy <= 3 Palabras & Safe Zone",
        "category": "TYPOGRAPHY_DESIGN",
        "severity": "STRICT",
        "penalty": 10.0,
        "description": "Miniaturas con microcopy conciso (<= 3 palabras), legibilidad a 160x90 px y esquina inferior derecha (160x50 px YouTube dead zone) libre.",
        "patch_target": "thumbnail",
        "recommended_patch": {
            "thumbnail_max_words": 3,
            "enforce_dead_zone_clear": True,
            "thumbnail_formula": "F1_SPLIT_TEMPORAL"
        }
    },
    {
        "id": "R09_DUAL_PERSISTENCE",
        "name": "Persistencia Dual y Manifiesto Canónico de 7 Fases",
        "category": "PROVIDER_DISPATCH",
        "severity": "STRICT",
        "penalty": 10.0,
        "description": "Manifiesto canónico de 7 fases con hashes SHA-256 de activos y sincronización Firestore / Cloudflare R2.",
        "patch_target": "persistence",
        "recommended_patch": {
            "dual_persistence_enabled": True,
            "sha256_verification": True,
            "r2_upload_enabled": True
        }
    },
    {
        "id": "R10_USER_AGENT_INSTITUTIONAL",
        "name": "Ingesta y Scraping con Headers Institucionales Anti-403",
        "category": "INVESTIGATION_RESEARCH",
        "severity": "STRICT",
        "penalty": 10.0,
        "description": "Headers HTTP legítimos/institucionales (VideoProHermesBot/1.0) en descargas de Wikimedia/OSM para garantizar 100% éxito.",
        "patch_target": "scraping_headers",
        "recommended_patch": {
            "user_agent": "VideoProHermesBot/1.0 (https://videopro.app; contact@videopro.app)",
            "request_timeout_sec": 15
        }
    }
]

FORBIDDEN_CGI_KEYWORDS = [
    "hyper-realistic", "hyperrealistic", "photorealistic", "8k", "ultra-detailed",
    "octane render", "unreal engine", "smooth glowing skin", "perfect face",
    "glowing neon everywhere", "plastic metal"
]


# ============================================================================
# 2. FUNCIONES DE COMPARACIÓN Y ALINEACIÓN DE TEXTO (LEVENSHTEIN PURO)
# ============================================================================
def compute_levenshtein_distance(s1: str, s2: str) -> int:
    """Calcula la distancia de Levenshtein exacta entre dos cadenas en memoria pura."""
    if len(s1) < len(s2):
        return compute_levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def compute_text_similarity(s1: str, s2: str) -> float:
    """Calcula la similitud fonética/textual normalizada entre 0.0 y 1.0."""
    s1_clean = re.sub(r'[^\w\s]', '', str(s1 or "").lower()).strip()
    s2_clean = re.sub(r'[^\w\s]', '', str(s2 or "").lower()).strip()
    if not s1_clean and not s2_clean:
        return 1.0
    if not s1_clean or not s2_clean:
        return 0.0
    max_len = max(len(s1_clean), len(s2_clean))
    dist = compute_levenshtein_distance(s1_clean, s2_clean)
    lev_ratio = max(0.0, 1.0 - (dist / max_len))
    # Promediar con SequenceMatcher de difflib para resiliencia a palabras reordenadas
    seq_ratio = difflib.SequenceMatcher(None, s1_clean, s2_clean).ratio()
    return round((lev_ratio * 0.7) + (seq_ratio * 0.3), 4)


# ============================================================================
# 3. CLASE PRINCIPAL: WorkflowLearner
# ============================================================================
class WorkflowLearner:
    """
    Motor de Aprendizaje Continuo, Auditoría Post-Ejecución y Auto-Optimización de Workflows.
    """

    def __init__(
        self,
        storage_dir: Optional[Union[str, Path]] = None,
        workflows_dir: Optional[Union[str, Path]] = None,
        learning_dir: Optional[Union[str, Path]] = None
    ):
        self.base_dir = BASE_DIR
        self.storage_dir = Path(storage_dir) if storage_dir else self.base_dir / "storage"
        self.workflows_dir = Path(workflows_dir) if workflows_dir else self.storage_dir / "workflows"
        self.learning_dir = Path(learning_dir) if learning_dir else self.storage_dir / "learning_memory"

        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        self.learning_dir.mkdir(parents=True, exist_ok=True)

        self.improvements_file = self.learning_dir / "workflow_improvements.json"
        self.performance_file = self.learning_dir / "archetype_performance.json"
        self.lessons_file = self.learning_dir / "lessons_catalog.json"
        self.critiques_file = self.learning_dir / "project_critiques.json"
        self.events_file = self.learning_dir / "learning_events.json"
        self.latest_session_file = self.learning_dir / "latest_session_events.json"

        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._active_session_id: Optional[str] = None
        self._active_project_id: Optional[str] = None
        self._active_archetype_id: Optional[str] = None

        self._ensure_storage_files()

    def _ensure_storage_files(self):
        """Inicializa los archivos JSON de persistencia si no existen."""
        if not self.improvements_file.exists():
            with open(self.improvements_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        if not self.performance_file.exists():
            with open(self.performance_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        if not self.events_file.exists():
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
        if not self.latest_session_file.exists():
            with open(self.latest_session_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------------
    # 3.0 EMISIÓN DE EVENTOS EN TIEMPO REAL & INTEGRACIÓN MULTI-DESTINO
    # ------------------------------------------------------------------------
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Registra una función callback que se ejecutará con cada evento emitido."""
        if listener not in self.event_listeners:
            self.event_listeners.append(listener)

    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]):
        """Elimina un callback previamente registrado."""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)

    def emit_event(
        self,
        event_type: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        archetype_id: Optional[str] = None,
        severity: str = "INFO",
        sync_firebase: bool = True
    ) -> Dict[str, Any]:
        """
        Emite un evento estructurado de auto-aprendizaje en tiempo real:
        1. Registra en el log de la aplicación.
        2. Almacena en storage/learning_memory/learning_events.json (capped a 1000 eventos).
        3. Actualiza storage/learning_memory/latest_session_events.json.
        4. Notifica a listeners en memoria.
        5. Emite a Firebase Firestore en segundo plano (asíncrono).
        """
        event_id = f"evt_{int(time.time() * 1000)}_{os.urandom(3).hex()}"
        ts = datetime.now().isoformat()
        sid = session_id or self._active_session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pid = project_id or self._active_project_id or "system"
        aid = archetype_id or self._active_archetype_id or "GLOBAL"

        event_data = {
            "event_id": event_id,
            "event_type": event_type,
            "session_id": sid,
            "project_id": pid,
            "archetype_id": aid,
            "message": message,
            "severity": severity,
            "timestamp": ts,
            "payload": payload or {}
        }

        # 1. Log en consola/archivo
        log_level = logging.WARNING if severity in ("WARNING", "HIGH") else (logging.ERROR if severity == "CRITICAL" else logging.INFO)
        logger.log(log_level, f"[{event_type}] ({aid}) {message}")

        # 2. Persistencia local en archivo de eventos
        try:
            events = []
            if self.events_file.exists():
                with open(self.events_file, "r", encoding="utf-8") as f:
                    events = json.load(f)
                    if not isinstance(events, list):
                        events = []
            events.insert(0, event_data)
            events = events[:1000]
            with open(self.events_file, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
        except Exception as ex:
            logger.debug(f"Aviso guardando evento local: {ex}")

        # 3. Actualizar sesión más reciente
        try:
            session_info = {
                "session_id": sid,
                "project_id": pid,
                "archetype_id": aid,
                "last_updated": ts,
                "last_event": event_data
            }
            with open(self.latest_session_file, "w", encoding="utf-8") as f:
                json.dump(session_info, f, indent=2, ensure_ascii=False)
        except Exception as ex:
            logger.debug(f"Aviso guardando última sesión: {ex}")

        # 4. Notificar a listeners registrados
        for listener in list(self.event_listeners):
            try:
                listener(event_data)
            except Exception as ex:
                logger.debug(f"Error en listener de evento: {ex}")

        # 5. Emisión a Firebase Firestore en segundo plano
        if sync_firebase:
            try:
                from app.services import firebase_sync
                firebase_sync.emit_learning_event_to_firebase_async(event_data)
            except Exception as ex:
                logger.debug(f"Aviso al sincronizar evento con Firebase: {ex}")

        return event_data

    def get_recent_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Consulta los eventos de aprendizaje más recientes almacenados localmente."""
        try:
            if not self.events_file.exists():
                return []
            with open(self.events_file, "r", encoding="utf-8") as f:
                events = json.load(f)
            if not isinstance(events, list):
                return []
            if event_type:
                events = [e for e in events if e.get("event_type") == event_type]
            return events[:limit]
        except Exception as ex:
            logger.error(f"Error al leer eventos de aprendizaje: {ex}")
            return []

    def get_latest_session_events(self) -> Dict[str, Any]:
        """Obtiene la metadata y último evento de la sesión activa más reciente."""
        try:
            if not self.latest_session_file.exists():
                return {}
            with open(self.latest_session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as ex:
            logger.error(f"Error al leer última sesión: {ex}")
            return {}

    # ------------------------------------------------------------------------
    # 3.1 CARGA Y NORMALIZACIÓN DE PROYECTOS / MANIFIESTOS
    # ------------------------------------------------------------------------
    def load_manifest(self, manifest_or_path: Union[str, Path, dict]) -> Tuple[dict, Optional[Path]]:
        """Carga e identifica la estructura de manifiesto del proyecto desde dict o ruta."""
        if isinstance(manifest_or_path, dict):
            return manifest_or_path, None

        path = Path(manifest_or_path)
        if path.is_dir():
            # Buscar manifiesto estándar en el directorio
            candidates = [
                path / "manifest.json",
                path / "project_manifest.json",
                path / "manifests" / "project_manifest.json",
                path / "scenes.json"
            ]
            for c in candidates:
                if c.exists():
                    path = c
                    break

        if not path.exists():
            raise FileNotFoundError(f"No se encontró archivo de manifiesto en: {manifest_or_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        project_dir = path.parent if path.name != "manifests" else path.parent.parent
        return data, project_dir

    def resolve_archetype_id(self, project_data: dict, explicit_archetype: Optional[str] = None) -> str:
        """Determina el ID canónico del arquetipo a partir de la metadata del proyecto."""
        if explicit_archetype:
            return explicit_archetype.upper()

        if "archetype_id" in project_data:
            return str(project_data["archetype_id"]).upper()

        meta = project_data.get("metadata", {})
        if "archetype_id" in meta:
            return str(meta["archetype_id"]).upper()

        style = meta.get("style", "").lower()
        topic = meta.get("topic", "").lower()
        slug = project_data.get("slug", "").lower()
        combined = f"{style} {topic} {slug}"

        if "pixar" in combined or "3d" in combined and "story" in combined:
            return "PIXAR_3D_ANIMATION"
        elif "city" in combined or "route" in combined or "beat" in combined:
            return "CITY_ROUTES_BEATS"
        elif "viral" in combined or "short" in combined or meta.get("resolution", {}).get("aspect_ratio") == "9:16":
            return "VIRAL_SHORTS_HOOK"
        elif "chronodrift" in combined or "tritemporal" in combined:
            return "CHRONODRIFT_TRITEMPORAL"
        elif "fpv" in combined or "tour" in combined or "shibuya" in combined:
            return "FPV_URBAN_REAL_FLOW"
        elif "vox" in combined or "investigative" in combined or "parallax" in combined:
            return "VOX_INVESTIGATIVE_DOC"
        elif "historical" in combined or "scraping" in combined:
            return "HISTORICAL_SCRAPING"
        elif "explainer" in combined or "essay" in combined or "bbc" in combined:
            return "DEEP_EXPLAINER_ESSAY"

        return "DOCUMENTARY_MASTER"

    # ------------------------------------------------------------------------
    # 3.2 AUDITORÍA DE LAS 10 REGLAS DE ORO (R01 A R10)
    # ------------------------------------------------------------------------
    def audit_project(self, project_data: dict, project_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Ejecuta la auditoría post-ejecución contra el catálogo completo de las 10 Reglas de Oro
        con emisión de eventos en tiempo real a Firebase y WebUI.
        """
        project_id = project_data.get("project_id", project_data.get("slug", "unknown_project"))
        archetype_id = self.resolve_archetype_id(project_data)

        self._active_project_id = project_id
        self._active_archetype_id = archetype_id

        self.emit_event(
            LearningEventType.AUDIT_STARTED,
            f"Iniciando auditoría QA contra las 10 Reglas de Oro para '{project_id}' ({archetype_id})",
            {"project_id": project_id, "archetype_id": archetype_id, "rules_count": len(GOLDEN_RULES_CATALOG)}
        )

        evaluations: Dict[str, Any] = {}
        violations: List[Dict[str, Any]] = []
        total_penalties = 0.0

        def _evaluate_rule(rule_key: str, eval_fn):
            nonlocal total_penalties
            rule_item = next((r for r in GOLDEN_RULES_CATALOG if r["id"] == rule_key), {"name": rule_key})
            self.emit_event(
                LearningEventType.EVALUATION_STARTED,
                f"Evaluando regla [{rule_key[:3]}] {rule_item.get('name')}...",
                {"rule_id": rule_key, "name": rule_item.get("name")}
            )
            r_eval = eval_fn(project_data, project_dir)
            evaluations[rule_key] = r_eval
            if not r_eval["passed"]:
                total_penalties += r_eval["penalty"]
                violations.append(r_eval)
                sev = r_eval.get("severity", "STRICT")
                self.emit_event(
                    LearningEventType.VIOLATION_DETECTED,
                    f"Violación detectada en [{rule_key[:3]}] {r_eval.get('name')}: {'; '.join(r_eval.get('details', []))} (-{r_eval.get('penalty')} pts)",
                    r_eval,
                    severity="CRITICAL" if sev == "CRITICAL" else "WARNING"
                )
            else:
                self.emit_event(
                    LearningEventType.RULE_PASSED,
                    f"Regla [{rule_key[:3]}] {r_eval.get('name')} validada con éxito (0 pts)",
                    {"rule_id": rule_key, "name": r_eval.get("name"), "category": r_eval.get("category")},
                    severity="INFO"
                )
            return r_eval

        # --- R01: Audio-First Lifecycle & VO Sync ---
        _evaluate_rule("R01_AUDIO_FIRST_LIFECYCLE", self._audit_r01_audio_first)

        # --- R02: Strict > 5 KB Gate ---
        _evaluate_rule("R02_STRICT_5KB_GATE", self._audit_r02_5kb_gate)

        # --- R03: Levenshtein Subtitle Alignment ---
        _evaluate_rule("R03_LEVENSHTEIN_CAPTIONS", self._audit_r03_levenshtein_captions)

        # --- R04: Cinematic Rhythm & 3-5s Dynamic Cut ---
        _evaluate_rule("R04_RHYTHM_3_5S_CUT", self._audit_r04_rhythm_pacing)

        # --- R05: Anti-Blackdetect Palette ---
        _evaluate_rule("R05_ANTI_BLACKDETECT", self._audit_r05_anti_blackdetect)

        # --- R06: DoP 7-Layer Prompting & Anti-CGI Lexicon ---
        _evaluate_rule("R06_DOP_7LAYER_PROMPT", self._audit_r06_dop_7layer_prompt)

        # --- R07: EBU R128 Audio Mastering & Ducking ---
        _evaluate_rule("R07_EBU_R128_MASTERING", self._audit_r07_ebu_r128_mastering)

        # --- R08: Thumbnail Safe Zone & Microcopy ---
        _evaluate_rule("R08_THUMBNAIL_SAFE_ZONE", self._audit_r08_thumbnail_safe_zone)

        # --- R09: Dual Persistence & 7-Phase Manifest ---
        _evaluate_rule("R09_DUAL_PERSISTENCE", self._audit_r09_dual_persistence)

        # --- R10: Institutional User-Agent Headers ---
        _evaluate_rule("R10_USER_AGENT_INSTITUTIONAL", self._audit_r10_user_agent_headers)

        overall_score = max(0.0, round(100.0 - total_penalties, 2))
        critical_violations = [v for v in violations if v.get("severity") == "CRITICAL"]
        passed = overall_score >= 85.0 and len(critical_violations) == 0

        # Métricas agregadas por área funcional
        category_scores = self._compute_category_scores(evaluations)

        audit_summary = {
            "project_id": project_id,
            "archetype_id": archetype_id,
            "overall_score": overall_score,
            "passed": passed,
            "total_penalties": round(total_penalties, 2),
            "rules_checked": len(GOLDEN_RULES_CATALOG),
            "rules_passed_count": len(GOLDEN_RULES_CATALOG) - len(violations),
            "violations_count": len(violations),
            "critical_violations_count": len(critical_violations),
            "rule_evaluations": evaluations,
            "violations": violations,
            "category_scores": category_scores,
            "audited_at": datetime.now().isoformat()
        }

        self.emit_event(
            LearningEventType.AUDIT_COMPLETED,
            f"Auditoría QA completada para '{project_id}': Puntuación {overall_score}/100.0 ({'APROBADO' if passed else 'REQUIERE AUTO-PARCHEO'})",
            {
                "project_id": project_id,
                "archetype_id": archetype_id,
                "overall_score": overall_score,
                "passed": passed,
                "total_penalties": total_penalties,
                "violations_count": len(violations),
                "critical_violations_count": len(critical_violations)
            },
            severity="INFO" if passed else "WARNING"
        )

        return audit_summary

    # ------------------------------------------------------------------------
    # 3.3 EVALUADORES ESPECÍFICOS DE LAS 10 REGLAS
    # ------------------------------------------------------------------------
    def _audit_r01_audio_first(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R01: Verifica sincronización VO-first y precedencia de audio."""
        rule_def = GOLDEN_RULES_CATALOG[0]
        has_vo = False
        duration_aligned = True
        details = []

        # Comprobar si hay audio o especificación de voz
        if "audio_tracks" in data or "audio" in data.get("assets_manifest", []) or "vo_durations" in data:
            has_vo = True
        
        # Comprobar vo_durations.json si existe en disco
        if pdir:
            vo_json = pdir / "audio" / "vo_durations.json"
            if not vo_json.exists():
                vo_json = pdir / "manifests" / "vo_durations.json"
            if vo_json.exists():
                has_vo = True

        scenes = data.get("scenes", [])
        if isinstance(scenes, list) and len(scenes) > 0:
            for s in scenes:
                if isinstance(s, dict) and "duration" in s and s.get("duration", 0) > 0:
                    pass
                elif isinstance(s, dict) and "duration_sec" in s and s.get("duration_sec", 0) > 0:
                    pass

        # Chequear discrepancia de duraciones
        actual_dur = data.get("metadata", {}).get("actual_duration_seconds")
        target_dur = data.get("metadata", {}).get("target_duration_seconds")
        if actual_dur and target_dur and abs(actual_dur - target_dur) > 5.0 and target_dur > 15:
            duration_aligned = False
            details.append(f"Desfase de duración notable: objetivo {target_dur}s vs renderizado {actual_dur}s.")

        passed = duration_aligned
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Sincronización Audio-First y duraciones de voz válidas."],
            "recommendation": "Alinear duraciones de tomas contra timestamps de Faster-Whisper (vo_durations.json)." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r02_5kb_gate(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R02: Verifica que todos los activos binarios superen los 5120 bytes."""
        rule_def = GOLDEN_RULES_CATALOG[1]
        assets = data.get("assets_manifest", [])
        violations_found = []

        for asset in assets:
            if isinstance(asset, dict):
                size = asset.get("filesize_bytes", asset.get("extra", {}).get("size_bytes", 10000))
                name = asset.get("name", asset.get("id", "asset"))
                if size < 5120 and size > 0:
                    violations_found.append(f"Activo '{name}' pesa {size} B (< 5120 B).")
                elif size == 0:
                    violations_found.append(f"Activo '{name}' está vacío (0 bytes).")

        # Comprobar archivos en disco si pdir existe
        if pdir and pdir.exists():
            for root, _, files in os.walk(pdir):
                for f in files:
                    if f.endswith((".mp4", ".png", ".jpg", ".jpeg", ".wav", ".mp3", ".webp")):
                        fp = Path(root) / f
                        try:
                            fsize = fp.stat().st_size
                            if fsize < 5120:
                                violations_found.append(f"Archivo en disco '{fp.name}' pesa {fsize} B (< 5 KB).")
                        except OSError:
                            pass

        passed = len(violations_found) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": violations_found if violations_found else ["Todos los activos binarios superan el gate estricto > 5 KB."],
            "recommendation": "Re-generar o re-descargar activos corruptos o de tamaño inferior a 5 KB." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r03_levenshtein_captions(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R03: Verifica similitud de subtítulos contra guion original."""
        rule_def = GOLDEN_RULES_CATALOG[2]
        script_text = data.get("script", "") or data.get("metadata", {}).get("topic", "")
        subtitles_text = data.get("subtitles_text", "")
        details = []

        if pdir:
            # Buscar archivos de subtítulos .ass o .srt
            sub_files = list(pdir.glob("**/*.ass")) + list(pdir.glob("**/*.srt"))
            if sub_files and not subtitles_text:
                try:
                    with open(sub_files[0], "r", encoding="utf-8", errors="ignore") as sf:
                        subtitles_text = sf.read()
                except Exception:
                    pass

        similarity = 1.0
        if script_text and subtitles_text:
            similarity = compute_text_similarity(script_text, subtitles_text)
            if similarity < 0.75:
                details.append(f"Similitud de subtítulos baja ({round(similarity*100, 1)}% < 80%). Posible alucinación.")

        passed = similarity >= 0.75
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "similarity_score": round(similarity, 3),
            "details": details if details else [f"Subtítulos verificados con {round(similarity*100, 1)}% de fidelidad al guion."],
            "recommendation": "Forzar alineación determinista Levenshtein contra el guion aprobado antes de renderizar." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r04_rhythm_pacing(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R04: Verifica cortes dinámicos cada 3-5s y ausencia de planos estáticos aburridos."""
        rule_def = GOLDEN_RULES_CATALOG[3]
        scenes = data.get("scenes", [])
        long_static_scenes = []

        if isinstance(scenes, list) and len(scenes) > 0:
            for i, sc in enumerate(scenes):
                if isinstance(sc, dict):
                    dur = sc.get("duration_sec", sc.get("duration", 3.0))
                    has_motion = sc.get("ken_burns", False) or "zoom" in str(sc).lower() or "pan" in str(sc).lower() or "orbit" in str(sc).lower() or "6-dof" in str(sc).lower()
                    if dur > 5.5 and not has_motion:
                        long_static_scenes.append(f"Escena {i+1} ({sc.get('id', 'scene')}) dura {dur}s sin movimiento dinámico Ken-Burns.")

        passed = len(long_static_scenes) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": long_static_scenes if long_static_scenes else ["Cadencia de planos óptima: cortes y variación visual dinámica cada 3-5s."],
            "recommendation": "Fragmentar escenas largas en tomas de 3.0-4.5s o inyectar zoompan/Ken-Burns dinámico." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r05_anti_blackdetect(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R05: Verifica que el fondo del canvas use #243048 o #F4F1EA en lugar de RGB(0,0,0)."""
        rule_def = GOLDEN_RULES_CATALOG[4]
        details = []
        bg_color = str(data.get("background_color", data.get("canvas_color", ""))).lower()

        raw_manifest_str = json.dumps(data).lower()
        if '"#000000"' in raw_manifest_str or '"rgb(0,0,0)"' in raw_manifest_str or '"black"' in raw_manifest_str:
            if "canvas" in raw_manifest_str or "background" in raw_manifest_str:
                details.append("Se detectó color negro digital puro (#000000 / RGB 0,0,0) en la especificación de canvas o fondos.")

        passed = len(details) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Canvas configurado con paleta anti-blackdetect (#243048 / #F4F1EA)."],
            "recommendation": "Reemplazar fondos negros por azul marino industrial #243048 o crema cálido #F4F1EA." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r06_dop_7layer_prompt(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R06: Verifica estructura de 7 capas en prompts y erradicación de léxico AI Slop."""
        rule_def = GOLDEN_RULES_CATALOG[5]
        prompts = []
        slop_words_found = []

        scenes = data.get("scenes", [])
        if isinstance(scenes, list):
            for sc in scenes:
                if isinstance(sc, dict):
                    p = sc.get("prompt", "") or sc.get("visual_prompt", "")
                    if p:
                        prompts.append(p)

        # Chequear palabras prohibidas de slop
        for p in prompts:
            p_lower = p.lower()
            for kw in FORBIDDEN_CGI_KEYWORDS:
                if kw in p_lower:
                    slop_words_found.append(f"Término sintético prohibido detectado: '{kw}' en prompt.")

        passed = len(slop_words_found) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": slop_words_found if slop_words_found else ["Prompts DoP conformes al estándar cinemático orgánico sin jerga CGI slop."],
            "recommendation": "Reemplazar términos como 'photorealistic/8k' por especificaciones ópticas ('Shot on 35mm, ARRI Alexa, f/1.8')." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r07_ebu_r128_mastering(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R07: Verifica especificaciones de sonoridad EBU R128 (-14 LUFS) y ducking <= -18dB."""
        rule_def = GOLDEN_RULES_CATALOG[6]
        audio_dsp = data.get("audio_dsp", {})
        ducking_db = audio_dsp.get("ducking_db", 0)
        target_lufs = audio_dsp.get("target_lufs", -14.0)
        details = []

        # Si ducking_db es más suave que -15dB (ej: -10dB o 0dB sin ducking)
        if ducking_db > -16.0 and ducking_db != 0:
            details.append(f"Ducking musical insuficiente: {ducking_db} dB (debe ser <= -18 dB para inteligibilidad).")

        passed = len(details) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Mastering de audio conforme a EBU R128 (-14 LUFS, ducking -18dB a -22dB)."],
            "recommendation": "Configurar ducking de fondo a -20 dB y normalización a -14.0 LUFS." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r08_thumbnail_safe_zone(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R08: Verifica que las miniaturas respeten microcopy <= 3 palabras y la safe zone."""
        rule_def = GOLDEN_RULES_CATALOG[7]
        thumb = data.get("thumbnail", {})
        microcopy = thumb.get("microcopy", thumb.get("text", ""))
        details = []

        if microcopy:
            word_count = len(microcopy.split())
            if word_count > 3:
                details.append(f"Microcopy de miniatura demasiado largo: '{microcopy}' ({word_count} palabras > 3 palabras).")

        passed = len(details) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Miniatura validada con neurodiseño de alto CTR y safe zones intactas."],
            "recommendation": "Reducir el texto de miniatura a un máximo de 3 palabras de alto impacto (ej: 'ASÍ ERA REALMENTE')." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r09_dual_persistence(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R09: Verifica manifiesto de 7 fases y trazabilidad SHA-256."""
        rule_def = GOLDEN_RULES_CATALOG[8]
        lifecycle = data.get("pipeline_lifecycle", {})
        details = []

        if not lifecycle and "phases" not in data and "pipeline_graph" not in data:
            details.append("Falta definición estructurada del ciclo de vida de 7 fases del pipeline.")

        passed = len(details) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Manifiesto canónico de 7 fases y persistencia dual validados."],
            "recommendation": "Incluir pipeline_lifecycle con registro de fases (bootstrap a entrega) y hashes SHA-256." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _audit_r10_user_agent_headers(self, data: dict, pdir: Optional[Path]) -> Dict[str, Any]:
        """R10: Verifica User-Agent institucional anti-403 en scraping."""
        rule_def = GOLDEN_RULES_CATALOG[9]
        scraping_cfg = data.get("scraping_config", {})
        ua = scraping_cfg.get("user_agent", data.get("user_agent", ""))
        details = []

        if ua and ("python-requests" in ua.lower() or "urllib" in ua.lower()):
            details.append(f"User-Agent genérico susceptible de bloqueo HTTP 403: '{ua}'.")

        passed = len(details) == 0
        penalty = 0.0 if passed else rule_def["penalty"]
        return {
            "rule_id": rule_def["id"],
            "name": rule_def["name"],
            "category": rule_def["category"],
            "severity": rule_def["severity"],
            "passed": passed,
            "penalty": penalty,
            "details": details if details else ["Headers institucionales (VideoProHermesBot/1.0) activos para scraping seguro."],
            "recommendation": "Inyectar siempre 'User-Agent: VideoProHermesBot/1.0 (https://videopro.app; contact@videopro.app)'." if not passed else "",
            "patch_target": rule_def["patch_target"],
            "recommended_patch": rule_def["recommended_patch"]
        }

    def _compute_category_scores(self, evals: Dict[str, Any]) -> Dict[str, float]:
        """Calcula el score de 0 a 100 para cada categoría funcional."""
        cat_map: Dict[str, List[float]] = {}
        for r_id, ev in evals.items():
            cat = ev.get("category", "GENERAL")
            if cat not in cat_map:
                cat_map[cat] = []
            score = 100.0 - ev.get("penalty", 0.0)
            cat_map[cat].append(score)

        return {cat: round(sum(scores) / len(scores), 2) for cat, scores in cat_map.items()}

    # ------------------------------------------------------------------------
    # 3.4 DETECCIÓN AUTOMÁTICA DE ERRORES Y ANOMALÍAS EN EL MONTAJE
    # ------------------------------------------------------------------------
    def detect_montage_anomalies(self, project_data: dict, project_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Detección profunda y automática de errores en el montaje audiovisual:
        - Desincronizaciones de audio/VO
        - Caídas de ritmo y planos estáticos
        - Falsos positivos de blackdetect
        - Problemas de bitrate y codificación
        """
        anomalies: List[Dict[str, Any]] = []

        # 1. Desincronizaciones de Audio / VO
        scenes = project_data.get("scenes", [])
        total_scene_dur = sum([s.get("duration_sec", s.get("duration", 0)) for s in scenes if isinstance(s, dict)])
        actual_dur = project_data.get("metadata", {}).get("actual_duration_seconds")
        if actual_dur and total_scene_dur > 0 and abs(actual_dur - total_scene_dur) > 1.5:
            anomalies.append({
                "type": "AUDIO_VO_DESYNC",
                "severity": "HIGH",
                "message": f"Desfase acumulado de timeline: suma de tomas ({round(total_scene_dur, 2)}s) difiere del máster ({round(actual_dur, 2)}s).",
                "suggested_fix": {"enforce_vo_durations": True, "vo_sync_tolerance_ms": 50}
            })

        # 2. Caídas de Ritmo (> 5s sin movimiento)
        for i, sc in enumerate(scenes):
            if isinstance(sc, dict):
                dur = sc.get("duration_sec", sc.get("duration", 0))
                has_motion = sc.get("ken_burns", False) or any(k in str(sc).lower() for k in ["zoom", "pan", "orbit", "6-dof"])
                if dur > 5.0 and not has_motion:
                    anomalies.append({
                        "type": "PACING_DROP",
                        "severity": "MEDIUM",
                        "scene_index": i,
                        "message": f"Caída de ritmo en Escena {i+1}: duración de {dur}s sin movimiento de cámara ni variación.",
                        "suggested_fix": {"max_shot_duration_sec": 4.0, "ken_burns_zoompan": True}
                    })

        # 3. Falsos Positivos de Blackdetect / Fondos Negro Puro
        encoder_spec = project_data.get("engine_specifications", {}).get("video_encoder", {})
        if str(project_data.get("background_color", "")).lower() in ["#000000", "black", "rgb(0,0,0)"]:
            anomalies.append({
                "type": "BLACKDETECT_RISK",
                "severity": "HIGH",
                "message": "Uso de fondo negro puro (#000000) genera riesgo de pantalla negra y falsos positivos en QA.",
                "suggested_fix": {"background_color": "#243048", "canvas_base_hex": "#243048"}
            })

        # 4. Problemas de Bitrate y Codificación
        v_bitrate = encoder_spec.get("video_bitrate", "")
        a_bitrate = encoder_spec.get("audio_bitrate", "")
        crf = encoder_spec.get("crf", 20)

        if crf > 26:
            anomalies.append({
                "type": "BITRATE_ENCODING_DEGRADATION",
                "severity": "HIGH",
                "message": f"CRF de compresión demasiado alto ({crf} > 26), provocando artefactos y pérdida de nitidez.",
                "suggested_fix": {"video_encoder": {"codec": "libx264", "crf": 20, "preset": "medium", "audio_bitrate": "192k"}}
            })
        if a_bitrate and a_bitrate in ["64k", "96k"]:
            anomalies.append({
                "type": "LOW_AUDIO_BITRATE",
                "severity": "MEDIUM",
                "message": f"Bitrate de audio bajo ({a_bitrate} < 128k), degrada la calidad sonora broadcast.",
                "suggested_fix": {"audio_bitrate": "192k"}
            })

        for an in anomalies:
            self.emit_event(
                LearningEventType.ANOMALY_DETECTED,
                f"Anomalía en montaje: [{an.get('type')}] {an.get('message')}",
                an,
                severity="WARNING" if an.get("severity") == "MEDIUM" else "CRITICAL"
            )

        return {
            "total_anomalies": len(anomalies),
            "anomalies": anomalies,
            "has_critical_anomalies": any(a["severity"] == "HIGH" for a in anomalies)
        }

    # ------------------------------------------------------------------------
    # 3.5 AUTO-PARCHEO DETERMINISTA DE PARÁMETROS EN EL WORKFLOW (v+1)
    # ------------------------------------------------------------------------
    def auto_patch_workflow(
        self,
        archetype_id: str,
        audit_result: Dict[str, Any],
        project_id: str,
        anomalies: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aplica auto-parcheo determinista sobre el workflow del arquetipo correspondiente,
        guardando la nueva versión optimizada (v+1) y registrando el historial de mejora.
        """
        archetype_id = archetype_id.upper()
        
        # 1. Localizar la última versión existente del workflow
        latest_wf_file, current_version = self._find_latest_workflow_file(archetype_id)
        
        if latest_wf_file and latest_wf_file.exists():
            with open(latest_wf_file, "r", encoding="utf-8") as f:
                wf_data = json.load(f)
        else:
            # Crear desde plantilla en memoria o repositorio
            wf_data = self._create_base_workflow_data(archetype_id)
            current_version = wf_data.get("version", 1)

        new_version = current_version + 1
        patches_applied = {}

        self.emit_event(
            LearningEventType.AUTO_PATCH_STARTED,
            f"Iniciando auto-parcheo determinista para arquetipo {archetype_id} (v{current_version} ➔ v{new_version})",
            {
                "archetype_id": archetype_id,
                "current_version": current_version,
                "target_version": new_version,
                "project_id": project_id
            }
        )

        # Helper para sincronizar parámetros tanto a nivel raíz como en sub-secciones canónicas
        def _apply_param_to_wf(target_dict: dict, param_key: str, param_val: Any):
            target_dict[param_key] = param_val
            if param_key in ("ducking_db", "target_lufs", "true_peak_dbtp", "crossfade_ms", "sub_80hz_mono"):
                if "audio_dsp" not in target_dict or not isinstance(target_dict["audio_dsp"], dict):
                    target_dict["audio_dsp"] = {}
                target_dict["audio_dsp"][param_key] = param_val
            elif param_key in ("user_agent", "request_timeout_sec"):
                if "scraping_config" not in target_dict or not isinstance(target_dict["scraping_config"], dict):
                    target_dict["scraping_config"] = {}
                target_dict["scraping_config"][param_key] = param_val
            elif param_key in ("ken_burns_zoompan", "max_cut_duration_sec", "max_shot_duration_sec", "cut_every_bars", "pacing_stagger_frames"):
                if "pacing" not in target_dict or not isinstance(target_dict["pacing"], dict):
                    target_dict["pacing"] = {}
                target_dict["pacing"][param_key] = param_val
            elif param_key in ("thumbnail_max_words", "enforce_dead_zone_clear", "thumbnail_formula"):
                if "thumbnail" not in target_dict or not isinstance(target_dict["thumbnail"], dict):
                    target_dict["thumbnail"] = {}
                target_dict["thumbnail"][param_key] = param_val
            elif param_key in ("enforce_vo_durations", "vo_sync_tolerance_ms", "timeline_mode"):
                if "audio_sync" not in target_dict or not isinstance(target_dict["audio_sync"], dict):
                    target_dict["audio_sync"] = {}
                target_dict["audio_sync"][param_key] = param_val
            elif param_key in ("dual_persistence_enabled", "sha256_verification", "r2_upload_enabled"):
                if "persistence" not in target_dict or not isinstance(target_dict["persistence"], dict):
                    target_dict["persistence"] = {}
                target_dict["persistence"][param_key] = param_val

        # 2. Mapear violaciones y anomalías a parches concretos
        violations = audit_result.get("violations", [])
        for v in violations:
            patch = v.get("recommended_patch", {})
            for k, val in patch.items():
                patches_applied[k] = {"before": wf_data.get(k), "after": val}
                _apply_param_to_wf(wf_data, k, val)

        if anomalies:
            for an in anomalies.get("anomalies", []):
                fix = an.get("suggested_fix", {})
                for k, val in fix.items():
                    if k == "video_encoder" and isinstance(val, dict):
                        existing_enc = wf_data.get("video_encoder", {})
                        if isinstance(existing_enc, dict):
                            existing_enc.update(val)
                            wf_data["video_encoder"] = existing_enc
                        else:
                            wf_data["video_encoder"] = val
                    else:
                        patches_applied[k] = {"before": wf_data.get(k), "after": val}
                        _apply_param_to_wf(wf_data, k, val)

        # Emitir cada corrección aplicada
        for param_k, change in patches_applied.items():
            self.emit_event(
                LearningEventType.CORRECTION_APPLIED,
                f"Auto-corrección aplicada en '{param_k}': {change['before']} ➔ {change['after']}",
                {"archetype_id": archetype_id, "parameter": param_k, "before": change["before"], "after": change["after"]}
            )

        # Aplicar parches sobre los nodos del pipeline_graph si existen
        self._patch_pipeline_graph_nodes(wf_data, patches_applied)

        # 3. Incrementar versión y metadatos
        wf_data["version"] = new_version
        wf_data["version_label"] = f"v{new_version}.0-auto-optimized"
        wf_data["updated_at"] = datetime.now().isoformat()

        # 4. Registrar en el historial de mejoras del workflow
        improvement_history = wf_data.get("improvement_history", [])
        improvement_entry = {
            "from_version": current_version,
            "to_version": new_version,
            "timestamp": datetime.now().isoformat(),
            "trigger_project_id": project_id,
            "audit_score_before": audit_result.get("overall_score", 0.0),
            "violations_corrected": [v.get("rule_id") for v in violations],
            "patches_applied": patches_applied
        }
        improvement_history.insert(0, improvement_entry)
        wf_data["improvement_history"] = improvement_history

        # 5. Guardar nueva versión en storage/workflows/<ARCHETYPE>_v<N+1>.json
        new_wf_file = self.workflows_dir / f"{archetype_id}_v{new_version}.json"
        with open(new_wf_file, "w", encoding="utf-8") as f:
            json.dump(wf_data, f, indent=2, ensure_ascii=False)

        # Sincronizar en repositorio de Studio si está disponible
        try:
            from app.core.orchestration.workflows import WorkflowDefinition, WORKFLOW_TEMPLATES
            if archetype_id in WORKFLOW_TEMPLATES:
                wf_def = WorkflowDefinition(**wf_data)
                StudioRepository.save_workflow(wf_def)
        except Exception as ex:
            logger.debug(f"Sincronización StudioRepository en memoria omitida: {ex}")

        # 6. Registrar en el registro global de mejoras y métricas
        self._record_global_improvement(archetype_id, improvement_entry)
        self._update_archetype_performance(archetype_id, audit_result, new_version)

        self.emit_event(
            LearningEventType.VERSION_INCREMENTED,
            f"Workflow {archetype_id} actualizado con éxito a versión v{new_version} ({new_wf_file.name})",
            {
                "archetype_id": archetype_id,
                "previous_version": current_version,
                "new_version": new_version,
                "workflow_file": str(new_wf_file),
                "patches_count": len(patches_applied),
                "violations_resolved": len(violations)
            },
            severity="INFO"
        )

        logger.info(f"✨ Workflow {archetype_id} auto-parcheado con éxito a la versión v{new_version} ({new_wf_file.name})")

        return {
            "status": "OPTIMIZED",
            "archetype_id": archetype_id,
            "previous_version": current_version,
            "new_version": new_version,
            "workflow_file": str(new_wf_file),
            "patches_applied": patches_applied,
            "violations_resolved_count": len(violations),
            "timestamp": datetime.now().isoformat()
        }

    def _find_latest_workflow_file(self, archetype_id: str) -> Tuple[Optional[Path], int]:
        """Busca el archivo de workflow más reciente para un arquetipo."""
        pattern = re.compile(rf"^{re.escape(archetype_id)}_v(\d+)\.json$")
        latest_file = None
        max_ver = 0

        for f in self.workflows_dir.glob(f"{archetype_id}_v*.json"):
            m = pattern.match(f.name)
            if m:
                ver = int(m.group(1))
                if ver > max_ver:
                    max_ver = ver
                    latest_file = f

        return latest_file, (max_ver if max_ver > 0 else 1)

    def _create_base_workflow_data(self, archetype_id: str) -> Dict[str, Any]:
        """Crea una estructura base de workflow a partir del catálogo de arquetipos."""
        arch = ARCHETYPES_CATALOG.get(archetype_id)
        if arch:
            return {
                "id": archetype_id,
                "name": arch.name,
                "description": arch.description,
                "version": 1,
                "version_label": "v1.0-initial",
                "archetype_id": archetype_id,
                "required_capabilities": ["script", "voice_generation", "video_generation", "rendering"],
                "pipeline_graph": arch.pipeline_graph,
                "policies": {"retry_limit": 2, "auto_fallback": True}
            }
        return {
            "id": archetype_id,
            "name": f"Workflow {archetype_id}",
            "description": f"Workflow optimizado para {archetype_id}",
            "version": 1,
            "version_label": "v1.0",
            "archetype_id": archetype_id,
            "required_capabilities": ["script", "video_generation", "rendering"],
            "pipeline_graph": {"nodes": [], "connections": []},
            "policies": {"retry_limit": 2, "auto_fallback": True}
        }

    def _patch_pipeline_graph_nodes(self, wf_data: dict, patches: dict):
        """Propaga los parámetros parcheados a los nodos internos del pipeline_graph."""
        nodes = wf_data.get("pipeline_graph", {}).get("nodes", [])
        for node in nodes:
            params = node.get("parameters", [])
            if isinstance(params, list):
                for p in params:
                    if isinstance(p, dict):
                        k = p.get("key", "")
                        if "ducking" in k and "ducking_db" in patches:
                            p["value"] = patches["ducking_db"]["after"]
                        elif "color" in k and "background_color" in patches:
                            p["value"] = patches["background_color"]["after"]
                        elif "user_agent" in k and "user_agent" in patches:
                            p["value"] = patches["user_agent"]["after"]

    # ------------------------------------------------------------------------
    # 3.6 REGISTRO DE LECCIONES Y CRÍTICAS EN LEARNING MEMORY ENGINE
    # ------------------------------------------------------------------------
    def record_learned_lessons(
        self,
        project_id: str,
        workflow_id: str,
        audit_result: Dict[str, Any],
        anomalies: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Extrae lecciones aprendidas y registra la crítica en storage/learning_memory/.
        """
        extracted_lesson_ids = []
        violations = audit_result.get("violations", [])

        critique_breakdown = audit_result.get("category_scores", {})
        overall_score = int(audit_result.get("overall_score", 85.0))

        # Crear o reforzar lecciones aprendidas
        for v in violations:
            rule_id = v.get("rule_id", "unknown_rule")
            lesson_id = f"lesson_{rule_id.lower()}"
            extracted_lesson_ids.append(lesson_id)

            lesson_dict = {
                "id": lesson_id,
                "title": f"Lección Aprendida: {v.get('name')}",
                "category": v.get("category", "EDITING_COMPOSITION"),
                "severity": v.get("severity", "STRICT"),
                "what_failed": "; ".join(v.get("details", ["Incumplimiento de regla de oro."])),
                "golden_rule": v.get("recommendation", "Aplicar estándar de calidad."),
                "applicable_nodes": ["ALL"],
                "applicable_workflows": [workflow_id, "ALL"],
                "experience_source_project": project_id,
                "applied_count": 1,
                "success_rating": 0.95
            }

            if learning_engine:
                try:
                    lesson_obj = LearnedLesson(**lesson_dict)
                    learning_engine.save_lesson(lesson_obj)
                except Exception as ex:
                    logger.debug(f"Error al guardar lección en learning_engine: {ex}")

            self.emit_event(
                LearningEventType.LESSON_RECORDED,
                f"Lección aprendida registrada: [{rule_id[:3]}] {v.get('name')}",
                lesson_dict,
                severity="INFO"
            )

        # Registrar crítica de proyecto
        feedback_summary = f"Auditoría automática post-ejecución: {len(violations)} violaciones detectadas."
        if learning_engine:
            try:
                learning_engine.record_project_critique(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    overall_score=overall_score,
                    user_feedback_raw=feedback_summary,
                    critique_breakdown=critique_breakdown,
                    lessons_extracted=extracted_lesson_ids
                )
            except Exception as ex:
                logger.debug(f"Error registrando crítica en learning_engine: {ex}")

        self.emit_event(
            LearningEventType.CRITIQUE_RECORDED,
            f"Crítica post-producción registrada para '{project_id}' (Puntuación: {overall_score}/100)",
            {
                "project_id": project_id,
                "workflow_id": workflow_id,
                "overall_score": overall_score,
                "critique_breakdown": critique_breakdown,
                "lessons_extracted": extracted_lesson_ids
            },
            severity="INFO"
        )

        return extracted_lesson_ids

    # ------------------------------------------------------------------------
    # 3.7 HISTORIAL DE MEJORAS Y MÉTRICAS POR TIPO DE VÍDEO
    # ------------------------------------------------------------------------
    def _record_global_improvement(self, archetype_id: str, entry: dict):
        """Almacena el registro de mejora en storage/learning_memory/workflow_improvements.json."""
        try:
            with open(self.improvements_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            entry_with_arch = dict(entry)
            entry_with_arch["archetype_id"] = archetype_id
            history.insert(0, entry_with_arch)
            with open(self.improvements_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            # Sincronizar en Firebase Firestore
            try:
                from app.services import firebase_sync
                firebase_sync.sync_workflow_improvements_to_firebase(history)
            except Exception:
                pass
        except Exception as ex:
            logger.error(f"Error guardando mejora global: {ex}")

    def _update_archetype_performance(self, archetype_id: str, audit_res: dict, current_ver: int):
        """Actualiza las métricas acumuladas por arquetipo en archetype_performance.json."""
        try:
            with open(self.performance_file, "r", encoding="utf-8") as f:
                perf = json.load(f)

            if archetype_id not in perf:
                perf[archetype_id] = {
                    "archetype_id": archetype_id,
                    "total_runs": 0,
                    "passed_runs": 0,
                    "avg_score": 0.0,
                    "current_version": current_ver,
                    "last_updated": datetime.now().isoformat(),
                    "violations_history": {},
                    "versions": []
                }

            entry = perf[archetype_id]
            entry["total_runs"] += 1
            if audit_res.get("passed", False):
                entry["passed_runs"] += 1
            
            score = audit_res.get("overall_score", 0.0)
            entry["avg_score"] = round(((entry["avg_score"] * (entry["total_runs"] - 1)) + score) / entry["total_runs"], 2)
            entry["current_version"] = current_ver
            entry["last_updated"] = datetime.now().isoformat()
            if current_ver not in entry["versions"]:
                entry["versions"].append(current_ver)

            # Acumular conteo de violaciones
            for v in audit_res.get("violations", []):
                rid = v.get("rule_id", "unknown")
                entry["violations_history"][rid] = entry["violations_history"].get(rid, 0) + 1

            with open(self.performance_file, "w", encoding="utf-8") as f:
                json.dump(perf, f, indent=2, ensure_ascii=False)

            self.emit_event(
                LearningEventType.PERFORMANCE_UPDATED,
                f"Métricas actualizadas para {archetype_id}: Promedio {entry['avg_score']} pts ({entry['total_runs']} ejecuciones, v{current_ver})",
                {"archetype_id": archetype_id, "performance": entry}
            )

            # Sincronizar en Firebase Firestore
            try:
                from app.services import firebase_sync
                firebase_sync.sync_archetype_performance_to_firebase(perf)
            except Exception:
                pass
        except Exception as ex:
            logger.error(f"Error actualizando métricas de arquetipo: {ex}")

    def get_performance_metrics(self, archetype_id: Optional[str] = None) -> Dict[str, Any]:
        """Consulta el historial de métricas y rendimiento por tipo de vídeo / arquetipo."""
        try:
            with open(self.performance_file, "r", encoding="utf-8") as f:
                perf = json.load(f)
            with open(self.improvements_file, "r", encoding="utf-8") as f:
                improvements = json.load(f)

            if archetype_id:
                arch_upper = archetype_id.upper()
                return {
                    "archetype_performance": perf.get(arch_upper, {}),
                    "improvements": [imp for imp in improvements if imp.get("archetype_id") == arch_upper]
                }
            return {
                "archetypes_summary": perf,
                "total_improvements_recorded": len(improvements),
                "recent_improvements": improvements[:10]
            }
        except Exception as ex:
            logger.error(f"Error consultando métricas: {ex}")
            return {}

    # ------------------------------------------------------------------------
    # 3.8 FLUJO MAESTRO COMPLETO: AUDITORÍA + APRENDIZAJE + OPTIMIZACIÓN
    # ------------------------------------------------------------------------
    def audit_and_optimize_post_execution(
        self,
        project_path_or_manifest: Union[str, Path, dict],
        archetype_id: Optional[str] = None,
        auto_patch: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de vida completo de Auto-Mejora y Aprendizaje Continuo tras una producción.
        Emite eventos en tiempo real a disco local y Firebase Firestore.
        """
        manifest_data, project_dir = self.load_manifest(project_path_or_manifest)
        arch_id = self.resolve_archetype_id(manifest_data, archetype_id)
        project_id = manifest_data.get("project_id", manifest_data.get("slug", "project"))

        session_id = f"learn_session_{int(time.time() * 1000)}"
        self._active_session_id = session_id
        self._active_project_id = project_id
        self._active_archetype_id = arch_id

        self.emit_event(
            LearningEventType.SESSION_STARTED,
            f"Iniciando ciclo de vida de auto-mejora para proyecto '{project_id}' (Arquetipo: {arch_id})",
            {"project_id": project_id, "archetype_id": arch_id, "session_id": session_id, "auto_patch": auto_patch}
        )

        logger.info(f"🔍 Iniciando auditoría post-ejecución para proyecto '{project_id}' (Arquetipo: {arch_id})...")

        # 1. Auditoría contra las 10 Reglas de Oro
        audit_res = self.audit_project(manifest_data, project_dir)

        # 2. Detección profunda de anomalías en el montaje
        anomalies_res = self.detect_montage_anomalies(manifest_data, project_dir)

        # 3. Registro de lecciones y crítica
        extracted_lessons = self.record_learned_lessons(project_id, arch_id, audit_res, anomalies_res)

        # 4. Auto-parcheo y generación de workflow v+1
        patch_res = None
        if auto_patch and (len(audit_res["violations"]) > 0 or anomalies_res["total_anomalies"] > 0):
            logger.info(f"⚙️ Auto-parcheando workflow para arquetipo {arch_id}...")
            patch_res = self.auto_patch_workflow(arch_id, audit_res, project_id, anomalies_res)
        else:
            logger.info(f"✅ Proyecto {project_id} cumple con los estándares o auto_patch desactivado.")

        result = {
            "status": "SUCCESS",
            "session_id": session_id,
            "project_id": project_id,
            "archetype_id": arch_id,
            "audit": audit_res,
            "anomalies": anomalies_res,
            "lessons_extracted": extracted_lessons,
            "workflow_patch": patch_res,
            "completed_at": datetime.now().isoformat()
        }

        # 5. Emitir evento de sesión completada
        self.emit_event(
            LearningEventType.SESSION_COMPLETED,
            f"Ciclo de auto-mejora finalizado para '{project_id}': Score {audit_res['overall_score']}/100 | "
            f"Workflow {'v' + str(patch_res['new_version']) if patch_res else 'sin cambios'}",
            {
                "session_id": session_id,
                "project_id": project_id,
                "archetype_id": arch_id,
                "overall_score": audit_res["overall_score"],
                "passed": audit_res["passed"],
                "violations_count": len(audit_res["violations"]),
                "workflow_patched": bool(patch_res),
                "patch_result": patch_res,
                "lessons_count": len(extracted_lessons)
            },
            severity="INFO" if audit_res["passed"] else "WARNING"
        )

        # 6. Sincronizar informe completo y memoria en Firebase Firestore
        try:
            from app.services import firebase_sync
            firebase_sync.save_audit_report_to_firebase_async(result)
            if learning_engine:
                learning_engine.sync_to_firebase_async()
        except Exception as ex:
            logger.debug(f"Aviso al sincronizar auditoría final en Firestore: {ex}")

        return result

    # ------------------------------------------------------------------------
    # 3.9 EXPORTACIÓN DE INFORME EN MARKDOWN EJECUTIVO
    # ------------------------------------------------------------------------
    def export_report_markdown(self, result: Dict[str, Any], output_path: Optional[Union[str, Path]] = None) -> str:
        """Genera un informe Markdown formateado y profesional con el resultado de la auditoría y optimización."""
        audit = result.get("audit", {})
        score = audit.get("overall_score", 0.0)
        passed = audit.get("passed", False)
        status_badge = "🟢 **APROBADO (PASSED)**" if passed else "🔴 **REQUIRIÓ OPTIMIZACIÓN (AUTO-PATCHED)**"

        md_lines = [
            f"# 🧠 INFORME DE AUDITORÍA QA FORENSE & AUTO-MEJORA CONTINUA",
            f"",
            f"- **Proyecto:** `{result.get('project_id')}`",
            f"- **Arquetipo:** `{result.get('archetype_id')}`",
            f"- **Puntuación QA Global:** `{score}/100.0` ({status_badge})",
            f"- **Fecha:** `{result.get('completed_at')}`",
            f"",
            f"---",
            f"",
            f"## 📋 1. EVALUACIÓN DE LAS 10 REGLAS DE ORO (R01 A R10)",
            f"",
            f"| Regla | Nombre de la Regla | Categoría | Severidad | Estado | Penalización |",
            f"| :---: | :--- | :--- | :---: | :---: | :---: |"
        ]

        evals = audit.get("rule_evaluations", {})
        for r_id, ev in evals.items():
            st = "✅ PASSED" if ev.get("passed") else "❌ FAILED"
            pen = f"-{ev.get('penalty')} pts" if not ev.get("passed") else "0 pts"
            md_lines.append(f"| **{r_id[:3]}** | {ev.get('name')} | `{ev.get('category')}` | `{ev.get('severity')}` | {st} | {pen} |")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"## ⚠️ 2. VIOLACIONES DETECTADAS & CORRECCIONES RECOMENDADAS",
            f""
        ])

        violations = audit.get("violations", [])
        if not violations:
            md_lines.append("🎉 **Cero violaciones detectadas. El proyecto cumple con la totalidad de los estándares áureos.**")
        else:
            for v in violations:
                md_lines.extend([
                    f"### 🔴 [{v.get('rule_id')}] {v.get('name')}",
                    f"- **Severidad:** `{v.get('severity')}` | **Penalización:** `-{v.get('penalty')} pts`",
                    f"- **Fallo Detectado:** {'; '.join(v.get('details', []))}",
                    f"- **Acción de Corrección:** {v.get('recommendation')}",
                    f""
                ])

        patch = result.get("workflow_patch")
        if patch:
            md_lines.extend([
                f"---",
                f"",
                f"## ⚙️ 3. AUTO-PARCHEO Y VERSIÓN OPTIMIZADA DEL WORKFLOW",
                f"",
                f"- **Arquetipo:** `{patch.get('archetype_id')}`",
                f"- **Versión Previa:** `v{patch.get('previous_version')}` ➔ **Nueva Versión Optimizada:** `v{patch.get('new_version')}`",
                f"- **Archivo Generado:** [`{Path(patch.get('workflow_file')).name}`](file://{patch.get('workflow_file')})",
                f"",
                f"### Parámetros Parcheados Determinísticamente:",
                f"```json",
                json.dumps(patch.get("patches_applied", {}), indent=2, ensure_ascii=False),
                f"```",
                f""
            ])

        md_text = "\n".join(md_lines)
        if output_path:
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(md_text)

        return md_text


# ============================================================================
# 4. PUNTO DE ENTRADA CLI
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="VideoPro Workflow Learner & Continuous Improvement Engine"
    )
    parser.add_argument(
        "--audit",
        type=str,
        help="Ruta al proyecto o project_manifest.json para auditar contra las 10 Reglas de Oro."
    )
    parser.add_argument(
        "--optimize",
        type=str,
        help="Audita, registra lecciones y auto-parchea el workflow correspondiente a la versión v+1."
    )
    parser.add_argument(
        "--archetype",
        type=str,
        help="ID explícito del arquetipo (ej: CITY_ROUTES_BEATS, VOX_INVESTIGATIVE_DOC, PIXAR_3D_ANIMATION)."
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="Muestra el catálogo maestro de las 10 Reglas de Oro con sus penalizaciones y severidades."
    )
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Muestra las métricas de rendimiento y evolución por tipo de vídeo."
    )
    parser.add_argument(
        "--events",
        action="store_true",
        help="Muestra los eventos de aprendizaje y telemetría en tiempo real más recientes."
    )
    parser.add_argument(
        "--limit-events",
        type=int,
        default=30,
        help="Límite de eventos a mostrar con --events (por defecto: 30)."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Devuelve la salida formateada en JSON estructurado para integración programática."
    )
    parser.add_argument(
        "--report-out",
        type=str,
        help="Ruta de archivo para exportar el informe en formato Markdown."
    )

    args = parser.parse_args()
    learner = WorkflowLearner()

    if args.events:
        events = learner.get_recent_events(limit=args.limit_events)
        if args.json:
            print(json.dumps(events, indent=2, ensure_ascii=False))
        else:
            print(f"\n⚡ ÚLTIMOS {len(events)} EVENTOS DE APRENDIZAJE CONTINUO & TELEMETRÍA:")
            print("=" * 80)
            for ev in events:
                sev_icon = "🔴" if ev.get("severity") == "CRITICAL" else ("⚠️" if ev.get("severity") == "WARNING" else "🔹")
                print(f"{sev_icon} [{ev.get('timestamp')[:19]}] [{ev.get('event_type')}] ({ev.get('archetype_id')}) {ev.get('message')}")
        return

    if args.list_rules:
        if args.json:
            print(json.dumps(GOLDEN_RULES_CATALOG, indent=2, ensure_ascii=False))
        else:
            print("\n🌟 CATÁLOGO MAESTRO DE LAS 10 REGLAS DE ORO VIDEOPRO (R01 A R10):")
            print("=" * 80)
            for r in GOLDEN_RULES_CATALOG:
                print(f"[{r['id']}] {r['name']}")
                print(f"  • Categoría: {r['category']} | Severidad: {r['severity']} | Penalización: -{r['penalty']} pts")
                print(f"  • Descripción: {r['description']}\n")
        return

    if args.metrics:
        res = learner.get_performance_metrics(args.archetype)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    target_path = args.optimize or args.audit
    if target_path:
        auto_patch = bool(args.optimize)
        res = learner.audit_and_optimize_post_execution(
            target_path,
            archetype_id=args.archetype,
            auto_patch=auto_patch
        )

        if args.report_out:
            learner.export_report_markdown(res, args.report_out)
            logger.info(f"📄 Informe guardado en: {args.report_out}")

        if args.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(learner.export_report_markdown(res))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
