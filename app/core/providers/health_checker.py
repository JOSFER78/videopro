"""
Motor Unificado de Diagnóstico y Salud de Proveedores — VideoPro Studio
Arquitectura Local-First y de Diagnóstico Manual / Persistente (No en Tiempo Real en cada Render).

El estado de salud se almacena en disco ('storage/system/health_status.json').
Durante la navegación normal de la WebUI, se lee el estado guardado en < 0.1ms sin peticiones de red.
El usuario puede ejecutar el diagnóstico en vivo bajo demanda ('⚡ Diagnóstico Manual') o según cadencia (12h/24h).
"""

import os
import sys
import time
import json
import socket
import shutil
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

HEALTH_STORAGE_DIR = os.path.join(BASE_DIR, "storage", "system")
HEALTH_STORAGE_FILE = os.path.join(HEALTH_STORAGE_DIR, "health_status.json")

# Memoria RAM en caché para evitar lectura constante a disco
_RAM_CACHE: Optional[Dict[str, Any]] = None
_RAM_CACHE_TS: float = 0.0


def is_port_open(host: str, port: int, timeout: float = 0.15) -> bool:
    """Verifica si un puerto TCP local está escuchando con timeout ultracorto (150ms)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


# ==============================================================================
# VALIDADORES INDIVIDUALES DE PROVEEDORES (EJECUTADOS SOLO BAJO DEMANDA)
# ==============================================================================

def verify_gemini(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    t0 = time.time()
    try:
        import requests
        r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key.strip()}", timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"Conexión exitosa ({ms}ms) · Gemini 2.5/3.7", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            err_msg = r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
            return {"status": "error", "latency_ms": ms, "message": f"Error: {err_msg[:50]}", "badge": f"🔴 Inválida ({r.status_code})"}
    except Exception as ex:
        return {"status": "error", "message": f"Timeout/Error: {str(ex)[:35]}", "badge": "🔴 Error de red"}


def verify_groq(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    t0 = time.time()
    try:
        import requests
        r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key.strip()}"}, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"Conexión ultra-rápida ({ms}ms) · Llama 3.3 70B", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"Fallo Auth (HTTP {r.status_code})", "badge": f"🔴 Inválida ({r.status_code})"}
    except Exception as ex:
        return {"status": "error", "message": f"Error: {str(ex)[:35]}", "badge": "🔴 Error de red"}


def verify_openai(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    if key.strip().startswith("local-"):
        return {"status": "ok", "message": "Bridge Local Antigravity", "badge": "🟢 Local Bridge"}
    t0 = time.time()
    try:
        import requests
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key.strip()}"}, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"Verificado ({ms}ms) · GPT-4o / Whisper", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"Fallo (HTTP {r.status_code})", "badge": f"🔴 Inválida ({r.status_code})"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error de red"}


def verify_replicate(token: str) -> Dict[str, Any]:
    if not token or not token.strip():
        return {"status": "empty", "message": "Sin token (Usa ZeroGPU por defecto)", "badge": "⚪ ZeroGPU $0"}
    t0 = time.time()
    try:
        import requests
        r = requests.get("https://api.replicate.com/v1/account", headers={"Authorization": f"Bearer {token.strip()}"}, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            username = r.json().get("username", "josfer78")
            return {"status": "ok", "latency_ms": ms, "message": f"Clúster H100 Conectado ({username})", "badge": f"🟢 Conectado ({username})"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"Token inválido (HTTP {r.status_code})", "badge": "🔴 Token inválido"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error de red"}


def verify_pexels(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada", "badge": "⚪ Sin configurar"}
    t0 = time.time()
    try:
        import requests
        r = requests.get("https://api.pexels.com/v1/curated?per_page=1", headers={"Authorization": key.strip()}, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"Stock 4K Pexels Verificado ({ms}ms)", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"HTTP {r.status_code}", "badge": "🔴 Inválida"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error de red"}


def verify_elevenlabs(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Usa Kokoro HD $0)", "badge": "⚪ Sin configurar"}
    t0 = time.time()
    try:
        import requests
        r = requests.get("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": key.strip()}, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"ElevenLabs Cinema Verificado ({ms}ms)", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"HTTP {r.status_code}", "badge": "🔴 Inválida"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error de red"}


def verify_cloudflare_ai() -> Dict[str, Any]:
    cf_key = config.app.get("cloudflare_api_key", "").strip()
    cf_acc = config.app.get("cloudflare_account_id", "").strip()
    if not (cf_key and cf_acc):
        return {"status": "empty", "message": "Cloudflare Workers AI no configurado", "badge": "⚪ Sin configurar"}
    t0 = time.time()
    try:
        import requests
        url = f"https://api.cloudflare.com/client/v4/accounts/{cf_acc}/ai/models/search"
        headers = {"Authorization": f"Bearer {cf_key}"}
        r = requests.get(url, headers=headers, timeout=2.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            return {"status": "ok", "latency_ms": ms, "message": f"Workers AI Conectado ({ms}ms) · Llama/FLUX", "badge": f"🟢 Conectado ({ms}ms)"}
        else:
            return {"status": "error", "latency_ms": ms, "message": f"Fallo Cloudflare (HTTP {r.status_code})", "badge": "🔴 Error Auth"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error red"}


def verify_antigravity_bridge(endpoint: str = "http://127.0.0.1:8742/v1") -> Dict[str, Any]:
    p_8742 = is_port_open("127.0.0.1", 8742)
    if p_8742:
        return {"status": "ok", "message": "Antigravity Bridge Activo en puerto 8742 (Gemini 3.7 / NanoBanana Pro 2)", "badge": "🟢 Bridge Online (8742)"}
    gemini_k = config.app.get("gemini_api_key", "")
    if gemini_k:
        return {"status": "ok", "message": "Conectado vía Google AI Studio Cloud", "badge": "🟢 AI Studio Cloud"}
    return {"status": "error", "message": "Puerto 8742 inactivo y sin clave Gemini", "badge": "🔴 Offline"}


def verify_cloud_storage() -> Dict[str, Any]:
    ep = config.app.get("s3_endpoint", "").strip()
    acc = config.app.get("s3_access_key", "").strip()
    sec = config.app.get("s3_secret_key", "").strip()
    bkt = config.app.get("s3_bucket", "").strip()
    if not (ep and acc and sec and bkt):
        return {"status": "empty", "message": "Cloud Storage no configurado (Usa almacenamiento local)", "badge": "⚪ Almacenamiento Local"}
    try:
        import boto3
        from botocore.config import Config
        client_config = Config(signature_version="s3v4", connect_timeout=2, read_timeout=2, retries={"max_attempts": 1})
        s3 = boto3.client("s3", endpoint_url=ep, aws_access_key_id=acc, aws_secret_access_key=sec, config=client_config)
        s3.list_objects_v2(Bucket=bkt, MaxKeys=1)
        return {"status": "ok", "message": f"Bucket '{bkt}' conectado (Zero Egress)", "badge": "🟢 R2 Conectado"}
    except Exception as ex:
        return {"status": "error", "message": f"Fallo: {str(ex)[:40]}", "badge": "🔴 Error conexión"}


def verify_firebase() -> Dict[str, Any]:
    try:
        from app.services import firebase_sync
        st = firebase_sync.get_firebase_status()
        if st.get("connected"):
            return {"status": "ok", "message": f"Firestore conectado ({st.get('project_id', '')})", "badge": "🟢 Firestore Conectado"}
        return {"status": "error", "message": st.get("message", "Offline"), "badge": "🔴 Firestore Offline"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error"}


# ==============================================================================
# GESTOR DE PERSISTENCIA Y DIAGNÓSTICO EN PARALELO
# ==============================================================================

def _build_static_fast_baseline() -> Dict[str, Dict[str, Any]]:
    """Construye un estado base instantáneo (< 0.1ms) sin hacer ninguna llamada de red."""
    from app.core.providers import registry as prov_reg
    reg = prov_reg.load_registry()
    tombstones = prov_reg.load_deleted_providers()

    matrix = {}
    p_8742 = is_port_open("127.0.0.1", 8742)
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    npx_ok = shutil.which("npx") is not None

    for p_id, p_info in reg.items():
        if p_id in tombstones:
            continue
        name = p_info.get("name", p_id)
        cat = p_info.get("category", "")
        infra = p_info.get("infra_type", "cloud")
        is_enabled = bool(p_info.get("enabled", True))
        api_field = p_info.get("api_key_field")
        api_val = config.app.get(api_field, "") if api_field else ""

        if not is_enabled:
            matrix[p_id] = {
                "name": name,
                "category": cat,
                "status": "disabled",
                "badge": "⚪ Inactivo (Desactivado)",
                "message": "Deshabilitado en la Matriz"
            }
            continue

        if p_id in ("ffmpeg_core", "ffmpeg"):
            status_info = {
                "status": "ok" if ffmpeg_ok else "error",
                "badge": "🟢 FFmpeg 4K Nativo" if ffmpeg_ok else "🔴 FFmpeg No encontrado",
                "message": "Ensamble y ducking"
            }
        elif p_id in ("remotion_engine", "hyperframes_engine"):
            status_info = {
                "status": "ok" if npx_ok else "error",
                "badge": "🟢 Motor Listo ($0)" if npx_ok else "🔴 Node/npx No encontrado",
                "message": "Render React / Motion"
            }
        elif infra in ("local", "serverless", "local_headless"):
            status_info = {
                "status": "ok",
                "badge": "🟢 ZeroGPU / Local ($0)",
                "message": "Inferencia $0"
            }
        elif p_id in ("antigravity", "nanobanana"):
            status_info = {
                "status": "ok" if (p_8742 or config.app.get("gemini_api_key")) else "empty",
                "badge": "🟢 Bridge Online" if p_8742 else ("🟢 AI Studio Cloud" if config.app.get("gemini_api_key") else "⚪ Sin configurar"),
                "message": "Bridge local / Google Cloud"
            }
        elif api_field:
            if api_val and len(str(api_val).strip()) > 4:
                status_info = {
                    "status": "ok",
                    "badge": "🟢 Clave Registrada",
                    "message": f"Credencial activa para {name}"
                }
            else:
                status_info = {
                    "status": "empty",
                    "badge": "⚪ Sin configurar",
                    "message": "Falta clave API en Ajustes"
                }
        else:
            status_info = {
                "status": "ok",
                "badge": "🟢 Operativo",
                "message": "Operativo"
            }

        matrix[p_id] = {
            "name": name,
            "category": cat,
            **status_info
        }

    return matrix


def run_full_diagnostic() -> Dict[str, Any]:
    """
    Ejecuta el diagnóstico en vivo de todos los proveedores en paralelo con ThreadPoolExecutor.
    Guarda los resultados en 'storage/system/health_status.json' y actualiza la caché en RAM.
    """
    global _RAM_CACHE, _RAM_CACHE_TS

    from app.core.providers import registry as prov_reg
    reg = prov_reg.load_registry()
    tombstones = prov_reg.load_deleted_providers()

    matrix = {}
    tasks = {}

    p_8742 = is_port_open("127.0.0.1", 8742)
    ffmpeg_ok = shutil.which("ffmpeg") is not None
    npx_ok = shutil.which("npx") is not None

    with ThreadPoolExecutor(max_workers=8) as executor:
        for p_id, p_info in reg.items():
            if p_id in tombstones:
                continue
            name = p_info.get("name", p_id)
            cat = p_info.get("category", "")
            infra = p_info.get("infra_type", "cloud")
            is_enabled = bool(p_info.get("enabled", True))
            api_field = p_info.get("api_key_field")
            api_val = config.app.get(api_field, "") if api_field else ""

            if not is_enabled:
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "disabled",
                    "badge": "⚪ Inactivo (Desactivado)",
                    "message": "Deshabilitado por el usuario en la Matriz"
                }
                continue

            if p_id in ("antigravity", "nanobanana"):
                tasks[executor.submit(verify_antigravity_bridge, config.app.get("antigravity_endpoint", "http://127.0.0.1:8742/v1"))] = (p_id, name, cat)
            elif p_id == "gemini":
                tasks[executor.submit(verify_gemini, api_val)] = (p_id, name, cat)
            elif p_id == "groq":
                tasks[executor.submit(verify_groq, api_val)] = (p_id, name, cat)
            elif p_id == "openai":
                tasks[executor.submit(verify_openai, api_val)] = (p_id, name, cat)
            elif p_id in ("replicate", "flux_replicate", "ltx25"):
                tasks[executor.submit(verify_replicate, api_val)] = (p_id, name, cat)
            elif p_id == "pexels":
                tasks[executor.submit(verify_pexels, api_val)] = (p_id, name, cat)
            elif p_id == "elevenlabs":
                tasks[executor.submit(verify_elevenlabs, api_val)] = (p_id, name, cat)
            elif p_id == "cloudflare_ai":
                tasks[executor.submit(verify_cloudflare_ai)] = (p_id, name, cat)
            elif p_id == "r2_storage":
                tasks[executor.submit(verify_cloud_storage)] = (p_id, name, cat)
            elif p_id == "firebase_db":
                tasks[executor.submit(verify_firebase)] = (p_id, name, cat)
            elif p_id in ("ffmpeg_core", "ffmpeg"):
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "ok" if ffmpeg_ok else "error",
                    "badge": "🟢 FFmpeg 4K Nativo" if ffmpeg_ok else "🔴 FFmpeg No encontrado",
                    "message": "Ensamble, transiciones y ducking"
                }
            elif p_id in ("remotion_engine", "hyperframes_engine"):
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "ok" if npx_ok else "error",
                    "badge": "🟢 Motor Listo ($0)" if npx_ok else "🔴 Node/npx No encontrado",
                    "message": p_info.get("description", "Listo")
                }
            elif infra in ("local", "serverless", "local_headless"):
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "ok",
                    "badge": "🟢 ZeroGPU / Local ($0)",
                    "message": p_info.get("description", "Inferencia distribuida $0")
                }
            elif api_field:
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "ok" if api_val else "empty",
                    "badge": "🟢 Configurado" if api_val else "⚪ Sin configurar",
                    "message": f"Clave activa para {name}" if api_val else "Falta clave API"
                }
            else:
                matrix[p_id] = {
                    "name": name,
                    "category": cat,
                    "status": "ok",
                    "badge": "🟢 Operativo",
                    "message": "Operativo"
                }

        for fut in as_completed(tasks):
            p_id, name, cat = tasks[fut]
            try:
                res = fut.result()
            except Exception as ex:
                res = {"status": "error", "message": str(ex)[:35], "badge": "🔴 Error"}
            matrix[p_id] = {
                "name": name,
                "category": cat,
                **res
            }

    now_ts = time.time()
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    payload = {
        "last_checked_at": now_ts,
        "last_checked_str": now_str,
        "matrix": matrix
    }

    try:
        os.makedirs(HEALTH_STORAGE_DIR, exist_ok=True)
        with open(HEALTH_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    _RAM_CACHE = payload
    _RAM_CACHE_TS = now_ts
    return payload


def get_all_providers_matrix(force: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Obtiene la matriz de estado de proveedores.
    - force=False: Lee el estado persistido en disco/memoria en < 0.1ms (CERO peticiones de red).
    - force=True: Ejecuta el diagnóstico de red completo bajo demanda y guarda el resultado.
    """
    global _RAM_CACHE, _RAM_CACHE_TS

    if force:
        res = run_full_diagnostic()
        return res.get("matrix", {})

    # 1. Verificar si tenemos caché en memoria fresca
    if _RAM_CACHE and isinstance(_RAM_CACHE.get("matrix"), dict):
        return _RAM_CACHE["matrix"]

    # 2. Leer desde el archivo persistente en disco
    if os.path.isfile(HEALTH_STORAGE_FILE):
        try:
            with open(HEALTH_STORAGE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "matrix" in data and isinstance(data["matrix"], dict):
                _RAM_CACHE = data
                _RAM_CACHE_TS = data.get("last_checked_at", time.time())
                return data["matrix"]
        except Exception:
            pass

    # 3. Si nunca se ha ejecutado un diagnóstico, generar una base estática instantánea y guardarla
    baseline_matrix = _build_static_fast_baseline()
    now_ts = time.time()
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    payload = {
        "last_checked_at": now_ts,
        "last_checked_str": now_str,
        "matrix": baseline_matrix
    }
    try:
        os.makedirs(HEALTH_STORAGE_DIR, exist_ok=True)
        with open(HEALTH_STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    _RAM_CACHE = payload
    _RAM_CACHE_TS = now_ts
    return baseline_matrix


def get_health_meta() -> Dict[str, Any]:
    """Retorna los metadatos del último chequeo para la UI (fecha, tiempo transcurrido, contadores)."""
    matrix = get_all_providers_matrix(force=False)
    
    last_str = "Inicial"
    last_ts = _RAM_CACHE_TS if _RAM_CACHE_TS else time.time()
    
    if _RAM_CACHE and isinstance(_RAM_CACHE, dict):
        last_str = _RAM_CACHE.get("last_checked_str", last_str)
        last_ts = _RAM_CACHE.get("last_checked_at", last_ts)

    diff_sec = max(0, time.time() - last_ts)
    if diff_sec < 60:
        time_ago = "Hace unos segundos"
    elif diff_sec < 3600:
        mins = int(diff_sec / 60)
        time_ago = f"Hace {mins} min"
    elif diff_sec < 86400:
        hrs = int(diff_sec / 3600)
        time_ago = f"Hace {hrs}h"
    else:
        days = int(diff_sec / 86400)
        time_ago = f"Hace {days} días"

    total = len(matrix)
    active = sum(1 for v in matrix.values() if isinstance(v, dict) and ("🟢" in v.get("badge", "") or v.get("status") == "ok"))
    errors = sum(1 for v in matrix.values() if isinstance(v, dict) and ("🔴" in v.get("badge", "") or v.get("status") == "error"))
    unconfigured = sum(1 for v in matrix.values() if isinstance(v, dict) and ("⚪" in v.get("badge", "") or v.get("status") == "empty"))

    return {
        "last_checked_str": last_str,
        "time_ago": time_ago,
        "total": total,
        "active": active,
        "errors": errors,
        "unconfigured": unconfigured,
        "is_stale": diff_sec > 86400  # Sugerir refresco si lleva más de 24 horas
    }
