#!/usr/bin/env python3
"""
Genera la locución de un guion frase a frase y la comprueba transcribiéndola.

    python voz_guion.py <guion.json> <salida.wav> [--desde N]

Requiere un entorno con chatterbox-tts y faster-whisper (no forman parte de las dependencias del repo).
Escribe <salida.wav> y <salida.wav>.marcas.json ([{start, end, texto, coincidencia}]). Cada frase se
guarda aparte en <salida>_frases/, así que una ejecución interrumpida continúa donde se quedó.
Una frase cuya transcripción se aleja del guion se repite con otra semilla (hasta 3 veces) y, si sigue
mal, queda señalada en las marcas con "revisar": true.
"""

import difflib
import json
import os
import re
import sys
import unicodedata


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", texto).split()


NUMEROS = set("""cero un uno una dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis
diecisiete dieciocho diecinueve veinte veintiun veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete
veintiocho veintinueve treinta cuarenta cincuenta sesenta setenta ochenta noventa cien ciento doscientos trescientos
cuatrocientos quinientos seiscientos setecientos ochocientos novecientos mil millon millones y por""".split())


def contenido(texto):
    # La transcripción escribe los números en cifras («1961») y el guion en letras: se comparan sin ellos
    return [p for p in normalizar(texto) if p not in NUMEROS and not p.isdigit()]


def parecido(a, b):
    """Parecido entre lo que se pidió decir y lo que se oye, y si el final de la frase está (la voz a veces lo corta)."""
    pedido, oido = contenido(a), contenido(b)
    if not pedido:
        return 1.0
    ratio = difflib.SequenceMatcher(None, pedido, oido).ratio()
    final = pedido[-1]
    llega_al_final = any(difflib.SequenceMatcher(None, final, palabra).ratio() >= 0.7 for palabra in oido[-4:])
    return ratio if llega_al_final else min(ratio, 0.5)


UMBRAL = 0.78


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    import torch
    import torchaudio
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    from faster_whisper import WhisperModel

    guion = json.load(open(argv[1], encoding="utf-8"))
    salida = argv[2]
    carpeta = salida[:-4] + "_frases"
    os.makedirs(carpeta, exist_ok=True)
    frases = [f for parte in guion["partes"] for f in parte["frases"]]

    tts = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    oido = WhisperModel("small", device="cpu", compute_type="int8")
    sr = tts.sr
    silencio = lambda seg: torch.zeros(1, int(sr * seg))

    trozos, marcas, t = [silencio(1.0)], [], 1.0
    for i, frase in enumerate(frases):
        archivo = os.path.join(carpeta, f"{i:03d}.wav")
        meta = archivo + ".json"
        # lo que se lee puede escribirse distinto de lo que se muestra (fechas, nombres extranjeros)
        dicho = frase.get("pronunciacion") or frase["texto"]
        if os.path.exists(archivo) and os.path.exists(meta) and json.load(open(meta))["dicho"] == dicho:
            onda, _ = torchaudio.load(archivo)
            guardado = json.load(open(meta))
            if "oido" not in guardado:                  # audio de una versión anterior: se vuelve a escuchar
                partes, _ = oido.transcribe(archivo, language="es")
                guardado["oido"] = " ".join(p.text for p in partes)
            coincidencia = parecido(dicho, guardado["oido"])
            json.dump({"dicho": dicho, "oido": guardado["oido"], "coincidencia": coincidencia}, open(meta, "w"))
        else:
            mejor = None
            for intento in range(3):
                torch.manual_seed(1000 + i * 17 + intento * 101)
                onda = tts.generate(dicho, language_id="es", exaggeration=frase.get("emocion", 0.5),
                                    cfg_weight=frase.get("cfg", 0.5))
                torchaudio.save(archivo + ".tmp.wav", onda, sr)
                partes, _ = oido.transcribe(archivo + ".tmp.wav", language="es")
                escuchado = " ".join(p.text for p in partes)
                coincidencia = parecido(dicho, escuchado)
                if mejor is None or coincidencia > mejor[1]:
                    mejor = (onda, coincidencia, escuchado)
                if coincidencia >= UMBRAL:
                    break
            onda, coincidencia, escuchado = mejor
            torchaudio.save(archivo, onda, sr)
            os.remove(archivo + ".tmp.wav")
            json.dump({"dicho": dicho, "oido": escuchado, "coincidencia": coincidencia}, open(meta, "w"))
        if frase.get("pausa"):                       # silencio para la pregunta «pausa y piensa»
            seg = frase.get("pausa_seg", 2.8)
            trozos.append(silencio(seg)); t += seg
        dur = onda.shape[-1] / sr
        marca = {"start": round(t, 2), "end": round(t + dur, 2), "texto": frase["texto"], "coincidencia": round(coincidencia, 3)}
        if coincidencia < UMBRAL:
            marca["revisar"] = True
        marcas.append(marca)
        despues = frase.get("silencio_despues", 0.55)
        trozos += [onda, silencio(despues)]
        t += dur + despues
        print(f"{i + 1}/{len(frases)}  {dur:5.1f}s  coincidencia {coincidencia:.2f}  {'REVISAR' if coincidencia < UMBRAL else ''}", flush=True)

    torchaudio.save(salida, torch.cat(trozos, dim=-1), sr)
    json.dump(marcas, open(salida + ".marcas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    malas = [m for m in marcas if m.get("revisar")]
    print(f"OK {salida}  {t:.0f}s  frases a revisar: {len(malas)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
