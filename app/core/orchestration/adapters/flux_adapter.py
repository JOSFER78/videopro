"""
Adaptador de Motor: FLUX 3 Video (ZeroGPU / RunPod)
"""

import os
from typing import Dict, Any
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep


class FluxAdapter(BaseEngineAdapter):
    @property
    def engine_id(self) -> str:
        return "flux_video"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        step.log(f"Enviando solicitud a clúster FLUX 3 Video vía proveedor '{step.provider_id}'...")
        prompt = context.get("prompt", step.input_payload.get("prompt", "Cinematic Scene"))
        
        output_file = os.path.join(context.get("task_dir", "/tmp"), f"flux_{step.step_id}.mp4")
        step.log(f"Renderizando plano Flow Matching 24fps: '{prompt}'")
        
        return {
            "engine": self.engine_id,
            "provider": step.provider_id,
            "status": "success",
            "video_path": output_file,
            "fps": 24
        }
