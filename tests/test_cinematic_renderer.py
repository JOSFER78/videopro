"""
test_cinematic_renderer.py
Pruebas Unitarias del Motor de Renderizado Cinemático FFmpeg, Subtítulos ASS y Auto-Ducking.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.cinematic_ffmpeg_renderer import (
    CinematicFFmpegRenderer,
    CinematicSceneInput,
    levenshtein_char_distance,
    word_similarity
)
from app.core.orchestration.videopro_system_registry import SYSTEM_WORKFLOWS, SYSTEM_NODES, SYSTEM_CAPABILITIES
from app.services.learning_memory_engine import learning_engine


class TestCinematicRendererAndOntology(unittest.TestCase):

    def test_ontology_vox_integration(self):
        """Verifica que el arquetipo VOX y sus capacidades asociadas estén en el registro maestro."""
        self.assertIn("workflow_vox_investigative_doc", SYSTEM_WORKFLOWS)
        self.assertIn("node_04_composicion_3d_parallax", SYSTEM_NODES)
        self.assertIn("cap_vox_paper_parallax_3d", SYSTEM_CAPABILITIES)
        self.assertIn("cap_vox_cinematic_map_3d", SYSTEM_CAPABILITIES)
        self.assertIn("cap_kinetic_word_subtitles", SYSTEM_CAPABILITIES)
        self.assertIn("cap_stagger_psicoacustico_motion", SYSTEM_CAPABILITIES)

    def test_learning_memory_rules_count(self):
        """Verifica que el motor de aprendizaje tenga las 10 reglas áureas canónicas."""
        lessons = learning_engine.get_all_lessons()
        self.assertGreaterEqual(len(lessons), 10)
        rule_ids = [l.id for l in lessons]
        self.assertIn("rule_stagger_entry_3frames", rule_ids)
        self.assertIn("rule_paper_texture_tint", rule_ids)
        self.assertIn("rule_map_dashed_route_78", rule_ids)
        self.assertIn("rule_z_axis_offset_0001", rule_ids)

    def test_levenshtein_distance_and_similarity(self):
        """Verifica los algoritmos de distancia de Levenshtein y similitud léxica."""
        self.assertEqual(levenshtein_char_distance("Madrid", "madrid"), 0)
        self.assertEqual(levenshtein_char_distance("qanats", "canales"), 3)
        self.assertGreater(word_similarity("subterráneo", "subterraneo"), 0.8)
        self.assertLess(word_similarity("oro", "plata"), 0.4)

    def test_levenshtein_forced_alignment(self):
        """Verifica que la alineación forzada Levenshtein alinee texto del guion con marcas de audio."""
        renderer = CinematicFFmpegRenderer(width=1920, height=1080, fps=60)
        script_text = "El laberinto subterráneo de Madrid oculta canales persas del año 854."
        whisper_tokens = [
            {"word": "el", "start": 0.1, "end": 0.3},
            {"word": "laberinto", "start": 0.3, "end": 0.9},
            {"word": "subterráneo", "start": 0.9, "end": 1.6},
            {"word": "de", "start": 1.6, "end": 1.8},
            {"word": "madrid", "start": 1.8, "end": 2.3},
            {"word": "oculta", "start": 2.4, "end": 2.9},
            {"word": "canales", "start": 2.9, "end": 3.4},
            {"word": "persas", "start": 3.4, "end": 3.9},
            {"word": "del", "start": 3.9, "end": 4.1},
            {"word": "año", "start": 4.1, "end": 4.4},
            {"word": "854", "start": 4.4, "end": 5.1},
        ]
        cues = renderer.align_script_with_timestamps(script_text, whisper_tokens, max_words_per_cue=5)
        self.assertGreater(len(cues), 0)
        self.assertTrue(any("laberinto" in c["text"] for c in cues))
        self.assertTrue(any("854" in c["text"] for c in cues))
        self.assertLessEqual(cues[0]["start_time"], 0.5)

    def test_ass_subtitles_builder(self):
        """Verifica que el generador de subtítulos ASS construya el formato Broadcast y Gold Cinema."""
        renderer = CinematicFFmpegRenderer(width=1920, height=1080, fps=60)
        with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as tf:
            temp_ass = tf.name

        subs_data = [
            {"start_time": 0.0, "end_time": 3.5, "msg": "Prueba de subtítulo estilizado."},
            {"start_time": 3.6, "end_time": 7.0, "msg": "Segunda línea sin cajas negras."}
        ]
        out_path = renderer.build_ass_subtitles(subs_data, temp_ass, style_mode="gold_cinema")
        self.assertTrue(os.path.isfile(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("BroadcastMain", content)
        self.assertIn("GoldCinema", content)
        self.assertIn("&H0000D7FF", content)  # Color Oro #FFD700
        self.assertIn("Prueba de subtítulo estilizado.", content)
        if os.path.exists(temp_ass):
            os.remove(temp_ass)

    def test_srt_subtitles_builder(self):
        """Verifica la generación correcta de archivos SRT estándar."""
        renderer = CinematicFFmpegRenderer(width=1920, height=1080, fps=60)
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tf:
            temp_srt = tf.name

        subs_data = [
            {"start_time": 1.0, "end_time": 4.5, "msg": "Subtítulo en formato SRT."}
        ]
        out_path = renderer.build_srt_subtitles(subs_data, temp_srt)
        self.assertTrue(os.path.isfile(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("00:00:01,000 --> 00:00:04,500", content)
        self.assertIn("Subtítulo en formato SRT.", content)
        if os.path.exists(temp_srt):
            os.remove(temp_srt)


if __name__ == "__main__":
    unittest.main()
