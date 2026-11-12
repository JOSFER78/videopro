#!/usr/bin/env python3
"""Comprueba cuánto está usado un nombre de canal en YouTube.

    python3 comprobar_nombre.py Nombre [Otro ...]

Para cada nombre mira dos cosas:
  1. si existe un canal público en youtube.com/@Nombre (y variantes habituales);
  2. qué canales devuelve el buscador de YouTube, filtrado a canales, con ese nombre.

Límite importante: un 404 en @Nombre NO garantiza que el identificador esté libre.
YouTube también bloquea identificadores reservados o de cuentas inactivas, y eso solo se
ve al intentar cogerlo desde una cuenta. Las palabras sueltas y corrientes suelen estar cogidas.
"""
import json, re, subprocess, sys, time, urllib.parse

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
SUFIJOS = ["", "Explains", "Explained", "Docs", "Series", "Channel", "TV", "HQ", "Official"]


def bajar(url):
    r = subprocess.run(["curl", "-s", "-L", "-A", UA, "-H", "Accept-Language: en", "-w", "\n%{http_code}", url],
                       capture_output=True, text=True, errors="ignore")
    cuerpo, _, codigo = r.stdout.rpartition("\n")
    return codigo.strip(), cuerpo


def canal_en(handle):
    codigo, html = bajar(f"https://www.youtube.com/@{handle}")
    if codigo != "200":
        return None
    titulo = re.search(r"<title>([^<]*)", html)
    subs = re.findall(r"([\d.,]+[KM]? subscribers)", html)
    desc = re.search(r'"description":"((?:[^"\\]|\\.){0,140})', html)
    return {"handle": handle, "titulo": (titulo.group(1) if titulo else "").replace(" - YouTube", "").strip(),
            "subs": subs[0] if subs else "?", "desc": (desc.group(1) if desc else "").replace("\\n", " ")[:140]}


def buscar_canales(nombre):
    q = urllib.parse.quote(nombre)
    _, html = bajar(f"https://www.youtube.com/results?search_query={q}&sp=EgIQAg%253D%253D")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        return None
    salida = []

    def recorrer(o):
        if isinstance(o, dict):
            c = o.get("channelRenderer")
            if c:
                t = c.get("title", {}).get("simpleText", "")
                s = c.get("videoCountText", {}).get("simpleText") or c.get("subscriberCountText", {}).get("simpleText", "")
                salida.append((t, s))
            for v in o.values():
                recorrer(v)
        elif isinstance(o, list):
            for v in o:
                recorrer(v)
    try:
        recorrer(json.loads(m.group(1)))
    except Exception:
        return None
    return salida


for nombre in sys.argv[1:]:
    compacto = re.sub(r"[^A-Za-z0-9]", "", nombre)
    print(f"\n=== {nombre}")
    usados = []
    for suf in SUFIJOS:
        c = canal_en(compacto + suf)
        if c:
            usados.append(c)
        time.sleep(0.5)
    print(f"  Identificadores con canal público ({len(usados)} de {len(SUFIJOS)} variantes probadas):")
    for c in usados:
        print(f"    @{c['handle']} · «{c['titulo']}» · {c['subs']} · {c['desc']}")
    if not any(c["handle"].lower() == compacto.lower() for c in usados):
        print(f"    @{compacto}: sin canal público (puede estar reservado igualmente; solo YouTube lo confirma)")
    r = buscar_canales(nombre)
    if r is None:
        print("  Buscador de canales: no se pudo leer")
    else:
        igual = [x for x in r if compacto.lower() in re.sub(r"[^a-z0-9]", "", x[0].lower())]
        print(f"  Buscador de canales: {len(r)} resultados, {len(igual)} llevan el nombre:")
        for t, s in igual[:12]:
            print(f"    «{t}» · {s}")
