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

## Decisión 4: Arquitectura Desacoplada FastAPI (8080) + Streamlit (7001) + ComfyUI Studio
- **Contexto:** Se requiere un motor API REST de alto rendimiento para automatización externa y una interfaz visual completa con editor de nodos estilo ComfyUI y suite de edición tipo Word.
- **Decisión:** El backend principal corre en FastAPI (`app.asgi:app`) en el puerto 8080 y la WebUI corre en Streamlit en el puerto 7001 con inyección dinámica del canvas ComfyUI.
- **Resultado:** Desacoplamiento total entre capa de control, capa de render y capa de presentación.

## Decisión 5: Persistencia Bidireccional en Firestore y Almacenamiento Cloudflare R2
- **Contexto:** Las configuraciones, catálogos de proveedores y estados de pipeline deben persistir en la nube para acceso multi-dispositivo y exportación sin coste por ancho de banda.
- **Decisión:** Usar Firestore en `ayuda-emilio-83261` (`videopro_settings`) como fuente de verdad en la nube con caché local en `storage/`, y Cloudflare R2 para másters MP4 con $0 egress.
- **Resultado:** Configuración resiliente, tolerante a fallos y sin costes de descarga.

## Decisión 6: Saneamiento Forense y Desactivación de Servicios en Bucle
- **Contexto:** Existía un servicio `videopro-v2.service` compitiendo por el puerto 7001 con más de 800 reinicios fallidos y copias de seguridad `.bak` en el repositorio.
- **Decisión:** Desactivar el unit file obsoleto, aislar los prototipos monolíticos en `legacy/` y purgar archivos `.bak` y `.log`.
- **Resultado:** Estabilidad absoluta de recursos en el VPS y repositorio 100% limpio.
