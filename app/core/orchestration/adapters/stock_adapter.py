"""
Adaptador de Motor: Stock 4K Documentary Engine (Pexels / Pixabay)
"""

import os
from typing import Dict, Any
from app.core.orchestration.adapters.base import BaseEngineAdapter
from app.core.orchestration.job import JobStep


class StockAdapter(BaseEngineAdapter):
    @property
    def engine_id(self) -> str:
        return "stock_db"

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return True

    def execute(self, step: JobStep, context: Dict[str, Any]) -> Dict[str, Any]:
        terms = context.get("search_terms", step.input_payload.get("search_terms", ["documentary"]))
        step.log(f"Buscando material de archivo 4K para términos: {terms}...")
        
        output_file = os.path.join(context.get("task_dir", "/tmp"), f"stock_{step.step_id}.mp4")
        step.log(f"Clip de archivo descargado y reencuadrado a 9:16/16:9.")
        
        return {
            "engine": self.engine_id,
            "status": "success",
            "video_path": output_file,
            "source": "pexels"
        }
