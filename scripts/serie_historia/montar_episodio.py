#!/usr/bin/env python3
"""
Monta un episodio de la serie de historia a partir del guion y de la voz ya grabada.

    python3 scripts/serie_historia/montar_episodio.py <guion.json> <carpeta_wav> <voz_salida.wav> <config_salida.json>

- El guion es data/serie_historia/epNN_*.json (una frase de locución = un archivo <id>.wav en la carpeta).
- Junta las frases con sus silencios (pausas de pregunta incluidas) en una sola pista de voz.
- Con los tiempos reales de cada frase escribe la configuración de templates/atlas/: partes, imágenes, mapa, dato,
  pausas, «Aprendido», eje e índice final. Aquí no se decide nada de contenido: todo sale del guion.

Solo librería estándar y ffmpeg.
"""
import array
import json
import math
import subprocess
import sys
import wave

SR = 48000
GAP = 0.55            # silencio entre frases
PART_IN = 1.6         # la parte se anuncia en pantalla antes de que empiece la voz
PART_OUT = 2.4        # respiro al cerrar la parte, con «Aprendido» todavía en pantalla
INTRO = 1.0
OUTRO = 3.5


def leer(path):
    """Frase a PCM de 16 bits, sin los silencios de los extremos y con el volumen igualado."""
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-ar", str(SR), "-ac", "1", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    x = array.array("h"); x.frombytes(raw)
    win = SR // 100                                   # ventanas de 10 ms
    rms = [math.sqrt(sum(v * v for v in x[i:i + win]) / win) for i in range(0, len(x) - win, win)]
    voz = [i for i, r in enumerate(rms) if r > 180]   # ≈ -45 dB
    if not voz:
        return raw
    x = x[max(0, voz[0] - 3) * win:(voz[-1] + 8) * win]
    activo = [r for r in rms if r > 180]
    nivel = math.sqrt(sum(r * r for r in activo) / len(activo))
    g = min(3300 / nivel, 30000 / max(1, max(abs(v) for v in x)))   # mismo volumen en todas las frases, sin saturar
    x = array.array("h", (int(v * g) for v in x))
    fade = SR // 100                                   # 10 ms de entrada y salida para que no haya chasquidos
    for i in range(min(fade, len(x))):
        x[i] = int(x[i] * i / fade); x[-1 - i] = int(x[-1 - i] * i / fade)
    return x.tobytes()


def main(guion_path, wav_dir, voz_out, config_out):
    G = json.load(open(guion_path, encoding="utf8"))
    pcm = bytearray()
    now = lambda: len(pcm) / 2 / SR
    silencio = lambda s: pcm.extend(b"\0\0" * int(round(s * SR)))
    t0, t1 = {}, {}                      # inicio y fin de cada frase
    partes = []

    silencio(INTRO)
    for p in G["partes"]:
        part_at = now()
        silencio(PART_IN)
        ask = p.get("pregunta_pausa")
        ask_at = None
        for s in p["locucion"]:
            t0[s["id"]] = now()
            pcm.extend(leer(f"{wav_dir}/{s['id']}.wav"))
            t1[s["id"]] = now()
            if ask and ask["despues_de"] == s["id"]:
                ask_at = now() + 0.25
                silencio(ask["segundos"] + 0.7)
            else:
                silencio(GAP)
        silencio(PART_OUT - GAP)
        partes.append((p, part_at, now(), ask_at))
    silencio(OUTRO)
    duration = round(now(), 2)

    with wave.open(voz_out, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(pcm))

    r = lambda x: round(x, 2)
    caps = [p for p in G["partes"] if p.get("step")]
    C = {
        "duration": duration,
        "series": G["serie"],
        "season": G["temporada_titulo"],
        "episode": G["episodio"],
        "episodes": [{"title": p["titulo"], "when": p["cuando"], "yearsAgo": p["anios_atras"], "idea": p.get("idea_indice", p["aprendido"]["texto"])} for p in caps],
        "parts": [], "visuals": [], "map": {"bounds": G["mapa_general"], "places": [], "views": []},
        "data": [], "asks": [], "learned": [], "journey": [{"at": 0, "yearsAgo": G["eje"]["to"]}],
        "axis": G["eje"],
    }
    for p, at, end, ask_at in partes:
        part = {"label": p["label"], "at": r(at), "title": p["titulo"], "idea": p["idea"], "kicker": p["kicker"]}
        if p.get("step"):
            part["step"] = p["step"]
            part["beats"] = [{"label": b["label"], "at": r(at if i == 0 else t0[b["desde"]] - 0.2)} for i, b in enumerate(p["beats"])]
        C["parts"].append(part)
        for i, v in enumerate(p.get("visuales", [])):
            vis = {"at": r(at if i == 0 else t0[v["desde"]] - 0.35), "src": v["archivo"], "credit": v["credito_pantalla"]}
            for k in ("focus", "zoom", "start"):
                if k in v: vis[k] = v[k]
            C["visuals"].append(vis)
        lugares = p.get("lugar") or []
        for l in ([lugares] if isinstance(lugares, dict) else lugares):
            l_at = r(max(at, t0[l["desde"]] - 0.3))
            C["map"]["places"].append({"at": l_at, "until": r(end), "name": l["nombre"], "where": l["pais"], "lon": l["lon"], "lat": l["lat"]})
            C["map"]["views"].append({"at": l_at, "bounds": l["encuadre"]})
        if lugares:
            C["map"]["views"].append({"at": r(end), "bounds": G["mapa_general"]})
        for j in p.get("viaje", []):
            C["journey"].append({"at": r(max(at + 0.2, t0[j["desde"]])), "yearsAgo": j["anios_atras"], "travel": 2.2})
        d = p.get("dato")
        if d:
            C["data"].append({"at": r(t0[d["desde"]] + 0.15), "until": r(end - 0.4), "label": d["rotulo"], "value": d["valor"], "unit": d["unidad"], "compare": d["comparacion"]})
        if ask_at is not None:
            a = p["pregunta_pausa"]
            C["asks"].append({"at": r(ask_at), "hold": a["segundos"], "kicker": a.get("rotulo", "Pausa y piensa"), "text": a["texto"]})
        ap = p.get("aprendido")
        if ap:
            C["learned"].append({"at": r(t0[ap["desde"]] + 0.3), "hold": r(end - t0[ap["desde"]] - 0.5), "text": ap["texto"]})
        idx = p.get("indice")
        if idx:
            C["index"] = {"at": r(at), "kicker": idx["rotulo"], "takeaway": idx["frases"][0]["texto"],
                          "takes": [{"at": r(at if i == 0 else t0[f["desde"]] - 0.2), "text": f["texto"]} for i, f in enumerate(idx["frases"])],
                          "rows": [{"at": r(t0[i] - 0.1)} for i in idx["filas_desde"]],
                          "nextAt": r(t0[idx["siguiente_desde"]])}
    C["journey"].sort(key=lambda j: j["at"])
    if "miniaturas" in G:
        C["thumbs"] = G["miniaturas"]
    json.dump(C, open(config_out, "w", encoding="utf8"), ensure_ascii=False, indent=1)

    # tiempos por parte, para las marcas de tiempo de YouTube
    for p, at, end, _ in partes:
        print(f"{int(at // 60)}:{int(at % 60):02d}  {p['titulo']}")
    print(f"duración {duration:.1f} s = {duration / 60:.2f} min")
    json.dump({"inicio": t0, "fin": t1}, open(config_out.replace(".json", ".tiempos.json"), "w"), indent=0)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
