"""
Ejecutor Orquestador de Workflows con Reintentos y Fallback Automático — VideoPro Studio
Garantiza que la ejecución de un Job avance paso a paso de forma auditable, aplicando fallbacks transparentes.
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.orchestration.job import ExecutionJob, JobStep, JobStatus, JobStepStatus
from app.core.orchestration.engines import get_engine
from app.core.orchestration.providers import get_primary_provider
from app.core.orchestration.adapters.registry import AdapterRegistry

logger = logging.getLogger("videopro.orchestration.executor")


class WorkflowExecutor:
    """Motor de ejecución secuencial y concurrente de Jobs de producción."""

    def __init__(self, max_retries_per_step: int = 2):
        self.max_retries_per_step = max_retries_per_step

    @classmethod
    def execute_job_sync(cls, job: ExecutionJob, context: Optional[Dict[str, Any]] = None, max_retries: int = 2) -> ExecutionJob:
        """Ejecuta un job sincrónicamente usando una instancia de WorkflowExecutor."""
        executor = cls(max_retries_per_step=max_retries)
        return executor.execute_job(job, context=context)

    def execute_job(self, job: ExecutionJob, context: Optional[Dict[str, Any]] = None) -> ExecutionJob:
        """Ejecuta todos los pasos de un Job, manejando fallbacks y recopilando artefactos."""
        context = context or {}
        context["job_id"] = job.job_id
        context["project_id"] = job.project_id

        job.status = JobStatus.RUNNING
        job.updated_at = datetime.now().isoformat()
        logger.info(f"Iniciando ejecución de Job '{job.job_id}' (Workflow: {job.workflow_id} v{job.workflow_version})...")

        for step in job.steps:
            step_success = self._execute_step_with_fallbacks(step, context)
            if not step_success:
                job.status = JobStatus.FAILED
                job.error_summary = f"Fallo irrecuperable en el paso [{step.name}] tras agotar la cadena de fallbacks."
                job.completed_at = datetime.now().isoformat()
                job.update_totals()
                logger.error(job.error_summary)
                return job

        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now().isoformat()
        job.update_totals()
        job.final_output = {
            "status": "success",
            "job_id": job.job_id,
            "duration_seconds": job.total_duration_seconds,
            "cost": job.total_cost,
            "steps_completed": len(job.steps)
        }
        logger.info(f"Job '{job.job_id}' completado con éxito en {job.total_duration_seconds}s.")
        return job

    def _execute_step_with_fallbacks(self, step: JobStep, context: Dict[str, Any]) -> bool:
        """Ejecuta un paso individual. Si falla, intenta reintentos y luego conmutación a motores de fallback."""
        engine_spec = get_engine(step.engine_id)
        fallback_chain = engine_spec.fallbacks.copy() if engine_spec else []

        current_engine = step.engine_id
        current_provider = step.provider_id

        while True:
            step.start()
            adapter = AdapterRegistry.get_adapter(current_engine)

            if not adapter:
                step.log(f"Adaptador para '{current_engine}' no encontrado en registro. Conmutando a fallback...")
                if fallback_chain:
                    current_engine = fallback_chain.pop(0)
                    prov = get_primary_provider(current_engine)
                    current_provider = prov.id if prov else "local_vps"
                    step.apply_fallback(current_engine, current_provider, "Adaptador inicial no disponible")
                    continue
                else:
                    step.fail(f"No existe adaptador ni fallback para {current_engine}.")
                    return False

            try:
                # Intento de ejecución con el adaptador
                output = adapter.execute(step, context)
                cost = engine_spec.estimated_cost_per_scene if engine_spec else 0.0
                step.complete(output, cost=cost)
                context.update(output)
                return True

            except Exception as ex:
                step.log(f"Excepción en '{current_engine}': {ex}")
                step.retry_count += 1

                if step.retry_count <= self.max_retries_per_step:
                    step.log(f"Reintentando ({step.retry_count}/{self.max_retries_per_step})...")
                    time.sleep(0.5)
                    continue

                # Si se agotan los reintentos, comprobar cadena de fallbacks
                if fallback_chain:
                    next_engine = fallback_chain.pop(0)
                    prov = get_primary_provider(next_engine)
                    next_provider = prov.id if prov else "local_vps"
                    step.apply_fallback(next_engine, next_provider, f"Agotados reintentos por error: {ex}")
                    current_engine = next_engine
                    current_provider = next_provider
                    step.retry_count = 0
                    continue
                else:
                    step.fail(f"Agotados todos los reintentos y la cadena de fallbacks para el paso.")
                    return False
