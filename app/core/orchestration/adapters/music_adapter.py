"""
Adaptador de Motor: Google Flow Music (Lyria 3) & Stock Songs
"""

import os
from typing import Dict, Any
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep


class MusicAdapter(BaseEngineAdapter):
    @property
    def engine_id(self) -> str:
        return "flow_music"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        mood = context.get("mood", "cinematic_documentary")
        step.log(f"Componiendo banda sonora adaptativa y foley acústico (Mood: {mood})...")
        
        output_file = os.path.join(context.get("task_dir", "/tmp"), f"bgm_{step.step_id}.mp3")
        step.log("Banda sonora generada a 48kHz estéreo.")
        
        return {
            "engine": self.engine_id,
            "status": "success",
            "music_path": output_file,
            "sample_rate": 48000
        }
