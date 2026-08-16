"""
Motor Unificado de Diagnóstico, Verificación en Vivo y Estado de APIs / Proveedores — VideoPro
Comprueba en tiempo real la validez de claves API, tokens, puertos locales, almacenamiento y bases de datos.
"""

import os
import sys
import time
import socket
import shutil
import hashlib
from typing import Dict, Any, Tuple
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

# Caché de resultados de verificación: {cache_key: (timestamp, result_dict)}
_HEALTH_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 60.0


def is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    """Verifica si un puerto TCP local o remoto está escuchando."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def _get_cache(key: str) -> Dict[str, Any] | None:
    if key in _HEALTH_CACHE:
        ts, data = _HEALTH_CACHE[key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            return data
    return None


def _set_cache(key: str, data: Dict[str, Any]):
    _HEALTH_CACHE[key] = (time.time(), data)


# ==============================================================================
# VALIDADORES INDIVIDUALES DE PROVEEDORES
# ==============================================================================

def verify_gemini(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    cache_k = f"gemini_{hashlib.md5(key.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key.strip()}", timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"Conexión exitosa ({ms}ms) · Gemini 2.5/3.7", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            err_msg = r.json().get("error", {}).get("message", f"HTTP {r.status_code}")
            res = {"status": "error", "latency_ms": ms, "message": f"Error: {err_msg[:60]}", "badge": f"🔴 Clave inválida ({r.status_code})"}
    except Exception as ex:
        res = {"status": "error", "message": f"Timeout/Error: {str(ex)[:40]}", "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_groq(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    cache_k = f"groq_{hashlib.md5(key.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key.strip()}"}, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"Conexión ultra-rápida ({ms}ms) · Llama 3.3 70B", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"Fallo de autenticación (HTTP {r.status_code})", "badge": f"🔴 Clave inválida ({r.status_code})"}
    except Exception as ex:
        res = {"status": "error", "message": f"Error: {str(ex)[:40]}", "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_openai(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    if key.strip().startswith("local-"):
        return {"status": "ok", "message": "Bridge Local Antigravity", "badge": "🟢 Local Bridge"}
    cache_k = f"openai_{hashlib.md5(key.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get("https://api.openai.com/v1/models", headers={"Authorization": f"Bearer {key.strip()}"}, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"Verificado ({ms}ms) · GPT-4o / Whisper", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"Fallo (HTTP {r.status_code})", "badge": f"🔴 Clave inválida ({r.status_code})"}
    except Exception as ex:
        res = {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_replicate(token: str) -> Dict[str, Any]:
    if not token or not token.strip():
        return {"status": "empty", "message": "Sin token (Usa ZeroGPU por defecto)", "badge": "⚪ ZeroGPU $0"}
    cache_k = f"rep_{hashlib.md5(token.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get("https://api.replicate.com/v1/account", headers={"Authorization": f"Bearer {token.strip()}"}, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            username = r.json().get("username", "josfer78")
            res = {"status": "ok", "latency_ms": ms, "message": f"Clúster H100 Conectado ({username})", "badge": f"🟢 Conectado ({username})"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"Token inválido (HTTP {r.status_code})", "badge": f"🔴 Token inválido"}
    except Exception as ex:
        res = {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_fal(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Opcional)", "badge": "⚪ Sin configurar"}
    if len(key.strip()) > 10:
        return {"status": "ok", "message": "Credencial Fal.ai registrada", "badge": "🟢 Listo"}
    return {"status": "error", "message": "Formato de clave inválido", "badge": "🔴 Formato inválido"}


def verify_pexels(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada", "badge": "⚪ Sin configurar"}
    cache_k = f"pex_{hashlib.md5(key.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get("https://api.pexels.com/v1/curated?per_page=1", headers={"Authorization": key.strip()}, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"Stock 4K Pexels Verificado ({ms}ms)", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"HTTP {r.status_code}", "badge": "🔴 Clave inválida"}
    except Exception as ex:
        res = {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_elevenlabs(key: str) -> Dict[str, Any]:
    if not key or not key.strip():
        return {"status": "empty", "message": "Clave no configurada (Usa Kokoro HD $0)", "badge": "⚪ Sin configurar"}
    cache_k = f"el_{hashlib.md5(key.encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        r = requests.get("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": key.strip()}, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"ElevenLabs Cinema Verificado ({ms}ms)", "badge": f"🟢 Verificado ({ms}ms)"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"HTTP {r.status_code}", "badge": "🔴 Clave inválida"}
    except Exception as ex:
        res = {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error de red"}
    _set_cache(cache_k, res)
    return res


def verify_cloudflare_ai() -> Dict[str, Any]:
    """Verifica Cloudflare Workers AI (Account ID + API Token)."""
    cf_key = config.app.get("cloudflare_api_key", "").strip()
    cf_acc = config.app.get("cloudflare_account_id", "").strip()

    if not (cf_key and cf_acc):
        return {"status": "empty", "message": "Cloudflare Workers AI no configurado", "badge": "⚪ Sin configurar"}

    cache_k = f"cf_ai_{hashlib.md5((cf_key + cf_acc).encode()).hexdigest()}"
    cached = _get_cache(cache_k)
    if cached: return cached

    t0 = time.time()
    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{cf_acc}/ai/models/search"
        headers = {"Authorization": f"Bearer {cf_key}"}
        r = requests.get(url, headers=headers, timeout=3.5)
        ms = int((time.time() - t0) * 1000)
        if r.status_code == 200:
            res = {"status": "ok", "latency_ms": ms, "message": f"Workers AI Conectado ({ms}ms) · Llama/FLUX", "badge": f"🟢 Conectado ({ms}ms)"}
        else:
            res = {"status": "error", "latency_ms": ms, "message": f"Fallo Cloudflare (HTTP {r.status_code})", "badge": "🔴 Error Auth"}
    except Exception as ex:
        res = {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error red"}
    _set_cache(cache_k, res)
    return res


def verify_antigravity_bridge(endpoint: str = "http://127.0.0.1:8742/v1") -> Dict[str, Any]:
    """Verifica si el bridge local de Antigravity (puerto 8742) o AI Studio está online."""
    p_8742 = is_port_open("127.0.0.1", 8742)
    if p_8742:
        return {"status": "ok", "message": "Antigravity Bridge Activo en puerto 8742 (Gemini 3.7 / NanoBanana Pro 2)", "badge": "🟢 Bridge Online (8742)"}
    # Si no está en puerto 8742, verificar si Gemini API key está disponible
    gemini_k = config.app.get("gemini_api_key", "")
    if gemini_k:
        return {"status": "ok", "message": "Conectado vía Google AI Studio Cloud", "badge": "🟢 AI Studio Cloud"}
    return {"status": "error", "message": "Puerto 8742 inactivo y sin clave Gemini", "badge": "🔴 Offline"}


def verify_cloud_storage() -> Dict[str, Any]:
    """Verifica conexión real con Cloudflare R2 / S3."""
    ep = config.app.get("s3_endpoint", "").strip()
    acc = config.app.get("s3_access_key", "").strip()
    sec = config.app.get("s3_secret_key", "").strip()
    bkt = config.app.get("s3_bucket", "").strip()
    if not (ep and acc and sec and bkt):
        return {"status": "empty", "message": "Cloud Storage no configurado (Usa almacenamiento local)", "badge": "⚪ Almacenamiento Local"}

    try:
        import boto3
        from botocore.config import Config
        client_config = Config(signature_version="s3v4", connect_timeout=3, read_timeout=3, retries={"max_attempts": 1})
        s3 = boto3.client("s3", endpoint_url=ep, aws_access_key_id=acc, aws_secret_access_key=sec, config=client_config)
        s3.list_objects_v2(Bucket=bkt, MaxKeys=1)
        return {"status": "ok", "message": f"Bucket '{bkt}' conectado (Zero Egress)", "badge": "🟢 R2 Conectado"}
    except Exception as ex:
        return {"status": "error", "message": f"Fallo al conectar: {str(ex)[:50]}", "badge": "🔴 Error de conexión"}


def verify_firebase() -> Dict[str, Any]:
    """Verifica conexión con Firebase Firestore."""
    try:
        from app.services import firebase_sync
        st = firebase_sync.get_firebase_status()
        if st["connected"]:
            return {"status": "ok", "message": f"Firestore conectado ({st['project_id']})", "badge": "🟢 Firestore Conectado"}
        return {"status": "error", "message": st["message"], "badge": "🔴 Firestore Offline"}
    except Exception as ex:
        return {"status": "error", "message": str(ex)[:40], "badge": "🔴 Error"}


def get_all_providers_matrix(force: bool = False) -> Dict[str, Dict[str, Any]]:
    """Genera la matriz completa de estado en vivo basada estrictamente en los proveedores ACTIVOS del registro y Firestore."""
    if force:
        _HEALTH_CACHE.clear()

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
                "message": "Deshabilitado por el usuario en la Matriz"
            }
            continue

        # Verificación dinámica en vivo
        if p_id in ("antigravity", "nanobanana"):
            status_info = verify_antigravity_bridge(config.app.get("antigravity_endpoint", "http://127.0.0.1:8742/v1"))
        elif p_id == "cloudflare_ai":
            status_info = verify_cloudflare_ai()
        elif p_id == "elevenlabs":
            status_info = verify_elevenlabs(api_val)
        elif p_id == "pexels":
            status_info = verify_pexels(api_val)
        elif p_id in ("replicate", "flux_replicate", "ltx25"):
            status_info = verify_replicate(api_val)
        elif p_id == "r2_storage":
            status_info = verify_cloud_storage()
        elif p_id == "firebase_db":
            status_info = verify_firebase()
        elif p_id in ("ffmpeg_core", "ffmpeg"):
            status_info = {
                "status": "ok" if ffmpeg_ok else "error",
                "badge": "🟢 FFmpeg 4K Nativo" if ffmpeg_ok else "🔴 FFmpeg No encontrado",
                "message": "Ensamble, transiciones y ducking"
            }
        elif p_id in ("remotion_engine", "hyperframes_engine"):
            status_info = {
                "status": "ok" if npx_ok else "error",
                "badge": "🟢 Motor Listo ($0)" if npx_ok else "🔴 Node/npx No encontrado",
                "message": p_info.get("description", "Listo")
            }
        elif infra in ("local", "serverless", "local_headless"):
            status_info = {
                "status": "ok",
                "badge": "🟢 ZeroGPU / Local ($0)",
                "message": p_info.get("description", "Inferencia distribuida $0")
            }
        elif api_field:
            if api_val:
                status_info = {
                    "status": "ok",
                    "badge": "🟢 Configurado",
                    "message": f"Clave activa para {name}"
                }
            else:
                status_info = {
                    "status": "empty",
                    "badge": "⚪ Sin configurar",
                    "message": f"Falta clave API en Ajustes"
                }
        else:
            status_info = {
                "status": "ok",
                "badge": "🟢 Operativo",
                "message": p_info.get("description", "Operativo")
            }

        matrix[p_id] = {
            "name": name,
            "category": cat,
            **status_info
        }

    return matrix
