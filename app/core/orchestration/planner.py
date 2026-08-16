"""
Planificador de Peticiones (Request Planner & Normalizer) — VideoPro Studio
Transforma una petición humana o parámetros de producción en un ExecutionPlan explícito y auditable.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability
from app.core.orchestration.engines import get_engines_by_capability, get_engine
from app.core.orchestration.providers import get_primary_provider
from app.core.orchestration.workflows import get_workflow, WORKFLOW_TEMPLATES, WorkflowDefinition
from app.core.orchestration.scene_router import SceneEngineRouter, VisualStrategy, ScenePlan
from app.core.orchestration.job import ExecutionJob, JobStep, JobStatus


class PlannedStep(BaseModel):
    step_id: str
    capability: Capability
    engine_id: str
    provider_id: str
    fallback_engines: List[str] = Field(default_factory=list)
    description: str
    estimated_duration_seconds: float = 2.0
    estimated_cost: float = 0.0


class ExecutionPlan(BaseModel):
    project_id: str
    workflow_id: str
    workflow_version: int
    visual_strategy: VisualStrategy
    steps: List[PlannedStep]
    scenes: List[ScenePlan] = Field(default_factory=list)
    estimated_total_cost: float = 0.0
    estimated_total_duration_seconds: float = 0.0


class RequestPlanner:
    """Orquestador que normaliza peticiones y resuelve el plan de ejecución óptimo."""

    @staticmethod
    def plan_request(
        project_id: str,
        user_prompt: str,
        target_duration: int = 60,
        workflow_id: str = "DOCUMENTARY_MASTER",
        visual_strategy: VisualStrategy = VisualStrategy.HYBRID,
        preferences: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """Genera un plan de ejecución completo resolviendo capabilities, engines y providers."""
        preferences = preferences or {}
        workflow = get_workflow(workflow_id) or WORKFLOW_TEMPLATES["DOCUMENTARY_MASTER"]

        planned_steps: List[PlannedStep] = []

        # 1. Resolver motor por cada capacidad requerida por el workflow
        for node in workflow.nodes:
            cap = node.capability
            
            # Si el nodo ya tiene un engine fijado explícitamente en el workflow:
            if node.engine_id:
                chosen_engine_id = node.engine_id
            else:
                # Resolver el mejor motor disponible para esa capacidad
                available_engines = get_engines_by_capability(cap)
                chosen_engine_id = available_engines[0].id if available_engines else "ffmpeg"

            engine_spec = get_engine(chosen_engine_id)
            fallbacks = engine_spec.fallbacks if engine_spec else []

            # Resolver proveedor primario
            prov_spec = get_primary_provider(chosen_engine_id)
            prov_id = prov_spec.id if prov_spec else "local_vps"

            step = PlannedStep(
                step_id=node.id,
                capability=cap,
                engine_id=chosen_engine_id,
                provider_id=prov_id,
                fallback_engines=fallbacks,
                description=f"Ejecución de {node.title} con motor {chosen_engine_id} ({prov_id})",
                estimated_duration_seconds=3.0,
                estimated_cost=engine_spec.estimated_cost_per_scene if engine_spec else 0.0
            )
            planned_steps.append(step)

        # 2. Planificar escenas iniciales de ejemplo o derivadas
        num_scenes = max(3, target_duration // 5)
        initial_scenes = [
            {"id": f"scene_{i+1}", "prompt": f"Plano {i+1} para {user_prompt}", "duration": 4.0}
            for i in range(num_scenes)
        ]
        scene_plans = SceneEngineRouter.route_scenes(initial_scenes, strategy=visual_strategy)

        total_cost = sum(s.estimated_cost for s in planned_steps)
        total_duration = sum(s.estimated_duration_seconds for s in planned_steps) + (len(scene_plans) * 4.0)

        return ExecutionPlan(
            project_id=project_id,
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            visual_strategy=visual_strategy,
            steps=planned_steps,
            scenes=scene_plans,
            estimated_total_cost=round(total_cost, 4),
            estimated_total_duration_seconds=round(total_duration, 2)
        )

    @staticmethod
    def create_job_from_plan(plan: ExecutionPlan) -> ExecutionJob:
        """Instancia un ExecutionJob auditable listo para el ejecutor a partir de un ExecutionPlan."""
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        job_steps: List[JobStep] = []
        for p_step in plan.steps:
            j_step = JobStep(
                step_id=p_step.step_id,
                name=p_step.description,
                capability=p_step.capability,
                engine_id=p_step.engine_id,
                provider_id=p_step.provider_id,
                input_payload={"project_id": plan.project_id}
            )
            job_steps.append(j_step)

        return ExecutionJob(
            job_id=job_id,
            project_id=plan.project_id,
            workflow_id=plan.workflow_id,
            workflow_version=plan.workflow_version,
            status=JobStatus.QUEUED,
            steps=job_steps,
            metadata={"scenes_count": len(plan.scenes), "visual_strategy": plan.visual_strategy}
        )
