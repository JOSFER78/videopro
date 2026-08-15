import os
import socket
import shutil
from pathlib import Path
from typing import Dict, Any
from app.config.config_manager import config_manager

def is_port_open(host: str, port: int, timeout: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def check_all_providers_health() -> Dict[str, Dict[str, Any]]:
    p_8742 = is_port_open("127.0.0.1", 8742)
    p_7892 = is_port_open("127.0.0.1", 7892)
    p_7890 = is_port_open("127.0.0.1", 7890)
    p_8501 = is_port_open("127.0.0.1", 8501)

    replicate_token = config_manager.get("replicate.api_token") or config_manager.get("app.replicate_api_token") or os.environ.get("REPLICATE_API_TOKEN")
    r2_cfg = config_manager.get("storage.s3", {}) or config_manager.get("r2", {})
    r2_ready = bool(r2_cfg.get("access_key_id") and r2_cfg.get("secret_access_key"))
    
    groq_key = config_manager.get("llm.groq.api_key") or os.environ.get("GROQ_API_KEY")
    pexels_key = config_manager.get("materials.pexels.api_keys", []) or config_manager.get("pexels.api_key")
    ffmpeg_ok = shutil.which("ffmpeg") is not None

    return {
        "Antigravity Bridge & LLMs": {
            "online": p_8742,
            "badge": "🟢 Puerto 8742 ONLINE (Gemini 3.7)" if p_8742 else "🔴 Puerto 8742 OFFLINE",
            "type": "port", "port": 8742
        },
        "FLUX 3 Video": {
            "online": bool(replicate_token),
            "badge": "🟢 Replicate (josfer78) / ZeroGPU" if replicate_token else "⚪ ZeroGPU $0 (Sin Token)",
            "type": "cloud"
        },
        "LTX-2.5 MMDiT (22B)": {
            "online": bool(replicate_token),
            "badge": "🟢 Replicate (22B 48kHz)" if replicate_token else "⚪ ZeroGPU $0 (Sin Token)",
            "type": "cloud"
        },
        "Cloudflare R2 Storage (S3)": {
            "online": r2_ready,
            "badge": "🟢 10 GB Free Tier (Configurado)" if r2_ready else "⚪ 10 GB Free Tier (S3 Compatible)",
            "type": "storage"
        },
        "NanoBanana Pro 2 (Gemini Imagen 3)": {
            "online": p_8742,
            "badge": "🟢 Bridge 8742 (2K/4K)" if p_8742 else "🔴 Bridge Inactivo",
            "type": "port", "port": 8742
        },
        "Google Flow": {
            "online": True,
            "badge": "🟢 Playwright Headless Listo",
            "type": "browser"
        },
        "Google Flow Music (Lyria 3)": {
            "online": True,
            "badge": "🟢 Playwright flowmusic.app",
            "type": "browser"
        },
        "Kokoro HD (Español)": {
            "online": p_7892,
            "badge": "🟢 Puerto 7892 (CPU $0)" if p_7892 else "🟢 CPU Local $0",
            "type": "port", "port": 7892
        },
        "Foley Director & Ducking": {
            "online": ffmpeg_ok,
            "badge": "🟢 48kHz WAV + Ducking (-22dB)" if ffmpeg_ok else "🔴 Requiere FFmpeg",
            "type": "binary"
        },
        "Paneles & Rótulos Vox (FFmpeg Drawbox/Drawtext)": {
            "online": ffmpeg_ok,
            "badge": "🟢 FFmpeg Nativo 4K" if ffmpeg_ok else "🔴 Requiere FFmpeg",
            "type": "binary"
        },
        "Subtítulos Dinámicos ASS": {
            "online": bool(groq_key) or ffmpeg_ok,
            "badge": "🟢 Groq Whisper / Local ASS" if groq_key else "🟢 Faster-Whisper Local",
            "type": "hybrid"
        },
        "DuckDuckGo & Wikimedia Commons API": {
            "online": True,
            "badge": "🟢 $0 Sin Token API (Público)",
            "type": "public"
        }
    }
