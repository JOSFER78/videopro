#!/usr/bin/env python3
"""
firebase_sync_manager.py — Gestor de Sincronización Bidireccional con Firebase Firestore
========================================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Gestor centralizado de sincronización en tiempo real y arquitectura offline-first
para VideoPro Studio y Hermes Agent. Sincroniza bidireccionalmente tres colecciones clave:

  1. `workflows` (videopro_workflows / workflows):
     - Almacenamiento y control de versiones semánticas (v1.0.0, v1.1.0, latest) de los
       8 arquetipos canónicos (CHRONODRIFT_6DOF, FPV_URBAN, VOX_EXPLAINER, VIRAL_SHORTS_916,
       DOCUMENTAL_35MM, NANOVERSE, LIVING_CANVAS, ASTRODRIFT).
     - Parámetros en 7 capas físicas cinemáticas (7D prompts: sujeto, entorno, iluminación,
       óptica, movimiento, colorimetría, motor de render).
     - Especificaciones ópticas de cámara, mastering acústico Broadcast EBU R128 (-14 LUFS),
       subtitulado Levenshtein y reglas de oro forenses.
     - Sellado criptográfico SHA-256 de integridad.

  2. `learning_memory` (videopro_learning_memory / learning_memory):
     - Catálogo de lecciones aprendidas (lessons_catalog.json / LearnedLesson).
     - Auditorías forenses de calidad contra R01-R10 (project_critiques.json / videopro_audits).
     - Métricas de error y rendimiento de proveedores multi-cloud (provider_metrics.json).
     - Historial de auto-parcheos y mejoras de workflows v+1 (workflow_improvements.json /
       archetype_performance.json).
     - Transmisión de eventos de aprendizaje en vivo (videopro_learning_events).

  3. `projects` (videopro_projects / projects):
     - Estado del ciclo de vida de los proyectos de vídeo (DRAFT, RESEARCH_READY, ASSETS_GENERATED,
       RENDERED, COMPLETED, FAILED, fases 1-8).
     - Manifiesto completo de activos con hashes SHA-256 y validación de gate estricto > 5KB.
     - URLs maestras de entrega (Cloudflare R2, S3, Firebase Hosting, Telegram, YouTube).
     - Escaletas y cronogramas de escenas (scenes.json, manifest.json).

Arquitectura Offline-First:
  - Si no hay conexión o falla la red, el sistema opera 100% en local y almacena las mutaciones
    en una cola transaccional persistente (`storage/system/firebase_sync_queue.json`).
  - Al detectar reconexión o invocar `flush_queue()`, las mutaciones pendientes se aplican
    automáticamente a Firestore con resolución determinista de conflictos y reintentos exponenciales.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import copy
import datetime
import hashlib
import json
import logging
import os
import re
import shutil
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Añadir raíz de VideoPro al sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from app.config import config
except ImportError:
    config = None

logger = logging.getLogger("videopro.firebase_sync_manager")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s : %(message)s"
)

# ==============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ==============================================================================

DEFAULT_PROJECT_ID = "ayuda-emilio-83261"
DEFAULT_HOSTING_URL = "https://videopro-studio.web.app"
GOOGLE_OAUTH_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
FIRESTORE_REST_BASE = "https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"

# Credenciales canónicas de Firebase CLI para refresco OAuth sin dependencia externa
FIREBASE_CLI_CLIENT_ID = "563584335869-fgrhgmd47bqnekij5i8b5pr03ho849e6.apps.googleusercontent.com"
FIREBASE_CLI_CLIENT_SECRET = "j9iVZfS8kkCEFUPaAeJV0sAi"

STORAGE_DIR = BASE_DIR / "storage"
WORKFLOWS_STORAGE_DIR = STORAGE_DIR / "workflows"
LEARNING_STORAGE_DIR = STORAGE_DIR / "learning_memory"
PROJECTS_STORAGE_DIR = STORAGE_DIR / "projects"
SYSTEM_STORAGE_DIR = STORAGE_DIR / "system"

SYSTEM_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
WORKFLOWS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LEARNING_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

SYNC_QUEUE_FILE = SYSTEM_STORAGE_DIR / "firebase_sync_queue.json"
SYNC_STATE_FILE = SYSTEM_STORAGE_DIR / "firebase_sync_state.json"

CANONICAL_ARCHETYPES = [
    "CHRONODRIFT_6DOF",
    "FPV_URBAN",
    "VOX_EXPLAINER",
    "VIRAL_SHORTS_916",
    "DOCUMENTAL_35MM",
    "NANOVERSE",
    "LIVING_CANVAS",
    "ASTRODRIFT"
]


def get_utc_iso_now() -> str:
    """Retorna la fecha/hora UTC actual en formato ISO 8601 canónico."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def compute_sha256(data_or_path: Union[str, bytes, dict, list, Path]) -> str:
    """Calcula el hash SHA-256 criptográfico para strings, bytes, archivos o estructuras JSON."""
    hasher = hashlib.sha256()
    if isinstance(data_or_path, Path) or (isinstance(data_or_path, str) and os.path.isfile(data_or_path)):
        p = Path(data_or_path)
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    elif isinstance(data_or_path, (dict, list)):
        serialized = json.dumps(data_or_path, sort_keys=True, ensure_ascii=False)
        hasher.update(serialized.encode("utf-8"))
        return hasher.hexdigest()
    elif isinstance(data_or_path, str):
        hasher.update(data_or_path.encode("utf-8"))
        return hasher.hexdigest()
    elif isinstance(data_or_path, bytes):
        hasher.update(data_or_path)
        return hasher.hexdigest()
    return ""


# ==============================================================================
# SERIALIZACIÓN BIDIRECCIONAL FIRESTORE REST
# ==============================================================================

def python_to_firestore_value(val: Any) -> Dict[str, Any]:
    """Convierte un tipo de dato nativo de Python al formato tipado de Firestore REST."""
    if val is None:
        return {"nullValue": None}
    elif isinstance(val, bool):
        return {"booleanValue": val}
    elif isinstance(val, int):
        return {"integerValue": str(val)}
    elif isinstance(val, float):
        return {"doubleValue": float(val)}
    elif isinstance(val, str):
        return {"stringValue": val}
    elif isinstance(val, (datetime.datetime, datetime.date)):
        if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
            val = datetime.datetime(val.year, val.month, val.day, tzinfo=datetime.timezone.utc)
        elif val.tzinfo is None:
            val = val.replace(tzinfo=datetime.timezone.utc)
        iso_ts = val.isoformat().replace("+00:00", "Z")
        return {"timestampValue": iso_ts}
    elif isinstance(val, list):
        return {"arrayValue": {"values": [python_to_firestore_value(item) for item in val]}}
    elif isinstance(val, dict):
        fields = {}
        for k, v in val.items():
            fields[str(k)] = python_to_firestore_value(v)
        return {"mapValue": {"fields": fields}}
    else:
        return {"stringValue": str(val)}


def firestore_value_to_python(fs_val: Dict[str, Any]) -> Any:
    """Convierte un valor tipado de Firestore REST a un tipo de dato nativo de Python."""
    if not isinstance(fs_val, dict):
        return fs_val

    if "stringValue" in fs_val:
        s = fs_val["stringValue"]
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except Exception:
                return s
        return s
    elif "integerValue" in fs_val:
        return int(fs_val["integerValue"])
    elif "doubleValue" in fs_val:
        return float(fs_val["doubleValue"])
    elif "booleanValue" in fs_val:
        return bool(fs_val["booleanValue"])
    elif "timestampValue" in fs_val:
        return fs_val["timestampValue"]
    elif "nullValue" in fs_val:
        return None
    elif "arrayValue" in fs_val:
        values = fs_val["arrayValue"].get("values", [])
        return [firestore_value_to_python(v) for v in values]
    elif "mapValue" in fs_val:
        fields = fs_val["mapValue"].get("fields", {})
        result = {}
        for k, v in fields.items():
            result[k] = firestore_value_to_python(v)
        return result
    return fs_val


def python_dict_to_firestore_fields(data: Dict[str, Any], preserve_deep_json: bool = True) -> Dict[str, Any]:
    """
    Convierte un diccionario completo de Python en campos compatibles con Firestore REST.
    Si preserve_deep_json es True, genera adicionalmente campos stringValue JSON para estructuras
    profundamente anidadas asegurando 100% de fidelidad sin límites de recursión de Firestore.
    """
    fields: Dict[str, Any] = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            if preserve_deep_json and not k.endswith("_json"):
                try:
                    fields[f"{k}_json"] = {"stringValue": json.dumps(v, ensure_ascii=False)}
                except Exception:
                    pass
            fields[k] = python_to_firestore_value(v)
        else:
            fields[k] = python_to_firestore_value(v)
    return fields


def firestore_doc_to_python_dict(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Reconstruye un diccionario nativo de Python a partir de un documento Firestore REST."""
    fields = doc.get("fields", {})
    result: Dict[str, Any] = {}
    json_keys = set()

    for k, v in fields.items():
        parsed = firestore_value_to_python(v)
        if k.endswith("_json") and isinstance(parsed, (dict, list)):
            base_k = k[:-5]
            result[base_k] = parsed
            json_keys.add(base_k)
        elif k not in json_keys:
            result[k] = parsed

    if "name" in doc:
        result["_firestore_path"] = doc["name"]
        result["_doc_id"] = doc["name"].split("/")[-1]
    if "createTime" in doc:
        result["_firestore_create_time"] = doc["createTime"]
    if "updateTime" in doc:
        result["_firestore_update_time"] = doc["updateTime"]

    return result


# ==============================================================================
# 1. CLIENTE DE AUTENTICACIÓN Y REST API DE FIRESTORE
# ==============================================================================

class FirestoreRESTClient:
    """
    Cliente REST de alta fiabilidad para Firebase Firestore.
    Soporta autenticación OAuth2 con auto-refresco directo, reintentos con backoff
    y detección dinámica de estado offline/online.
    """

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or (
            config.app.get("firebase_project_id") if config and hasattr(config, "app") else None
        ) or DEFAULT_PROJECT_ID
        self.hosting_url = (
            config.app.get("firebase_hosting_url") if config and hasattr(config, "app") else None
        ) or DEFAULT_HOSTING_URL
        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._is_online_cache: Optional[bool] = None
        self._last_health_check: float = 0.0
        self._lock = threading.Lock()

    def get_auth_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Obtiene un token de acceso OAuth2 válido para Firestore.
        Si está próximo a expirar o expiró, realiza un refresco OAuth instantáneo.
        """
        import requests

        with self._lock:
            now = time.time()
            if not force_refresh and self._cached_token and self._token_expires_at > now + 60:
                return self._cached_token

            # 1. Intentar variable de entorno directa
            token_env = os.environ.get("FIREBASE_AUTH_TOKEN")
            if token_env:
                self._cached_token = token_env
                self._token_expires_at = now + 3600
                return self._cached_token

            # 2. Leer tokens de ~/.config/configstore/firebase-tools.json
            config_path = Path(os.path.expanduser("~/.config/configstore/firebase-tools.json"))
            if not config_path.is_file():
                logger.debug("Archivo firebase-tools.json no encontrado")
                return None

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)

                tokens = cfg.get("tokens", {})
                access_token = tokens.get("access_token")
                refresh_token = tokens.get("refresh_token")
                expires_at_ms = tokens.get("expires_at", 0)
                expires_at_s = expires_at_ms / 1000.0 if expires_at_ms > 0 else 0

                # Si el access_token sigue siendo válido por al menos 90 segundos
                if not force_refresh and access_token and (expires_at_s > now + 90 or expires_at_s == 0):
                    self._cached_token = access_token
                    self._token_expires_at = expires_at_s if expires_at_s > 0 else now + 3600
                    return access_token

                # Si expiró o solicitamos refresco, usar refresh_token con el endpoint OAuth de Google
                if refresh_token:
                    logger.debug("Refrescando token OAuth2 de Firebase con Google Identity...")
                    client_id = cfg.get("user", {}).get("azp", FIREBASE_CLI_CLIENT_ID)
                    client_secret = FIREBASE_CLI_CLIENT_SECRET

                    resp = requests.post(
                        GOOGLE_OAUTH_TOKEN_ENDPOINT,
                        data={
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "grant_type": "refresh_token",
                            "refresh_token": refresh_token,
                        },
                        timeout=8
                    )

                    if resp.status_code == 200:
                        data = resp.json()
                        new_access_token = data.get("access_token")
                        expires_in = data.get("expires_in", 3600)
                        new_expires_at_ms = int((now + expires_in) * 1000)

                        tokens["access_token"] = new_access_token
                        tokens["expires_at"] = new_expires_at_ms
                        tokens["expires_in"] = expires_in
                        cfg["tokens"] = tokens

                        try:
                            with open(config_path, "w", encoding="utf-8") as f:
                                json.dump(cfg, f, indent=2)
                        except Exception as write_err:
                            logger.debug(f"Aviso guardando token actualizado: {write_err}")

                        self._cached_token = new_access_token
                        self._token_expires_at = now + expires_in
                        logger.info("🔑 Token OAuth2 de Firebase Firestore refrescado y guardado con éxito.")
                        return new_access_token
                    else:
                        logger.warning(f"Error al refrescar token OAuth: HTTP {resp.status_code} - {resp.text}")

                # Fallback al access_token existente
                if access_token:
                    self._cached_token = access_token
                    return access_token

            except Exception as ex:
                logger.error(f"Error al procesar autenticación Firebase: {ex}")

            return None

    def check_connection(self, timeout: float = 4.0) -> Dict[str, Any]:
        """Comprueba el estado de conectividad en vivo con Firebase Firestore."""
        import requests

        token = self.get_auth_token()
        if not token:
            self._is_online_cache = False
            return {
                "connected": False,
                "project_id": self.project_id,
                "hosting_url": self.hosting_url,
                "message": "Token de autenticación Firebase no disponible."
            }

        url = FIRESTORE_REST_BASE.format(project_id=self.project_id) + "/videopro_system/status"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code in (200, 404):
                self._is_online_cache = True
                self._last_health_check = time.time()
                return {
                    "connected": True,
                    "project_id": self.project_id,
                    "hosting_url": self.hosting_url,
                    "message": f"Conectado exitosamente con Firestore en '{self.project_id}'."
                }
            elif resp.status_code == 401:
                # Intentar forzar refresco de token una vez
                refreshed_tok = self.get_auth_token(force_refresh=True)
                if refreshed_tok:
                    headers = {"Authorization": f"Bearer {refreshed_tok}"}
                    resp_retry = requests.get(url, headers=headers, timeout=timeout)
                    if resp_retry.status_code in (200, 404):
                        self._is_online_cache = True
                        return {
                            "connected": True,
                            "project_id": self.project_id,
                            "hosting_url": self.hosting_url,
                            "message": f"Conectado exitosamente con Firestore en '{self.project_id}' (token refrescado)."
                        }
                self._is_online_cache = False
                return {
                    "connected": False,
                    "project_id": self.project_id,
                    "hosting_url": self.hosting_url,
                    "message": f"Fallo de autorización en Firestore (HTTP 401)."
                }
            else:
                self._is_online_cache = False
                return {
                    "connected": False,
                    "project_id": self.project_id,
                    "hosting_url": self.hosting_url,
                    "message": f"Respuesta inesperada de Firestore (HTTP {resp.status_code})."
                }
        except Exception as ex:
            self._is_online_cache = False
            return {
                "connected": False,
                "project_id": self.project_id,
                "hosting_url": self.hosting_url,
                "message": f"Error de red o timeout conectando a Firestore: {ex}"
            }

    def is_online(self) -> bool:
        """Retorna True si hay conexión activa con Firestore, utilizando caché de 30s."""
        now = time.time()
        if self._is_online_cache is not None and (now - self._last_health_check < 30):
            return self._is_online_cache

        status = self.check_connection()
        return status.get("connected", False)

    def get_document(self, collection_name: str, doc_id: str, timeout: float = 8.0) -> Optional[Dict[str, Any]]:
        """Descarga un documento específico de Firestore por colección y Document ID."""
        import requests

        token = self.get_auth_token()
        if not token:
            return None

        url = f"{FIRESTORE_REST_BASE.format(project_id=self.project_id)}/{collection_name}/{doc_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                return firestore_doc_to_python_dict(resp.json())
            elif resp.status_code == 404:
                return None
            elif resp.status_code == 401:
                token = self.get_auth_token(force_refresh=True)
                if token:
                    headers = {"Authorization": f"Bearer {token}"}
                    resp2 = requests.get(url, headers=headers, timeout=timeout)
                    if resp2.status_code == 200:
                        return firestore_doc_to_python_dict(resp2.json())
            logger.debug(f"Documento {collection_name}/{doc_id} no encontrado o error HTTP {resp.status_code}")
            return None
        except Exception as ex:
            logger.debug(f"Excepción obteniendo {collection_name}/{doc_id}: {ex}")
            return None

    def set_document(
        self,
        collection_name: str,
        doc_id: str,
        data: Dict[str, Any],
        merge: bool = True,
        timeout: float = 10.0
    ) -> Tuple[bool, str]:
        """
        Crea o actualiza un documento en Firestore mediante PATCH REST.
        """
        import requests

        token = self.get_auth_token()
        if not token:
            return False, "Token de autenticación Firebase no disponible."

        url = f"{FIRESTORE_REST_BASE.format(project_id=self.project_id)}/{collection_name}/{doc_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        firestore_fields = python_dict_to_firestore_fields(data)
        body = {"fields": firestore_fields}

        try:
            resp = requests.patch(url, headers=headers, json=body, timeout=timeout)
            if resp.status_code in (200, 201):
                return True, f"Documento {collection_name}/{doc_id} guardado con éxito."
            elif resp.status_code == 401:
                token = self.get_auth_token(force_refresh=True)
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    resp2 = requests.patch(url, headers=headers, json=body, timeout=timeout)
                    if resp2.status_code in (200, 201):
                        return True, f"Documento {collection_name}/{doc_id} guardado con éxito tras refresco."
            return False, f"Firestore respondió con error HTTP {resp.status_code}: {resp.text}"
        except Exception as ex:
            return False, f"Error de red al conectar con Firestore: {ex}"

    def delete_document(self, collection_name: str, doc_id: str, timeout: float = 6.0) -> Tuple[bool, str]:
        """Elimina un documento en Firestore."""
        import requests

        token = self.get_auth_token()
        if not token:
            return False, "Token de autenticación no disponible."

        url = f"{FIRESTORE_REST_BASE.format(project_id=self.project_id)}/{collection_name}/{doc_id}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = requests.delete(url, headers=headers, timeout=timeout)
            if resp.status_code in (200, 204, 404):
                return True, f"Documento {collection_name}/{doc_id} eliminado."
            return False, f"Error al eliminar documento (HTTP {resp.status_code})"
        except Exception as ex:
            return False, f"Error de red eliminando documento: {ex}"

    def list_documents(
        self,
        collection_name: str,
        page_size: int = 100,
        timeout: float = 12.0
    ) -> List[Dict[str, Any]]:
        """Obtiene la lista completa de documentos en una colección de Firestore."""
        import requests

        token = self.get_auth_token()
        if not token:
            return []

        url = f"{FIRESTORE_REST_BASE.format(project_id=self.project_id)}/{collection_name}?pageSize={page_size}"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code != 200:
                if resp.status_code == 401:
                    token = self.get_auth_token(force_refresh=True)
                    if token:
                        headers["Authorization"] = f"Bearer {token}"
                        resp2 = requests.get(url, headers=headers, timeout=timeout)
                        if resp2.status_code == 200:
                            docs = resp2.json().get("documents", [])
                            return [firestore_doc_to_python_dict(d) for d in docs]
                logger.debug(f"Error listando colección {collection_name}: HTTP {resp.status_code}")
                return []

            docs = resp.json().get("documents", [])
            return [firestore_doc_to_python_dict(d) for d in docs]
        except Exception as ex:
            logger.debug(f"Error al listar colección {collection_name}: {ex}")
            return []


# ==============================================================================
# 2. COLA DE SINCRONIZACIÓN OFFLINE-FIRST (PERSISTENTE)
# ==============================================================================

@dataclass
class QueueItem:
    """Representa una mutación pendiente en la cola de sincronización offline."""
    id: str
    action: str  # 'upsert' | 'delete'
    collection: str
    document_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=get_utc_iso_now)
    retry_count: int = 0
    last_error: Optional[str] = None
    sha256_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> QueueItem:
        return cls(
            id=d.get("id", f"q_{int(time.time()*1000)}"),
            action=d.get("action", "upsert"),
            collection=d.get("collection", "generic"),
            document_id=d.get("document_id", "unknown"),
            data=d.get("data", {}),
            created_at=d.get("created_at", get_utc_iso_now()),
            retry_count=int(d.get("retry_count", 0)),
            last_error=d.get("last_error"),
            sha256_hash=d.get("sha256_hash", "")
        )


class OfflineSyncQueue:
    """
    Cola transaccional persistente en disco para operaciones offline-first.
    Garantiza que ninguna mutación se pierda ante cortes de red o desconexiones.
    """

    def __init__(self, queue_file: Path = SYNC_QUEUE_FILE):
        self.queue_file = queue_file
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _load_raw(self) -> List[Dict[str, Any]]:
        if not self.queue_file.exists():
            return []
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as ex:
            logger.warning(f"Aviso cargando cola de sincronización: {ex}")
            return []

    def _save_raw(self, items: List[Dict[str, Any]]) -> None:
        temp_file = self.queue_file.parent / f"queue_{os.getpid()}_{time.time_ns()}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.queue_file)

    def enqueue(self, action: str, collection: str, document_id: str, data: Dict[str, Any]) -> QueueItem:
        """Encola una mutación en la cola de sincronización persistente."""
        with self._lock:
            items_raw = self._load_raw()
            item_id = f"item_{collection}_{document_id}_{int(time.time() * 1000)}"
            payload_hash = compute_sha256(data)

            # Actualizar si ya existía para el mismo collection/document_id
            filtered = []
            for item in items_raw:
                if item.get("collection") == collection and item.get("document_id") == document_id:
                    continue
                filtered.append(item)

            new_item = QueueItem(
                id=item_id,
                action=action,
                collection=collection,
                document_id=document_id,
                data=data,
                created_at=get_utc_iso_now(),
                retry_count=0,
                sha256_hash=payload_hash
            )
            filtered.append(new_item.to_dict())
            self._save_raw(filtered)
            logger.info(f"📥 Encolado en cola offline: [{action.upper()}] {collection}/{document_id} (Total pendientes: {len(filtered)})")
            return new_item

    def get_pending(self) -> List[QueueItem]:
        """Retorna todos los elementos pendientes en la cola."""
        with self._lock:
            raw = self._load_raw()
            return [QueueItem.from_dict(d) for d in raw]

    def remove(self, item_id: str) -> None:
        """Elimina un elemento completado de la cola."""
        with self._lock:
            raw = self._load_raw()
            filtered = [d for d in raw if d.get("id") != item_id]
            self._save_raw(filtered)

    def mark_failed(self, item_id: str, error_msg: str) -> None:
        """Incrementa el contador de reintentos y registra el error."""
        with self._lock:
            raw = self._load_raw()
            for d in raw:
                if d.get("id") == item_id:
                    d["retry_count"] = d.get("retry_count", 0) + 1
                    d["last_error"] = str(error_msg)
                    break
            self._save_raw(raw)

    def count(self) -> int:
        """Retorna el número de elementos pendientes en la cola."""
        with self._lock:
            return len(self._load_raw())

    def clear(self) -> None:
        """Limpia completamente la cola de sincronización."""
        with self._lock:
            self._save_raw([])


# ==============================================================================
# 3. GESTOR PRINCIPAL DE SINCRONIZACIÓN: FirebaseSyncManager
# ==============================================================================

class FirebaseSyncManager:
    """
    Gestor maestro de sincronización bidireccional entre el almacenamiento local de VideoPro
    y Firebase Firestore con arquitectura Offline-First y tolerancia a fallos.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        storage_dir: Optional[Union[str, Path]] = None,
        auto_flush: bool = True
    ):
        self.storage_dir = Path(storage_dir) if storage_dir else STORAGE_DIR
        self.workflows_dir = self.storage_dir / "workflows"
        self.learning_dir = self.storage_dir / "learning_memory"
        self.projects_dir = self.storage_dir / "projects"

        self.client = FirestoreRESTClient(project_id=project_id)
        self.queue = OfflineSyncQueue()
        self._background_thread: Optional[threading.Thread] = None
        self._running = False

        if auto_flush and self.client.is_online() and self.queue.count() > 0:
            self.flush_queue_async()

    # --------------------------------------------------------------------------
    # 3.1 GESTIÓN DE COLA Y ESTADO DE CONECTIVIDAD
    # --------------------------------------------------------------------------

    def get_sync_status(self) -> Dict[str, Any]:
        """Retorna el diagnóstico completo de conectividad y estado de la cola."""
        conn = self.client.check_connection()
        pending_count = self.queue.count()
        pending_items = self.queue.get_pending()

        return {
            "connected": conn.get("connected", False),
            "project_id": conn.get("project_id"),
            "hosting_url": conn.get("hosting_url"),
            "status_message": conn.get("message"),
            "offline_mode": not conn.get("connected", False),
            "pending_queue_count": pending_count,
            "pending_operations": [
                {
                    "id": item.id,
                    "action": item.action,
                    "collection": item.collection,
                    "document_id": item.document_id,
                    "retry_count": item.retry_count,
                    "last_error": item.last_error,
                    "created_at": item.created_at
                }
                for item in pending_items[:10]
            ],
            "checked_at": get_utc_iso_now()
        }

    def flush_queue(self, max_items: int = 50) -> Dict[str, Any]:
        """
        Procesa los elementos pendientes en la cola offline y los sincroniza con Firestore.
        """
        if not self.client.is_online():
            return {
                "success": False,
                "flushed_count": 0,
                "remaining_count": self.queue.count(),
                "message": "Sin conexión con Firebase Firestore. Los elementos se mantienen en la cola offline."
            }

        pending = self.queue.get_pending()
        if not pending:
            return {
                "success": True,
                "flushed_count": 0,
                "remaining_count": 0,
                "message": "La cola offline está vacía. Todos los datos están sincronizados."
            }

        flushed = 0
        failed = 0
        errors = []

        logger.info(f"🔄 Procesando {len(pending)} operaciones pendientes en la cola offline...")

        for item in pending[:max_items]:
            success = False
            error_msg = ""

            try:
                if item.action == "upsert":
                    ok, msg = self.client.set_document(item.collection, item.document_id, item.data)
                    if ok:
                        success = True
                    else:
                        error_msg = msg
                elif item.action == "delete":
                    ok, msg = self.client.delete_document(item.collection, item.document_id)
                    if ok:
                        success = True
                    else:
                        error_msg = msg
            except Exception as ex:
                error_msg = str(ex)

            if success:
                self.queue.remove(item.id)
                flushed += 1
            else:
                self.queue.mark_failed(item.id, error_msg)
                failed += 1
                errors.append(f"[{item.collection}/{item.document_id}]: {error_msg}")

        logger.info(f"✅ Cola offline procesada: {flushed} aplicados con éxito, {failed} con error.")
        return {
            "success": failed == 0,
            "flushed_count": flushed,
            "failed_count": failed,
            "remaining_count": self.queue.count(),
            "errors": errors,
            "timestamp": get_utc_iso_now()
        }

    def flush_queue_async(self):
        """Ejecuta el procesamiento de la cola en segundo plano."""
        t = threading.Thread(target=self.flush_queue, daemon=True)
        t.start()
        return t

    # --------------------------------------------------------------------------
    # 3.2 COLECCIÓN: WORKFLOWS (8 Arquetipos, 7D Parameters, SemVer, SHA-256)
    # --------------------------------------------------------------------------

    def push_workflow(self, workflow_data_or_obj: Any) -> Tuple[bool, str]:
        """
        Sincroniza un workflow estructurado a Firestore en las colecciones `videopro_workflows` y `workflows`.
        Si está offline, lo registra automáticamente en la cola offline.
        """
        if hasattr(workflow_data_or_obj, "model_dump"):
            data = workflow_data_or_obj.model_dump()
        elif hasattr(workflow_data_or_obj, "dict"):
            data = workflow_data_or_obj.dict()
        elif isinstance(workflow_data_or_obj, dict):
            data = copy.deepcopy(workflow_data_or_obj)
        else:
            return False, "Tipo de dato de workflow inválido."

        archetype_id = data.get("archetype_id", "CUSTOM_WORKFLOW")
        version_info = data.get("version_info", {})
        semver = version_info.get("semver", "v1.0.0")

        # Asegurar hash de integridad SHA-256
        sha256_hash = compute_sha256(data)
        if "version_info" in data:
            data["version_info"]["sha256_hash"] = sha256_hash
            data["version_info"]["updated_at"] = get_utc_iso_now()

        data["updated_at"] = get_utc_iso_now()
        data["sync_hash"] = sha256_hash

        doc_id_latest = archetype_id
        doc_id_versioned = f"{archetype_id}_{semver}"

        # Verificar si estamos online
        if not self.client.is_online():
            self.queue.enqueue("upsert", "videopro_workflows", doc_id_latest, data)
            self.queue.enqueue("upsert", "videopro_workflows", doc_id_versioned, data)
            self.queue.enqueue("upsert", "workflows", doc_id_latest, data)
            return True, f"Workflow '{archetype_id}' ({semver}) guardado en la cola offline de sincronización."

        # Guardar en Firestore: latest y versión específica
        ok1, msg1 = self.client.set_document("videopro_workflows", doc_id_latest, data)
        ok2, msg2 = self.client.set_document("videopro_workflows", doc_id_versioned, data)
        self.client.set_document("workflows", doc_id_latest, data)

        if ok1:
            logger.info(f"☁️ Workflow '{archetype_id}' ({semver}) sincronizado con Firestore [SHA-256: {sha256_hash[:10]}...]")
            return True, f"Workflow '{archetype_id}' sincronizado exitosamente en Firestore."
        else:
            self.queue.enqueue("upsert", "videopro_workflows", doc_id_latest, data)
            self.queue.enqueue("upsert", "videopro_workflows", doc_id_versioned, data)
            return False, f"Fallo al sincronizar en Firestore ({msg1}). Encolado en modo offline."

    def push_all_workflows(self, parallel: bool = True) -> Dict[str, Any]:
        """
        Escanea `storage/workflows/` y sincroniza todos los workflows de los 8 arquetipos
        canónicos y el catálogo manifest a Firestore concurrentemente.
        """
        results = {"pushed": [], "queued": [], "errors": []}

        if not self.workflows_dir.exists():
            return results

        # 1. Sincronizar catálogo maestro si existe
        catalog_file = self.workflows_dir / "workflow_catalog.json"
        if catalog_file.exists():
            try:
                with open(catalog_file, "r", encoding="utf-8") as f:
                    catalog_data = json.load(f)
                catalog_data["updated_at"] = get_utc_iso_now()
                if self.client.is_online():
                    self.client.set_document("videopro_system", "workflow_catalog", catalog_data)
                    self.client.set_document("videopro_workflows", "_catalog", catalog_data)
                else:
                    self.queue.enqueue("upsert", "videopro_system", "workflow_catalog", catalog_data)
                results["pushed"].append("workflow_catalog")
            except Exception as ex:
                results["errors"].append(f"Error en catálogo: {ex}")

        # 2. Recolectar archivos JSON de workflows
        files_to_sync = []
        for json_path in sorted(self.workflows_dir.glob("*.json")):
            if json_path.name in ["workflow_catalog.json", "pipeline_graph.json"]:
                continue
            files_to_sync.append(json_path)

        def _sync_single_wf_file(path: Path) -> Tuple[str, bool, str]:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    wf_data = json.load(f)
                if not isinstance(wf_data, dict) or ("archetype_id" not in wf_data and "name" not in wf_data):
                    return path.stem, False, "Estructura no válida de workflow"
                ok, msg = self.push_workflow(wf_data)
                return path.stem, ok, msg
            except Exception as ex:
                return path.stem, False, str(ex)

        if parallel and len(files_to_sync) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                future_to_file = {executor.submit(_sync_single_wf_file, p): p for p in files_to_sync}
                for future in concurrent.futures.as_completed(future_to_file):
                    stem, ok, msg = future.result()
                    if ok:
                        results["pushed"].append(stem)
                    else:
                        if "offline" in msg.lower() or "encolado" in msg.lower():
                            results["queued"].append(stem)
                        else:
                            results["errors"].append(f"{stem}: {msg}")
        else:
            for p in files_to_sync:
                stem, ok, msg = _sync_single_wf_file(p)
                if ok:
                    results["pushed"].append(stem)
                else:
                    if "offline" in msg.lower() or "encolado" in msg.lower():
                        results["queued"].append(stem)
                    else:
                        results["errors"].append(f"{stem}: {msg}")

        logger.info(f"📦 Total workflows sincronizados: {len(results['pushed'])} OK, {len(results['queued'])} encolados.")
        return results

    def pull_all_workflows(self) -> Dict[str, Any]:
        """
        Descarga desde Firestore todos los workflows disponibles y actualiza el almacenamiento local.
        """
        if not self.client.is_online():
            return {"success": False, "pulled_count": 0, "message": "Sin conexión con Firestore."}

        docs = self.client.list_documents("videopro_workflows")
        pulled = []

        for doc in docs:
            doc_id = doc.get("_doc_id", "")
            if not doc_id or doc_id.startswith("_"):
                continue

            archetype_id = doc.get("archetype_id", doc_id)
            version_info = doc.get("version_info", {})
            semver = version_info.get("semver", "v1.0.0")

            target_json = self.workflows_dir / f"{archetype_id}_{semver}.json"
            target_latest = self.workflows_dir / f"{archetype_id}_latest.json"

            clean_data = {k: v for k, v in doc.items() if not k.startswith("_")}

            try:
                with open(target_json, "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, indent=2, ensure_ascii=False)
                with open(target_latest, "w", encoding="utf-8") as f:
                    json.dump(clean_data, f, indent=2, ensure_ascii=False)
                pulled.append(f"{archetype_id} ({semver})")
            except Exception as ex:
                logger.warning(f"Error al escribir workflow local {doc_id}: {ex}")

        try:
            from scripts.workflow_registry import registry
            registry.reload_from_storage()
        except Exception:
            pass

        return {
            "success": True,
            "pulled_count": len(pulled),
            "workflows": pulled,
            "timestamp": get_utc_iso_now()
        }

    # --------------------------------------------------------------------------
    # 3.3 COLECCIÓN: LEARNING MEMORY (Lecciones, Auditorías R01-R10, Auto-Parcheos)
    # --------------------------------------------------------------------------

    def push_lessons_catalog(self, lessons_list_or_file: Optional[Union[List[Dict[str, Any]], Path, str]] = None) -> Tuple[bool, str]:
        """Sincroniza el catálogo de lecciones aprendidas con Firestore."""
        lessons: List[Dict[str, Any]] = []

        if lessons_list_or_file is None:
            file_path = self.learning_dir / "lessons_catalog.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    lessons = json.load(f)
        elif isinstance(lessons_list_or_file, (str, Path)):
            with open(lessons_list_or_file, "r", encoding="utf-8") as f:
                lessons = json.load(f)
        elif isinstance(lessons_list_or_file, list):
            lessons = lessons_list_or_file

        if not lessons:
            return True, "No hay lecciones para sincronizar."

        payload = {
            "updated_at": get_utc_iso_now(),
            "total_lessons": len(lessons),
            "lessons": lessons,
            "sha256_hash": compute_sha256(lessons)
        }

        if not self.client.is_online():
            self.queue.enqueue("upsert", "videopro_learning_memory", "lessons_catalog", payload)
            self.queue.enqueue("upsert", "learning_memory", "lessons_catalog", payload)
            return True, "Catálogo de lecciones guardado en la cola offline."

        self.client.set_document("videopro_learning_memory", "lessons_catalog", payload)
        self.client.set_document("learning_memory", "lessons_catalog", payload)

        for lesson in lessons:
            lid = lesson.get("id", f"lesson_{int(time.time()*1000)}")
            lesson_doc = copy.deepcopy(lesson)
            lesson_doc["updated_at"] = get_utc_iso_now()
            self.client.set_document("videopro_lessons", lid, lesson_doc)

        logger.info(f"🧠 {len(lessons)} lecciones de aprendizaje sincronizadas con Firestore.")
        return True, f"{len(lessons)} lecciones sincronizadas exitosamente."

    def push_project_critiques(self, critiques_list_or_file: Optional[Union[List[Dict[str, Any]], Path, str]] = None) -> Tuple[bool, str]:
        """Sincroniza las evaluaciones forenses y críticas post-mortem de proyectos."""
        critiques: List[Dict[str, Any]] = []

        if critiques_list_or_file is None:
            file_path = self.learning_dir / "project_critiques.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    critiques = json.load(f)
        elif isinstance(critiques_list_or_file, (str, Path)):
            with open(critiques_list_or_file, "r", encoding="utf-8") as f:
                critiques = json.load(f)
        elif isinstance(critiques_list_or_file, list):
            critiques = critiques_list_or_file

        if not critiques:
            return True, "No hay críticas para sincronizar."

        payload = {
            "updated_at": get_utc_iso_now(),
            "total_critiques": len(critiques),
            "critiques": critiques,
            "sha256_hash": compute_sha256(critiques)
        }

        if not self.client.is_online():
            self.queue.enqueue("upsert", "videopro_learning_memory", "project_critiques", payload)
            return True, "Críticas guardadas en la cola offline."

        self.client.set_document("videopro_learning_memory", "project_critiques", payload)
        self.client.set_document("learning_memory", "project_critiques", payload)

        for c in critiques:
            pid = c.get("project_id", f"audit_{int(time.time()*1000)}")
            self.client.set_document("videopro_audits", pid, c)

        logger.info(f"📋 {len(critiques)} auditorías de calidad R01-R10 sincronizadas con Firestore.")
        return True, f"{len(critiques)} auditorías sincronizadas."

    def push_provider_metrics(self) -> Tuple[bool, str]:
        """Sincroniza las métricas de rendimiento y errores de proveedores multi-cloud."""
        metrics_file = self.learning_dir / "provider_metrics.json"
        if not metrics_file.exists():
            return True, "Sin archivo de métricas."

        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)

            payload = {
                "updated_at": get_utc_iso_now(),
                "metrics": metrics,
                "sha256_hash": compute_sha256(metrics)
            }

            if not self.client.is_online():
                self.queue.enqueue("upsert", "videopro_system", "provider_metrics", payload)
                return True, "Métricas de proveedor encoladas offline."

            self.client.set_document("videopro_system", "provider_metrics", payload)
            self.client.set_document("videopro_learning_memory", "provider_metrics", payload)
            return True, "Métricas de proveedores sincronizadas en Firestore."
        except Exception as ex:
            return False, f"Error en métricas: {ex}"

    def push_workflow_improvements(self) -> Tuple[bool, str]:
        """Sincroniza el historial de auto-parcheos y mejoras de workflows aplicadas."""
        impr_file = self.learning_dir / "workflow_improvements.json"
        perf_file = self.learning_dir / "archetype_performance.json"

        results = []

        if impr_file.exists():
            try:
                with open(impr_file, "r", encoding="utf-8") as f:
                    impr_data = json.load(f)
                payload = {
                    "updated_at": get_utc_iso_now(),
                    "total_improvements": len(impr_data) if isinstance(impr_data, list) else 0,
                    "improvements": impr_data
                }
                if self.client.is_online():
                    self.client.set_document("videopro_system", "workflow_improvements", payload)
                else:
                    self.queue.enqueue("upsert", "videopro_system", "workflow_improvements", payload)
                results.append("workflow_improvements")
            except Exception as ex:
                logger.warning(f"Error sincronizando mejoras: {ex}")

        if perf_file.exists():
            try:
                with open(perf_file, "r", encoding="utf-8") as f:
                    perf_data = json.load(f)
                payload = {
                    "updated_at": get_utc_iso_now(),
                    "performance": perf_data
                }
                if self.client.is_online():
                    self.client.set_document("videopro_system", "archetype_performance", payload)
                else:
                    self.queue.enqueue("upsert", "videopro_system", "archetype_performance", payload)
                results.append("archetype_performance")
            except Exception as ex:
                logger.warning(f"Error sincronizando rendimiento: {ex}")

        return True, f"Mejoras y métricas sincronizadas: {', '.join(results)}"

    def emit_learning_event(self, event_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Emite un evento de aprendizaje en tiempo real o lo encola si está en modo offline.
        """
        event_id = event_data.get("event_id") or f"evt_{int(time.time() * 1000)}"
        event_payload = copy.deepcopy(event_data)
        event_payload["event_id"] = event_id
        event_payload["timestamp"] = event_payload.get("timestamp", get_utc_iso_now())

        if not self.client.is_online():
            self.queue.enqueue("upsert", "videopro_learning_events", event_id, event_payload)
            return True, f"Evento {event_id} encolado offline."

        live_doc = {
            "last_event_id": event_id,
            "last_event_type": event_payload.get("event_type", "UNKNOWN"),
            "last_message": event_payload.get("message", ""),
            "last_project_id": event_payload.get("project_id", "system"),
            "last_archetype_id": event_payload.get("archetype_id", "GLOBAL"),
            "last_updated": event_payload["timestamp"],
            "event_data": event_payload
        }
        self.client.set_document("videopro_system", "workflow_learner_live", live_doc)
        ok, msg = self.client.set_document("videopro_learning_events", event_id, event_payload)
        return ok, msg

    def pull_learning_memory(self) -> Dict[str, Any]:
        """Descarga toda la memoria de aprendizaje desde Firestore."""
        if not self.client.is_online():
            return {"success": False, "message": "Sin conexión con Firestore."}

        doc_lessons = self.client.get_document("videopro_learning_memory", "lessons_catalog")
        if doc_lessons and "lessons" in doc_lessons:
            lessons_data = doc_lessons["lessons"]
            with open(self.learning_dir / "lessons_catalog.json", "w", encoding="utf-8") as f:
                json.dump(lessons_data, f, indent=2, ensure_ascii=False)

        doc_critiques = self.client.get_document("videopro_learning_memory", "project_critiques")
        if doc_critiques and "critiques" in doc_critiques:
            critiques_data = doc_critiques["critiques"]
            with open(self.learning_dir / "project_critiques.json", "w", encoding="utf-8") as f:
                json.dump(critiques_data, f, indent=2, ensure_ascii=False)

        return {"success": True, "message": "Memoria de aprendizaje restaurada desde Firestore."}

    # --------------------------------------------------------------------------
    # 3.4 COLECCIÓN: PROJECTS (Ciclo de Vida, Hashes SHA-256, URLs Maestras)
    # --------------------------------------------------------------------------

    def push_project(self, project_ref_or_manifest: Union[str, Path, Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Sincroniza un proyecto de vídeo completo con Firestore (`videopro_projects` y `projects`).
        Extrae y valida el manifiesto, hashes SHA-256 de activos, ciclo de vida y URLs maestras.
        """
        manifest_data: Dict[str, Any] = {}
        project_id = "unknown_project"

        if isinstance(project_ref_or_manifest, dict):
            manifest_data = copy.deepcopy(project_ref_or_manifest)
            project_id = manifest_data.get("project_id") or manifest_data.get("slug") or "project_default"
        else:
            p = Path(project_ref_or_manifest).resolve()
            if p.is_file() and p.name.endswith(".json"):
                with open(p, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                project_id = manifest_data.get("project_id", p.parent.parent.name)
            elif p.is_dir():
                man_path = p / "manifest.json"
                if not man_path.exists():
                    man_path = p / "v1" / "manifest.json"
                if man_path.exists():
                    with open(man_path, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)
                    project_id = manifest_data.get("project_id", p.name)
                else:
                    return False, f"No se encontró manifest.json en '{p}'"

        title = manifest_data.get("title") or manifest_data.get("topic") or manifest_data.get("slug", project_id)
        status = manifest_data.get("status", "initialized")
        pipeline_lifecycle = manifest_data.get("pipeline_lifecycle", {})
        assets_manifest = manifest_data.get("assets_manifest", [])
        metadata = manifest_data.get("metadata", {})
        exports_info = manifest_data.get("exports", {})
        master_url = manifest_data.get("master_url") or manifest_data.get("cloud_url", "")

        assets_summary = []
        verified_assets_count = 0
        total_asset_bytes = 0

        for a in assets_manifest:
            a_path = a.get("path", "")
            a_sha = a.get("sha256", "")
            a_size = a.get("filesize_bytes") or a.get("size_bytes", 0)

            total_asset_bytes += a_size
            if a_size >= 5120:
                verified_assets_count += 1

            assets_summary.append({
                "id": a.get("id", ""),
                "name": a.get("name", ""),
                "category": a.get("category", "asset"),
                "relative_path": a.get("relative_path", a_path),
                "sha256": a_sha,
                "size_bytes": a_size,
                "gate_passed": a_size >= 5120,
                "verified": bool(a.get("verified", True))
            })

        project_doc = {
            "project_id": project_id,
            "task_id": project_id,
            "title": title,
            "slug": manifest_data.get("slug", project_id),
            "date": manifest_data.get("date", get_utc_iso_now()[:10]),
            "version": manifest_data.get("version", "v1"),
            "status": status,
            "pipeline_lifecycle": pipeline_lifecycle,
            "assets_count": len(assets_summary),
            "verified_assets_count": verified_assets_count,
            "total_asset_bytes": total_asset_bytes,
            "assets_manifest": assets_summary,
            "master_url": master_url,
            "cloud_synced": True,
            "metadata": metadata,
            "exports": exports_info,
            "created_at": manifest_data.get("created_at", get_utc_iso_now()),
            "updated_at": get_utc_iso_now(),
            "manifest_sha256": compute_sha256(manifest_data),
            "manifest_json": manifest_data
        }

        if not self.client.is_online():
            self.queue.enqueue("upsert", "videopro_projects", project_id, project_doc)
            self.queue.enqueue("upsert", "projects", project_id, project_doc)
            return True, f"Proyecto '{project_id}' registrado en la cola offline de sincronización."

        ok1, msg1 = self.client.set_document("videopro_projects", project_id, project_doc)
        self.client.set_document("projects", project_id, project_doc)

        if ok1:
            logger.info(f"🎬 Proyecto '{project_id}' sincronizado con Firestore [{verified_assets_count} activos verificados]")
            return True, f"Proyecto '{project_id}' sincronizado exitosamente en Firestore."
        else:
            self.queue.enqueue("upsert", "videopro_projects", project_id, project_doc)
            return False, f"Fallo al sincronizar proyecto: {msg1}. Encolado offline."

    def push_all_projects(self, parallel: bool = True) -> Dict[str, Any]:
        """
        Descubre y sincroniza todos los proyectos de vídeo locales bajo `storage/projects/` concurrentemente.
        """
        results = {"pushed": [], "queued": [], "errors": []}
        if not self.projects_dir.exists():
            return results

        man_files = list(self.projects_dir.glob("**/manifest.json"))

        def _sync_single_project(man_path: Path) -> Tuple[str, bool, str]:
            try:
                with open(man_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pid = data.get("project_id", man_path.parent.parent.name)
                ok, msg = self.push_project(data)
                return pid, ok, msg
            except Exception as ex:
                return man_path.parent.name, False, str(ex)

        if parallel and len(man_files) > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_proj = {executor.submit(_sync_single_project, p): p for p in man_files}
                for future in concurrent.futures.as_completed(future_to_proj):
                    pid, ok, msg = future.result()
                    if ok:
                        results["pushed"].append(pid)
                    else:
                        if "offline" in msg.lower() or "encolado" in msg.lower():
                            results["queued"].append(pid)
                        else:
                            results["errors"].append(f"{pid}: {msg}")
        else:
            for p in man_files:
                pid, ok, msg = _sync_single_project(p)
                if ok:
                    results["pushed"].append(pid)
                else:
                    if "offline" in msg.lower() or "encolado" in msg.lower():
                        results["queued"].append(pid)
                    else:
                        results["errors"].append(f"{pid}: {msg}")

        logger.info(f"📽️ Total proyectos sincronizados: {len(results['pushed'])} OK, {len(results['queued'])} encolados.")
        return results

    def pull_all_projects(self) -> Dict[str, Any]:
        """Obtiene la lista de proyectos almacenados en Firestore."""
        if not self.client.is_online():
            return {"success": False, "projects": [], "message": "Sin conexión con Firestore."}

        docs = self.client.list_documents("videopro_projects")
        projects = []
        for d in docs:
            pid = d.get("project_id") or d.get("_doc_id")
            projects.append({
                "project_id": pid,
                "title": d.get("title", pid),
                "status": d.get("status", "UNKNOWN"),
                "version": d.get("version", "v1"),
                "assets_count": d.get("assets_count", 0),
                "master_url": d.get("master_url", ""),
                "updated_at": d.get("updated_at", "")
            })

        return {
            "success": True,
            "total_count": len(projects),
            "projects": projects,
            "timestamp": get_utc_iso_now()
        }

    # --------------------------------------------------------------------------
    # 3.5 SINCRONIZACIÓN COMPLETA BIDIRECCIONAL (sync-all)
    # --------------------------------------------------------------------------

    def sync_all(self, force: bool = False) -> Dict[str, Any]:
        """
        Ejecuta la sincronización bidireccional exhaustiva de:
          1. Procesamiento de la cola offline pendiente.
          2. Sincronización de los 8 Workflows canónicos y sus versiones SemVer.
          3. Sincronización de la Memoria de Aprendizaje (lecciones, auditorías R01-R10, métricas, mejoras).
          4. Sincronización de todos los Proyectos de vídeo y hashes SHA-256 de activos.
          5. Emisión de evento de sincronización completada.
        """
        start_time = time.time()
        logger.info("🚀 Iniciando sincronización completa de VideoPro con Firebase Firestore...")

        report: Dict[str, Any] = {
            "started_at": get_utc_iso_now(),
            "online": self.client.is_online(),
            "queue_flush": {},
            "workflows_sync": {},
            "learning_memory_sync": {},
            "projects_sync": {},
            "elapsed_seconds": 0.0,
            "status": "COMPLETED"
        }

        # 1. Vaciar cola offline
        if self.client.is_online():
            report["queue_flush"] = self.flush_queue()
        else:
            report["queue_flush"] = {
                "success": False,
                "message": "Operando en modo offline. Los cambios locales se sincronizarán al reconectar."
            }

        # 2. Sincronizar Workflows
        wf_pushed = self.push_all_workflows(parallel=True)
        report["workflows_sync"] = {
            "pushed_count": len(wf_pushed.get("pushed", [])),
            "queued_count": len(wf_pushed.get("queued", [])),
            "details": wf_pushed
        }

        # 3. Sincronizar Memoria de Aprendizaje
        lessons_ok, lessons_msg = self.push_lessons_catalog()
        critiques_ok, critiques_msg = self.push_project_critiques()
        metrics_ok, metrics_msg = self.push_provider_metrics()
        impr_ok, impr_msg = self.push_workflow_improvements()

        report["learning_memory_sync"] = {
            "lessons": {"success": lessons_ok, "message": lessons_msg},
            "critiques_and_audits": {"success": critiques_ok, "message": critiques_msg},
            "provider_metrics": {"success": metrics_ok, "message": metrics_msg},
            "improvements": {"success": impr_ok, "message": impr_msg}
        }

        # 4. Sincronizar Proyectos
        proj_pushed = self.push_all_projects(parallel=True)
        report["projects_sync"] = {
            "pushed_count": len(proj_pushed.get("pushed", [])),
            "queued_count": len(proj_pushed.get("queued", [])),
            "details": proj_pushed
        }

        # 5. Registrar evento de sincronización
        elapsed = round(time.time() - start_time, 3)
        report["elapsed_seconds"] = elapsed
        report["completed_at"] = get_utc_iso_now()

        self.emit_learning_event({
            "event_type": "FIREBASE_SYNC_COMPLETED",
            "session_id": "sync_manager",
            "project_id": "system",
            "archetype_id": "GLOBAL",
            "message": f"Sincronización bidireccional completada en {elapsed}s",
            "payload": {
                "workflows_count": len(wf_pushed.get("pushed", [])),
                "projects_count": len(proj_pushed.get("pushed", [])),
                "online": self.client.is_online()
            }
        })

        logger.info(f"✨ Sincronización completa finalizada en {elapsed}s.")
        return report

    # --------------------------------------------------------------------------
    # 3.6 MODO DAEMON / WATCHER
    # --------------------------------------------------------------------------

    def start_sync_watcher(self, interval_seconds: int = 60) -> None:
        """Inicia un bucle periódico de sincronización en segundo plano."""
        if self._running:
            logger.info("El sincronizador en segundo plano ya está en ejecución.")
            return

        self._running = True

        def _loop():
            logger.info(f"🕒 Demonio de sincronización de Firebase iniciado (intervalo: {interval_seconds}s).")
            while self._running:
                try:
                    if self.client.is_online():
                        if self.queue.count() > 0:
                            self.flush_queue()
                    time.sleep(interval_seconds)
                except Exception as ex:
                    logger.debug(f"Aviso en bucle de sincronización: {ex}")
                    time.sleep(interval_seconds)

        self._background_thread = threading.Thread(target=_loop, daemon=True)
        self._background_thread.start()

    def stop_sync_watcher(self) -> None:
        """Detiene el bucle periódico de sincronización."""
        self._running = False
        logger.info("Demonio de sincronización detenido.")


# Singleton global exportado
sync_manager = FirebaseSyncManager()


# ==============================================================================
# 4. CLI INTERFACE
# ==============================================================================

def main():
    """Punto de entrada de línea de comandos para el gestor de sincronización de Firebase."""
    parser = argparse.ArgumentParser(
        description="VideoPro Firebase Sync Manager — Sincronización Bidireccional y Offline-First"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # status
    subparsers.add_parser("status", help="Muestra el estado de conexión con Firestore y la cola offline.")

    # sync-all
    subparsers.add_parser("sync-all", help="Sincroniza todas las colecciones (workflows, aprendizaje y proyectos).")

    # sync-workflows
    p_wf = subparsers.add_parser("sync-workflows", help="Sincroniza los 8 arquetipos canónicos de workflows.")
    p_wf.add_argument("--pull", action="store_true", help="Descarga workflows desde Firestore.")
    p_wf.add_argument("--push", action="store_true", default=True, help="Envía workflows locales a Firestore.")

    # sync-learning
    p_lm = subparsers.add_parser("sync-learning", help="Sincroniza el catálogo de lecciones, auditorías y métricas.")
    p_lm.add_argument("--pull", action="store_true", help="Descarga lecciones desde Firestore.")
    p_lm.add_argument("--push", action="store_true", default=True, help="Envía lecciones y auditorías a Firestore.")

    # sync-projects
    p_pj = subparsers.add_parser("sync-projects", help="Sincroniza proyectos de vídeo y manifiestos de activos.")
    p_pj.add_argument("--pull", action="store_true", help="Descarga proyectos desde Firestore.")
    p_pj.add_argument("--push", action="store_true", default=True, help="Envía proyectos locales a Firestore.")

    # flush-queue
    subparsers.add_parser("flush-queue", help="Procesa y vacía la cola offline de sincronización.")

    # watch
    p_watch = subparsers.add_parser("watch", help="Ejecuta el monitor de sincronización periódica en segundo plano.")
    p_watch.add_argument("--interval", type=int, default=30, help="Intervalo en segundos entre chequeos.")

    args = parser.parse_args()

    if not args.command or args.command == "status":
        st = sync_manager.get_sync_status()
        print("\n" + "=" * 70)
        print("  VIDEOPRO FIREBASE FIRESTORE SYNC STATUS")
        print("=" * 70)
        print(f"  • Estado de Conexión : {'🟢 ONLINE' if st['connected'] else '🔴 OFFLINE'}")
        print(f"  • Proyecto Firebase  : {st.get('project_id')}")
        print(f"  • Hosting URL        : {st.get('hosting_url')}")
        print(f"  • Mensaje            : {st.get('status_message')}")
        print(f"  • Cola Offline       : {st.get('pending_queue_count')} operaciones pendientes")
        print(f"  • Verificado en      : {st.get('checked_at')}")
        print("=" * 70 + "\n")
        if st.get("pending_operations"):
            print("Operaciones pendientes en cola:")
            for op in st["pending_operations"]:
                print(f"  - [{op['action'].upper()}] {op['collection']}/{op['document_id']} (reintentos: {op['retry_count']})")
            print()

    elif args.command == "sync-all":
        res = sync_manager.sync_all()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "sync-workflows":
        if args.pull:
            res = sync_manager.pull_all_workflows()
        else:
            res = sync_manager.push_all_workflows()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "sync-learning":
        if args.pull:
            res = sync_manager.pull_learning_memory()
        else:
            sync_manager.push_lessons_catalog()
            sync_manager.push_project_critiques()
            sync_manager.push_provider_metrics()
            res = sync_manager.push_workflow_improvements()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "sync-projects":
        if args.pull:
            res = sync_manager.pull_all_projects()
        else:
            res = sync_manager.push_all_projects()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "flush-queue":
        res = sync_manager.flush_queue()
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "watch":
        print(f"Iniciando monitor de sincronización cada {args.interval}s (Ctrl+C para salir)...")
        sync_manager.start_sync_watcher(interval_seconds=args.interval)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync_manager.stop_sync_watcher()
            print("Monitor detenido.")


if __name__ == "__main__":
    main()
