"""
Audio Transcription Engine for VideoPro Subtitle Suite
=====================================================
Integrates OpenAI Whisper & Faster-Whisper for high-accuracy word-level
timestamp extraction from voiceover narration.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger


class AudioTranscriber:
    """
    Transcribes audio and extracts word-level timing for forced alignment.
    """

    def __init__(self, model_size: str = "base", language: str = "es"):
        self.model_size = model_size
        self.language = language
        self._model = None

    def _get_whisper_model(self):
        if self._model is None:
            try:
                import whisper
                logger.info(f"Loading Whisper model '{self.model_size}'...")
                self._model = whisper.load_model(self.model_size)
                logger.info("Whisper model loaded successfully.")
            except ImportError:
                logger.warning("Standard whisper package not available.")
                self._model = None
        return self._model

    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """
        Transcribes audio and returns segments with word-level timestamps.
        """
        audio_path = Path(audio_path).resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Attempt 1: Standard Whisper
        model = self._get_whisper_model()
        if model is not None:
            try:
                logger.info(f"Transcribing {audio_path.name} with Whisper (language={self.language})...")
                result = model.transcribe(
                    str(audio_path),
                    language=self.language,
                    word_timestamps=True,
                    fp16=False
                )
                logger.info(f"Transcription complete. Segments: {len(result.get('segments', []))}")
                return result
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")

        # Attempt 2: Faster-Whisper
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Attempting faster-whisper with model '{self.model_size}'...")
            fw_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = fw_model.transcribe(str(audio_path), language=self.language, word_timestamps=True)
            
            seg_list = []
            full_text = []
            for s in segments:
                words_data = []
                if s.words:
                    for w in s.words:
                        words_data.append({
                            "word": w.word,
                            "start": w.start,
                            "end": w.end,
                            "probability": w.probability
                        })
                seg_list.append({
                    "id": s.id,
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "words": words_data
                })
                full_text.append(s.text)

            return {
                "text": " ".join(full_text),
                "segments": seg_list,
                "language": info.language
            }
        except ImportError:
            logger.warning("faster-whisper not available.")
        except Exception as e:
            logger.error(f"faster-whisper failed: {e}")

        # Fallback: synthesize linear timing from audio duration
        logger.warning("Using fallback audio duration distributor.")
        duration = self._probe_duration(audio_path)
        return {
            "text": "",
            "segments": [
                {
                    "start": 0.0,
                    "end": duration,
                    "text": "",
                    "words": []
                }
            ],
            "language": self.language
        }

    @staticmethod
    def _probe_duration(audio_path: Path) -> float:
        """Probe audio file duration in seconds using ffprobe or wave."""
        try:
            import subprocess
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)]
            out = subprocess.check_output(cmd, text=True).strip()
            return float(out)
        except Exception:
            return 120.0
