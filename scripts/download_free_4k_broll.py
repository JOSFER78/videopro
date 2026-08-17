#!/usr/bin/env python3
"""
download_free_4k_broll.py — Ingestador de Recursos Visuales 4K Gratuitos (NASA & Wikimedia)
========================================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Busca y descarga recursos visuales 4K/HD gratuitos y de dominio público:
- NASA Open Data / Images API (Vídeos MP4 HD/4K y fotos de satélite, espacio, criogenia, láseres)
- Wikimedia Commons (con User-Agent institucional obligatorio, fotos e infografías de alta resolución)
Aplica la regla estricta R02_STRICT_5KB_GATE (> 5 KB) y registra hashes SHA-256 en project_manifest.json.
========================================================================================
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

WORKSPACE_ROOT = Path("/home/ubuntu/workspace/pro/hermes/10_videopro")
sys.path.insert(0, str(WORKSPACE_ROOT / "scripts"))

try:
    from video_storage_manager import VideoStorageManager, MIN_ASSET_SIZE_BYTES
except ImportError:
    MIN_ASSET_SIZE_BYTES = 5120

USER_AGENT_INSTITUTIONAL = "VideoProHermesBot/1.0 (https://videopro.hermes.ai; video-research@hermes.ai)"

BROLL_SEARCH_TARGETS = [
    {
        "category": "space_orbital",
        "nasa_query": "earth orbit",
        "wiki_query": "Earth from space orbit high resolution",
        "target_filename": "broll_nasa_earth_orbit_4k.mp4",
        "asset_type": "video"
    },
    {
        "category": "iss_laboratory",
        "nasa_query": "international space station laboratory",
        "wiki_query": "ISS Columbus laboratory interior",
        "target_filename": "broll_nasa_iss_station_lab.mp4",
        "asset_type": "video"
    },
    {
        "category": "satellite_aurora",
        "nasa_query": "aurora",
        "wiki_query": "Aurora Australis From ISS",
        "target_filename": "broll_nasa_aurora_orbital.mp4",
        "asset_type": "video"
    },
    {
        "category": "cryogenic_physics",
        "nasa_query": "cryogenic test",
        "wiki_query": "Superconducting magnet laboratory CERN",
        "target_filename": "broll_cryogenic_lab_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "cleanroom_silicon",
        "nasa_query": "cleanroom",
        "wiki_query": "Semiconductor cleanroom wafer silicon",
        "target_filename": "broll_cleanroom_silicon_wafer_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "deep_space_jwst",
        "nasa_query": "james webb space telescope mirror",
        "wiki_query": "James Webb Space Telescope primary mirror gold",
        "target_filename": "broll_jwst_gold_mirror_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "fusion_plasma",
        "nasa_query": "fusion energy experiment",
        "wiki_query": "EAST Tokamak plasma image3",
        "target_filename": "broll_tokamak_fusion_torus_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "supercomputer_servers",
        "nasa_query": "supercomputer pleiades",
        "wiki_query": "Pleiades supercomputer NASA Ames",
        "target_filename": "broll_supercomputer_datacenter_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "solar_array",
        "nasa_query": "solar array station",
        "wiki_query": "Solar array International Space Station",
        "target_filename": "broll_solar_array_orbital_4k.jpg",
        "asset_type": "image"
    },
    {
        "category": "telescope_array",
        "nasa_query": "atacama array telescope",
        "wiki_query": "ALMA antennas under the Milky Way",
        "target_filename": "broll_atacama_alma_telescope_4k.jpg",
        "asset_type": "image"
    }
]

def safe_url_quote(url: str) -> str:
    try:
        parts = urllib.parse.urlsplit(url)
        quoted_path = urllib.parse.quote(parts.path)
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, quoted_path, parts.query, parts.fragment))
    except Exception:
        return url.replace(" ", "%20")

def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def fetch_nasa_media(query: str, media_type: str = "video") -> Optional[Tuple[str, str]]:
    try:
        url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type={media_type}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT_INSTITUTIONAL})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("collection", {}).get("items", [])
            for item in items[:10]:
                d_list = item.get("data", [])
                if not d_list:
                    continue
                d = d_list[0]
                nasa_id = d.get("nasa_id", "")
                title = d.get("title", "")
                
                asset_url = f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nasa_id)}"
                req_a = urllib.request.Request(asset_url, headers={"User-Agent": USER_AGENT_INSTITUTIONAL})
                with urllib.request.urlopen(req_a, timeout=10) as resp_a:
                    a_data = json.loads(resp_a.read().decode("utf-8"))
                    asset_items = a_data.get("collection", {}).get("items", [])
                    
                    if media_type == "video":
                        mp4s = [f["href"] for f in asset_items if f.get("href", "").endswith(".mp4")]
                        if mp4s:
                            med_mp4s = [u for u in mp4s if "~medium.mp4" in u or "~large.mp4" in u or "~orig.mp4" in u]
                            chosen = med_mp4s[0] if med_mp4s else mp4s[0]
                            chosen = safe_url_quote(chosen.replace("http://", "https://"))
                            return chosen, title
                    else:
                        imgs = [f["href"] for f in asset_items if f.get("href", "").lower().endswith((".jpg", ".png", ".webp"))]
                        if imgs:
                            large_imgs = [u for u in imgs if "~large." in u or "~orig." in u or "~medium." in u]
                            chosen = large_imgs[0] if large_imgs else imgs[0]
                            chosen = safe_url_quote(chosen.replace("http://", "https://"))
                            return chosen, title
    except Exception as e:
        print(f"Error buscando en NASA ({query}): {e}")
    return None

def fetch_wikimedia_image(query: str) -> Optional[Tuple[str, str]]:
    try:
        url = (
            f"https://commons.wikimedia.org/w/api.php?action=query&format=json"
            f"&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}"
            f"&gsrlimit=8&prop=imageinfo&iiprop=url|size|mime"
        )
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT_INSTITUTIONAL})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                infos = page.get("imageinfo", [])
                if infos:
                    info = infos[0]
                    img_url = info.get("url")
                    title = page.get("title", "")
                    mime = info.get("mime", "")
                    if img_url and mime.startswith("image/"):
                        if not img_url.lower().endswith(".pdf") and not img_url.lower().endswith(".tiff"):
                            return safe_url_quote(img_url), title
    except Exception as e:
        print(f"Error buscando en Wikimedia ({query}): {e}")
    return None

def download_asset_safe(url: str, dest_path: Path, min_size: int = 5000) -> bool:
    temp_path = dest_path.with_suffix(".tmp")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    headers = {"User-Agent": USER_AGENT_INSTITUTIONAL}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=90) as resp, open(temp_path, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)
                
        file_size = temp_path.stat().st_size
        if file_size < min_size:
            print(f"Archivo descargado demasiado pequeno: {file_size} B < {min_size} B")
            if temp_path.exists():
                temp_path.unlink()
            return False
            
        temp_path.replace(dest_path)
        return True
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False

def verify_with_ffprobe(file_path: Path) -> Tuple[bool, Dict[str, Any]]:
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=width,height,codec_name,duration",
            "-of", "json",
            str(file_path)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        streams = data.get("streams", [])
        if not streams:
            return False, {"error": "No streams found"}
        s = streams[0]
        return True, {
            "width": s.get("width"),
            "height": s.get("height"),
            "codec": s.get("codec_name"),
            "duration": s.get("duration"),
            "size_bytes": file_path.stat().st_size
        }
    except Exception as e:
        return False, {"error": str(e)}

def ingest_broll_suite(project_vsm: VideoStorageManager) -> List[Dict[str, Any]]:
    print("================================================================================")
    print("INICIANDO INGESTA DE B-ROLL 4K/HD (NASA & WIKIMEDIA COMMONS)")
    print(f"   Proyecto: {project_vsm.project_id} (Version: {project_vsm.version})")
    print(f"   Directorio: {project_vsm.project_dir}")
    print("   User-Agent Institucional: Activado")
    print("   Estandar: R02_STRICT_5KB_GATE")
    print("================================================================================")

    downloaded_records: List[Dict[str, Any]] = []

    for idx, target in enumerate(BROLL_SEARCH_TARGETS, 1):
        cat = target["category"]
        asset_type = target["asset_type"]
        fn = target["target_filename"]
        print(f"\n[{idx:02d}/{len(BROLL_SEARCH_TARGETS):02d}] Procesando recurso: {cat} ({asset_type.upper()})...")

        media_url = None
        media_title = None
        source_engine = "nasa_open_data"

        nasa_res = fetch_nasa_media(target["nasa_query"], media_type=asset_type)
        if nasa_res:
            media_url, media_title = nasa_res
            source_engine = "nasa_images_api"
            print(f"   [OK] Encontrado en NASA: {media_title[:50]}...")
        else:
            wiki_res = fetch_wikimedia_image(target["wiki_query"])
            if wiki_res:
                media_url, media_title = wiki_res
                source_engine = "wikimedia_commons"
                print(f"   [OK] Encontrado en Wikimedia: {media_title[:50]}...")

        if not media_url:
            print(f"   [WARN] No se pudo obtener URL remota para {cat}")
            continue

        subfolder = "raw_clips" if asset_type == "video" else "assets"
        dest_path = project_vsm.get_asset_path(subfolder, fn)

        if dest_path.exists() and dest_path.stat().st_size >= MIN_ASSET_SIZE_BYTES:
            print(f"   [SKIP] Recurso ya existe en disco: {dest_path.name} ({dest_path.stat().st_size:,} bytes)")
            v_ok, probe_info = verify_with_ffprobe(dest_path)
            if v_ok:
                sha = compute_sha256(dest_path)
                record = {
                    "filename": fn,
                    "relative_path": str(dest_path.relative_to(project_vsm.project_dir)),
                    "absolute_path": str(dest_path),
                    "category": subfolder,
                    "asset_type": asset_type,
                    "source_engine": source_engine,
                    "source_url": media_url,
                    "title": media_title,
                    "size_bytes": dest_path.stat().st_size,
                    "sha256": sha,
                    "r02_gate": "PASSED",
                    "ffprobe_info": probe_info
                }
                downloaded_records.append(record)
                project_vsm.register_asset(
                    file_path=dest_path,
                    asset_type=subfolder,
                    source_engine=source_engine,
                    metadata=record
                )
                continue

        print(f"   [DOWNLOAD] Descargando desde: {media_url[:60]}...")
        success = download_asset_safe(media_url, dest_path, min_size=5000)

        if success:
            v_ok, probe_info = verify_with_ffprobe(dest_path)
            if v_ok and dest_path.stat().st_size >= MIN_ASSET_SIZE_BYTES:
                sha = compute_sha256(dest_path)
                print(f"   [R02_PASS] Tamano: {dest_path.stat().st_size:,} bytes | SHA: {sha[:12]}...")
                
                record = {
                    "filename": fn,
                    "relative_path": str(dest_path.relative_to(project_vsm.project_dir)),
                    "absolute_path": str(dest_path),
                    "category": subfolder,
                    "asset_type": asset_type,
                    "source_engine": source_engine,
                    "source_url": media_url,
                    "title": media_title,
                    "size_bytes": dest_path.stat().st_size,
                    "sha256": sha,
                    "r02_gate": "PASSED",
                    "ffprobe_info": probe_info
                }
                downloaded_records.append(record)
                
                project_vsm.register_asset(
                    file_path=dest_path,
                    asset_type=subfolder,
                    source_engine=source_engine,
                    metadata=record
                )
            else:
                print(f"   [FAIL] Fallo en verificacion ffprobe para {fn}: {probe_info}")
        else:
            print(f"   [FAIL] Fallo en descarga de {fn}")

    print("\n================================================================================")
    print(f"INGESTA DE B-ROLL COMPLETADA: {len(downloaded_records)} ACTIVOS VERIFICADOS (>5KB)")
    print("================================================================================")
    return downloaded_records

if __name__ == "__main__":
    os.environ["VIDEOPRO_PROJECTS_DIR"] = "/home/ubuntu/workspace/pro/hermes/10_videopro/storage/projects"
    vsm = VideoStorageManager(project_ref="documental_futurista_4k_40tomas_120s", auto_create=True)
    ingest_broll_suite(vsm)
