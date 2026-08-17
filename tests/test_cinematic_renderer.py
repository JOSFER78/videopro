"""
test_cinematic_renderer.py
Pruebas Unitarias del Motor de Renderizado Cinemático FFmpeg, Subtítulos ASS y Auto-Ducking.
"""

import os
import sys
import unittest
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.cinematic_ffmpeg_renderer import CinematicFFmpegRenderer, CinematicSceneInput
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

    def test_ass_subtitles_builder(self):
        """Verifica que el generador de subtítulos ASS construya el formato Broadcast correcto."""
        renderer = CinematicFFmpegRenderer(width=1920, height=1080, fps=60)
        temp_ass = "/tmp/test_broadcast.ass"
        subs_data = [
            {"start_time": 0.0, "end_time": 3.5, "msg": "Prueba de subtítulo estilizado."},
            {"start_time": 3.6, "end_time": 7.0, "msg": "Segunda línea sin cajas negras."}
        ]
        out_path = renderer.build_ass_subtitles(subs_data, temp_ass)
        self.assertTrue(os.path.isfile(out_path))
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("BroadcastMain", content)
        self.assertIn("Prueba de subtítulo estilizado.", content)
        if os.path.exists(temp_ass):
            os.remove(temp_ass)


if __name__ == "__main__":
    unittest.main()
