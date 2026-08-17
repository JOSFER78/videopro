"""
app/core/copilot/voice_transcriber.py
================================================================================
TRANSCRIPTOR DE AUDIO Y MENSAJES DE VOZ PARA EL COASISTENTE CONVERSACIONAL
================================================================================
Utiliza Faster-Whisper local (o Whisper API como fallback) para convertir notas de
voz del usuario en texto para el chat conversacional.
"""

import io
import os
import tempfile
from typing import Optional
from loguru import logger
from app.config import config


class VoiceTranscriber:
    """Manejador de transcripción de audio a texto para el asistente conversacional."""

    _whisper_model = None

    @classmethod
    def get_whisper_model(cls, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """Carga en caché el modelo Faster-Whisper."""
        if cls._whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"Cargando modelo Faster-Whisper '{model_size}' en {device}...")
                cls._whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
            except Exception as e:
                logger.warning(f"No se pudo cargar Faster-Whisper: {e}")
                cls._whisper_model = None
        return cls._whisper_model

    @classmethod
    def transcribe_audio_bytes(cls, audio_bytes: bytes, language: Optional[str] = "es") -> str:
        """Transcribe un buffer de bytes de audio (grabado con micrófono o subido)."""
        if not audio_bytes or len(audio_bytes) < 100:
            return ""

        # Intentar con Faster-Whisper local
        try:
            model = cls.get_whisper_model()
            if model is not None:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name

                try:
                    segments, _ = model.transcribe(tmp_path, language=language, beam_size=5)
                    text = " ".join([seg.text.strip() for seg in segments]).strip()
                    if text:
                        return text
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"Error en transcripción local con Faster-Whisper: {e}")

        # Fallback con OpenAI Whisper API si hay clave configurada
        openai_key = config.app.get("openai_api_key", "")
        if openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "audio.wav"
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
                return transcript.text.strip()
            except Exception as e:
                logger.warning(f"Error en transcripción OpenAI Whisper: {e}")

        return ""
