"""
Módulo de Sincronización y Persistencia con Firebase Firestore — VideoPro Studio
Permite persistir configuraciones globales, claves API, proyectos y estado en Firestore.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config
from app.config.config_manager import config_manager

logger = logging.getLogger("videopro.firebase")

DEFAULT_PROJECT_ID = "ayuda-emilio-83261"
HOSTING_URL = "https://videopro-studio.web.app"


def _get_firebase_auth_token():
    """Obtiene un token de acceso OAuth2 válido desde configstore o entorno."""
    token_from_env = os.environ.get("FIREBASE_AUTH_TOKEN")
    if token_from_env:
        return token_from_env

    config_path = os.path.expanduser("~/.config/configstore/firebase-tools.json")
    if not os.path.isfile(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        tokens = cfg.get("tokens", {})
        access_token = tokens.get("access_token")
        expires_at = tokens.get("expires_at", 0)

        # Si el token no ha expirado
        if access_token and (expires_at > time.time() * 1000 or expires_at == 0):
            return access_token

        # Si ha expirado, intentar refrescarlo
        import subprocess
        try:
            subprocess.run(["npx", "-y", "firebase-tools", "projects:list"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
            with open(config_path, "r", encoding="utf-8") as f:
                cfg_refreshed = json.load(f)
            new_tok = cfg_refreshed.get("tokens", {}).get("access_token")
            if new_tok:
                return new_tok
        except Exception:
            pass

        return access_token
    except Exception as ex:
        logger.error(f"Error al obtener token Firebase: {ex}")
        return None


def get_firebase_status():
    """Retorna el estado de conexión con Firebase Firestore y Hosting."""
    token = _get_firebase_auth_token()
    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID

    if not token:
        return {
            "connected": False,
            "project_id": project_id,
            "hosting_url": HOSTING_URL,
            "message": "Token de autenticación Firebase no disponible."
        }

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/status",
            headers=headers,
            timeout=6
        )
        if resp.status_code in (200, 404):
            return {
                "connected": True,
                "project_id": project_id,
                "hosting_url": HOSTING_URL,
                "message": f"Conectado con Firestore en proyecto '{project_id}'."
            }
        else:
            return {
                "connected": False,
                "project_id": project_id,
                "hosting_url": HOSTING_URL,
                "message": f"Respuesta inesperada de Firestore (HTTP {resp.status_code})."
            }
    except Exception as ex:
        return {
            "connected": False,
            "project_id": project_id,
            "hosting_url": HOSTING_URL,
            "message": f"Error de conexión: {ex}"
        }


def save_settings_to_firebase():
    """Persiste la configuración completa de VideoPro en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Serializar config.app de forma segura
    app_data = {}
    for k, v in config.app.items():
        if isinstance(v, (str, int, float, bool)):
            app_data[k] = v
        elif isinstance(v, list):
            app_data[k] = json.dumps(v)
        elif isinstance(v, dict):
            app_data[k] = json.dumps(v)

    firestore_fields = {
        "updated_at": {"stringValue": datetime.now().isoformat()},
        "app_name": {"stringValue": "VideoPro Creative Studio"},
        "hosting_url": {"stringValue": HOSTING_URL},
        "config_json": {"stringValue": json.dumps(app_data, ensure_ascii=False)}
    }

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_settings/global_config"
        resp = requests.patch(url, headers=headers, json={"fields": firestore_fields}, timeout=10)
        if resp.status_code == 200:
            return True, "Configuraciones guardadas y sincronizadas en Firebase Firestore."
        else:
            return False, f"Error al guardar en Firestore (HTTP {resp.status_code}): {resp.text}"
    except Exception as ex:
        return False, f"Error al conectar con Firestore: {ex}"


def load_settings_from_firebase():
    """Descarga y aplica la configuración guardada en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_settings/global_config"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return False, f"No se encontró configuración previa en Firestore (HTTP {resp.status_code})."

        doc = resp.json()
        fields = doc.get("fields", {})
        config_json_str = fields.get("config_json", {}).get("stringValue", "{}")
        app_data = json.loads(config_json_str)

        for k, v in app_data.items():
            if isinstance(v, str) and (v.startswith("[") or v.startswith("{")):
                try:
                    config.app[k] = json.loads(v)
                except Exception:
                    config.app[k] = v
            else:
                config.app[k] = v

        if hasattr(config, "save_config"):
            config.save_config()

        return True, "Configuraciones restauradas desde Firebase Firestore."
    except Exception as ex:
        return False, f"Error al descargar de Firestore: {ex}"


def backup_project_to_firebase(project):
    """Respalda metadata de un proyecto en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    task_id = project["task_id"]
    firestore_fields = {
        "task_id": {"stringValue": task_id},
        "subject": {"stringValue": str(project.get("subject", ""))},
        "script": {"stringValue": str(project.get("script", ""))[:1000]},
        "has_video": {"booleanValue": bool(project.get("has_video", False))},
        "cloud_synced": {"booleanValue": bool(project.get("cloud_synced", False))},
        "cloud_url": {"stringValue": str(project.get("cloud_url", ""))},
        "updated_at": {"stringValue": datetime.now().isoformat()}
    }

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_projects/{task_id}"
        resp = requests.patch(url, headers=headers, json={"fields": firestore_fields}, timeout=10)
        if resp.status_code == 200:
            return True, "Proyecto respaldado en Firebase Firestore."
        else:
            return False, f"Fallo al respaldar proyecto en Firestore (HTTP {resp.status_code})"
    except Exception as ex:
        return False, f"Error: {ex}"


def save_settings_to_firebase_async():
    """Ejecuta la sincronización en segundo plano para no bloquear la UI de Streamlit."""
    import threading
    t = threading.Thread(target=save_settings_to_firebase, daemon=True)
    t.start()
    return t
