"""Pruebas del buscador de material libre: lectura de respuestas y plan por guion, sin red."""

import sys
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services import free_media  # noqa: E402


class TestParsers(unittest.TestCase):
    def test_nasa_builds_direct_links_and_filters_kind(self):
        data = {"collection": {"items": [
            {"data": [{"nasa_id": "Earth in 4K", "title": "Earth", "media_type": "video", "center": "JSC"}]},
            {"data": [{"nasa_id": "PIA1", "title": "Foto", "media_type": "image"}]},
            {"data": [{"title": "sin id", "media_type": "video"}]},
        ]}}
        videos = free_media.parse_nasa(data, "video")
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0].media_url,
                         "https://images-assets.nasa.gov/video/Earth%20in%204K/Earth%20in%204K~large.mp4")
        self.assertEqual(videos[0].credit, "NASA / JSC")
        self.assertEqual(free_media.parse_nasa(data, "image")[0].media_url[-10:], "~large.jpg")

    def test_artic_keeps_only_public_domain_with_image(self):
        data = {"data": [
            {"id": 1, "title": "Libre", "image_id": "abc", "is_public_domain": True},
            {"id": 2, "title": "Con derechos", "image_id": "def", "is_public_domain": False},
            {"id": 3, "title": "Sin imagen", "image_id": None, "is_public_domain": True},
        ]}
        found = free_media.parse_artic(data)
        self.assertEqual([c.title for c in found], ["Libre"])
        self.assertEqual(found[0].license, "CC0")

    def test_loc_openverse_archive(self):
        loc = free_media.parse_loc({"results": [
            {"title": "T. rex", "image": {"full": "//tile.loc.gov/x.jpg"}, "links": {"item": "https://loc.gov/i"}},
            {"title": "sin imagen", "image": {}}]})
        self.assertEqual(loc[0].media_url, "https://tile.loc.gov/x.jpg")
        ov = free_media.parse_openverse({"results": [
            {"title": "Cueva", "url": "https://x/y.jpg", "license": "by", "license_version": "4.0", "creator": "Ana"}]})
        self.assertEqual((ov[0].license, ov[0].credit), ("CC BY 4.0", "Ana"))
        ar = free_media.parse_archive({"response": {"docs": [{"identifier": "film_1", "title": "Film"}]}})
        self.assertEqual(ar[0].page_url, "https://archive.org/details/film_1")
        self.assertEqual(ar[0].media_url, "")


class TestSearchAndPlan(unittest.TestCase):
    def test_a_failing_portal_does_not_break_the_search(self):
        ok = [free_media.Candidate("artic", "image", "Obra", "u", "p", "CC0", "AIC")]
        with mock.patch.dict(free_media.PROVIDERS, {
                "nasa": mock.Mock(side_effect=OSError("HTTP 429")), "artic": mock.Mock(return_value=ok)}):
            result = free_media.search("cueva", "image", ["nasa", "artic", "inventado"])
        self.assertEqual([c["title"] for c in result["candidates"]], ["Obra"])
        self.assertEqual(result["errors"], {"nasa": "HTTP 429", "inventado": "portal desconocido"})

    def test_plan_only_searches_scenes_that_ask_for_archive_media(self):
        scenes = [
            {"text": "plano recreado con Flow"},
            {"text": "la Tierra", "media_query": "earth from orbit", "media_kind": "video"},
        ]
        fake = mock.Mock(return_value=[])
        with mock.patch.dict(free_media.PROVIDERS, {"nasa": fake, "archive": fake}):
            plan = free_media.plan_media_for_script(scenes)
        self.assertEqual(plan[0], {"scene": 1, "skipped": "sin media_query"})
        self.assertEqual(plan[1]["query"], "earth from orbit")
        self.assertEqual(fake.call_count, 2)          # un plano, dos portales de vídeo

    def test_rejects_unknown_kind(self):
        with self.assertRaises(ValueError):
            free_media.search("x", "audio")


if __name__ == "__main__":
    unittest.main()
