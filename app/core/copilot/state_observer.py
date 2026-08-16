"""
VideoPro Studio - Copilot State Observer
File: app/core/copilot/state_observer.py
"""

from __future__ import annotations

import re
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
from pydantic import BaseModel, Field, ConfigDict

class ViewType(str, Enum):
    PROJECT_DASHBOARD = "project_dashboard"
    QUICK_GENERATION = "quick_generation"
    SCENE_DIRECTOR = "scene_director"
    TIMELINE_EDITOR = "timeline_editor"
    VOICE_STUDIO = "voice_studio"
    FOLEY_SFX_MIXER = "foley_sfx_mixer"
    SUBTITLE_KARAOKE = "subtitle_karaoke"
    PROVIDER_SETTINGS = "provider_settings"
    BATCH_RENDERER = "batch_renderer"
    STORAGE_GALLERY = "storage_gallery"
    YOUTUBE_MONETIZATION = "youtube_monetization"
    UNKNOWN = "unknown"

class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    BLOCKED = "blocked"
    CRITICAL_ABORT = "critical_abort"

class LogEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    level: str
    logger_name: str
    message: str

class ActiveViewContext(BaseModel):
    view_type: ViewType = ViewType.UNKNOWN
    view_title: str = "Vista Desconocida"
    route_path: str = "/"
    active_subtab: Optional[str] = None
    project_id: Optional[str] = None
    project_title: Optional[str] = None

class RuntimeErrorSnapshot(BaseModel):
    severity: ErrorSeverity = ErrorSeverity.WARNING
    error_type: str
    technical_message: str
    user_facing_message: str
    kid_friendly_analogy: str
    actionable_fix_steps: List[str] = Field(default_factory=list)

class StreamlitStateSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    snapshot_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str
    active_view: ActiveViewContext
    active_errors: List[RuntimeErrorSnapshot] = Field(default_factory=list)
    recent_logs: List[LogEntry] = Field(default_factory=list)
    sanitized_session_vars: Dict[str, Any] = Field(default_factory=dict)

class PedagogicalEngine:
    ERROR_ANALOGY_RULES = [
        {
            "pattern": re.compile(r"(?i)(cuda|out of memory|oom|vram|gpu memory)"),
            "error_type": "Falta de Memoria en Tarjeta Gráfica (VRAM)",
            "analogy": "Imagina que la tarjeta gráfica es una mesa de dibujo. Intentamos poner una hoja gigante (vídeo 4K) y ya no caben más lápices. La mesa se llenó.",
            "fix_steps": [
                "Baja la resolución de vídeo de 1080p a 720p en los ajustes.",
                "Reduce la duración de la escena a 3 o 4 segundos."
            ]
        },
        {
            "pattern": re.compile(r"(?i)(429|rate limit|quota exceeded|too many requests)"),
            "error_type": "Límite de Peticiones Alcanzado (Cuota API)",
            "analogy": "El camarero de la cocina de IA está atendiendo a mucha gente y nos pide esperar 1 minuto antes del siguiente plato.",
            "fix_steps": [
                "Espera 30 a 60 segundos antes de volver a pulsar 'Generar'.",
                "Usa un motor local gratuito como Kokoro para la voz."
            ]
        }
    ]

    @classmethod
    def translate_error(cls, raw_error: str, exc_type: str = "") -> RuntimeErrorSnapshot:
        combined = f"{exc_type} {raw_error}"
        for rule in cls.ERROR_ANALOGY_RULES:
            if rule["pattern"].search(combined):
                return RuntimeErrorSnapshot(
                    severity=ErrorSeverity.BLOCKED,
                    error_type=rule["error_type"],
                    technical_message=raw_error[:300],
                    user_facing_message=f"Atención: {rule['error_type']}",
                    kid_friendly_analogy=rule["analogy"],
                    actionable_fix_steps=rule["fix_steps"]
                )
        return RuntimeErrorSnapshot(
            severity=ErrorSeverity.WARNING,
            error_type="Ajuste Necesario",
            technical_message=raw_error[:300],
            user_facing_message="Ocurrió un tropiezo inesperado.",
            kid_friendly_analogy="Un engranaje se atascó un segundo con un ajuste.",
            actionable_fix_steps=["Vuelve a hacer clic en la pestaña para refrescar."]
        )

class StreamlitStateObserver:
    @staticmethod
    def capture_snapshot(st_module: Any = None) -> StreamlitStateSnapshot:
        if st_module is None:
            try:
                import streamlit as st
                st_module = st
            except ImportError:
                st_module = None

        session_state_dict = {}
        if st_module and hasattr(st_module, "session_state"):
            try:
                session_state_dict = {k: str(v)[:200] for k, v in dict(st_module.session_state).items()}
            except Exception:
                pass

        raw_view = session_state_dict.get("active_view", "home")
        active_view = ActiveViewContext(
            view_type=ViewType.YOUTUBE_MONETIZATION if "youtube" in raw_view else ViewType.PROJECT_DASHBOARD,
            view_title="Monetización & Canales" if "youtube" in raw_view else "Panel de Proyectos",
            route_path=f"/{raw_view}",
            project_id=session_state_dict.get("current_project_id")
        )

        return StreamlitStateSnapshot(
            snapshot_id=f"snap_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            session_id=session_state_dict.get("session_id", "default_session"),
            active_view=active_view,
            sanitized_session_vars=session_state_dict
        )
