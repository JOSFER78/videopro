"""
Pure Domain Entities (Project, Scene, Asset, Character, Decision)
"""
import uuid
import time
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.core.domain.enums import ProjectStatus, SceneStatus, LockLevel
from app.core.domain.specs import VisualSpec, AudioSpec, SubtitleSpec, RenderSpec, ProvenanceInfo

@dataclass
class DecisionRecord:
    decision_id: str
    target_path: str            # e.g., "scenes[2].visual.engine"
    value: Any
    lock_level: LockLevel
    source: str                 # "user", "director", "system"
    rationale: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class SceneEntity:
    scene_id: str = field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:8]}")
    index: int = 0
    title: str = ""
    status: SceneStatus = SceneStatus.PENDING
    visual_spec: VisualSpec = field(default_factory=VisualSpec)
    audio_spec: AudioSpec = field(default_factory=AudioSpec)
    subtitle_spec: SubtitleSpec = field(default_factory=SubtitleSpec)
    raw_video_path: Optional[str] = None
    voice_audio_path: Optional[str] = None
    provenance: Optional[ProvenanceInfo] = None
    error_message: Optional[str] = None

    def is_dirty(self) -> bool:
        return self.status != SceneStatus.RENDERED

@dataclass
class ProjectEntity:
    project_id: str = field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:10]}")
    title: str = "Nuevo Proyecto VideoPro"
    status: ProjectStatus = ProjectStatus.DRAFT
    scenes: List[SceneEntity] = field(default_factory=list)
    decisions: Dict[str, DecisionRecord] = field(default_factory=dict)
    render_spec: RenderSpec = field(default_factory=RenderSpec)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: int = 1

    def get_scene(self, scene_id: str) -> Optional[SceneEntity]:
        for s in self.scenes:
            if s.scene_id == scene_id:
                return s
        return None

    def set_decision(self, target_path: str, value: Any, lock_level: LockLevel, source: str, rationale: str = "") -> bool:
        """Enforces decision hierarchy: USER_LOCK > PROJECT_DECISION > DIRECTOR_SUGGESTION > DEFAULT."""
        existing = self.decisions.get(target_path)
        if existing and existing.lock_level > lock_level:
            return False  # Locked by higher authority
        
        record = DecisionRecord(
            decision_id=f"dec_{uuid.uuid4().hex[:8]}",
            target_path=target_path,
            value=value,
            lock_level=lock_level,
            source=source,
            rationale=rationale
        )
        self.decisions[target_path] = record
        self.updated_at = time.time()
        return True

    def calculate_affected_scope(self, target_path: str) -> List[str]:
        """Calculates granular affected scenes instead of full project invalidation."""
        m = re.search(r"scenes\[(\d+)\]", target_path)
        if m:
            idx = int(m.group(1))
            if 0 <= idx < len(self.scenes):
                return [self.scenes[idx].scene_id]
        return [s.scene_id for s in self.scenes]
