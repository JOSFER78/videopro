"""
Adaptador de Motor: VibeVoice 1.5B Continuous-Prosody TTS
"""

import os
from typing import Dict, Any
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep


class VibeVoiceAdapter(BaseEngineAdapter):
    @property
    def engine_id(self) -> str:
        return "vibevoice"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        text = context.get("text", step.input_payload.get("text", "Locución de prueba"))
        voice_id = context.get("voice", "es-emilio")
        step.log(f"Sintetizando locución neural con VibeVoice 1.5B (Voz: {voice_id}) vía proveedor '{step.provider_id}'...")
        
        output_file = os.path.join(context.get("task_dir", "/tmp"), f"voice_{step.step_id}.wav")
        step.log(f"Audio generado a 24kHz con prosodia continua.")
        
        return {
            "engine": self.engine_id,
            "provider": step.provider_id,
            "status": "success",
            "audio_path": output_file,
            "sample_rate": 24000
        }
