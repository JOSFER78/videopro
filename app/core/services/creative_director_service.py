"""
Creative Director Service (Interprets conversation, suggests styles, enforces user locks)
"""
from typing import Dict, Any, List, Tuple
from app.core.domain.entities import ProjectEntity
from app.core.domain.enums import LockLevel, VisualEngineType, VoiceEngineType, KaraokeStyle
from loguru import logger

class CreativeDirectorService:
    @classmethod
    def apply_director_instruction(cls, project: ProjectEntity, instruction: str) -> List[Tuple[str, bool]]:
        """
        Interprets natural language instructions and applies changesets adhering to lock hierarchy:
        USER_LOCK > PROJECT_DECISION > DIRECTOR_SUGGESTION > DEFAULT.
        """
        results = []
        instr_lower = instruction.lower()

        # 1. Check for Steampunk / Onirópolis directive
        if "steampunk" in instr_lower or "onirópolis" in instr_lower or "onirópolis" in instr_lower:
            for i, scene in enumerate(project.scenes):
                path_engine = f"scenes[{i}].visual.engine"
                path_palette = f"scenes[{i}].visual.color_palette"
                path_sub = f"scenes[{i}].subtitle.style"
                
                applied_e = project.set_decision(path_engine, VisualEngineType.LTX25.value, LockLevel.DIRECTOR_SUGGESTION, "director", "Steampunk cinematic animation")
                applied_p = project.set_decision(path_palette, "sepia, tarnish copper, oxidized bronze, emerald gaslight", LockLevel.DIRECTOR_SUGGESTION, "director", "Onirópolis palette")
                applied_s = project.set_decision(path_sub, KaraokeStyle.STEAMPUNK.value, LockLevel.DIRECTOR_SUGGESTION, "director", "Steampunk typography")
                
                if applied_e: scene.visual_spec.engine = VisualEngineType.LTX25
                if applied_p: scene.visual_spec.color_palette = "sepia, tarnish copper, oxidized bronze, emerald gaslight"
                if applied_s: scene.subtitle_spec.style = KaraokeStyle.STEAMPUNK
                
                results.append((path_engine, applied_e))

        # 2. Check for Vox / Documentary directive
        elif "vox" in instr_lower or "documentary" in instr_lower or "johnny harris" in instr_lower:
            for i, scene in enumerate(project.scenes):
                path_sub = f"scenes[{i}].subtitle.style"
                path_foley = f"scenes[{i}].audio.foley_enabled"
                
                applied_s = project.set_decision(path_sub, KaraokeStyle.VOX_HARRIS.value, LockLevel.DIRECTOR_SUGGESTION, "director", "Vox yellow 1-2 words")
                applied_f = project.set_decision(path_foley, True, LockLevel.DIRECTOR_SUGGESTION, "director", "Paper foley & typewriter")
                
                if applied_s: scene.subtitle_spec.style = KaraokeStyle.VOX_HARRIS
                if applied_f: scene.audio_spec.foley_enabled = True
                
                results.append((path_sub, applied_s))

        return results
