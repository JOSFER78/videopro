"""
Project Repository for Persistent Storage with Legacy Task Migration Support
"""
import os
import json
import time
from pathlib import Path
from typing import List, Optional
from loguru import logger
from app.core.domain.entities import ProjectEntity, SceneEntity, DecisionRecord
from app.core.domain.specs import VisualSpec, AudioSpec, SubtitleSpec, RenderSpec, ProvenanceInfo
from app.core.domain.enums import ProjectStatus, SceneStatus, LockLevel, VisualEngineType, VoiceEngineType, KaraokeStyle

class ProjectRepository:
    def __init__(self, base_storage_dir: Optional[str] = None):
        if not base_storage_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            base_storage_dir = os.path.join(base_dir, "storage")
        self.base_dir = base_storage_dir
        self.projects_dir = os.path.join(self.base_dir, "projects")
        self.legacy_tasks_dir = os.path.join(self.base_dir, "tasks")
        os.makedirs(self.projects_dir, exist_ok=True)

    def save_project(self, project: ProjectEntity) -> str:
        proj_dir = os.path.join(self.projects_dir, project.project_id)
        os.makedirs(proj_dir, exist_ok=True)
        manifest_path = os.path.join(proj_dir, "project.json")

        data = {
            "project_id": project.project_id,
            "title": project.title,
            "status": project.status.value,
            "version": project.version,
            "created_at": project.created_at,
            "updated_at": time.time(),
            "render_spec": {
                "resolution": project.render_spec.resolution,
                "fps": project.render_spec.fps,
                "codec": project.render_spec.codec,
                "burned_subtitles": project.render_spec.burned_subtitles
            },
            "decisions": {
                k: {
                    "decision_id": v.decision_id,
                    "target_path": v.target_path,
                    "value": v.value,
                    "lock_level": int(v.lock_level),
                    "source": v.source,
                    "rationale": v.rationale,
                    "timestamp": v.timestamp
                } for k, v in project.decisions.items()
            },
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "index": s.index,
                    "title": s.title,
                    "status": s.status.value,
                    "raw_video_path": s.raw_video_path,
                    "voice_audio_path": s.voice_audio_path,
                    "visual_spec": {
                        "subject": s.visual_spec.subject,
                        "action": s.visual_spec.action,
                        "environment": s.visual_spec.environment,
                        "lighting": s.visual_spec.lighting,
                        "camera_motion": s.visual_spec.camera_motion,
                        "color_palette": s.visual_spec.color_palette,
                        "engine": s.visual_spec.engine.value,
                        "duration_s": s.visual_spec.duration_s,
                        "locked": s.visual_spec.locked
                    },
                    "audio_spec": {
                        "voice_text": s.audio_spec.voice_text,
                        "voice_engine": s.audio_spec.voice_engine.value,
                        "voice_id": s.audio_spec.voice_id,
                        "auto_ducking": s.audio_spec.auto_ducking,
                        "foley_enabled": s.audio_spec.foley_enabled,
                        "locked": s.audio_spec.locked
                    },
                    "subtitle_spec": {
                        "enabled": s.subtitle_spec.enabled,
                        "style": s.subtitle_spec.style.value,
                        "highlight_color": s.subtitle_spec.highlight_color,
                        "locked": s.subtitle_spec.locked
                    }
                } for s in project.scenes
            ]
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved project manifest: {manifest_path}")
        return manifest_path

    def load_project(self, project_id: str) -> Optional[ProjectEntity]:
        manifest_path = os.path.join(self.projects_dir, project_id, "project.json")
        if not os.path.exists(manifest_path):
            # Check for legacy task migration
            legacy_path = os.path.join(self.legacy_tasks_dir, project_id, "config.json")
            if os.path.exists(legacy_path):
                return self._migrate_legacy_task(project_id, legacy_path)
            return None

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        proj = ProjectEntity(
            project_id=data["project_id"],
            title=data.get("title", "Proyecto VideoPro"),
            status=ProjectStatus(data.get("status", "draft")),
            version=data.get("version", 1),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )

        for s_data in data.get("scenes", []):
            v_data = s_data.get("visual_spec", {})
            a_data = s_data.get("audio_spec", {})
            sub_data = s_data.get("subtitle_spec", {})

            scene = SceneEntity(
                scene_id=s_data["scene_id"],
                index=s_data.get("index", 0),
                title=s_data.get("title", ""),
                status=SceneStatus(s_data.get("status", "pending")),
                raw_video_path=s_data.get("raw_video_path"),
                voice_audio_path=s_data.get("voice_audio_path"),
                visual_spec=VisualSpec(
                    subject=v_data.get("subject", ""),
                    action=v_data.get("action", ""),
                    environment=v_data.get("environment", ""),
                    lighting=v_data.get("lighting", ""),
                    camera_motion=v_data.get("camera_motion", ""),
                    color_palette=v_data.get("color_palette", ""),
                    engine=VisualEngineType(v_data.get("engine", "ltx25")),
                    duration_s=v_data.get("duration_s", 5.0),
                    locked=v_data.get("locked", False)
                ),
                audio_spec=AudioSpec(
                    voice_text=a_data.get("voice_text", ""),
                    voice_engine=VoiceEngineType(a_data.get("voice_engine", "kokoro_hd")),
                    voice_id=a_data.get("voice_id", "es_male_1"),
                    auto_ducking=a_data.get("auto_ducking", True),
                    foley_enabled=a_data.get("foley_enabled", True),
                    locked=a_data.get("locked", False)
                ),
                subtitle_spec=SubtitleSpec(
                    enabled=sub_data.get("enabled", True),
                    style=KaraokeStyle(sub_data.get("style", "vox_harris")),
                    highlight_color=sub_data.get("highlight_color", "#FFC924"),
                    locked=sub_data.get("locked", False)
                )
            )
            proj.scenes.append(scene)

        return proj

    def load_project_dict(self, project_id: str) -> Optional[dict]:
        """Carga el diccionario completo del proyecto desde disco o Firestore."""
        # 1. Intentar cargar desde disco local
        manifest_path = os.path.join(self.projects_dir, project_id, "project.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # 2. Intentar cargar desde Firestore
        try:
            from app.services import firebase_sync
            fb_proj = firebase_sync.fetch_single_project_from_firebase(project_id)
            if fb_proj:
                return fb_proj
        except Exception:
            pass

        return None

    def get_all_projects_summary(self, force_refresh: bool = False) -> List[dict]:
        """Retorna la lista unificada de todos los proyectos desde RAM/disco instantáneamente."""
        global _PROJECTS_SUMMARY_CACHE, _PROJECTS_SUMMARY_LAST_FETCH, _PROJECTS_SUMMARY_LOCK
        
        now = time.time()
        # Retornar instantáneamente de RAM si la caché tiene menos de 20 segundos
        if not force_refresh and _PROJECTS_SUMMARY_CACHE and (now - _PROJECTS_SUMMARY_LAST_FETCH < 20.0):
            return _PROJECTS_SUMMARY_CACHE

        projects_map = {}

        # 1. Escaneo ultrarrápido de storage/projects/ (Disco Local - 0ms latencia)
        import glob
        for p_dir in glob.glob(os.path.join(self.projects_dir, "*")):
            if not os.path.isdir(p_dir):
                continue
            pid = os.path.basename(p_dir)
            p_json = os.path.join(p_dir, "project.json")
            
            p_data = {}
            if os.path.isfile(p_json):
                try:
                    with open(p_json, "r", encoding="utf-8") as f:
                        p_data = json.load(f)
                except Exception:
                    pass

            # Buscar vídeo final si existe
            has_video = False
            final_video_path = ""
            for ext in ("*.mp4", "*.mkv", "*.mov", "*.webm"):
                vids = glob.glob(os.path.join(p_dir, ext)) + glob.glob(os.path.join(p_dir, "renders", ext))
                if vids:
                    has_video = True
                    final_video_path = vids[0]
                    break

            projects_map[pid] = {
                "project_id": pid,
                "task_id": pid,
                "title": p_data.get("title", pid),
                "subject": p_data.get("subject", p_data.get("title", pid)),
                "workflow_id": p_data.get("workflow_id", "PIXAR_3D_ANIMATION"),
                "workflow_name": p_data.get("workflow_name", "Producción Cinemática"),
                "workflow_icon": p_data.get("workflow_icon", "🎬"),
                "status": p_data.get("status", "DRAFT"),
                "aspect_ratio": p_data.get("aspect_ratio", "16:9"),
                "voice_id": p_data.get("voice_id", "vibevoice"),
                "scenes_count": len(p_data.get("scenes", [])),
                "has_video": has_video,
                "local_video_path": final_video_path,
                "director_spec": p_data.get("director_spec", {}),
                "scenes": p_data.get("scenes", []),
                "messages": p_data.get("messages", []),
                "updated_at": p_data.get("updated_at", time.time()),
                "created_at": p_data.get("created_at", time.time())
            }

        # 2. Sincronizar con Firestore
        try:
            from app.services import firebase_sync
            fb_projs = firebase_sync.fetch_all_projects_from_firebase()
            for p in fb_projs:
                pid = p.get("project_id") or p.get("task_id")
                if pid:
                    if pid in projects_map:
                        # Mantener ruta de vídeo local si existe
                        if projects_map[pid].get("has_video"):
                            p["has_video"] = True
                            p["local_video_path"] = projects_map[pid].get("local_video_path")
                    projects_map[pid] = p
        except Exception as ex:
            logger.warning(f"No se pudo consultar Firestore para listado de proyectos: {ex}")

        # Ordenar por updated_at descendente
        res = list(projects_map.values())
        res.sort(key=lambda x: str(x.get("updated_at", "")), reverse=True)
        
        _PROJECTS_SUMMARY_CACHE = res
        _PROJECTS_SUMMARY_LAST_FETCH = time.time()
        return res

    def delete_project(self, project_id: str) -> bool:
        """Elimina un proyecto de disco local y de Firebase Firestore."""
        # 1. Eliminar de disco
        proj_dir = os.path.join(self.projects_dir, project_id)
        if os.path.isdir(proj_dir):
            try:
                import shutil
                shutil.rmtree(proj_dir, ignore_errors=True)
            except Exception as e:
                logger.error(f"Error al borrar directorio local del proyecto {project_id}: {e}")

        # 2. Eliminar de Firestore
        try:
            from app.services import firebase_sync
            firebase_sync.delete_project_from_firebase(project_id)
        except Exception:
            pass

        return True

    def _migrate_legacy_task(self, task_id: str, legacy_path: str) -> ProjectEntity:
        logger.info(f"Migrating legacy task {task_id} into ProjectEntity...")
        with open(legacy_path, "r", encoding="utf-8") as f:
            t_data = json.load(f)

        proj = ProjectEntity(
            project_id=task_id,
            title=t_data.get("video_subject", f"Task {task_id}"),
            status=ProjectStatus.COMPLETED
        )
        self.save_project(proj)
        return proj
