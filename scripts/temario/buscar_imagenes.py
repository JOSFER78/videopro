#!/usr/bin/env python3
"""
Asigna a cada frase del guion la imagen real que pide, desde Wikimedia Commons.

    python3 scripts/temario/buscar_imagenes.py <guion.json> [--candidatos N] [--solo-buscar]

Solo actúa sobre frases con visual de tipo «archivo» y `busqueda`, y solo descarga la imagen elegida
(1920 px de ancho) en templates/atlas/media/<CODIGO>/. Escribe en el guion `archivo`, `credito`,
`licencia` y `pagina`. Lo que ya tiene archivo no se toca, así que se puede relanzar.
Solo acepta dominio público, CC0, CC BY y CC BY-SA. Va despacio a propósito: Commons limita las
peticiones. Con --solo-buscar lista candidatos sin descargar. Solo librería estándar.
"""

import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MEDIA = RAIZ / "templates" / "atlas" / "media"
UA = {"User-Agent": "videopro-media-search/1.0 (educational history series; github.com/JOSFER78/videopro)"}
PAUSA = 4.0


def pedir(url, binario=False, intentos=4):
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                datos = r.read()
            return datos if binario else json.loads(datos.decode("utf-8"))
        except Exception:
            time.sleep(6 + 5 * i)
    return None


def licencia_valida(nombre):
    n = (nombre or "").lower()
    if not n or "nc" in n.split("-") or "nd" in n.split("-") or "fair" in n or "non-free" in n:
        return False
    return n.startswith(("public domain", "cc0", "cc by", "pd", "no restrictions")) or "cc-by" in n or "cc by" in n


def limpiar(texto, tope=44):
    texto = re.sub(r"<[^>]+>", "", texto or "")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:tope].rstrip(" ,;") if len(texto) > tope else texto


def candidatos(busqueda, cuantos):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 12,
        "gsrsearch": busqueda + " filetype:bitmap", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1920})
    datos = pedir(url)
    time.sleep(PAUSA)
    if not datos:
        return None
    paginas = sorted((datos.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    salida = []
    for p in paginas:
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        licencia = (meta.get("LicenseShortName") or {}).get("value", "")
        if info.get("mime") not in ("image/jpeg", "image/png") or info.get("width", 0) < 1000:
            continue
        if not licencia_valida(licencia):
            continue
        salida.append({
            "titulo": p["title"].replace("File:", ""), "url": info.get("thumburl") or info.get("url"),
            "pagina": info.get("descriptionurl", ""), "licencia": licencia,
            "autor": limpiar((meta.get("Artist") or {}).get("value", "")) or "Wikimedia Commons",
            "ancho": info.get("width"), "alto": info.get("height"),
        })
    return salida[:cuantos]


def slug(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", texto).strip("_")[:40]


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    solo_buscar = "--solo-buscar" in argv
    cuantos = int(argv[argv.index("--candidatos") + 1]) if "--candidatos" in argv else 4
    ruta = Path(args[0])
    guion = json.load(open(ruta, encoding="utf-8"))
    carpeta = MEDIA / guion["codigo"]
    carpeta.mkdir(parents=True, exist_ok=True)
    vistos, sin_imagen, n, usadas = {}, [], 0, set()
    for parte in guion["partes"]:
        for frase in parte["frases"]:
            if (frase.get("visual") or {}).get("pagina"):
                usadas.add(frase["visual"]["pagina"])
    for parte in guion["partes"]:
        for frase in parte["frases"]:
            v = frase.get("visual") or {}
            if v.get("tipo") != "archivo" or not v.get("busqueda") or v.get("descartada"):
                continue
            n += 1
            if v.get("archivo") and (RAIZ / "templates" / "atlas" / v["archivo"]).exists():
                continue
            clave = v["busqueda"].lower()
            if clave in vistos:                      # misma búsqueda: misma imagen
                v.update(vistos[clave])
                continue
            # si la búsqueda exacta no da nada, se prueba con menos palabras (el nombre propio va delante)
            palabras_busqueda = v["busqueda"].split()
            lista = None
            for corte in sorted({len(palabras_busqueda), min(3, len(palabras_busqueda)), min(2, len(palabras_busqueda))}, reverse=True):
                lista = candidatos(" ".join(palabras_busqueda[:corte]), max(cuantos, 8))
                if lista:
                    break
            # no repetir la misma foto en frases distintas del episodio mientras haya otra
            if lista:
                nuevas = [c for c in lista if c["pagina"] not in usadas]
                lista = nuevas or lista
            if lista is None:
                sin_imagen.append((n, v["busqueda"], "Commons no responde"))
                continue
            if solo_buscar:
                print(f"\n{n}. {v['que_se_ve']}  [{v['busqueda']}]")
                for c in lista:
                    print(f"     {c['ancho']}x{c['alto']} {c['licencia']:14} {c['titulo'][:60]}")
                continue
            if not lista:
                sin_imagen.append((n, v["busqueda"], "sin resultados con licencia válida"))
                continue
            elegido = lista[0]
            destino = carpeta / f"{n:02d}_{slug(v['busqueda'])}.jpg"
            datos = pedir(elegido["url"], binario=True)
            time.sleep(PAUSA)
            if not datos or datos[:2] != b"\xff\xd8" and datos[:4] != b"\x89PNG":
                sin_imagen.append((n, v["busqueda"], "la descarga falló"))
                continue
            destino.write_bytes(datos)
            asignado = {
                "archivo": str(destino.relative_to(RAIZ / "templates" / "atlas")),
                "credito": f"{limpiar(v['que_se_ve'], 46)} · Foto: {elegido['autor']} · {elegido['licencia']}",
                "licencia": elegido["licencia"], "pagina": elegido["pagina"],
                "alternativas": [c["pagina"] for c in lista[1:]],
            }
            v.update(asignado)
            vistos[clave] = asignado
            usadas.add(elegido["pagina"])
            print(f"{n:02d}  {elegido['licencia']:14} {elegido['titulo'][:64]}", flush=True)
            json.dump(guion, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not solo_buscar:
        json.dump(guion, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n{guion['codigo']}: {n} imágenes de archivo pedidas, {len(sin_imagen)} sin resolver")
    for item in sin_imagen:
        print("   SIN IMAGEN", item)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
