"""
Enrutador de Motores a Nivel de Escena (Scene-Level Engine Selection) — VideoPro Studio
Permite que cada escena individual de un vídeo utilice un motor visual diferente según su tipo de plano y contenido:
scene 01 -> stock, scene 02 -> google_flow, scene 03 -> nanobanana, scene 04 -> flux_video, etc.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from app.core.orchestration.engines import get_engine, ENGINES_CATALOG


class VisualStrategy(str, Enum):
    AUTOMATIC = "automatic"          # La IA decide el motor óptimo por escena según el prompt y tipo de toma
    HYBRID = "hybrid"                # Distribución equilibrada (Stock + Flow + FLUX + NanoBanana)
    SINGLE_ENGINE = "single_engine"  # Todas las escenas usan el mismo motor
    MANUAL = "manual"                # El usuario especifica el motor escena por escena


class ScenePlan(BaseModel):
    scene_index: int
    scene_id: str
    prompt: str
    shot_type: str = "medium"        # wide_establishing, drone_aerial, character_close_up, macro_detail, action_tracking
    visual_theme: str = "general"    # real_location, character_dialogue, cinematic_action, abstract_concept
    recommended_engine: str          # google_flow, flux_video, nanobanana, ltx25, stock_db
    assigned_provider: str           # flow_playwright_local, flux_zerogpu, nanobanana_bridge, etc.
    fallback_engines: List[str] = Field(default_factory=list)
    duration_seconds: float = 4.0
    aspect_ratio: str = "9:16"
    requires_lip_sync: bool = False
    requires_3d_freeze: bool = False


class SceneEngineRouter:
    """Enrutador de directores de escena para resolver dinámicamente qué motor produce cada plano."""

    @staticmethod
    def route_scenes(
        scenes: List[Dict[str, Any]],
        strategy: VisualStrategy = VisualStrategy.AUTOMATIC,
        forced_engine: Optional[str] = None
    ) -> List[ScenePlan]:
        """
        Asigna el motor visual óptimo para cada escena individual basándose en su descripción semántica,
        tipo de plano y requerimientos ópticos.
        """
        planned_scenes: List[ScenePlan] = []

        for idx, sc in enumerate(scenes):
            scene_id = sc.get("id", f"scene_{idx + 1}")
            prompt = sc.get("prompt", sc.get("text", ""))
            shot_type = sc.get("shot_type", "medium")
            duration = float(sc.get("duration", 4.0))
            is_real_place = any(k in prompt.lower() for k in ["calle", "ciudad", "madrid", "shibuya", "tokyo", "paris", "edificio", "plaza", "monumento", "street", "city"])
            is_character = any(k in prompt.lower() for k in ["persona", "primer plano", "rostro", "habla", "personaje", "cara", "dialogo", "portrait"])
            is_aerial = any(k in prompt.lower() for k in ["dron", "vuelo", "aéreo", "vista de pájaro", "orbita", "aerial", "skyline", "paisaje"])

            if strategy == VisualStrategy.SINGLE_ENGINE and forced_engine:
                chosen_engine = forced_engine
            elif strategy == VisualStrategy.MANUAL and sc.get("engine"):
                chosen_engine = sc["engine"]
            elif strategy in (VisualStrategy.AUTOMATIC, VisualStrategy.HYBRID):
                # Reglas semánticas inteligentes de asignación de motores
                if is_aerial:
                    chosen_engine = "google_flow"      # Google Flow destaca en vuelos orbitales y panorámicas 4K
                elif is_character:
                    chosen_engine = "flux_video"       # FLUX 3 destaca en anatomía y primeros planos de personajes
                elif is_real_place:
                    chosen_engine = "nanobanana"       # NanoBanana / Imagen 3 destaca en fotorrealismo de lugares y Street View
                else:
                    # Alternancia balanceada híbrida
                    engines_pool = ["google_flow", "flux_video", "nanobanana", "stock_db"]
                    chosen_engine = engines_pool[idx % len(engines_pool)]
            else:
                chosen_engine = "google_flow"

            engine_spec = get_engine(chosen_engine)
            fallbacks = engine_spec.fallbacks if engine_spec else ["stock_db"]

            # Asignación de proveedor primario
            from app.core.orchestration.providers import get_primary_provider
            primary_prov = get_primary_provider(chosen_engine)
            provider_id = primary_prov.id if primary_prov else "local_vps"

            plan = ScenePlan(
                scene_index=idx,
                scene_id=scene_id,
                prompt=prompt,
                shot_type=shot_type,
                recommended_engine=chosen_engine,
                assigned_provider=provider_id,
                fallback_engines=fallbacks,
                duration_seconds=duration,
                requires_lip_sync=is_character,
                requires_3d_freeze=is_aerial
            )
            planned_scenes.append(plan)

        return planned_scenes
