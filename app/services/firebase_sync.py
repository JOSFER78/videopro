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
from typing import List, Optional, Dict, Any
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

    # 1. Persistir global_config
    firestore_fields = {
        "updated_at": {"stringValue": datetime.now().isoformat()},
        "app_name": {"stringValue": "VideoPro Creative Studio"},
        "hosting_url": {"stringValue": HOSTING_URL},
        "config_json": {"stringValue": json.dumps(app_data, ensure_ascii=False)}
    }

    try:
        url_cfg = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_settings/global_config"
        requests.patch(url_cfg, headers=headers, json={"fields": firestore_fields}, timeout=10)

        # 2. Persistir registro unificado y tombstones de borrados
        from app.core.providers import registry as prov_reg
        reg_file = prov_reg.REGISTRY_PATH
        del_file = prov_reg.DELETED_PROVIDERS_PATH

        reg_data_str = "{}"
        if os.path.isfile(reg_file):
            with open(reg_file, "r", encoding="utf-8") as f:
                reg_data_str = f.read()

        del_data_str = "[]"
        if os.path.isfile(del_file):
            with open(del_file, "r", encoding="utf-8") as f:
                del_data_str = f.read()

        firestore_reg_fields = {
            "updated_at": {"stringValue": datetime.now().isoformat()},
            "registry_json": {"stringValue": reg_data_str},
            "deleted_providers_json": {"stringValue": del_data_str}
        }
        url_reg = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_settings/providers_registry"
        requests.patch(url_reg, headers=headers, json={"fields": firestore_reg_fields}, timeout=10)

        return True, "Configuraciones, registro y lista de borrados sincronizados en Firebase Firestore."
    except Exception as ex:
        return False, f"Error al conectar con Firestore: {ex}"


def load_settings_from_firebase():
    """Descarga y aplica la configuración, registro y tombstones guardados en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}

    try:
        from app.core.providers import registry as prov_reg

        # 1. Cargar tombstones y registro de proveedores desde Firestore
        url_reg = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_settings/providers_registry"
        resp_reg = requests.get(url_reg, headers=headers, timeout=10)
        if resp_reg.status_code == 200:
            doc_reg = resp_reg.json()
            fields_reg = doc_reg.get("fields", {})
            del_json_str = fields_reg.get("deleted_providers_json", {}).get("stringValue", "[]")
            reg_json_str = fields_reg.get("registry_json", {}).get("stringValue", "{}")

            try:
                del_list = json.loads(del_json_str)
                if isinstance(del_list, list):
                    current_dels = prov_reg.load_deleted_providers()
                    current_dels.update(del_list)
                    os.makedirs(os.path.dirname(prov_reg.DELETED_PROVIDERS_PATH), exist_ok=True)
                    with open(prov_reg.DELETED_PROVIDERS_PATH, "w", encoding="utf-8") as f:
                        json.dump(sorted(list(current_dels)), f, indent=2)
            except Exception:
                pass

            try:
                parsed_reg = json.loads(reg_json_str)
                if isinstance(parsed_reg, dict) and len(parsed_reg) > 0:
                    prov_reg.save_registry(parsed_reg)
            except Exception:
                pass

        # 2. Cargar global_config
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

        return True, "Configuraciones y proveedores restaurados desde Firebase Firestore."
    except Exception as ex:
        return False, f"Error al descargar de Firestore: {ex}"


def backup_project_to_firebase(project: dict):
    """Respalda el documento relacional completo de un proyecto en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    task_id = project.get("task_id") or project.get("project_id", "project_default")
    
    firestore_fields = {
        "project_id": {"stringValue": task_id},
        "task_id": {"stringValue": task_id},
        "title": {"stringValue": str(project.get("title") or project.get("subject", "Proyecto VideoPro"))},
        "subject": {"stringValue": str(project.get("subject") or project.get("title", ""))},
        "workflow_id": {"stringValue": str(project.get("workflow_id", "PIXAR_3D_ANIMATION"))},
        "workflow_name": {"stringValue": str(project.get("workflow_name", "Producción Cinemática"))},
        "workflow_icon": {"stringValue": str(project.get("workflow_icon", "🎬"))},
        "status": {"stringValue": str(project.get("status", "DRAFT"))},
        "aspect_ratio": {"stringValue": str(project.get("aspect_ratio", "16:9"))},
        "voice_id": {"stringValue": str(project.get("voice_id", "vibevoice"))},
        "scenes_count": {"integerValue": str(len(project.get("scenes", [])))},
        "has_video": {"booleanValue": bool(project.get("has_video", False))},
        "cloud_synced": {"booleanValue": bool(project.get("cloud_synced", False))},
        "cloud_url": {"stringValue": str(project.get("cloud_url", ""))},
        "director_spec_json": {"stringValue": json.dumps(project.get("director_spec", {}), ensure_ascii=False)},
        "scenes_json": {"stringValue": json.dumps(project.get("scenes", []), ensure_ascii=False)},
        "messages_json": {"stringValue": json.dumps(project.get("messages", []), ensure_ascii=False)},
        "updated_at": {"stringValue": datetime.now().isoformat()}
    }

    if "created_at" in project:
        firestore_fields["created_at"] = {"stringValue": str(project["created_at"])}

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_projects/{task_id}"
        resp = requests.patch(url, headers=headers, json={"fields": firestore_fields}, timeout=10)
        if resp.status_code == 200:
            return True, "Proyecto respaldado en Firebase Firestore."
        else:
            return False, f"Fallo al respaldar proyecto en Firestore (HTTP {resp.status_code})"
    except Exception as ex:
        return False, f"Error: {ex}"


def backup_project_to_firebase_async(project: dict):
    """Ejecuta el respaldo de proyecto en segundo plano para no demorar la UI de Streamlit."""
    import threading
    t = threading.Thread(target=backup_project_to_firebase, args=(project,), daemon=True)
    t.start()
    return t


def fetch_all_projects_from_firebase() -> List[dict]:
    """Obtiene la colección completa de proyectos almacenados en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return []

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_projects"

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return []
        
        docs = resp.json().get("documents", [])
        projects = []
        for d in docs:
            fields = d.get("fields", {})
            p_id = fields.get("project_id", {}).get("stringValue") or fields.get("task_id", {}).get("stringValue") or d.get("name", "").split("/")[-1]
            
            # Deserializar campos JSON enriquecidos
            spec_str = fields.get("director_spec_json", {}).get("stringValue", "{}")
            scenes_str = fields.get("scenes_json", {}).get("stringValue", "[]")
            messages_str = fields.get("messages_json", {}).get("stringValue", "[]")

            director_spec = {}
            scenes = []
            messages = []
            try: director_spec = json.loads(spec_str)
            except Exception: pass
            try: scenes = json.loads(scenes_str)
            except Exception: pass
            try: messages = json.loads(messages_str)
            except Exception: pass

            projects.append({
                "project_id": p_id,
                "task_id": p_id,
                "title": fields.get("title", {}).get("stringValue") or fields.get("subject", {}).get("stringValue", p_id),
                "subject": fields.get("subject", {}).get("stringValue") or fields.get("title", {}).get("stringValue", p_id),
                "workflow_id": fields.get("workflow_id", {}).get("stringValue", "PIXAR_3D_ANIMATION"),
                "workflow_name": fields.get("workflow_name", {}).get("stringValue", "Producción"),
                "workflow_icon": fields.get("workflow_icon", {}).get("stringValue", "🎬"),
                "status": fields.get("status", {}).get("stringValue", "DRAFT"),
                "aspect_ratio": fields.get("aspect_ratio", {}).get("stringValue", "16:9"),
                "voice_id": fields.get("voice_id", {}).get("stringValue", "vibevoice"),
                "scenes_count": int(fields.get("scenes_count", {}).get("integerValue", len(scenes))),
                "has_video": fields.get("has_video", {}).get("booleanValue", False),
                "cloud_synced": fields.get("cloud_synced", {}).get("booleanValue", False),
                "cloud_url": fields.get("cloud_url", {}).get("stringValue", ""),
                "director_spec": director_spec,
                "scenes": scenes,
                "messages": messages,
                "updated_at": fields.get("updated_at", {}).get("stringValue", datetime.now().isoformat()),
                "created_at": fields.get("created_at", {}).get("stringValue", datetime.now().isoformat())
            })
        return projects
    except Exception as ex:
        logger.error(f"Error al obtener proyectos de Firestore: {ex}")
        return []


def fetch_single_project_from_firebase(project_id: str) -> Optional[dict]:
    """Obtiene un único proyecto desde Firestore por su ID."""
    token = _get_firebase_auth_token()
    if not token:
        return None

    fb_proj_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firestore.googleapis.com/v1/projects/{fb_proj_id}/databases/(default)/documents/videopro_projects/{project_id}"

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None
        
        fields = resp.json().get("fields", {})
        spec_str = fields.get("director_spec_json", {}).get("stringValue", "{}")
        scenes_str = fields.get("scenes_json", {}).get("stringValue", "[]")
        messages_str = fields.get("messages_json", {}).get("stringValue", "[]")

        director_spec = {}
        scenes = []
        messages = []
        try: director_spec = json.loads(spec_str)
        except Exception: pass
        try: scenes = json.loads(scenes_str)
        except Exception: pass
        try: messages = json.loads(messages_str)
        except Exception: pass

        return {
            "project_id": project_id,
            "task_id": project_id,
            "title": fields.get("title", {}).get("stringValue") or fields.get("subject", {}).get("stringValue", project_id),
            "subject": fields.get("subject", {}).get("stringValue") or fields.get("title", {}).get("stringValue", project_id),
            "workflow_id": fields.get("workflow_id", {}).get("stringValue", "PIXAR_3D_ANIMATION"),
            "workflow_name": fields.get("workflow_name", {}).get("stringValue", "Producción"),
            "workflow_icon": fields.get("workflow_icon", {}).get("stringValue", "🎬"),
            "status": fields.get("status", {}).get("stringValue", "DRAFT"),
            "aspect_ratio": fields.get("aspect_ratio", {}).get("stringValue", "16:9"),
            "voice_id": fields.get("voice_id", {}).get("stringValue", "vibevoice"),
            "scenes_count": int(fields.get("scenes_count", {}).get("integerValue", len(scenes))),
            "has_video": fields.get("has_video", {}).get("booleanValue", False),
            "cloud_synced": fields.get("cloud_synced", {}).get("booleanValue", False),
            "cloud_url": fields.get("cloud_url", {}).get("stringValue", ""),
            "director_spec": director_spec,
            "scenes": scenes,
            "messages": messages,
            "updated_at": fields.get("updated_at", {}).get("stringValue", datetime.now().isoformat()),
            "created_at": fields.get("created_at", {}).get("stringValue", datetime.now().isoformat())
        }
    except Exception as ex:
        logger.error(f"Error al descargar proyecto '{project_id}' de Firestore: {ex}")
        return None


def delete_project_from_firebase(project_id: str) -> bool:
    """Elimina permanentemente un proyecto de Firestore en todas las colecciones."""
    token = _get_firebase_auth_token()
    if not token:
        return False

    fb_proj_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Borrar de videopro_projects
    try:
        url1 = f"https://firestore.googleapis.com/v1/projects/{fb_proj_id}/databases/(default)/documents/videopro_projects/{project_id}"
        requests.delete(url1, headers=headers, timeout=5)
    except Exception:
        pass

    # 2. Borrar de projects
    try:
        url2 = f"https://firestore.googleapis.com/v1/projects/{fb_proj_id}/databases/(default)/documents/projects/{project_id}"
        requests.delete(url2, headers=headers, timeout=5)
    except Exception:
        pass

    return True


def save_settings_to_firebase_async():
    """Ejecuta la sincronización en segundo plano para no bloquear la UI de Streamlit."""
    import threading
    t = threading.Thread(target=save_settings_to_firebase, daemon=True)
    t.start()
    return t
