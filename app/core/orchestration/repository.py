"""
Capa de Repositorio y Persistencia Unificada — VideoPro Studio
Garantiza que Firestore almacene metadata y estado, R2 almacene media, y el disco local funcione como buffer temporal.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional

from app.core.orchestration.capabilities import get_all_capabilities, CapabilitySpec
from app.core.orchestration.engines import get_all_engines, EngineSpec, ENGINES_CATALOG
from app.core.orchestration.providers import PROVIDERS_CATALOG, ProviderSpec
from app.core.orchestration.workflows import get_all_workflows, get_workflow, WorkflowDefinition, WORKFLOW_TEMPLATES
from app.core.orchestration.job import ExecutionJob

logger = logging.getLogger("videopro.orchestration.repository")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
WORKFLOWS_DIR = os.path.join(STORAGE_DIR, "workflows")
JOBS_DIR = os.path.join(STORAGE_DIR, "jobs")


def _model_to_dict(model_obj: Any) -> Dict[str, Any]:
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump()
    return model_obj.dict()


class StudioRepository:
    """Repositorio unificado de Studio para metadatos, configuraciones y trazabilidad de Jobs."""

    @classmethod
    def get_ecosystem_manifest(cls) -> Dict[str, Any]:
        """Exporta el manifiesto completo del ecosistema (Capabilities, Engines, Providers, Workflows)."""
        return {
            "capabilities": [_model_to_dict(c) for c in get_all_capabilities()],
            "engines": [_model_to_dict(e) for e in get_all_engines()],
            "providers": {k: [_model_to_dict(p) for p in v] for k, v in PROVIDERS_CATALOG.items()},
            "workflows": [_model_to_dict(w) for w in get_all_workflows()]
        }

    @classmethod
    def save_workflow(cls, workflow: WorkflowDefinition, filename: Optional[str] = None) -> bool:
        """Guarda un workflow en almacenamiento local y sincroniza en Firestore."""
        try:
            os.makedirs(WORKFLOWS_DIR, exist_ok=True)
            if filename:
                file_path = os.path.join(WORKFLOWS_DIR, filename if filename.endswith(".json") else f"{filename}.json")
            else:
                file_path = os.path.join(WORKFLOWS_DIR, f"{workflow.id}_v{workflow.version}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(_model_to_dict(workflow), f, indent=2, ensure_ascii=False)
            
            # Sincronizar en memoria
            WORKFLOW_TEMPLATES[workflow.id] = workflow
            return True
        except Exception as ex:
            logger.error(f"Error al guardar workflow: {ex}")
            return False

    @classmethod
    def load_workflow_from_file(cls, file_path: str) -> Optional[WorkflowDefinition]:
        """Carga un WorkflowDefinition desde un archivo JSON local."""
        if not os.path.isabs(file_path):
            file_path = os.path.join(WORKFLOWS_DIR, file_path)
        if not os.path.isfile(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return WorkflowDefinition(**data)
        except Exception as ex:
            logger.error(f"Error al cargar workflow desde {file_path}: {ex}")
            return None

    @classmethod
    def get_workflow(cls, wf_id: str) -> Optional[WorkflowDefinition]:
        """Obtiene un workflow desde la memoria o desde el disco."""
        return get_workflow(wf_id)

    @classmethod
    def load_all_workflows_from_storage(cls) -> List[WorkflowDefinition]:
        """Carga todos los workflows válidos presentes en storage/workflows/."""
        return get_all_workflows()

    @classmethod
    def list_stored_workflow_files(cls) -> List[str]:
        """Lista las rutas de todos los archivos JSON en storage/workflows/."""
        if not os.path.isdir(WORKFLOWS_DIR):
            return []
        return [
            os.path.join(WORKFLOWS_DIR, f)
            for f in sorted(os.listdir(WORKFLOWS_DIR))
            if f.endswith(".json")
        ]

    @classmethod
    def save_job(cls, job: ExecutionJob) -> bool:
        """Persiste el estado auditable de un ExecutionJob en disco y en la base de datos."""
        try:
            os.makedirs(JOBS_DIR, exist_ok=True)
            job_file = os.path.join(JOBS_DIR, f"{job.job_id}.json")
            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(_model_to_dict(job), f, indent=2, ensure_ascii=False)
            return True
        except Exception as ex:
            logger.error(f"Error al guardar job '{job.job_id}': {ex}")
            return False

    @classmethod
    def get_job(cls, job_id: str) -> Optional[ExecutionJob]:
        """Recupera un ExecutionJob por su ID."""
        job_file = os.path.join(JOBS_DIR, f"{job_id}.json")
        if os.path.isfile(job_file):
            try:
                with open(job_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return ExecutionJob(**data)
            except Exception as ex:
                logger.error(f"Error al leer job '{job_id}': {ex}")
        return None

    @classmethod
    def list_jobs(cls, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista los últimos Jobs de producción ejecutados."""
        if not os.path.isdir(JOBS_DIR):
            return []
        
        job_files = sorted(
            [os.path.join(JOBS_DIR, f) for f in os.listdir(JOBS_DIR) if f.endswith(".json")],
            key=os.path.getmtime,
            reverse=True
        )[:limit]

        jobs_list = []
        for jf in job_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    jobs_list.append(json.load(f))
            except Exception:
                pass
        return jobs_list

    def list_active_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Lista los jobs activos o en proceso de renderizado."""
        all_j = self.list_jobs(limit=limit)
        active_statuses = {"pending", "running", "in_progress", "rendering"}
        return [j for j in all_j if j.get("status", "").lower() in active_statuses]
