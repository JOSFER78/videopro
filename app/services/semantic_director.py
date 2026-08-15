import json
import re
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services import llm
from app.config import config
from app.models.schema import VideoParams, VideoAspect, VideoConcatMode

DIRECTOR_SYSTEM_PROMPT = """
# ROL: Chief Creative Director & Executive Producer de VideoPro Studio
Eres el Director Creativo de Cine, Documentales y Vídeos Virales de VideoPro Studio.
Tu misión es co-crear interactivamente con el usuario el concepto, la narrativa, la dirección de arte y el plan de producción de su próximo vídeo.

## CAPACIDADES AUDIOVISUALES REALES DISPONIBLES:
1. **Fuentes de Vídeo y Metraje**:
   - `real_news` / `real_photo`: Fotografía histórica auténtica y noticias reales de alta resolución (Wikimedia Commons / Google News RSS) con efecto Ken Burns (zoom y paneo cinemático). Ideal para historia antigua, sucesos, empresas, biografías y datos verificables.
   - `google_flow` / `veo`: Generación de vídeo cinematográfico continuo ultra-fotorrealista (vuelos de dron 8K, ciudades, planos secuencia aéreos con Google Flow / Veo 3.1).
   - `flux`: Keyframes conceptuales y escenas generadas con FLUX.1 (creatividad ilimitada, ciencia ficción, surrealismo, Pixar 3D, anime, etc.).
   - `pexels` / `pixabay`: Metraje de vídeo de stock real en base de datos.
   - `hybrid`: Mezcla inteligente automática de todas las anteriores por escena.
2. **Estilos Visuales Infinitos** (NO hay límites fijos):
   - Documental periodístico táctil (tipo Vox / Johnny Harris, mapas 2.5D, papel texturizado).
   - Cinemático Dron 8K Golden Hour (tipo Autoflow, ARRI Alexa 65).
   - Animación 3D estilizada (tipo Pixar / Octane Render / Disney).
   - FinTech / Geopolítica (tipo Bloomberg / The Economist con telemetría HUD y dark glassmorphism).
   - Cine Noir, Anime Shonen, Cyberpunk 2077, Vintage Super 8mm, etc.
3. **Rótulos y Capas Gráficas**:
   - Tarjetas de datos en pantalla (Glassmorphism HUD).
   - Subtítulos dinámicos estilo Karaoke palabra por palabra (.ass).
4. **Voz y Sonido**:
   - VibeVoice 1.5B (`es-emilio`): Locución cinemática hiperrealista con cadencia emocional profunda (equivalente a ElevenLabs gratuito).
   - Azure Neural TTS (voces globales).
   - BGM Inteligente con ducking dinámico.

## INSTRUCCIONES DE INTERACCIÓN:
1. Responde SIEMPRE en español de forma entusiasta, concisa, profesional y cinematográfica (máximo 2-3 párrafos).
2. Si la idea del usuario es vaga, haz 1 o 2 preguntas creativas clave y ofrece ideas sorprendentes de dirección de arte.
3. Sugiere siempre 3 o 4 opciones interactivas rápidas (pills) que el usuario pueda pulsar.
4. Genera SIEMPRE al final de tu respuesta un bloque JSON delimitado por ```json ... ``` con la especificación técnica acumulada del proyecto.

### FORMATO DEL BLOQUE JSON OBLIGATORIO:
```json
{
  "subject": "Título/concepto refinado del vídeo",
  "visual_style": "Descripción detallada del estilo de arte y estética",
  "recommended_source": "hybrid" | "real_news" | "google_flow" | "flux" | "pexels",
  "aspect_ratio": "9:16" | "16:9",
  "overlay_graphics": "none" | "vox_cards" | "bloomberg_telemetry" | "minimal_subtitles",
  "voice_preset": "vibevoice:es-emilio-Male" | "es-ES-AlvaroNeural-Male" | "es-ES-ElviraNeural-Female",
  "narrative_tone": "periodístico / dramático / inspirador / técnico",
  "estimated_paragraphs": 2,
  "ready_to_produce": true | false,
  "summary_reasoning": "Breve justificación de la dirección elegida"
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
    Retorna la respuesta conversacional, las sugerencias interactivas y el estado del proyecto.
    """
    conversation_prompt = f"{DIRECTOR_SYSTEM_PROMPT}\n\n## HISTORIAL DE LA CONVERSACIÓN:\n"
    
    for msg in messages:
        role = "USUARIO" if msg.get("role") == "user" else "DIRECTOR CREATIVO"
        conversation_prompt += f"{role}: {msg.get('content', '')}\n"
    
    conversation_prompt += f"\nUSUARIO: {user_input}\nDIRECTOR CREATIVO:"

    try:
        raw_response = llm._generate_response(conversation_prompt, app_config=app_config_snapshot)
    except Exception as exc:
        logger.error(f"Error calling LLM in semantic director: {exc}")
        return {
            "response_text": f"He recibido tu propuesta: *'{user_input}'*. ¿Prefieres un enfoque documental histórico con fotos reales o una recreación cinemática 3D?",
            "suggestions": [
                "🏛️ Documental Histórico (Fotos Reales)",
                "🎥 Cinemático 3D Hiperrealista",
                "📊 Rótulos y Gráficos Tipo Vox",
                "✨ Iniciar Producción"
            ],
            "spec": {
                "subject": user_input,
                "visual_style": "Documental Cinemático",
                "recommended_source": "hybrid",
                "aspect_ratio": "9:16",
                "overlay_graphics": "vox_cards",
                "voice_preset": "vibevoice:es-emilio-Male",
                "narrative_tone": "inspirador",
                "estimated_paragraphs": 2,
                "ready_to_produce": True,
                "summary_reasoning": "Propuesta base generada automáticamente"
            }
        }

    # Extraer JSON de especificaciones
    spec = {
        "subject": user_input,
        "visual_style": "Cinemático / Personalizado",
        "recommended_source": "hybrid",
        "aspect_ratio": "9:16",
        "overlay_graphics": "minimal_subtitles",
        "voice_preset": "vibevoice:es-emilio-Male",
        "narrative_tone": "profesional",
        "estimated_paragraphs": 2,
        "ready_to_produce": False,
        "summary_reasoning": ""
    }
    
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_response, re.DOTALL)
    clean_text = raw_response
    if json_match:
        try:
            parsed = json.loads(json_match.group(1))
            spec.update(parsed)
            # Quitar el bloque json del texto visible para que quede limpio
            clean_text = raw_response[:json_match.start()].strip()
            after_json = raw_response[json_match.end():].strip()
            if after_json:
                clean_text += f"\n\n{after_json}"
        except Exception as e:
            logger.warning(f"Failed to parse director JSON spec: {e}")

    # Generar sugerencias interactivas según el estado
    suggestions = []
    if not spec.get("ready_to_produce"):
        suggestions = [
            "🏛️ Metraje Real + Fotos Históricas",
            "🎥 Vuelo de Dron 8K Ultra-Real",
            "🧸 Estilo Pixar 3D Animado",
            "📊 Añadir Rótulos de Telemetría Vox/Bloomberg",
            "✨ ¡Me gusta, comenzar producción!"
        ]
    else:
        suggestions = [
            "🚀 Iniciar Producción y Renderizado",
            "🎨 Cambiar a formato Horizontal 16:9",
            "🎙️ Probar otra voz de locutor",
            "✏️ Ajustar detalles del guion"
        ]

    return {
        "response_text": clean_text,
        "suggestions": suggestions,
        "spec": spec
    }
