"""Pruebas del paso de guion + tiempos de voz a configuración de la plantilla."""

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("construir_config", BASE_DIR / "scripts" / "temario" / "construir_config.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

TEMARIO = {"temporadas": [{"temporada": 1, "titulo": "De dónde venimos", "episodios": [
    {"codigo": "T1-E00", "titulo": "El mapa"},
    {"codigo": "T1-E01", "titulo": "Nuestro origen", "cuando": {"texto": "hace 300.000 años", "anios_atras": 300000}},
    {"codigo": "T1-E02", "titulo": "Salimos de África", "cuando": {"texto": "hace 60.000 años", "anios_atras": 60000}},
]}]}
GUION = {"codigo": "T1-E01", "canal": "Temario", "tema": "Historia de la humanidad", "cola": 5,
         "indice": {"kicker": "Quédate con esto", "conclusion": "Tenemos 300.000 años."},
         "partes": [
             {"label": "El hallazgo", "titulo": "Un cráneo", "idea": "Marruecos, 1961", "frases": [
                 {"texto": "Unos mineros encontraron un cráneo.", "visual": {"archivo": "media/a.jpg", "credito": "Foto: X · CC BY"},
                  "lugar": {"nombre": "Jebel Irhoud", "pais": "Marruecos", "lon": -8.87, "lat": 31.85}, "anios_atras": 65},
                 {"texto": "Tenía trescientos mil años.", "pausa": "¿Qué edad le pondrías?", "anios_atras": 300000,
                  "dato": {"rotulo": "Edad", "valor": "300.000", "unidad": "años"}, "aprendido": "Tenemos 300.000 años"}]},
             {"label": "Repaso", "frases": [{"texto": "Quédate con esto."}]}]}
MARCAS = [{"start": 1.0, "end": 5.0}, {"start": 8.4, "end": 12.0}, {"start": 12.6, "end": 15.0}]


class TestConstruir(unittest.TestCase):
    def setUp(self):
        self.config = cc.construir(GUION, MARCAS, TEMARIO)

    def test_everything_lands_when_the_voice_says_it(self):
        c = self.config
        self.assertEqual(c["duration"], 20.0)
        self.assertEqual([p["at"] for p in c["parts"]], [0, 12.3])
        self.assertEqual(c["visuals"], [{"at": 0.7, "src": "media/a.jpg", "credit": "Foto: X · CC BY"}])
        self.assertEqual(c["map"]["places"][0]["at"], 1.5)
        self.assertEqual(c["data"][0]["at"], 9.4)
        # la pregunta ocupa el silencio anterior a la frase que da la respuesta
        self.assertEqual((c["asks"][0]["at"], c["asks"][0]["hold"]), (5.6, 2.7))
        self.assertEqual(c["learned"][0]["at"], 12.1)
        self.assertEqual(c["index"]["at"], 12.6)

    def test_journey_starts_today_and_never_travels_longer_than_available(self):
        journey = self.config["journey"]
        self.assertEqual(journey[0], {"at": 0, "yearsAgo": 10})
        self.assertEqual([j["yearsAgo"] for j in journey[1:]], [65, 300000])
        for prev, cur in zip(journey, journey[1:]):
            self.assertLessEqual(cur["travel"], cur["at"] - prev["at"])

    def test_season_with_episode_zero_numbers_from_00(self):
        c = self.config
        self.assertEqual([e["n"] for e in c["episodes"]], ["00", "01", "02"])
        self.assertEqual(c["episode"], 2)                      # posición del T1-E01 en la lista
        self.assertIsNone(c["episodes"][0]["yearsAgo"])
        self.assertEqual(c["season"], "Temporada 1 · De dónde venimos")

    def test_rejects_inconsistent_inputs(self):
        with self.assertRaises(cc.GuionError):
            cc.construir(GUION, MARCAS[:2], TEMARIO)            # falta una marca
        sin_credito = copy.deepcopy(GUION)
        del sin_credito["partes"][0]["frases"][0]["visual"]["credito"]
        with self.assertRaises(cc.GuionError):
            cc.construir(sin_credito, MARCAS, TEMARIO)
        sin_imagen = copy.deepcopy(GUION)
        del sin_imagen["partes"][0]["frases"][0]["visual"]
        with self.assertRaises(cc.GuionError):
            cc.construir(sin_imagen, MARCAS, TEMARIO)
        otro = copy.deepcopy(GUION); otro["codigo"] = "T1-E07"
        with self.assertRaises(cc.GuionError):
            cc.construir(otro, MARCAS, TEMARIO)
        solapadas = [{"start": 1.0, "end": 5.0}, {"start": 4.0, "end": 12.0}, {"start": 12.6, "end": 15.0}]
        with self.assertRaises(cc.GuionError):
            cc.construir(GUION, solapadas, TEMARIO)


if __name__ == "__main__":
    unittest.main()


class TestPaqueteYoutube(unittest.TestCase):
    def test_timestamps_use_on_screen_names_and_start_at_zero(self):
        spec2 = importlib.util.spec_from_file_location("paquete_youtube", BASE_DIR / "scripts" / "temario" / "paquete_youtube.py")
        py = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(py)
        config = {"channel": "Temario", "series": "Historia", "season": "Temporada 1",
                  "parts": [{"label": "El hallazgo", "at": 0}, {"label": "La fecha", "at": 4}, {"label": "Toda África", "at": 95.4},
                            {"label": "Repaso", "at": 200}]}
        guion = copy.deepcopy(GUION)
        guion["fuentes"] = [{"afirmacion": "Datación", "url": "https://example.org/a"}]
        guion["partes"][0]["frases"][0]["visual"]["pagina"] = "https://commons.wikimedia.org/x"
        with self.assertRaises(ValueError):
            py.paquete(guion, config)                               # sin bloque youtube
        guion["youtube"] = {"titulos": ["Uno", "Dos", "Tres"], "descripcion": "Texto.", "comentario": "¿Y tú?"}
        texto = py.paquete(guion, config)
        # la parte que empieza a los 4 s se omite: YouTube pide 10 s entre marcas
        self.assertEqual(py.marcas(config), [(0, "El hallazgo"), (95.4, "Toda África"), (200, "Repaso")])
        self.assertIn("0:00 El hallazgo\n1:35 Toda África\n3:20 Repaso", texto)
        self.assertIn("Foto: X · CC BY — https://commons.wikimedia.org/x", texto)
        self.assertIn("no hace falta", texto)


if __name__ == "__main__":
    unittest.main()
