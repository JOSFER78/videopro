"""
app/core/copilot/state_observer.py
================================================================================
OBSERVADOR DE ESTADO EN TIEMPO REAL & TRADUCTOR PEDAGÓGICO
================================================================================
Monitorea el estado de Streamlit y traduce conceptos técnicos / errores crípticos
a explicaciones pedagógicas de nivel principiante ("explicado para 12 años").
"""

from typing import Dict, List, Any, Optional


class PedagogicalGlossary:
    """Diccionario de conceptos técnicos traducidos a analogías simples cotidianas."""

    TERMS = {
        "rpm": {
            "title": "RPM (Revenue Per Mille / Ingreso por cada 1.000 vistas)",
            "analogia": "Es el sueldo que te paga YouTube por cada 1.000 personas que ven tu vídeo completo con anuncios.",
            "ejemplo": "Si tu RPM es de $20 USD y tienes 100.000 vistas, ganas $2.000 USD limpios.",
            "consejo": "Para tener RPM alto ($18-$35), haz vídeos en inglés sobre ciencia, tecnología, viajes o historia para países como Estados Unidos o Alemania (Tier 1)."
        },
        "anti_slop": {
            "title": "Pentágono Anti-Slop (Calidad Editorial)",
            "analogia": "Es la vacuna para que YouTube no considere tus vídeos como 'basura automática' o 'contenido repetitivo'.",
            "ejemplo": "En vez de poner fotos fijas y voz robótica, usas guiones con inicio-nudo-desenlace, gráficos con datos reales (estilo Vox) y sonidos de fondo envolventes.",
            "consejo": "Sigue los 5 puntos: Guion con tesis, cámaras 6-DoF, consistencia visual, rótulos de datos y audio masterizado."
        },
        "6dof": {
            "title": "Control de Cámara 6-DoF (Seis Grados de Libertad)",
            "analogia": "Imagina que manejas un dron de carreras que puede volar hacia adelante/atrás, subir/bajar y girar en cualquier ángulo sin tropezar.",
            "ejemplo": "En lugar de una foto que solo hace zoom, la cámara vuela entre los edificios como si estuvieras allí de verdad.",
            "consejo": "VideoPro usa coordenadas de satélite reales (OpenStreetMap) para que el vuelo sea 100% realista."
        },
        "ebu_r128": {
            "title": "Audio EBU R128 (-14 LUFS / Sidechain Ducking)",
            "analogia": "Es como un director de orquesta que baja el volumen de la música de fondo cada vez que el narrador empieza a hablar para que se le escuche clarísimo.",
            "ejemplo": "La voz suena nítida al frente y la música a -18dB por debajo, sin que el espectador tenga que subir o bajar el volumen de sus auriculares.",
            "consejo": "YouTube premia los vídeos con volumen estándar de -14 LUFS porque la gente no los quita por molestias de audio."
        },
        "ypp": {
            "title": "YPP (YouTube Partner Program / Programa de Socios)",
            "analogia": "Es el carnet oficial que te entrega YouTube para empezar a cobrar dinero de los anuncios en tu cuenta bancaria.",
            "ejemplo": "Requiere 1.000 suscriptores y 4.000 horas de reproducción (con 10 vídeos buenos de 10 minutos y 4.800 vistas cada uno ya lo alcanzas).",
            "consejo": "Publica con regularidad 2 vídeos por semana con miniaturas de alto contraste para llegar en menos de 60 días."
        }
    }

    @classmethod
    def get_term_explanation(cls, term_key: str) -> Optional[Dict[str, str]]:
        term_clean = term_key.lower().strip()
        for k, v in cls.TERMS.items():
            if k in term_clean or term_clean in k:
                return v
        return None


class StateObserver:
    """Extrae y resume el contexto activo de la pantalla para el Copilot."""

    @staticmethod
    def get_screen_summary(view_name: str, subtab_name: Optional[str] = None, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Devuelve un resumen pedagógico de qué hace la pantalla actual y qué debe hacer el usuario."""
        
        summaries = {
            "youtube_monetization": {
                "title": "Centro de Mando de Canales & Monetización YouTube",
                "proposito": "Aquí planificas, gestionas y supervisas tus canales de YouTube para generar ingresos en dólares con contenido 4K.",
                "fase_sugerida": "Paso 1: Elige un canal o idea ➔ Paso 2: Revisa sus 10 episodios ➔ Paso 3: Genera metadatos SEO ➔ Paso 4: Audita el pipeline.",
                "subtabs_info": {
                    "academia": "Calcula cuánto dinero puedes ganar según tus vistas y aprende por qué los países ricos pagan hasta 27 veces más.",
                    "canales": "Revisa los 5 canales de VideoPro listos para producir (guiones de 10 episodios, miniaturas y estilo visual).",
                    "explorador": "Busca ideas de vídeos en tiempo real y descubre nichos con poca competencia (Océanos Azules).",
                    "seo": "Crea el título, descripción con marcas de tiempo y etiquetas perfectas para que YouTube recomiende tu vídeo.",
                    "multiplataforma": "Adapta tu vídeo horizontal 16:9 a formato vertical 9:16 (Shorts, TikTok y Reels) sin bandas negras.",
                    "auditoria": "Comprueba con 1 clic que los archivos, guiones y sonidos cumplen las normas antes de gastar recursos."
                }
            }
        }

        view_info = summaries.get(view_name, {
            "title": view_name.replace("_", " ").title(),
            "proposito": "Módulo de trabajo de VideoPro Studio.",
            "fase_sugerida": "Sigue las instrucciones del asistente paso a paso.",
            "subtabs_info": {}
        })

        return {
            "view_name": view_name,
            "subtab_name": subtab_name,
            "channel_id": channel_id,
            "title": view_info["title"],
            "proposito": view_info["proposito"],
            "fase_sugerida": view_info["fase_sugerida"],
            "subtabs_info": view_info.get("subtabs_info", {})
        }
