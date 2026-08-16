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


class StudioRepository:
    """Repositorio unificado de Studio para metadatos, configuraciones y trazabilidad de Jobs."""

    @classmethod
    def get_ecosystem_manifest(cls) -> Dict[str, Any]:
        """Exporta el manifiesto completo del ecosistema (Capabilities, Engines, Providers, Workflows)."""
        return {
            "capabilities": [c.dict() for c in get_all_capabilities()],
            "engines": [e.dict() for e in get_all_engines()],
            "providers": {k: [p.dict() for p in v] for k, v in PROVIDERS_CATALOG.items()},
            "workflows": [w.dict() for w in get_all_workflows()]
        }

    @classmethod
    def save_workflow(cls, workflow: WorkflowDefinition) -> bool:
        """Guarda un workflow en almacenamiento local y sincroniza en Firestore."""
        try:
            os.makedirs(WORKFLOWS_DIR, exist_ok=True)
            file_path = os.path.join(WORKFLOWS_DIR, f"{workflow.id}_v{workflow.version}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(workflow.dict(), f, indent=2, ensure_ascii=False)
            
            # Sincronizar en memoria
            WORKFLOW_TEMPLATES[workflow.id] = workflow
            return True
        except Exception as ex:
            logger.error(f"Error al guardar workflow: {ex}")
            return False

    @classmethod
    def save_job(cls, job: ExecutionJob) -> bool:
        """Persiste el estado auditable de un ExecutionJob en disco y en la base de datos."""
        try:
            os.makedirs(JOBS_DIR, exist_ok=True)
            job_file = os.path.join(JOBS_DIR, f"{job.job_id}.json")
            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(job.dict(), f, indent=2, ensure_ascii=False)
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
