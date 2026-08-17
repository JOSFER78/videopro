"""
app/core/copilot/copilot_engine.py
================================================================================
MOTOR DE COASISTENCIA CONVERSACIONAL INTELIGENTE & DINÁMICO (HERMES COPILOT)
================================================================================
Gestiona el diálogo interactivo multimodal (texto y voz transcrita), orquestando
llamadas directas al LLM con observabilidad del estado de la pantalla en tiempo real
y resolución semántica robusta.
"""

import copy
import re
from typing import Dict, List, Any, Optional
from loguru import logger
from app.config import config
from app.services.llm import _generate_response
from app.core.copilot.state_observer import StateObserver, PedagogicalGlossary


SYSTEM_COPILOT_PROMPT = """Eres Hermes Copilot, el coasistente conversacional interactivo y pedagógico de VideoPro Studio.

Tu rol:
- Responder de forma amigable, precisa y práctica a cualquier pregunta del creador sobre automatización de YouTube, monetización, canales, producción 4K, guiones y audios.
- Si el usuario te habla por voz (transcrito) o por chat de texto, mantén una conversación fluida y natural.
- Explica los conceptos técnicos con analogías simples de nivel cotidiano ("para 12 años").
- Si te piden consejos de monetización, destaca el RPM Tier 1 ($18-$35 USD), los mid-rolls en vídeos de +8 minutos y las miniaturas de alto contraste.
- Si te preguntan por canales, haz referencia a los 5 canales de VideoPro (01_CHRONODRIFT, 02_TERRAMORPH, 03_NANOVERSE, 04_CYBERMETRICS, 05_ASTRODRIFT).
- Usa Markdown limpio con listas o viñetas.
""".strip()


class CopilotEngine:
    """Motor de chat y razonamiento conversacional dinámico en tiempo real."""

    @classmethod
    def generate_chat_reply(
        cls,
        messages: List[Dict[str, str]],
        view_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera una respuesta conversacional dinámica invocando al LLM con el historial
        completo de la conversación y el contexto de pantalla actual.
        """
        if not messages:
            return "¡Hola! ¿En qué puedo orientarte hoy en VideoPro Studio?"

        last_user_msg = messages[-1].get("content", "").strip()

        # Preparar contexto de pantalla
        ctx_desc = ""
        if view_context:
            ctx_desc = (
                f"\n\n[CONTEXTO DE LA PANTALLA ACTIVA]:\n"
                f"- Vista: {view_context.get('view_name', 'general')}\n"
                f"- Pestaña / Sección: {view_context.get('subtab_name', 'principal')}\n"
                f"- Canal Seleccionado: {view_context.get('channel_id', 'ninguno')}\n"
                f"- Propósito: {view_context.get('proposito', '')}\n"
            )

        # Construir prompt conversacional
        prompt_parts = [
            f"{SYSTEM_COPILOT_PROMPT}{ctx_desc}\n\n[HISTORIAL DE LA CONVERSACIÓN]:"
        ]

        for msg in messages[-6:]:
            role_label = "Usuario" if msg.get("role") == "user" else "Hermes Copilot"
            prompt_parts.append(f"{role_label}: {msg.get('content', '')}")

        prompt_parts.append("Hermes Copilot:")
        full_prompt = "\n".join(prompt_parts)

        # 1. Intentar inferencia LLM en vivo
        try:
            runtime_cfg = copy.deepcopy(config.app)
            
            # Priorizar OpenAI o el proveedor con API key válida
            if not runtime_cfg.get("gemini_api_key") and runtime_cfg.get("openai_api_key"):
                runtime_cfg["llm_provider"] = "openai"
                if not runtime_cfg.get("openai_model_name"):
                    runtime_cfg["openai_model_name"] = "gpt-4o-mini"

            raw_reply = _generate_response(full_prompt, app_config=runtime_cfg)
            if raw_reply and not raw_reply.startswith("Error:") and "bad_gateway" not in raw_reply.lower():
                return raw_reply.strip()

        except Exception as e:
            logger.warning(f"Fallo en llamada primaria LLM: {e}")

        # 2. Inferencia Semántica Contextual en caso de fallback
        return cls._generate_contextual_reasoning(last_user_msg, view_context)

    @classmethod
    def _generate_contextual_reasoning(cls, query: str, view_context: Optional[Dict[str, Any]] = None) -> str:
        """Genera una respuesta pedagógica rica cuando la API externa no está disponible."""
        q_low = query.lower()

        # Comprobar términos clave del glosario
        for k in ["rpm", "anti_slop", "6dof", "ebu_r128", "ypp"]:
            if k in q_low or (k == "anti_slop" and "slop" in q_low) or (k == "6dof" and ("camara" in q_low or "6 dof" in q_low)):
                term = PedagogicalGlossary.get_term_explanation(k)
                if term:
                    return (
                        f"¡Con gusto te explico **{term['title']}**!\n\n"
                        f"💡 **En palabras simples (para 12 años):**\n{term['analogia']}\n\n"
                        f"📊 **Ejemplo real:**\n{term['ejemplo']}\n\n"
                        f"🎯 **Consejo de producción:**\n{term['consejo']}"
                    )

        if any(w in q_low for w in ["empezar", "canal", "conviene", "primer", "recomiend"]):
            return (
                "Para empezar con máxima velocidad y el mejor rendimiento, te recomiendo **01_CHRONODRIFT**:\n\n"
                "1. **¿Por qué?** Es el canal con mayor grado de madurez: ya tiene 12 ciudades configuradas, storyboards 6-DoF y audios listos.\n"
                "2. **Potencial Económico:** Los viajes temporales en 4K tienen alta demanda en mercados Tier 1 (USA, UK, Alemania) con un **RPM proyectado de $18.50 a $28.00 USD**.\n"
                "3. **Siguiente paso:** Ve a la pestaña **'🎬 2. Gestión de Canales'**, selecciona *01_CHRONODRIFT* y revisa el Episodio 01 de Tokio."
            )

        if any(w in q_low for w in ["dinero", "ganar", "ingreso", "mil", "1000", "2000", "dolar", "monetiz"]):
            return (
                "Para alcanzar tus primeros **$1.000 a $2.000 USD al mes** en YouTube con VideoPro, la fórmula probada es:\n\n"
                "1. **Audiencia Tier 1 (Arbitraje Geográfico):** Crear contenido en inglés para público de Estados Unidos o Europa. 50.000 visitas en USA generan lo mismo que 500.000 visitas en LATAM (~$1.000 USD).\n"
                "2. **Vídeos de más de 8 Minutos:** Coloca 2 pausas de mid-rolls (minutos 4:00 y 8:00) para aumentar un **+38%** tus ingresos.\n"
                "3. **Regularidad:** Publicar 2 vídeos de alta retención a la semana con miniaturas de contraste tripartito."
            )

        if any(w in q_low for w in ["slop", "rechaz", "penali", "calidad", "politica"]):
            return (
                "Para evitar que YouTube rechace la monetización por 'contenido repetitivo', VideoPro implementa el **Pentágono Anti-Slop**:\n\n"
                "- **Guion con Tesis:** Historias con conflicto y revelación real (no lecturas mecánicas).\n"
                "- **Cámaras 6-DoF:** Vuelos tridimensionales dinámicos basados en mapas reales de OpenStreetMap.\n"
                "- **Rótulos Vox/Bloomberg:** Gráficos en pantalla con datos concretos.\n"
                "- **Audio Masterizado EBU R128 (-14 LUFS):** La voz siempre al frente y la música atenuada a -18dB."
            )

        # Respuesta conversacional general
        return (
            f"Te entiendo perfectamente sobre: *\"{query}\"*.\n\n"
            f"En VideoPro Studio dispones de 4 etapas claras para ejecutar tu proyecto:\n"
            f"- **1. Aprender:** Conoce la viabilidad económica en la calculadora de RPM.\n"
            f"- **2. Explorar:** Descubre nichos Océano Azul con poca competencia.\n"
            f"- **3. Configurar:** Selecciona tu canal y personaliza los 10 primeros episodios.\n"
            f"- **4. Auditar:** Pasa la validación técnica antes de lanzar el renderizado.\n\n"
            f"¿Quieres profundizar en algún detalle específico?"
        )
