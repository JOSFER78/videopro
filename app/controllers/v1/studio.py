"""
Controlador REST del Studio de Orquestación de Workflows & Arquetipos — VideoPro Studio
Expone la arquitectura formal: Capabilities, Engines, Providers, Workflows, Arquetipos, Entrevistas y Jobs.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import get_all_capabilities
from app.core.orchestration.engines import get_all_engines
from app.core.orchestration.providers import PROVIDERS_CATALOG
from app.core.orchestration.workflows import get_all_workflows, get_workflow, WorkflowDefinition, WORKFLOW_TEMPLATES
from app.core.orchestration.workflow_archetypes import get_all_archetypes, get_archetype, ARCHETYPES_CATALOG
from app.core.orchestration.planner import RequestPlanner, ExecutionPlan
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.repository import StudioRepository
from app.core.orchestration.scene_router import VisualStrategy

router = APIRouter(prefix="/api/v1/studio", tags=["studio"])


class PlanRequest(BaseModel):
    project_id: str = "project_demo"
    prompt: str = "Documental cinematográfico sobre el skyline y la arquitectura de Tokio"
    target_duration: int = 60
    workflow_id: str = "DOCUMENTARY_MASTER"
    visual_strategy: VisualStrategy = VisualStrategy.HYBRID
    preferences: Dict[str, Any] = {}


class ArchetypePlanRequest(BaseModel):
    project_id: str = "project_archetype"
    archetype_id: str
    interview_answers: Dict[str, Any] = Field(default_factory=dict)


class WorkflowVersionRequest(BaseModel):
    workflow_id: str
    version_label: str
    name: Optional[str] = None
    description: Optional[str] = None
    pipeline_graph: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    connections: List[Dict[str, Any]] = Field(default_factory=list)


class ExecuteRequest(BaseModel):
    plan: Dict[str, Any]


@router.get("/manifest", summary="Obtiene el manifiesto completo de Capabilities, Engines, Providers, Workflows y Arquetipos")
def get_manifest():
    """Retorna el árbol arquitectónico completo de VideoPro Studio."""
    manifest = StudioRepository.get_ecosystem_manifest()
    manifest["archetypes"] = [a.dict() for a in get_all_archetypes()]
    return {"status": "ok", "manifest": manifest}


@router.get("/capabilities", summary="Lista todas las capacidades del sistema")
def list_capabilities():
    return {"status": "ok", "capabilities": [c.dict() for c in get_all_capabilities()]}


@router.get("/engines", summary="Lista todos los motores registrados con sus fallbacks y costes")
def list_engines():
    return {"status": "ok", "engines": [e.dict() for e in get_all_engines()]}


@router.get("/providers", summary="Lista los proveedores de infraestructura por motor")
def list_providers():
    return {"status": "ok", "providers": {k: [p.dict() for p in v] for k, v in PROVIDERS_CATALOG.items()}}


@router.get("/workflows", summary="Lista los workflows de producción oficiales")
def list_workflows():
    return {"status": "ok", "workflows": [w.dict() for w in get_all_workflows()]}


@router.get("/archetypes", summary="Lista todos los Arquetipos de Producción y sus pipelines ComfyUI asociados")
def list_archetypes():
    return {"status": "ok", "archetypes": [a.dict() for a in get_all_archetypes()]}


@router.get("/archetypes/{archetype_id}", summary="Obtiene el detalle, entrevista y grafo ComfyUI de un arquetipo")
def get_archetype_detail(archetype_id: str):
    arch = get_archetype(archetype_id)
    if not arch:
        raise HTTPException(status_code=404, detail=f"Arquetipo '{archetype_id}' no encontrado.")
    return {"status": "ok", "archetype": arch.dict()}


@router.post("/archetypes/{archetype_id}/plan", summary="Genera un ExecutionPlan especializado a partir de la entrevista adaptativa")
def plan_from_interview_endpoint(archetype_id: str, req: ArchetypePlanRequest):
    try:
        plan = RequestPlanner.plan_from_interview(
            archetype_id=archetype_id,
            interview_answers=req.interview_answers,
            project_id=req.project_id
        )
        return {"status": "ok", "plan": plan.dict()}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al generar plan para arquetipo: {ex}")


@router.post("/workflows/version", summary="Guarda una nueva versión congelada de un Workflow y su Grafo ComfyUI (Bucle de Perfeccionamiento)")
def save_workflow_version_endpoint(req: WorkflowVersionRequest):
    try:
        existing_wf = get_workflow(req.workflow_id)
        if not existing_wf:
            raise HTTPException(status_code=404, detail=f"Workflow base '{req.workflow_id}' no encontrado.")
        
        # Incrementar versión
        new_version_num = existing_wf.version + 1
        new_wf = existing_wf.copy(deep=True)
        new_wf.version = new_version_num
        new_wf.version_label = req.version_label
        if req.name:
            new_wf.name = req.name
        if req.description:
            new_wf.description = req.description
        if req.pipeline_graph:
            new_wf.pipeline_graph = req.pipeline_graph
            
        StudioRepository.save_workflow(new_wf)
        return {"status": "ok", "message": f"Versión '{req.version_label}' de {req.workflow_id} guardada con éxito.", "workflow": new_wf.dict()}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al versionar workflow: {ex}")


@router.post("/plan", summary="Transforma una petición en un Plan de Ejecución explícito")
def plan_request(req: PlanRequest):
    """Crea un ExecutionPlan estructurado resolviendo capacidades y motores por escena."""
    try:
        plan = RequestPlanner.plan_request(
            project_id=req.project_id,
            user_prompt=req.prompt,
            target_duration=req.target_duration,
            workflow_id=req.workflow_id,
            visual_strategy=req.visual_strategy,
            preferences=req.preferences
        )
        return {"status": "ok", "plan": plan.dict()}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al generar plan: {ex}")


@router.post("/execute", summary="Ejecuta un Job basado en un plan de ejecución")
def execute_plan(req: ExecuteRequest):
    """Convierte un plan en un ExecutionJob, lo ejecuta paso a paso y registra su trazabilidad."""
    try:
        plan_obj = ExecutionPlan(**req.plan)
        job = RequestPlanner.create_job_from_plan(plan_obj)
        
        executor = WorkflowExecutor()
        completed_job = executor.execute_job(job)
        StudioRepository.save_job(completed_job)

        return {"status": "ok", "job": completed_job.dict()}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar job: {ex}")


@router.get("/jobs", summary="Lista los últimos Jobs de producción ejecutados")
def list_recent_jobs(limit: int = 20):
    return {"status": "ok", "jobs": StudioRepository.list_jobs(limit=limit)}


@router.get("/jobs/{job_id}", summary="Obtiene el detalle y traza de ejecución de un Job concreto")
def get_job_detail(job_id: str):
    job = StudioRepository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return {"status": "ok", "job": job.dict()}
