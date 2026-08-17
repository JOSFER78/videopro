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
from pathlib import Path
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


def sync_learning_memory_to_firebase():
    """Sincroniza la memoria de aprendizaje completa (lecciones, críticas y métricas) en Firestore."""
    from app.services.learning_memory_engine import learning_engine
    return learning_engine.sync_to_firebase()


def load_learning_memory_from_firebase():
    """Descarga la memoria de aprendizaje desde Firestore."""
    from app.services.learning_memory_engine import learning_engine
    return learning_engine.load_from_firebase()


def emit_learning_event_to_firebase(event_data: dict) -> tuple[bool, str]:
    """
    Emite un evento de aprendizaje en tiempo real a Firebase Firestore.
    Actualiza el documento videopro_system/workflow_learner_live con el último evento
    y registra el evento en la colección videopro_learning_events.
    """
    token = _get_firebase_auth_token()
    if not token:
        return False, "Token de autenticación Firebase no disponible."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    event_id = event_data.get("event_id") or f"evt_{int(time.time() * 1000)}"

    firestore_event_fields = {
        "event_id": {"stringValue": str(event_id)},
        "event_type": {"stringValue": str(event_data.get("event_type", "UNKNOWN"))},
        "session_id": {"stringValue": str(event_data.get("session_id", "default_session"))},
        "project_id": {"stringValue": str(event_data.get("project_id", "system"))},
        "archetype_id": {"stringValue": str(event_data.get("archetype_id", "GLOBAL"))},
        "message": {"stringValue": str(event_data.get("message", ""))},
        "severity": {"stringValue": str(event_data.get("severity", "INFO"))},
        "timestamp": {"stringValue": str(event_data.get("timestamp", datetime.now().isoformat()))},
        "payload_json": {"stringValue": json.dumps(event_data.get("payload", {}), ensure_ascii=False)}
    }

    try:
        # 1. Actualizar el estado en vivo del motor de aprendizaje
        url_live = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/workflow_learner_live"
        live_fields = {
            "last_event_id": {"stringValue": str(event_id)},
            "last_event_type": {"stringValue": str(event_data.get("event_type", "UNKNOWN"))},
            "last_message": {"stringValue": str(event_data.get("message", ""))},
            "last_project_id": {"stringValue": str(event_data.get("project_id", "system"))},
            "last_archetype_id": {"stringValue": str(event_data.get("archetype_id", "GLOBAL"))},
            "last_updated": {"stringValue": str(event_data.get("timestamp", datetime.now().isoformat()))},
            "last_event_json": {"stringValue": json.dumps(event_data, ensure_ascii=False)}
        }
        requests.patch(url_live, headers=headers, json={"fields": live_fields}, timeout=8)

        # 2. Registrar el evento en la colección videopro_learning_events
        url_evt = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_learning_events/{event_id}"
        requests.patch(url_evt, headers=headers, json={"fields": firestore_event_fields}, timeout=8)

        return True, f"Evento {event_id} emitido a Firestore con éxito."
    except Exception as ex:
        logger.debug(f"Aviso al emitir evento a Firestore: {ex}")
        return False, f"Error emitiendo evento a Firestore: {ex}"


def emit_learning_event_to_firebase_async(event_data: dict):
    """Emite un evento de aprendizaje en segundo plano no bloqueante."""
    import threading
    t = threading.Thread(target=emit_learning_event_to_firebase, args=(event_data,), daemon=True)
    t.start()
    return t


def save_audit_report_to_firebase(report: dict) -> tuple[bool, str]:
    """Persiste el informe completo de auditoría y auto-mejora en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "Token de autenticación Firebase no disponible."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    target_pid = report.get("project_id", "project_audit")

    fields = {
        "project_id": {"stringValue": str(target_pid)},
        "archetype_id": {"stringValue": str(report.get("archetype_id", "GLOBAL"))},
        "score": {"doubleValue": float(report.get("audit", {}).get("overall_score", 0.0))},
        "passed": {"booleanValue": bool(report.get("audit", {}).get("passed", False))},
        "violations_count": {"integerValue": str(len(report.get("audit", {}).get("violations", [])))},
        "completed_at": {"stringValue": str(report.get("completed_at", datetime.now().isoformat()))},
        "report_json": {"stringValue": json.dumps(report, ensure_ascii=False)}
    }

    try:
        # Guardar auditoría por proyecto
        url_audit = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_audits/{target_pid}"
        requests.patch(url_audit, headers=headers, json={"fields": fields}, timeout=10)

        # Actualizar última auditoría global del sistema
        url_latest = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/latest_audit"
        requests.patch(url_latest, headers=headers, json={"fields": fields}, timeout=10)

        return True, f"Informe de auditoría para '{target_pid}' guardado en Firestore."
    except Exception as ex:
        logger.debug(f"Aviso guardando auditoría en Firestore: {ex}")
        return False, f"Error guardando auditoría: {ex}"


def save_audit_report_to_firebase_async(report: dict):
    """Persiste el informe de auditoría en segundo plano."""
    import threading
    t = threading.Thread(target=save_audit_report_to_firebase, args=(report,), daemon=True)
    t.start()
    return t


def sync_workflow_improvements_to_firebase(improvements: list) -> tuple[bool, str]:
    """Persiste el historial completo de auto-mejoras (v+1) en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "Token de autenticación Firebase no disponible."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    fields = {
        "updated_at": {"stringValue": datetime.now().isoformat()},
        "total_improvements": {"integerValue": str(len(improvements))},
        "improvements_json": {"stringValue": json.dumps(improvements, ensure_ascii=False)}
    }

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/workflow_improvements"
        resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=10)
        if resp.status_code in (200, 201):
            return True, "Historial de mejoras de workflows sincronizado en Firestore."
        return False, f"Firestore respondió con código HTTP {resp.status_code}"
    except Exception as ex:
        return False, f"Error al conectar con Firestore: {ex}"


def sync_archetype_performance_to_firebase(perf: dict) -> tuple[bool, str]:
    """Persiste las métricas de rendimiento por arquetipo en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "Token de autenticación Firebase no disponible."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    fields = {
        "updated_at": {"stringValue": datetime.now().isoformat()},
        "performance_json": {"stringValue": json.dumps(perf, ensure_ascii=False)}
    }

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_system/archetype_performance"
        resp = requests.patch(url, headers=headers, json={"fields": fields}, timeout=10)
        if resp.status_code in (200, 201):
            return True, "Métricas de rendimiento por arquetipo sincronizadas en Firestore."
        return False, f"Firestore HTTP {resp.status_code}"
    except Exception as ex:
        return False, f"Error al conectar con Firestore: {ex}"


def fetch_learning_events_from_firebase(limit: int = 30) -> list[dict]:
    """Obtiene los eventos recientes de aprendizaje desde Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return []

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_learning_events?pageSize={limit}"

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return []
        docs = resp.json().get("documents", [])
        events = []
        for d in docs:
            fields = d.get("fields", {})
            payload_str = fields.get("payload_json", {}).get("stringValue", "{}")
            payload = {}
            try:
                payload = json.loads(payload_str)
            except Exception:
                pass
            events.append({
                "event_id": fields.get("event_id", {}).get("stringValue", ""),
                "event_type": fields.get("event_type", {}).get("stringValue", "UNKNOWN"),
                "session_id": fields.get("session_id", {}).get("stringValue", ""),
                "project_id": fields.get("project_id", {}).get("stringValue", ""),
                "archetype_id": fields.get("archetype_id", {}).get("stringValue", ""),
                "message": fields.get("message", {}).get("stringValue", ""),
                "severity": fields.get("severity", {}).get("stringValue", "INFO"),
                "timestamp": fields.get("timestamp", {}).get("stringValue", ""),
                "payload": payload
            })
        return events
    except Exception as ex:
        logger.debug(f"Error descargando eventos de Firestore: {ex}")
        return []


def backup_workflow_to_firebase(workflow: dict) -> tuple[bool, str]:
    """Respalda un workflow en la colección 'videopro_workflows' de Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return False, "No autenticado en Firebase."

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    wf_id = workflow.get("id") or workflow.get("workflow_id", "workflow_default")
    
    firestore_fields = {
        "workflow_id": {"stringValue": str(wf_id)},
        "name": {"stringValue": str(workflow.get("name", wf_id))},
        "description": {"stringValue": str(workflow.get("description", ""))},
        "version": {"integerValue": str(workflow.get("version", 1))},
        "version_label": {"stringValue": str(workflow.get("version_label", f"v{workflow.get('version', 1)}.0"))},
        "archetype_id": {"stringValue": str(workflow.get("archetype_id", "GLOBAL"))},
        "updated_at": {"stringValue": str(workflow.get("updated_at", datetime.now().isoformat()))},
        "workflow_json": {"stringValue": json.dumps(workflow, ensure_ascii=False)}
    }
    if "created_at" in workflow:
        firestore_fields["created_at"] = {"stringValue": str(workflow["created_at"])}

    try:
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_workflows/{wf_id}"
        resp = requests.patch(url, headers=headers, json={"fields": firestore_fields}, timeout=10)
        if resp.status_code in (200, 201):
            return True, f"Workflow '{wf_id}' respaldado en Firebase Firestore."
        else:
            return False, f"Fallo al respaldar workflow en Firestore (HTTP {resp.status_code})"
    except Exception as ex:
        return False, f"Error: {ex}"


def backup_workflow_to_firebase_async(workflow: dict):
    """Ejecuta el respaldo de workflow en segundo plano."""
    import threading
    t = threading.Thread(target=backup_workflow_to_firebase, args=(workflow,), daemon=True)
    t.start()
    return t


def fetch_all_workflows_from_firebase() -> List[dict]:
    """Obtiene todos los workflows de la colección 'videopro_workflows' en Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return []

    project_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_workflows"

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return []
        docs = resp.json().get("documents", [])
        workflows = []
        for d in docs:
            fields = d.get("fields", {})
            wf_str = fields.get("workflow_json", {}).get("stringValue", "{}")
            try:
                wf_data = json.loads(wf_str)
            except Exception:
                wf_data = {
                    "id": fields.get("workflow_id", {}).get("stringValue", ""),
                    "name": fields.get("name", {}).get("stringValue", ""),
                    "description": fields.get("description", {}).get("stringValue", ""),
                    "version": int(fields.get("version", {}).get("integerValue", 1)),
                    "archetype_id": fields.get("archetype_id", {}).get("stringValue", "GLOBAL")
                }
            workflows.append(wf_data)
        return workflows
    except Exception as ex:
        logger.error(f"Error al obtener workflows de Firestore: {ex}")
        return []


def fetch_single_workflow_from_firebase(workflow_id: str) -> Optional[dict]:
    """Obtiene un workflow específico desde Firestore."""
    token = _get_firebase_auth_token()
    if not token:
        return None

    fb_proj_id = config.app.get("firebase_project_id") or DEFAULT_PROJECT_ID
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://firestore.googleapis.com/v1/projects/{fb_proj_id}/databases/(default)/documents/videopro_workflows/{workflow_id}"

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None
        fields = resp.json().get("fields", {})
        wf_str = fields.get("workflow_json", {}).get("stringValue", "{}")
        try:
            return json.loads(wf_str)
        except Exception:
            return {
                "id": fields.get("workflow_id", {}).get("stringValue", workflow_id),
                "name": fields.get("name", {}).get("stringValue", ""),
                "description": fields.get("description", {}).get("stringValue", ""),
                "version": int(fields.get("version", {}).get("integerValue", 1)),
                "archetype_id": fields.get("archetype_id", {}).get("stringValue", "GLOBAL")
            }
    except Exception as ex:
        logger.error(f"Error descargando workflow '{workflow_id}' de Firestore: {ex}")
        return None


def sync_all_workflows_to_firebase(workflows_dir: Optional[str] = None) -> tuple[bool, str]:
    """Sincroniza todos los workflows locales (JSON) con Firestore."""
    wf_dir = Path(workflows_dir) if workflows_dir else Path(BASE_DIR) / "storage" / "workflows"
    if not wf_dir.exists():
        return False, f"Directorio {wf_dir} no existe."
    
    count = 0
    errors = 0
    for jf in wf_dir.glob("*.json"):
        if jf.name in ("workflow_catalog.json", "improvements.json"):
            continue
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "id" in data:
                ok, _ = backup_workflow_to_firebase(data)
                if ok:
                    count += 1
                else:
                    errors += 1
        except Exception:
            errors += 1
    return (errors == 0), f"Sincronizados {count} workflows en Firestore (Errores: {errors})."


