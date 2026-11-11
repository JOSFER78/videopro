"""Pruebas del formato de episodio interactivo: guion, trabajos de vídeo y recuento de votos."""

import copy
import json
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.interactive_episode import (  # noqa: E402
    EpisodeError,
    build_video_jobs,
    estimate_flow_clips,
    extract_vote,
    load_episode,
    parse_episode,
    tally_votes,
)

PILOT = BASE_DIR / "data" / "interactive" / "ep01_pompeya.json"


class TestEpisodeScript(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(PILOT.read_text(encoding="utf-8"))

    def test_pilot_loads_and_builds_one_job_per_video(self):
        episode = load_episode(str(PILOT))
        jobs = build_video_jobs(episode)
        self.assertEqual([j["job_id"] for j in jobs], ["ep01_pompeya_main", "ep01_pompeya_A", "ep01_pompeya_B"])
        self.assertEqual(jobs[0]["end_screen_links"], ["ep01_pompeya_A", "ep01_pompeya_B"])
        # Cada rama enlaza a la otra, nunca a sí misma
        self.assertEqual(jobs[1]["end_screen_links"], ["ep01_pompeya_B"])
        self.assertIn("A) Por el puerto", jobs[0]["pinned_comment"])
        self.assertIn("Plinio el Joven", jobs[0]["description_footer"])

    def test_scenes_match_the_task_pipeline_format(self):
        scene = build_video_jobs(load_episode(str(PILOT)))[0]["scenes"][0]
        self.assertEqual(set(scene), {"mode", "prompt", "text", "duration", "image_reference"})
        self.assertTrue(scene["prompt"].startswith("First-person POV"))
        self.assertTrue(scene["text"].startswith("(con calma tensa)"))

    def test_flow_estimate_counts_every_generated_clip(self):
        estimate = estimate_flow_clips(build_video_jobs(load_episode(str(PILOT))), retries_per_clip=2)
        self.assertEqual(estimate["flow_clips"], 11)
        self.assertEqual(estimate["flow_generations"], 22)

    def test_rejects_scripts_that_cannot_be_published(self):
        cases = {
            "sin fuentes": lambda r: r.pop("sources"),
            "una sola opción": lambda r: r["options"].pop(),
            "opción repetida": lambda r: r["options"][1].update(key="a"),
            "clave fuera de A-D": lambda r: r["options"][1].update(key="Z"),
            "rama sin escenas": lambda r: r["options"][0].update(scenes=[]),
            "plano de Flow de 30 s": lambda r: r["scenes"][0].update(duration=30),
        }
        for name, mutate in cases.items():
            raw = copy.deepcopy(self.raw)
            mutate(raw)
            with self.subTest(name), self.assertRaises(EpisodeError):
                parse_episode(raw)


class TestVotes(unittest.TestCase):
    def test_extract_vote(self):
        keys = ["A", "B"]
        votes = {
            "A": "A", "b": "B", "b)": "B", "A!!!": "A", "Voto B": "B", "opción a": "A",
            "La B sin duda, por tierra": "B", "B - el mar es una trampa": "B",
            "a mí me gustó el vídeo": None,       # 'a' es preposición, no voto
            "Buen vídeo": None,
            "A o B, no sé": None,                 # nombra dos opciones
            "voto C": None,                       # opción que no existe en este episodio
            "": None,
        }
        for comment, expected in votes.items():
            with self.subTest(comment):
                self.assertEqual(extract_vote(comment, keys), expected)

    def test_tally_counts_one_vote_per_person(self):
        comments = [
            {"author": "u1", "text": "A"},
            {"author": "u2", "text": "voto B"},
            {"author": "u2", "text": "B"},        # segundo voto de la misma persona
            {"author": "u3", "text": "la b"},
            {"author": "u4", "text": "qué buen canal"},
        ]
        result = tally_votes(comments, ["A", "B"])
        self.assertEqual(result["counts"], {"A": 1, "B": 2})
        self.assertEqual(result["winner"], "B")
        self.assertEqual(result["total_votes"], 3)
        self.assertEqual(result["ignored"], 2)

    def test_tie_or_no_votes_has_no_winner(self):
        tie = tally_votes([{"author": "u1", "text": "A"}, {"author": "u2", "text": "B"}], ["A", "B"])
        self.assertIsNone(tie["winner"])
        self.assertIsNone(tally_votes([], ["A", "B"])["winner"])


if __name__ == "__main__":
    unittest.main()
