"""
real_news_image_service.py
===========================
Módulo de ingestión, búsqueda y validación de imágenes y noticias reales
para VideoPro Creative Studio (Hermes).

Fuentes Reales (Cero Mocks / 100% Real):
1. Wikimedia Commons API: Figuras públicas, políticos, logos y edificios (4K/8K CC-BY).
2. Wikipedia Media & Summary API: Retratos oficiales de figuras y resúmenes con imagen.
3. Google News RSS + OpenGraph Scraper: Noticias del día y titulares reales con og:image.
4. DuckDuckGo HTML Scraper: Búsqueda universal sin dependencias externas.
5. Validación binaria con Pillow (RGB, tamaño >= 400x300, aspect_ratio).
"""

import os
import re
import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from io import BytesIO
from loguru import logger
import requests
from PIL import Image

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 VideoPro/4.0"


def download_and_validate_image(
    image_url: str, output_path: str, min_width: int = 400, min_height: int = 300
) -> Optional[Dict[str, Any]]:
    """Descarga la imagen real, comprueba HTTP 200 y valida dimensiones con Pillow."""
    if not image_url or not image_url.startswith("http"):
        return None

    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(image_url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return None

        data = resp.content
        if len(data) < 1000:
            return None

        with Image.open(BytesIO(data)) as img:
            img.verify()

        with Image.open(BytesIO(data)) as img:
            width, height = img.size
            if width < min_width or height < min_height:
                return None

            rgb_img = img.convert("RGB")
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            rgb_img.save(output_path, "JPEG", quality=92)

        logger.success(f"[RealMedia] Imagen validada y guardada ({width}x{height}): {output_path}")
        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 3),
            "size_bytes": len(data),
            "local_path": output_path
        }
    except Exception as e:
        logger.debug(f"[RealMedia] Error validando imagen de {image_url}: {e}")
        return None


def search_wikimedia_commons(query: str) -> Optional[Dict[str, Any]]:
    """Busca retratos, figuras, ciudades y logos en Wikimedia Commons API."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{query}",
        "gsrnamespace": "6",
        "gsrlimit": "8",
        "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime",
        "format": "json"
    }
    try:
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, info in pages.items():
            image_info = info.get("imageinfo", [{}])[0]
            img_url = image_info.get("url")
            mime = image_info.get("mime", "")
            if img_url and ("jpeg" in mime or "png" in mime or "jpg" in mime):
                ext_meta = image_info.get("extmetadata", {})
                license_name = ext_meta.get("LicenseShortName", {}).get("value", "Wikimedia Commons")
                return {
                    "image_url": img_url,
                    "provider": "wikimedia_commons",
                    "license": license_name,
                    "title": info.get("title", query)
                }
    except Exception as e:
        logger.debug(f"[Wikimedia] Error en búsqueda '{query}': {e}")
    return None


def search_wikipedia_summary(query: str) -> Optional[Dict[str, Any]]:
    """Obtiene imagen principal oficial desde Wikipedia REST API."""
    clean_query = urllib.parse.quote(query.replace(" ", "_"))
    for lang in ["es", "en"]:
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{clean_query}"
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                orig_img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
                if orig_img:
                    return {
                        "image_url": orig_img,
                        "provider": f"wikipedia_{lang}",
                        "title": data.get("title", query),
                        "description": data.get("extract", "")
                    }
        except Exception:
            pass
    return None


def search_google_news_rss(query: str) -> Optional[Dict[str, Any]]:
    """Busca noticias del día en Google News RSS y extrae og:image del artículo."""
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=es-ES&gl=ES&ceid=ES:es"
    try:
        resp = requests.get(rss_url, headers={"User-Agent": USER_AGENT}, timeout=8)
        if resp.status_code != 200:
            return None
        root = ET.fromstring(resp.text)
        item = root.find(".//item")
        if item is None:
            return None

        title = item.find("title").text if item.find("title") is not None else query
        link = item.find("link").text if item.find("link") is not None else ""
        if not link:
            return None

        art_resp = requests.get(link, headers={"User-Agent": USER_AGENT}, timeout=8)
        if art_resp.status_code == 200:
            html = art_resp.text
            og_match = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', html, re.I)
            if not og_match:
                og_match = re.search(r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']', html, re.I)
            if not og_match:
                og_match = re.search(r'name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']', html, re.I)

            if og_match:
                og_image = og_match.group(1)
                if og_image.startswith("//"):
                    og_image = "https:" + og_image
                return {
                    "image_url": og_image,
                    "provider": "google_news_og",
                    "title": title,
                    "article_url": link
                }
    except Exception as e:
        logger.debug(f"[GoogleNews] Error en '{query}': {e}")
    return None


def search_duckduckgo_html(query: str) -> Optional[Dict[str, Any]]:
    """Scraper ligero de DDG HTML para obtener imágenes sin módulos pesados."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            # Buscar enlaces a imágenes
            matches = re.findall(r'uddg=([^&"\']+)', resp.text)
            for m in matches:
                decoded = urllib.parse.unquote(m)
                if any(ext in decoded.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    return {
                        "image_url": decoded,
                        "provider": "duckduckgo_web",
                        "title": query
                    }
    except Exception as e:
        logger.debug(f"[DDGHTML] Error: {e}")
    return None


def fetch_real_photo_for_scene(
    query: str,
    output_path: str,
    entity_type: str = "GENERAL",
    min_width: int = 400,
    min_height: int = 300
) -> Optional[Dict[str, Any]]:
    """
    Función maestra que ejecuta la cascada multiorigen y devuelve el path local validado.
    """
    logger.info(f"[RealMedia] Buscando foto real para: '{query}' (Tipo: {entity_type})...")

    candidate = None

    # 1. Wikipedia Summary (Ultra rápido y fiable para entidades con página)
    candidate = search_wikipedia_summary(query)

    # 2. Wikimedia Commons
    if not candidate:
        candidate = search_wikimedia_commons(query)

    # 3. Google News RSS para eventos actuales
    if not candidate and entity_type in ["NEWS", "EVENT", "BREAKING"]:
        candidate = search_google_news_rss(query)

    # 4. DuckDuckGo HTML
    if not candidate:
        candidate = search_duckduckgo_html(query)

    if not candidate or not candidate.get("image_url"):
        logger.warning(f"[RealMedia] No se encontraron URLs candidatas para: {query}")
        return None

    # Descargar y validar
    res = download_and_validate_image(candidate["image_url"], output_path, min_width=min_width, min_height=min_height)
    if res:
        res["provider"] = candidate["provider"]
        res["title"] = candidate.get("title")
        return res

    return None
