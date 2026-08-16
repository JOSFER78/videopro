"""
Planificador de Peticiones (Request Planner & Normalizer) — VideoPro Studio
Transforma una petición humana, parámetros de producción o respuestas de una entrevista en un ExecutionPlan explícito.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability
from app.core.orchestration.engines import get_engines_by_capability, get_engine
from app.core.orchestration.providers import get_primary_provider
from app.core.orchestration.workflows import get_workflow, WORKFLOW_TEMPLATES, WorkflowDefinition, get_workflow_by_archetype
from app.core.orchestration.workflow_archetypes import get_archetype, ARCHETYPES_CATALOG
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
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RequestPlanner:
    """Orquestador que normaliza peticiones y resuelve el plan de ejecución óptimo."""

    @staticmethod
    def plan_request(
        project_id: str,
        user_prompt: str,
        target_duration: Any = 60,
        workflow_id: str = "DOCUMENTARY_MASTER",
        visual_strategy: VisualStrategy = VisualStrategy.HYBRID,
        preferences: Optional[Dict[str, Any]] = None
    ) -> ExecutionPlan:
        """Genera un plan de ejecución completo resolviendo capabilities, engines y providers."""
        preferences = preferences or {}
        
        # Flexibilidad posicional: si el 3er argumento fue el workflow_id como string:
        if isinstance(target_duration, str) and not target_duration.isdigit():
            workflow_id = target_duration
            target_duration = 60
        else:
            try:
                target_duration = int(target_duration)
            except (ValueError, TypeError):
                target_duration = 60

        workflow = get_workflow(workflow_id) or WORKFLOW_TEMPLATES.get("DOCUMENTARY_MASTER")

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
    def plan_from_interview(
        archetype_id: str,
        interview_answers: Dict[str, Any],
        project_id: str = "project_interview"
    ) -> ExecutionPlan:
        """
        Genera un plan de producción especializado directamente a partir de las respuestas
        de la entrevista adaptativa del arquetipo.
        """
        archetype = get_archetype(archetype_id) or ARCHETYPES_CATALOG["HISTORICAL_SCRAPING"]
        workflow = get_workflow_by_archetype(archetype.id) or get_workflow(archetype.id) or WORKFLOW_TEMPLATES["DOCUMENTARY_MASTER"]

        # Extraer elementos de la entrevista según el arquetipo
        scenes_data: List[Dict[str, Any]] = []

        if archetype.id == "PIXAR_3D_ANIMATION":
            char_name = interview_answers.get("character_name", "Protagonista 3D")
            conflict = interview_answers.get("story_conflict", "Gran aventura")
            environment = interview_answers.get("visual_environment", "Mundo de cuento")
            scenes_data = [
                {"id": "scene_1", "prompt": f"Hollywood Pixar 3D Master: Plano general cinemático de {char_name} en {environment}, iluminación volumétrica cálida, texturas ricas y lentes anamórficas 35mm", "shot_type": "wide_establishing", "engine": "nanobanana", "duration": 4.0},
                {"id": "scene_2", "prompt": f"Hollywood Pixar 3D: Primer plano de alta expresividad emocional de {char_name} afrontando el conflicto: {conflict}, profundidad de campo bokeh T1.8", "shot_type": "character_close_up", "engine": "flux_video", "duration": 5.0},
                {"id": "scene_3", "prompt": f"Hollywood Pixar 3D: Secuencia de acción y superación dinámica con {char_name}, travelling de cámara fluido a 60 fps y efectos de partículas mágicas", "shot_type": "action_tracking", "engine": "flux_video", "duration": 4.5},
                {"id": "scene_4", "prompt": f"Hollywood Pixar 3D: Gran plano final emotivo y triunfal de {char_name} en {environment}, luz dorada de atardecer, etalonaje cinematográfico Disney/Pixar", "shot_type": "medium", "engine": "nanobanana", "duration": 4.0}
            ]

        elif archetype.id == "HISTORICAL_SCRAPING":
            subject = interview_answers.get("historical_subject", "Hecho histórico")
            scenes_data = [
                {"id": "scene_1", "prompt": f"Investigación Documental Master: Primer plano macro de documentos de archivo, grabados antiguos y mapas táctiles 2.5D sobre {subject}, textura papel fotográfico vintage", "shot_type": "macro_detail", "engine": "stock_db", "duration": 4.0},
                {"id": "scene_2", "prompt": f"Fotografía histórica auténtica restaurada en 4K Ultra-HD con efecto Ken Burns cinemático y profundidad multi-capa sobre {subject}", "shot_type": "wide_establishing", "engine": "nanobanana", "duration": 5.0},
                {"id": "scene_3", "prompt": f"Recreación cinematográfica 4K estilo película de época 35mm Kodak 5219 del momento clave de {subject}, humo, atmósfera y luz lateral ARRI Alexa", "shot_type": "action_tracking", "engine": "google_flow", "duration": 4.5},
                {"id": "scene_4", "prompt": f"Plano de síntesis histórica y legado monumental en 4K HDR, transición suave de archivo a época actual sobre {subject}", "shot_type": "medium", "engine": "stock_db", "duration": 4.0}
            ]

        elif archetype.id == "CITY_ROUTES_BEATS":
            spots = interview_answers.get("city_and_spots", "Ruta Urbana")
            beat_style = interview_answers.get("music_beat_style", "Electronic Synthwave")
            scenes_data = [
                {"id": "scene_1", "prompt": f"Hollywood Drone 8K: Vuelo orbital suave y continuo sobre {spots} con luz de amanecer dorado, gradación de color cinematográfica y arquitectura imponente", "shot_type": "drone_aerial", "engine": "google_flow", "duration": 4.0},
                {"id": "scene_2", "prompt": f"Travelling cinemático a ras de suelo con lente gran angular 24mm capturando el pulso urbano y vida moderna en {spots}", "shot_type": "action_tracking", "engine": "google_flow", "duration": 4.0},
                {"id": "scene_3", "prompt": f"Detalle arquitectónico de alta fidelidad 4K y texturas urbanas en {spots}, corte rítmico a tempo {beat_style}", "shot_type": "medium", "engine": "stock_db", "duration": 3.5},
                {"id": "scene_4", "prompt": f"Plano secuencia aéreo nocturno de {spots} con estelas de luz, neones vibrantes y atmósfera cinematográfica Cyber-City", "shot_type": "drone_aerial", "engine": "google_flow", "duration": 4.0}
            ]

        elif archetype.id == "VIRAL_SHORTS_HOOK":
            hook = interview_answers.get("hook_theme", "Curiosidad Viral")
            scenes_data = [
                {"id": "scene_1", "prompt": f"Gancho visual hiper-cinemático de 2s sobre {hook}, primer plano de impacto con iluminación dramática y movimiento rápido de cámara", "shot_type": "character_close_up", "engine": "flux_video", "duration": 2.0},
                {"id": "scene_2", "prompt": f"Montaje dinámico de alta retención revelando datos clave de {hook}, efectos de zoom óptico rápido y cortes rítmicos", "shot_type": "medium", "engine": "stock_db", "duration": 2.2},
                {"id": "scene_3", "prompt": f"Infografía animada de impacto visual 4K con telemetría HUD y micro-animaciones aceleradas", "shot_type": "action_tracking", "engine": "nanobanana", "duration": 2.5},
                {"id": "scene_4", "prompt": f"Plano de cierre con alta energía visual y llamada a la acción en pantalla", "shot_type": "medium", "engine": "flux_video", "duration": 2.0}
            ]

        else: # DEEP_EXPLAINER_ESSAY
            thesis = interview_answers.get("essay_thesis", "Tesis del ensayo")
            scenes_data = [
                {"id": "scene_1", "prompt": f"Hollywood Videoessay: Planteamiento visual cinemático del dilema central: {thesis}, plano general sobrio con iluminación claroscuro", "shot_type": "wide_establishing", "engine": "stock_db", "duration": 5.0},
                {"id": "scene_2", "prompt": f"Infografía gráfica de datos en movimiento 4K estilo Vox/Bloomberg, diseño minimalista sobre fondo dark glassmorphism", "shot_type": "macro_detail", "engine": "nanobanana", "duration": 6.0},
                {"id": "scene_3", "prompt": f"Análisis visual de relaciones de poder y factores estructurales, planos de archivo y recreación cinemática", "shot_type": "medium", "engine": "google_flow", "duration": 5.0},
                {"id": "scene_4", "prompt": f"Síntesis visual reflexiva y prospectiva de futuro en 4K, composición equilibrada y planos abiertos", "shot_type": "wide_establishing", "engine": "stock_db", "duration": 5.0}
            ]

        scene_plans = SceneEngineRouter.route_scenes(scenes_data, strategy=archetype.visual_strategy)

        # Generar PlannedSteps a partir del workflow
        planned_steps: List[PlannedStep] = []
        for node in workflow.nodes:
            cap = node.capability
            chosen_engine_id = node.engine_id or get_engines_by_capability(cap)[0].id
            engine_spec = get_engine(chosen_engine_id)
            prov_spec = get_primary_provider(chosen_engine_id)
            prov_id = prov_spec.id if prov_spec else "local_vps"

            step = PlannedStep(
                step_id=node.id,
                capability=cap,
                engine_id=chosen_engine_id,
                provider_id=prov_id,
                fallback_engines=engine_spec.fallbacks if engine_spec else [],
                description=f"Paso [{node.title}] para arquetipo {archetype.name}",
                estimated_duration_seconds=3.0,
                estimated_cost=engine_spec.estimated_cost_per_scene if engine_spec else 0.0
            )
            planned_steps.append(step)

        total_cost = sum(s.estimated_cost for s in planned_steps)
        total_duration = sum(s.estimated_duration_seconds for s in planned_steps) + sum(sc.duration_seconds for sc in scene_plans)

        return ExecutionPlan(
            project_id=project_id,
            workflow_id=workflow.id,
            workflow_version=workflow.version,
            visual_strategy=archetype.visual_strategy,
            steps=planned_steps,
            scenes=scene_plans,
            estimated_total_cost=round(total_cost, 4),
            estimated_total_duration_seconds=round(total_duration, 2),
            metadata={
                "archetype_id": archetype.id,
                "archetype_name": archetype.name,
                "interview_answers": interview_answers
            }
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
            metadata={
                "scenes_count": len(plan.scenes),
                "visual_strategy": plan.visual_strategy,
                "archetype_id": plan.metadata.get("archetype_id")
            }
        )
