# Registro de Decisiones de Arquitectura — VideoPro Studio

## Decisión 1: Sustitución del motor TTS por VibeVoice 1.5B Local
- **Contexto:** Las APIs externas comerciales (ElevenLabs, OpenAI TTS) suponen un coste recurrente por token y dependencia de red.
- **Decisión:** Integrar `/home/ubuntu/vibevoice-venv/bin/python` con el modelo local `microsoft/VibeVoice-1.5b` y la voz `es-emilio`.
- **Resultado:** Calidad de audio a 24kHz con control de expresividad y emoción a coste cero, con fallback automático a EdgeTTS para máxima robustez.

## Decisión 2: Pipeline de Generación Multimodal por Escena (3 Modos)
- **Contexto:** Un vídeo de alta calidad requiere combinar material real, planos fotográficos consistentes y generación con IA.
- **Decisión:** Permitir selección independiente por toma:
  1. *Modo 1 (Stock DB)*
  2. *Modo 2 (FLUX.1 Keyframe 0 + Síntesis 2.5D)*
  3. *Modo 3 (Google Flow vía Playwright con Gemini Omni Flash)*
- **Resultado:** Flexibilidad total para directores y creadores sin depender de un solo generador.

## Decisión 3: Despliegue en Nginx bajo HTTPS Canónico y Enrutamiento Unificado
- **Contexto:** Se prohíbe el uso de `localhost` en respuestas y URLs de cara a producción.
- **Decisión:** 
  - Exponer VideoPro Studio v2.0 (FastAPI backend + Glassmorphism WebUI en puerto `7895`) bajo la ruta pública oficial `https://143-47-35-167.sslip.io/pro/videopro/` (con todos sus endpoints `/api/v1/` y descargas `/outputs/` servidos de forma unificada).
  - Mantener la interfaz legacy Streamlit MPT en `https://143-47-35-167.sslip.io/pro/videopro-mpt/` (puerto `8501`).
- **Resultado:** La web oficial en la red pública y la vista previa del IDE/Hermes son idénticas y 100% funcionales.
