"""
app/api/workflows.py
Controlador y API REST Central de Workflows de Producción — VideoPro Studio & Hermes.

Expone endpoints para:
1. GET  /api/v1/workflows         -> Listar todos los workflows disponibles y sus versiones activas.
2. GET  /api/v1/workflows/{id}    -> Consultar detalles, parámetros, topología y mejoras recientes.
3. POST /api/v1/workflows/{id}/run -> Lanzar ejecución headless basada en el contrato de misión.
4. POST /api/v1/workflows/{id}/save -> Guardar ajustes personalizados o nuevas variantes desde la interfaz.
"""

import os
import json
import uuid
import threading
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body, Query, status
from pydantic import BaseModel, Field

from app.core.orchestration.workflows import (
    get_all_workflows, get_workflow, get_workflow_by_archetype,
    WorkflowDefinition, WorkflowNode, WorkflowConnection, WORKFLOW_TEMPLATES
)
from app.core.orchestration.workflow_archetypes import (
    get_all_archetypes, get_archetype, ARCHETYPES_CATALOG, WorkflowArchetype
)
from app.core.orchestration.videopro_system_registry import SYSTEM_WORKFLOWS, SYSTEM_NODES
from app.core.orchestration.capabilities import Capability, get_all_capabilities
from app.core.orchestration.engines import get_all_engines
from app.core.orchestration.scene_router import VisualStrategy
from app.core.orchestration.planner import RequestPlanner, ExecutionPlan
from app.core.orchestration.executor import WorkflowExecutor
from app.core.orchestration.job import ExecutionJob, JobStatus, JobStepStatus
from app.core.orchestration.repository import StudioRepository
from app.services.hermes_mission_dispatcher import HermesMissionDispatcher, HermesMissionStatus
from app.services.learning_memory_engine import LearningMemoryEngine

logger = logging.getLogger("videopro.api.workflows")

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

# Instancias auxiliares de servicios
mission_dispatcher = HermesMissionDispatcher()
learning_engine = LearningMemoryEngine()


def _dump_model(obj: Any) -> Any:
    """Helper para serialización limpia compatible con Pydantic v1 y v2."""
    if obj is None:
        return None
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return obj


def _copy_model(obj: Any, deep: bool = True) -> Any:
    """Helper para clonar modelos Pydantic compatible con v1 y v2."""
    if hasattr(obj, "model_copy"):
        return obj.model_copy(deep=deep)
    if hasattr(obj, "copy"):
        return obj.copy(deep=deep)
    return obj


# ============================================================================
# MODELOS DE PETICIÓN Y RESPUESTA (SCHEMAS)
# ============================================================================

class WorkflowRunRequest(BaseModel):
    """Contrato de misión para lanzamiento de ejecución headless."""
    project_id: Optional[str] = Field(None, description="ID único del proyecto o slug.")
    title: Optional[str] = Field(None, description="Título descriptivo del vídeo a producir.")
    topic: Optional[str] = Field(None, description="Tema central, premisa o concepto narrativo.")
    user_prompt: Optional[str] = Field(None, description="Prompt alternativo o extendido del usuario.")
    interview_answers: Dict[str, Any] = Field(default_factory=dict, description="Respuestas estructuradas a la entrevista del arquetipo.")
    target_channel: Optional[str] = Field(None, description="Canal de YouTube o nicho de monetización objetivo.")
    duration_target_sec: float = Field(180.0, description="Duración objetivo del vídeo en segundos.")
    visual_strategy: Optional[VisualStrategy] = Field(VisualStrategy.HYBRID, description="Estrategia de selección visual (hybrid, automatic, pure_flow, pure_flux).")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Ajustes opcionales (voz, aspect_ratio, bgm, resolucion).")
    async_execution: bool = Field(True, description="Si es True, ejecuta en segundo plano headless desacoplado.")


class WorkflowSaveRequest(BaseModel):
    """Petición para guardar versiones personalizadas o nuevas variantes de un workflow."""
    name: Optional[str] = Field(None, description="Nombre descriptivo del workflow o variante.")
    description: Optional[str] = Field(None, description="Descripción del pipeline y su propósito.")
    version_label: Optional[str] = Field(None, description="Etiqueta de versión (ej: 'v2.1', 'v1.0-custom').")
    nodes: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de nodos con posiciones y parámetros.")
    connections: Optional[List[Dict[str, Any]]] = Field(None, description="Lista de conexiones entre sockets.")
    pipeline_graph: Optional[Dict[str, Any]] = Field(None, description="Grafo ComfyUI completo si aplica.")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Ajustes globales de parámetros.")
    policies: Optional[Dict[str, Any]] = Field(None, description="Políticas de reintento y auto-fallback.")
    fallbacks: Optional[Dict[str, List[str]]] = Field(None, description="Mapeo de fallbacks por motor/nodo.")
    is_new_variant: bool = Field(False, description="Si es True, guarda como nueva variante independiente.")
    new_variant_id: Optional[str] = Field(None, description="ID único para la nueva variante.")


# ============================================================================
# FUNCIONES AUXILIARES DE RESOLUCIÓN
# ============================================================================

def _find_workflow_or_archetype(workflow_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca de forma unificada un workflow por ID en:
    1. WORKFLOW_TEMPLATES (Catálogo de grafos oficiales)
    2. ARCHETYPES_CATALOG (Arquetipos de producción y narración)
    3. SYSTEM_WORKFLOWS (Ontología Nivel 4)
    4. Archivos locales en storage/workflows/
    """
    # 1. WORKFLOW_TEMPLATES
    wf = get_workflow(workflow_id)
    arch = None
    
    if wf:
        arch_id = wf.archetype_id or workflow_id
        arch = get_archetype(arch_id)
        return {"workflow": wf, "archetype": arch, "source": "WORKFLOW_TEMPLATES"}

    # 2. ARCHETYPES_CATALOG
    arch = get_archetype(workflow_id)
    if arch:
        wf = get_workflow_by_archetype(arch.id) or get_workflow(arch.id)
        if not wf:
            # Construir WorkflowDefinition sintético a partir del arquetipo
            wf = WorkflowDefinition(
                id=arch.id,
                name=arch.name,
                description=arch.description,
                version=1,
                version_label=f"v{arch.version}",
                archetype_id=arch.id,
                pipeline_graph=arch.pipeline_graph
            )
        return {"workflow": wf, "archetype": arch, "source": "ARCHETYPES_CATALOG"}

    # 3. SYSTEM_WORKFLOWS
    if workflow_id in SYSTEM_WORKFLOWS:
        sys_wf = SYSTEM_WORKFLOWS[workflow_id]
        wf = WorkflowDefinition(
            id=sys_wf.id,
            name=sys_wf.name,
            description=sys_wf.description,
            version=1,
            version_label="v1.0",
            archetype_id=workflow_id,
            pipeline_graph={"nodes": [{"id": nid, "title": nid} for nid in sys_wf.ordered_nodes]}
        )
        return {"workflow": wf, "archetype": None, "source": "SYSTEM_WORKFLOWS"}

    # 4. Storage local en disco
    base_dir = Path(__file__).resolve().parent.parent.parent
    storage_wf_dir = base_dir / "storage" / "workflows"
    if storage_wf_dir.is_dir():
        for f in storage_wf_dir.glob(f"{workflow_id}*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    wf = WorkflowDefinition(**data)
                    arch = get_archetype(wf.archetype_id) if wf.archetype_id else None
                    return {"workflow": wf, "archetype": arch, "source": "LOCAL_STORAGE"}
            except Exception:
                pass

    return None


def _get_recent_improvements(workflow_id: str, archetype_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recupera lecciones aprendidas y reglas de calidad aplicables a este workflow."""
    try:
        lessons = learning_engine.get_all_lessons(workflow_id=workflow_id)
        if not lessons and archetype_id:
            lessons = learning_engine.get_all_lessons(workflow_id=archetype_id)
        if not lessons:
            lessons = learning_engine.get_all_lessons()
        
        return [
            {
                "id": l.id,
                "title": l.title,
                "category": l.category.value if hasattr(l.category, "value") else str(l.category),
                "severity": l.severity.value if hasattr(l.severity, "value") else str(l.severity),
                "golden_rule": l.golden_rule,
                "what_failed": l.what_failed,
                "success_rating": l.success_rating,
                "applied_count": l.applied_count
            }
            for l in lessons[:6]
        ]
    except Exception as ex:
        logger.warning(f"Aviso al obtener mejoras recientes para {workflow_id}: {ex}")
        return []


def _execute_headless_mission_worker(
    mission_id: str,
    job: ExecutionJob,
    workflow_id: str,
    title: str
):
    """
    Ejecutor en hilo secundario (headless) para orquestación desacoplada:
    1. Registra el avance paso a paso en la Mente de Hermes (thinking_logs).
    2. Actualiza el estado de los 7 Nodos de Producción.
    3. Ejecuta cada paso a través de WorkflowExecutor.
    4. Persiste el Job y la Misión en almacenamiento local y Firestore.
    """
    logger.info(f"🚀 [Headless Runner] Iniciando misión {mission_id} ({title})")
    
    try:
        # Paso 1: Razonamiento inicial CoT
        mission_dispatcher.append_thinking_log(
            mission_id=mission_id,
            log_message=f"🤖 [Hermes Headless] Evaluando contrato de misión para '{title}'. Workflow: {workflow_id}. Total pasos calculados: {len(job.steps)}.",
            new_status=HermesMissionStatus.REASONING,
            progress_percent=10.0
        )
        mission_dispatcher.update_node_progress(mission_id, "node_01_investigacion_y_storyboard", "IN_PROGRESS", 40)

        # Paso 2: Ejecución de pasos del Job
        executor = WorkflowExecutor()
        
        # Simular avance estructurado en los 7 nodos para trazabilidad en vivo
        node_ids = [
            "node_01_investigacion_y_storyboard",
            "node_02_audio_first_y_foley",
            "node_03_generacion_activos_vox",
            "node_04_composicion_3d_parallax",
            "node_05_subtitulos_y_hud",
            "node_06_masterizacion_ebu_r128",
            "node_07_qa_contact_sheet_sync"
        ]

        total_nodes = len(node_ids)
        for idx, nid in enumerate(node_ids, 1):
            pct = 15.0 + (idx / total_nodes) * 75.0
            mission_dispatcher.append_thinking_log(
                mission_id=mission_id,
                log_message=f"⚙️ [Hermes CoT] Ejecutando etapa {idx}/{total_nodes}: {nid} con motores óptimos.",
                new_status=HermesMissionStatus.PRODUCING_ASSETS if idx <= 3 else HermesMissionStatus.COMPOSING,
                progress_percent=pct
            )
            mission_dispatcher.update_node_progress(mission_id, nid, "IN_PROGRESS", 80)

        # Ejecutar el job completo
        completed_job = executor.execute_job(job)
        StudioRepository.save_job(completed_job)

        # Finalizar todos los nodos
        for nid in node_ids:
            mission_dispatcher.update_node_progress(mission_id, nid, "COMPLETED", 100)

        # Registrar éxito y sincronizar artefactos
        mission_dispatcher.append_thinking_log(
            mission_id=mission_id,
            log_message=f"✅ [Hermes Headless] ¡Misión completada con éxito! Job ID: {completed_job.job_id}. Vídeo master renderizado.",
            new_status=HermesMissionStatus.COMPLETED,
            progress_percent=100.0
        )
        logger.info(f"✨ [Headless Runner] Misión {mission_id} completada exitosamente.")

    except Exception as ex:
        logger.error(f"❌ [Headless Runner] Error en misión {mission_id}: {ex}")
        mission_dispatcher.append_thinking_log(
            mission_id=mission_id,
            log_message=f"❌ [Hermes Error] Fallo durante la ejecución headless: {str(ex)}",
            new_status=HermesMissionStatus.FAILED,
            progress_percent=100.0
        )


# ============================================================================
# ENDPOINTS REST DE WORKFLOWS
# ============================================================================

@router.get("", summary="Listar todos los workflows disponibles y sus versiones activas")
def list_all_workflows_endpoint(
    category: Optional[str] = Query(None, description="Filtrar por categoría (documentary, storytelling, educational, social_media, travel_fpv_action)"),
    aspect_ratio: Optional[str] = Query(None, description="Filtrar por aspecto (16:9, 9:16, 1:1)")
):
    """
    Retorna la lista completa de workflows oficiales, arquetipos de producción y variantes guardadas,
    incluyendo sus versiones activas, capacidades requeridas y mejoras recientes de experiencia.
    """
    workflows = get_all_workflows()
    results = []
    
    for wf in workflows:
        arch = get_archetype(wf.archetype_id) if wf.archetype_id else get_archetype(wf.id)
        cat = arch.category if arch else "general"
        asp = arch.default_aspect_ratio if arch else "16:9"
        strat = arch.visual_strategy.value if arch and hasattr(arch.visual_strategy, "value") else "hybrid"
        target_aud = arch.target_audience if arch else "Audiencias generales de vídeo digital"
        
        # Filtros opcionales
        if category and category.lower() != cat.lower() and category.upper() != "TODAS":
            continue
        if aspect_ratio and aspect_ratio != asp and aspect_ratio.upper() != "TODOS":
            continue

        improvements = _get_recent_improvements(wf.id, wf.archetype_id)

        results.append({
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "version": wf.version,
            "version_label": wf.version_label,
            "archetype_id": wf.archetype_id,
            "category": cat,
            "target_audience": target_aud,
            "default_aspect_ratio": asp,
            "visual_strategy": strat,
            "required_capabilities": [c.value if hasattr(c, "value") else str(c) for c in wf.required_capabilities],
            "nodes_count": len(wf.nodes) if wf.nodes else len(wf.pipeline_graph.get("nodes", [])),
            "connections_count": len(wf.connections) if wf.connections else len(wf.pipeline_graph.get("connections", [])),
            "recent_improvements": improvements,
            "is_active": True,
            "status": "ACTIVE"
        })

    return {
        "status": "ok",
        "total": len(results),
        "workflows": results
    }


@router.get("/{workflow_id}", summary="Consultar detalles, parámetros y mejoras recientes de un workflow")
def get_workflow_detail_endpoint(workflow_id: str):
    """
    Consulta los detalles exhaustivos de un workflow:
    - Definición formal de nodos y conexiones
    - Parámetros por nodo y variables de configuración
    - Esquema de entrevista adaptativa del arquetipo
    - Reglas de aprendizaje continuo y mejoras recientes aplicadas
    - Historial de versiones registradas
    """
    resolved = _find_workflow_or_archetype(workflow_id)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow o Arquetipo '{workflow_id}' no encontrado en el sistema."
        )

    wf: WorkflowDefinition = resolved["workflow"]
    arch: Optional[WorkflowArchetype] = resolved.get("archetype")
    
    # 1. Consolidar parámetros de los nodos
    parameters_summary = {}
    if wf.nodes:
        for n in wf.nodes:
            parameters_summary[n.id] = {
                "title": n.title,
                "capability": n.capability.value if hasattr(n.capability, "value") else str(n.capability),
                "engine_id": n.engine_id,
                "parameters": n.parameters
            }
    elif wf.pipeline_graph and "nodes" in wf.pipeline_graph:
        for n in wf.pipeline_graph["nodes"]:
            nid = n.get("id", "node")
            parameters_summary[nid] = {
                "title": n.get("title", nid),
                "parameters": n.get("parameters", [])
            }

    # 2. Entrevista del arquetipo si existe
    interview_schema = []
    if arch and arch.interview_schema:
        interview_schema = [_dump_model(q) for q in arch.interview_schema]

    # 3. Mejoras recientes de aprendizaje
    improvements = _get_recent_improvements(wf.id, wf.archetype_id)

    # 4. Historial de versiones locales
    base_dir = Path(__file__).resolve().parent.parent.parent
    storage_wf_dir = base_dir / "storage" / "workflows"
    versions = [{"version": wf.version, "version_label": wf.version_label, "source": resolved["source"]}]
    
    if storage_wf_dir.is_dir():
        for f in storage_wf_dir.glob(f"{wf.id}_v*.json"):
            try:
                v_num = int(f.stem.split("_v")[-1])
                if v_num != wf.version:
                    versions.append({"version": v_num, "version_label": f"v{v_num}.0", "file": f.name})
            except Exception:
                pass

    return {
        "status": "ok",
        "workflow": {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "version": wf.version,
            "version_label": wf.version_label,
            "archetype_id": wf.archetype_id,
            "required_capabilities": [c.value if hasattr(c, "value") else str(c) for c in wf.required_capabilities],
            "nodes": [_dump_model(n) for n in wf.nodes],
            "connections": [_dump_model(c) for c in wf.connections],
            "pipeline_graph": wf.pipeline_graph,
            "inputs": wf.inputs,
            "outputs": wf.outputs,
            "policies": wf.policies,
            "fallbacks": wf.fallbacks
        },
        "archetype": _dump_model(arch),
        "parameters": parameters_summary,
        "interview_schema": interview_schema,
        "recent_improvements": improvements,
        "versions": versions
    }


@router.post("/{workflow_id}/run", summary="Lanzar ejecución headless basada en el contrato de misión del workflow")
def run_workflow_headless_endpoint(
    workflow_id: str,
    req: WorkflowRunRequest = Body(...),
    background_tasks: BackgroundTasks = None
):
    """
    Lanza una ejecución headless y autónoma del workflow:
    1. Resuelve la definición del workflow y arquetipo.
    2. Construye el contrato de misión declarativo con HermesMissionDispatcher.
    3. Compila el ExecutionPlan óptimo y el ExecutionJob formal.
    4. Despacha la ejecución en segundo plano (headless) manteniendo sincronización con Firestore y local.
    """
    resolved = _find_workflow_or_archetype(workflow_id)
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow o Arquetipo '{workflow_id}' no encontrado para ejecución."
        )

    wf: WorkflowDefinition = resolved["workflow"]
    arch: Optional[WorkflowArchetype] = resolved.get("archetype")

    # Normalizar títulos y premisas
    title = req.title or req.topic or req.user_prompt or f"{wf.name} — Producción Headless"
    topic = req.topic or req.user_prompt or req.title or "Producción cinematográfica autónoma"
    project_id = req.project_id or f"proj_{uuid.uuid4().hex[:8]}"

    # 1. Crear el contrato de misión en HermesMissionDispatcher
    mission = mission_dispatcher.create_mission(
        workflow_id=wf.id,
        title=title,
        topic=topic,
        interview_answers=req.interview_answers,
        target_channel=req.target_channel or (arch.target_audience if arch else "YouTube Studio"),
        duration_target_sec=req.duration_target_sec
    )
    mission_id = mission["mission_id"]

    # 2. Generar el ExecutionPlan estructurado
    try:
        if req.interview_answers and arch:
            plan = RequestPlanner.plan_from_interview(
                archetype_id=arch.id,
                interview_answers=req.interview_answers,
                project_id=project_id
            )
        else:
            plan = RequestPlanner.plan_request(
                project_id=project_id,
                user_prompt=topic,
                target_duration=int(req.duration_target_sec),
                workflow_id=wf.id,
                visual_strategy=req.visual_strategy or (arch.visual_strategy if arch else VisualStrategy.HYBRID),
                preferences=req.preferences
            )
        
        # 3. Crear el Job formal
        job = RequestPlanner.create_job_from_plan(plan)
        StudioRepository.save_job(job)

    except Exception as ex:
        logger.error(f"Error al planificar ejecución de workflow {workflow_id}: {ex}")
        mission_dispatcher.append_thinking_log(
            mission_id=mission_id,
            log_message=f"❌ Error durante la planificación: {str(ex)}",
            new_status=HermesMissionStatus.FAILED
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo al generar el plan de ejecución: {ex}"
        )

    # 4. Despachar ejecución headless (Asíncrona por defecto o síncrona)
    if req.async_execution:
        worker_thread = threading.Thread(
            target=_execute_headless_mission_worker,
            args=(mission_id, job, wf.id, title),
            daemon=True
        )
        worker_thread.start()
        
        return {
            "status": "dispatched",
            "message": f"Misión headless lanzada exitosamente con el workflow '{wf.name}'.",
            "mission_id": mission_id,
            "job_id": job.job_id,
            "workflow_id": wf.id,
            "execution_mode": "headless_async",
            "plan": _dump_model(plan),
            "telemetry_url": f"/api/v1/studio/jobs/{job.job_id}"
        }
    else:
        # Ejecución síncrona
        _execute_headless_mission_worker(mission_id, job, wf.id, title)
        updated_mission = mission_dispatcher.get_mission(mission_id)
        completed_job = StudioRepository.get_job(job.job_id)
        
        return {
            "status": "completed",
            "message": f"Misión completada de forma síncrona.",
            "mission_id": mission_id,
            "job_id": job.job_id,
            "workflow_id": wf.id,
            "mission": updated_mission,
            "job": _dump_model(completed_job)
        }


@router.post("/{workflow_id}/save", summary="Guardar ajustes personalizados o nuevas variantes desde la interfaz")
def save_workflow_variant_endpoint(
    workflow_id: str,
    req: WorkflowSaveRequest = Body(...)
):
    """
    Guarda ajustes personalizados, nuevos parámetros o registra una nueva variante del workflow.
    - Si `is_new_variant` es True, crea una nueva entrada de workflow independiente.
    - Si es False, incrementa la versión congelada del workflow existente y la persiste en disco y Firestore.
    """
    is_variant = req.is_new_variant or bool(req.new_variant_id)
    resolved = _find_workflow_or_archetype(workflow_id)
    if not resolved and not is_variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow base '{workflow_id}' no encontrado para guardar ajustes."
        )

    base_wf = resolved["workflow"] if resolved else None

    try:
        if is_variant:
            # Crear nueva variante independiente
            new_id = req.new_variant_id or f"{workflow_id}_custom_{uuid.uuid4().hex[:4]}".upper()
            new_name = req.name or (f"{base_wf.name} (Variante Personalizada)" if base_wf else new_id)
            new_desc = req.description or (base_wf.description if base_wf else "Variante personalizada de workflow.")
            
            new_wf = WorkflowDefinition(
                id=new_id,
                name=new_name,
                description=new_desc,
                version=1,
                version_label=req.version_label or "v1.0-custom",
                archetype_id=base_wf.archetype_id if base_wf else None,
                required_capabilities=base_wf.required_capabilities if base_wf else [],
                nodes=[WorkflowNode(**n) for n in req.nodes] if req.nodes else (base_wf.nodes if base_wf else []),
                connections=[WorkflowConnection(**c) for c in req.connections] if req.connections else (base_wf.connections if base_wf else []),
                pipeline_graph=req.pipeline_graph or (base_wf.pipeline_graph if base_wf else {}),
                policies=req.policies or (base_wf.policies if base_wf else {"retry_limit": 2, "auto_fallback": True}),
                fallbacks=req.fallbacks or (base_wf.fallbacks if base_wf else {})
            )
            
            StudioRepository.save_workflow(new_wf)
            WORKFLOW_TEMPLATES[new_wf.id] = new_wf
            
            return {
                "status": "ok",
                "message": f"Nueva variante '{new_wf.id}' ({new_wf.name}) creada y guardada con éxito.",
                "workflow": _dump_model(new_wf)
            }
        else:
            # Actualizar versión del workflow existente
            new_version_num = (base_wf.version or 1) + 1
            new_version_label = req.version_label or f"v{new_version_num}.0"
            
            updated_wf = _copy_model(base_wf, deep=True)
            updated_wf.version = new_version_num
            updated_wf.version_label = new_version_label
            
            if req.name:
                updated_wf.name = req.name
            if req.description:
                updated_wf.description = req.description
            if req.nodes:
                updated_wf.nodes = [WorkflowNode(**n) for n in req.nodes]
            if req.connections:
                updated_wf.connections = [WorkflowConnection(**c) for c in req.connections]
            if req.pipeline_graph:
                updated_wf.pipeline_graph = req.pipeline_graph
            if req.policies:
                updated_wf.policies = req.policies
            if req.fallbacks:
                updated_wf.fallbacks = req.fallbacks

            StudioRepository.save_workflow(updated_wf)
            WORKFLOW_TEMPLATES[updated_wf.id] = updated_wf

            return {
                "status": "ok",
                "message": f"Workflow '{updated_wf.id}' actualizado a versión {updated_wf.version_label}.",
                "workflow": _dump_model(updated_wf)
            }

    except Exception as ex:
        logger.error(f"Error al guardar workflow/variante {workflow_id}: {ex}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al persistir cambios del workflow: {ex}"
        )
