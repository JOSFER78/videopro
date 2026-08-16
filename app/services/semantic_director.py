"""
Director Creativo Semántico — VideoPro Studio
Motor de Conversación y Pulido Interactivo de Información por Arquetipo de Workflow.
Guía al usuario en un diálogo de co-creación adaptativo antes de lanzar la producción.
"""

import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services import llm
from app.config import config
from app.models.schema import VideoParams, VideoAspect, VideoConcatMode
from app.core.orchestration.workflow_archetypes import ARCHETYPES_CATALOG, get_archetype, get_all_archetypes

DIRECTOR_SYSTEM_PROMPT = """
# ROL: Chief Creative Director & Executive Producer de VideoPro Studio
Eres el Director Creativo de Cine, Documentales y Vídeos Virales de VideoPro Studio.
Tu misión es guiar un diálogo interactivo de **PULIDO DE INFORMACIÓN** con el usuario al comienzo de cada proyecto/workflow para extraer con precisión los parámetros artísticos, narrativos y técnicos antes de lanzar la producción.

## 🎬 ARQUETIPOS DE PRODUCCIÓN Y SUS PIPELINES COMFYUI DISPONIBLES:
1. `PIXAR_3D_ANIMATION` (🧸 Cuentos & Animación 3D):
   - Requiere pulir: Nombre/diseño del personaje, conflicto de la historia, tono emotivo (conmovedor vs cómico) y entorno 3D.
   - Pipeline: Character Sheet LoRA 3D -> FLUX 3 / NanoBanana 3D -> VibeVoice animado -> Flow Music orquestal cuento -> Foley dibujos animados.
2. `HISTORICAL_SCRAPING` (📜 Documental Histórico & Archivo Real):
   - Requiere pulir: Personaje/hecho histórico, fuentes primarias para scraping (Wikipedia/Commons/Hemerotecas), rigor documental y política de recreación de lagunas sin fotos.
   - Pipeline: Hermes Scraping Subagents -> NanoBanana 4K Restorer -> Google Flow 4K Recreaciones -> VibeVoice es-emilio -> Subtítulos y Mapas Vox.
3. `CITY_ROUTES_BEATS` (🏙️ Rutas Urbanas & Vídeos Musicales):
   - Requiere pulir: Ciudad y puntos GPS de parada, estilo de beat musical (Synthwave 118 BPM, Lo-Fi 85 BPM, Trap 135 BPM) y curiosidades a resaltar.
   - Pipeline: Mapeador GPS -> Google Flow Vuelos Orbitales 4K -> Flow Music Lyria 3 a Tempo Constante -> Overlays Gráficos Vox -> Beat-Cutter.
4. `VIRAL_SHORTS_HOOK` (⚡ Viral Shorts & Retención Extrema):
   - Requiere pulir: Gancho de 3s (pregunta shock / creencia falsa / dato prohibido), llamada a la acción final y formato vertical 9:16.
   - Pipeline: Gancho A/B -> Fast Visual Loops 1.8s (Stock + FLUX) -> Subtítulos Karaoke Amarillo Flúor -> SFX Impacto cada 3s.
5. `DEEP_EXPLAINER_ESSAY` (📊 Deep Explainer & Videoensayo Dialéctico):
   - Requiere pulir: Tesis central y antítesis, datos estadísticos cuantitativos y estilo de infografía (Vox Minimalista vs Bloomberg).
   - Pipeline: Guion Dialéctico 3 Actos -> Infografías Remotion React TSX / HyperFrames -> Voz Pensativa -> BGM Minimalista.

## 📋 REGLAS DEL PROCESO DE PULIDO CONVERSACIONAL:
1. Responde SIEMPRE en español con tono entusiasta, profesional y cinematográfico (máximo 2 párrafos concisos).
2. Si el usuario acaba de elegir un arquetipo o tema, haz **1 o 2 preguntas clave de pulido específicas de ese arquetipo**.
3. Ofrece siempre **3 o 4 sugerencias rápidas (pills)** que respondan directamente a tus preguntas para que el usuario pueda avanzar con un solo clic.
4. Si ya se han definido el personaje/tema, el conflicto/enfoque y el estilo, marca `"ready_to_produce": true`.
5. Genera SIEMPRE al final de tu respuesta un bloque JSON delimitado por ```json ... ``` con la especificación técnica acumulada del proyecto.

### FORMATO DEL BLOQUE JSON OBLIGATORIO:
```json
{
  "archetype_id": "PIXAR_3D_ANIMATION" | "HISTORICAL_SCRAPING" | "CITY_ROUTES_BEATS" | "VIRAL_SHORTS_HOOK" | "DEEP_EXPLAINER_ESSAY",
  "subject": "Título o concepto refinado del vídeo",
  "visual_style": "Descripción detallada del estilo de arte y estética",
  "recommended_source": "google_flow" | "flux" | "nanobanana" | "stock" | "hybrid",
  "aspect_ratio": "9:16" | "16:9",
  "overlay_graphics": "none" | "vox_cards" | "karaoke_yellow" | "bloomberg_charts",
  "voice_preset": "vibevoice:es-emilio-Male" | "es-ES-AlvaroNeural-Male" | "es-ES-ElviraNeural-Female",
  "music_genre": "pixar_orchestral" | "synthwave" | "lofi" | "historical_strings" | "minimal_ambient",
  "narrative_tone": "emotivo / épico / solemne / dinámico / analítico",
  "estimated_paragraphs": 2,
  "ready_to_produce": true | false,
  "interview_step": 1 | 2 | 3,
  "summary_reasoning": "Resumen de la dirección creativa y pipeline configurado"
}
```
"""


def chat_with_director(
    messages: List[Dict[str, str]],
    user_input: str,
    app_config_snapshot=None
) -> Dict[str, Any]:
    """
    Gestiona la conversación con el Director Creativo Semántico.
    Ejecuta el pulido interactivo de información por arquetipo antes de la producción.
    """
    # Detectar si el usuario seleccionó un arquetipo explícito
    detected_archetype = None
    u_lower = user_input.lower()
    if "pixar" in u_lower or "3d" in u_lower or "animac" in u_lower or "cuento" in u_lower:
        detected_archetype = "PIXAR_3D_ANIMATION"
    elif "histór" in u_lower or "histor" in u_lower or "scrap" in u_lower or "archivo" in u_lower or "antigu" in u_lower:
        detected_archetype = "HISTORICAL_SCRAPING"
    elif "ruta" in u_lower or "ciuda" in u_lower or "urban" in u_lower or "músic" in u_lower or "music" in u_lower or "beat" in u_lower:
        detected_archetype = "CITY_ROUTES_BEATS"
    elif "viral" in u_lower or "short" in u_lower or "tiktok" in u_lower or "reel" in u_lower or "gancho" in u_lower:
        detected_archetype = "VIRAL_SHORTS_HOOK"
    elif "ensayo" in u_lower or "explainer" in u_lower or "vox" in u_lower or "bloomberg" in u_lower or "análisis" in u_lower:
        detected_archetype = "DEEP_EXPLAINER_ESSAY"

    conversation_prompt = f"{DIRECTOR_SYSTEM_PROMPT}\n\n## HISTORIAL DE LA CONVERSACIÓN:\n"
    
    for msg in messages:
        role = "USUARIO" if msg.get("role") == "user" else "DIRECTOR CREATIVO"
        conversation_prompt += f"{role}: {msg.get('content', '')}\n"
    
    conversation_prompt += f"\nUSUARIO: {user_input}\nDIRECTOR CREATIVO:"

    try:
        raw_response = llm._generate_response(conversation_prompt, app_config=app_config_snapshot)
    except Exception as exc:
        logger.error(f"Error calling LLM in semantic director: {exc}")
        return _build_fallback_director_response(user_input, detected_archetype)

    # Extraer JSON de especificaciones
    spec = {
        "archetype_id": detected_archetype or "HISTORICAL_SCRAPING",
        "subject": user_input,
        "visual_style": "Documental Cinemático",
        "recommended_source": "hybrid",
        "aspect_ratio": "9:16",
        "overlay_graphics": "vox_cards",
        "voice_preset": "vibevoice:es-emilio-Male",
        "music_genre": "cinematic",
        "narrative_tone": "profesional",
        "estimated_paragraphs": 2,
        "ready_to_produce": False,
        "interview_step": 1,
        "summary_reasoning": "Diálogo de pulido en curso."
    }
    
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
    clean_text = raw_response
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            spec.update(parsed)
            clean_text = raw_response[:json_match.start()].strip()
            after_json = raw_response[json_match.end():].strip()
            if after_json:
                clean_text += f"\n\n{after_json}"
        except Exception as e:
            logger.warning(f"Failed to parse director JSON spec: {e}")

    # Generar sugerencias interactivas según el arquetipo y estado del pulido
    arch_id = spec.get("archetype_id", detected_archetype or "HISTORICAL_SCRAPING")
    suggestions = _generate_contextual_suggestions(arch_id, spec)

    return {
        "response_text": clean_text,
        "suggestions": suggestions,
        "spec": spec
    }


def _generate_contextual_suggestions(archetype_id: str, spec: Dict[str, Any]) -> List[str]:
    """Genera sugerencias rápidas adaptativas para avanzar en el pulido del arquetipo."""
    if spec.get("ready_to_produce"):
        return [
            "🚀 Iniciar Producción con Pipeline Específico",
            "🎨 Cambiar Formato (16:9 / 9:16)",
            "🎙️ Ajustar Tono de Voz",
            "✏️ Modificar un Detalle"
        ]

    if archetype_id == "PIXAR_3D_ANIMATION":
        return [
            "🧸 Protagonista: Lupo el lobezno curioso",
            "🌟 Conflicto: Encender las estrellas apagadas",
            "🌲 Mundo: Bosque Mágico de Cuento",
            "✨ ¡Perfecto, lanzar producción 3D!"
        ]
    elif archetype_id == "CITY_ROUTES_BEATS":
        return [
            "🏙️ Ruta: Madrid (Gran Vía, Malasaña, Cuatro Torres)",
            "🎧 Beat: Electronic City Synthwave (118 BPM)",
            "🏷️ Curiosidades: Secretos Arquitectónicos & Récords",
            "✨ ¡Todo listo, compilar vídeo musical!"
        ]
    elif archetype_id == "HISTORICAL_SCRAPING":
        return [
            "📜 Tema: El Metro de Madrid en 1919",
            "🔬 Scraping: Wikipedia + Commons + Hemerotecas",
            "🎥 Lagunas: Recrear con Google Flow 4K e Imagen 3",
            "✨ ¡Comenzar investigación y documental!"
        ]
    elif archetype_id == "VIRAL_SHORTS_HOOK":
        return [
            "⚡ Gancho: Pregunta Shock ('¿Sabías que...?')",
            "🔥 Ritmo: Ultra Rápido (1.8s por toma)",
            "💬 Cierre: Pregunta para debate en comentarios",
            "✨ ¡Lanzar producción del Short!"
        ]
    elif archetype_id == "DEEP_EXPLAINER_ESSAY":
        return [
            "📊 Tesis: La geopolítica secreta de los semiconductores",
            "📈 Infografías: Estilo Vox Minimalista Neón",
            "🧠 Estructura: Dialéctica Tesis-Antítesis-Síntesis",
            "✨ ¡Generar videoensayo completo!"
        ]
    else:
        return [
            "🧸 Cuentos & Animación 3D",
            "📜 Documental Histórico (Scraping + 4K)",
            "🏙️ Rutas Urbanas & City Beats",
            "⚡ Viral Shorts (TikTok / Reels)",
            "📊 Deep Explainer (Gráficos Vox)"
        ]


def _build_fallback_director_response(user_input: str, archetype_id: Optional[str]) -> Dict[str, Any]:
    arch_id = archetype_id or "HISTORICAL_SCRAPING"
    arch = get_archetype(arch_id) or ARCHETYPES_CATALOG["HISTORICAL_SCRAPING"]
    
    return {
        "response_text": f"¡Excelente propuesta para **{arch.name}**! Vamos a pulir los detalles para configurar el pipeline exacto. ¿Qué aspecto o enfoque narrativo prefieres priorizar?",
        "suggestions": _generate_contextual_suggestions(arch_id, {"ready_to_produce": False}),
        "spec": {
            "archetype_id": arch_id,
            "subject": user_input,
            "visual_style": arch.name,
            "recommended_source": "google_flow" if arch_id == "CITY_ROUTES_BEATS" else "hybrid",
            "aspect_ratio": arch.default_aspect_ratio,
            "overlay_graphics": "vox_cards",
            "voice_preset": f"{arch.default_voice_engine}:{arch.default_voice_id}",
            "music_genre": arch.default_music_genre,
            "narrative_tone": "cinematográfico",
            "estimated_paragraphs": 2,
            "ready_to_produce": True,
            "summary_reasoning": f"Configurado pipeline especializado de {arch.name} con parámetros adaptativos."
        }
    }
