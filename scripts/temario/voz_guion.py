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


def parecido(a, b):
    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()


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
            coincidencia = json.load(open(meta))["coincidencia"]
        else:
            mejor = None
            for intento in range(3):
                torch.manual_seed(1000 + i * 17 + intento * 101)
                onda = tts.generate(dicho, language_id="es", exaggeration=frase.get("emocion", 0.5),
                                    cfg_weight=frase.get("cfg", 0.5))
                torchaudio.save(archivo + ".tmp.wav", onda, sr)
                partes, _ = oido.transcribe(archivo + ".tmp.wav", language="es")
                coincidencia = parecido(dicho, " ".join(p.text for p in partes))
                if mejor is None or coincidencia > mejor[1]:
                    mejor = (onda, coincidencia)
                if coincidencia >= 0.86:
                    break
            onda, coincidencia = mejor
            torchaudio.save(archivo, onda, sr)
            os.remove(archivo + ".tmp.wav")
            json.dump({"dicho": dicho, "coincidencia": coincidencia}, open(meta, "w"))
        if frase.get("pausa"):                       # silencio para la pregunta «pausa y piensa»
            seg = frase.get("pausa_seg", 2.8)
            trozos.append(silencio(seg)); t += seg
        dur = onda.shape[-1] / sr
        marca = {"start": round(t, 2), "end": round(t + dur, 2), "texto": frase["texto"], "coincidencia": round(coincidencia, 3)}
        if coincidencia < 0.86:
            marca["revisar"] = True
        marcas.append(marca)
        despues = frase.get("silencio_despues", 0.55)
        trozos += [onda, silencio(despues)]
        t += dur + despues
        print(f"{i + 1}/{len(frases)}  {dur:5.1f}s  coincidencia {coincidencia:.2f}  {'REVISAR' if coincidencia < 0.86 else ''}", flush=True)

    torchaudio.save(salida, torch.cat(trozos, dim=-1), sr)
    json.dump(marcas, open(salida + ".marcas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    malas = [m for m in marcas if m.get("revisar")]
    print(f"OK {salida}  {t:.0f}s  frases a revisar: {len(malas)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
