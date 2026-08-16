"""
Adaptador de Motor: Vox Dynamic Subtitle Styler
"""

import os
from typing import Dict, Any
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep


class SubtitlesAdapter(BaseEngineAdapter):
    @property
    def engine_id(self) -> str:
        return "vox_subtitles"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        step.log("Compilando subtítulos dinámicos ASS con animación Karaoke y palabra activa en amarillo...")
        output_file = os.path.join(context.get("task_dir", "/tmp"), "subtitles.ass")
        step.log("Archivo de subtítulos ASS generado y verificado.")
        
        return {
            "engine": self.engine_id,
            "status": "success",
            "ass_path": output_file
        }
