"""
Modelo de Ejecución de Trabajos (Execution Job Model) — VideoPro Studio
Toda ejecución en VideoPro se convierte en un Job explícito con Steps auditables y trazables.
"""

import time
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.orchestration.capabilities import Capability


class JobStatus(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    FALLBACK = "fallback"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    FALLBACK_APPLIED = "fallback_applied"
    SKIPPED = "skipped"


class JobStep(BaseModel):
    step_id: str
    name: str
    capability: Capability
    engine_id: str
    provider_id: str
    status: JobStepStatus = JobStepStatus.PENDING
    input_payload: Dict[str, Any] = Field(default_factory=dict)
    output_payload: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: float = 0.0
    cost: float = 0.0
    retry_count: int = 0
    fallback_used: Optional[str] = None
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def start(self):
        self.status = JobStepStatus.RUNNING
        self.start_time = time.time()
        self.log(f"Iniciando paso [{self.name}] con motor '{self.engine_id}' en proveedor '{self.provider_id}'.")

    def complete(self, output: Dict[str, Any], cost: float = 0.0):
        self.status = JobStepStatus.COMPLETED
        self.output_payload = output
        self.cost = cost
        self.end_time = time.time()
        if self.start_time:
            self.duration_seconds = round(self.end_time - self.start_time, 2)
        self.log(f"Paso [{self.name}] completado con éxito en {self.duration_seconds}s.")

    def fail(self, error: str):
        self.status = JobStepStatus.FAILED
        self.error_message = error
        self.end_time = time.time()
        if self.start_time:
            self.duration_seconds = round(self.end_time - self.start_time, 2)
        self.log(f"ERROR en paso [{self.name}]: {error}")

    def apply_fallback(self, new_engine: str, new_provider: str, reason: str):
        self.status = JobStepStatus.FALLBACK_APPLIED
        self.fallback_used = new_engine
        self.log(f"⚠️ FALLBACK APLICADO: Conmutando de '{self.engine_id}' a '{new_engine}' ({new_provider}). Causa: {reason}")
        self.engine_id = new_engine
        self.provider_id = new_provider

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.logs.append(f"[{timestamp}] {message}")


class ExecutionJob(BaseModel):
    job_id: str
    project_id: str
    workflow_id: str
    workflow_version: int = 1
    status: JobStatus = JobStatus.QUEUED
    steps: List[JobStep] = Field(default_factory=list)
    total_duration_seconds: float = 0.0
    total_cost: float = 0.0
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    final_output: Dict[str, Any] = Field(default_factory=dict)
    error_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def update_totals(self):
        self.total_duration_seconds = round(sum(s.duration_seconds for s in self.steps), 2)
        self.total_cost = round(sum(s.cost for s in self.steps), 4)
        self.updated_at = datetime.now().isoformat()
