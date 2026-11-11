"""
free_media.py — Buscador de imagen y vídeo de uso libre, bajo demanda.

Regla de uso: aquí NO se descarga nada. Solo se busca, y solo cuando ya hay guion: cada plano del
guion trae su `media_query` y este módulo devuelve candidatos (enlace, licencia y crédito) para que
el montaje elija. La descarga la hace el pipeline en el momento de renderizar el plano elegido.

Fuentes sin clave (funcionan tal cual):
  nasa        vídeo y foto   dominio público          images-api.nasa.gov
  archive     vídeo          dominio público / CC     archive.org (filtrado por licencia)
  loc         foto           según ficha              Library of Congress
  artic       foto de obras  CC0                      Art Institute of Chicago
  openverse   foto           CC (uso comercial)       agrega Flickr, Wikimedia, museos

Fuentes con clave gratuita (ya integradas en app/services/material.py; claves en config.toml):
  pexels, pixabay, coverr    vídeo de stock

Fuentes opcionales con cuenta gratuita:
  apify       actores que buscan en Pexels/Mixkit/Openverse sin clave propia; el plan gratuito
              incluye un crédito mensual. También expone un servidor MCP (mcp.apify.com).
  unsplash    fotos; hay conector MCP para Claude.

Solo librería estándar.
"""

import json
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Callable, Dict, Iterable, List, Optional

USER_AGENT = "videopro-media-search/1.0"
TIMEOUT = 25


@dataclass
class Candidate:
    provider: str
    kind: str            # "video" | "image"
    title: str
    media_url: str       # enlace directo al archivo ("" si hay que abrir la ficha para obtenerlo)
    page_url: str        # ficha de origen, para comprobar la licencia
    license: str
    credit: str


def _get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _q(params: dict) -> str:
    return urllib.parse.urlencode(params)


# ---------------------------------------------------------------------------
# Lectores: convierten la respuesta de cada portal en candidatos. Sin red, para poder probarlos.
# ---------------------------------------------------------------------------

def parse_nasa(data: dict, kind: str) -> List[Candidate]:
    out = []
    for item in data.get("collection", {}).get("items", []):
        meta = (item.get("data") or [{}])[0]
        nasa_id = meta.get("nasa_id")
        if not nasa_id or meta.get("media_type") != kind:
            continue
        quoted = urllib.parse.quote(nasa_id)
        suffix = "~large.mp4" if kind == "video" else "~large.jpg"
        out.append(Candidate(
            provider="nasa", kind=kind, title=meta.get("title", ""),
            media_url=f"https://images-assets.nasa.gov/{kind}/{quoted}/{quoted}{suffix}",
            page_url=f"https://images.nasa.gov/details/{quoted}",
            license="Dominio público (NASA)",
            credit="NASA" + (f" / {meta['center']}" if meta.get("center") else ""),
        ))
    return out


def parse_archive(data: dict) -> List[Candidate]:
    out = []
    for doc in data.get("response", {}).get("docs", []):
        identifier = doc.get("identifier")
        if not identifier:
            continue
        out.append(Candidate(
            provider="archive", kind="video", title=str(doc.get("title", identifier)),
            media_url="",   # cada ficha lista sus archivos; se resuelve al elegir el plano
            page_url=f"https://archive.org/details/{urllib.parse.quote(identifier)}",
            license=str(doc.get("licenseurl", "")), credit="Internet Archive",
        ))
    return out


def parse_loc(data: dict) -> List[Candidate]:
    out = []
    for result in data.get("results", []):
        image = (result.get("image") or {}).get("full", "")
        if not image:
            continue
        links = result.get("links") or {}
        out.append(Candidate(
            provider="loc", kind="image", title=result.get("title", ""),
            media_url=image if image.startswith("http") else "https:" + image,
            page_url=links.get("item", ""),
            license="Ver derechos en la ficha (Library of Congress)",
            credit="Library of Congress" + (f" / {result['creator']}" if result.get("creator") else ""),
        ))
    return out


def parse_artic(data: dict) -> List[Candidate]:
    out = []
    for art in data.get("data", []):
        if not art.get("image_id") or not art.get("is_public_domain"):
            continue
        out.append(Candidate(
            provider="artic", kind="image", title=art.get("title", ""),
            media_url=f"https://www.artic.edu/iiif/2/{art['image_id']}/full/1686,/0/default.jpg",
            page_url=f"https://www.artic.edu/artworks/{art.get('id')}",
            license="CC0", credit="Art Institute of Chicago",
        ))
    return out


def parse_openverse(data: dict) -> List[Candidate]:
    out = []
    for result in data.get("results", []):
        if not result.get("url"):
            continue
        license_name = f"CC {result.get('license', '').upper()} {result.get('license_version') or ''}".strip()
        out.append(Candidate(
            provider="openverse", kind="image", title=result.get("title") or "",
            media_url=result["url"], page_url=result.get("foreign_landing_url", ""),
            license=license_name, credit=result.get("creator") or result.get("source", ""),
        ))
    return out


# ---------------------------------------------------------------------------
# Búsquedas (una llamada pequeña de texto por portal; no descargan ningún archivo)
# ---------------------------------------------------------------------------

def search_nasa(query: str, kind: str, limit: int) -> List[Candidate]:
    url = "https://images-api.nasa.gov/search?" + _q({"q": query, "media_type": kind, "page_size": limit})
    return parse_nasa(_get_json(url), kind)[:limit]


def search_archive(query: str, kind: str, limit: int) -> List[Candidate]:
    if kind != "video":
        return []
    q = f"({query}) AND mediatype:movies AND (licenseurl:*publicdomain* OR licenseurl:*creativecommons.org/licenses/by/*)"
    url = "https://archive.org/advancedsearch.php?" + _q(
        {"q": q, "rows": limit, "output": "json"}) + "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=licenseurl"
    return parse_archive(_get_json(url))[:limit]


def search_loc(query: str, kind: str, limit: int) -> List[Candidate]:
    if kind != "image":
        return []
    return parse_loc(_get_json("https://www.loc.gov/pictures/search/?" + _q({"q": query, "fo": "json"})))[:limit]


def search_artic(query: str, kind: str, limit: int) -> List[Candidate]:
    if kind != "image":
        return []
    url = "https://api.artic.edu/api/v1/artworks/search?" + _q({
        "q": query, "limit": limit, "fields": "id,title,image_id,is_public_domain",
        "query[term][is_public_domain]": "true"})
    return parse_artic(_get_json(url))[:limit]


def search_openverse(query: str, kind: str, limit: int) -> List[Candidate]:
    if kind != "image":
        return []
    url = "https://api.openverse.org/v1/images/?" + _q({"q": query, "license_type": "commercial", "page_size": limit})
    return parse_openverse(_get_json(url))[:limit]


PROVIDERS: Dict[str, Callable[[str, str, int], List[Candidate]]] = {
    "nasa": search_nasa,
    "archive": search_archive,
    "loc": search_loc,
    "artic": search_artic,
    "openverse": search_openverse,
}
# Orden de preferencia: primero lo que es dominio público sin condiciones
DEFAULT_ORDER = {"video": ["nasa", "archive"], "image": ["nasa", "artic", "openverse", "loc"]}


def search(query: str, kind: str = "video", providers: Optional[Iterable[str]] = None,
           limit: int = 5) -> Dict[str, object]:
    """Busca en los portales indicados. Un portal caído no tumba la búsqueda: queda en `errors`."""
    if kind not in DEFAULT_ORDER:
        raise ValueError(f"kind debe ser 'video' o 'image', no {kind!r}")
    candidates: List[Candidate] = []
    errors: Dict[str, str] = {}
    for name in (providers or DEFAULT_ORDER[kind]):
        if name not in PROVIDERS:
            errors[name] = "portal desconocido"
            continue
        try:
            candidates += PROVIDERS[name](query, kind, limit)
        except Exception as exc:        # red, límite de peticiones, respuesta inesperada
            errors[name] = str(exc)
    return {"query": query, "kind": kind, "candidates": [asdict(c) for c in candidates], "errors": errors}


def plan_media_for_script(scenes: Iterable[dict], limit: int = 3) -> List[dict]:
    """
    Para cada plano del guion que pida material de archivo (`media_query`), devuelve candidatos.

    Los planos sin `media_query` (por ejemplo, los que se recrean con Flow) se dejan sin tocar.
    No descarga nada: el resultado es la lista de enlaces entre los que elegir.
    """
    plan = []
    for index, scene in enumerate(scenes):
        query = str(scene.get("media_query", "")).strip()
        if not query:
            plan.append({"scene": index + 1, "skipped": "sin media_query"})
            continue
        found = search(query, scene.get("media_kind", "video"), scene.get("media_providers"), limit)
        plan.append({"scene": index + 1, **found})
    return plan
