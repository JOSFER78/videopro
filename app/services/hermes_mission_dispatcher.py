"""
hermes_mission_dispatcher.py
Despachador y Gestor de Misiones Asíncronas para Hermes Agent.
Estructura la delegación desacoplada entre la WebUI y el Cerebro de Hermes:
1. Recibe especificaciones de misiones declarativas (Workflow, Entrevista, Parámetros).
2. Persiste el contrato en almacenamiento local (storage/missions/<id>/) y en Firebase Firestore (videopro_missions/<id>).
3. Gestiona el ciclo de vida agéntico (PENDING ➔ REASONING ➔ PRODUCING_ASSETS ➔ COMPOSING ➔ QA_VERIFYING ➔ COMPLETED).
4. Transmite en tiempo real el razonamiento CoT (Thinking Log), el avance de los 7 Nodos y los artefactos generados.
"""

import os
import json
import time
import uuid
import threading
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
try:
    from loguru import logger
except ImportError:
    import logging as logger

from app.config import config
from app.services import firebase_sync


class HermesMissionStatus:
    PENDING = "PENDING"
    REASONING = "REASONING"
    PRODUCING_ASSETS = "PRODUCING_ASSETS"
    COMPOSING = "COMPOSING"
    QA_VERIFYING = "QA_VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class HermesMissionDispatcher:
    """Orquestador de misiones desacopladas para Hermes Agent."""

    def __init__(self, base_storage_dir: Optional[str] = None):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.storage_dir = Path(base_storage_dir) if base_storage_dir else project_root / "storage" / "missions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_firestore_headers(self) -> Dict[str, str]:
        token = firebase_sync._get_firebase_auth_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _get_project_id(self) -> str:
        return config.app.get("firebase_project_id") or "ayuda-emilio-83261"

    def create_mission(
        self,
        workflow_id: str,
        title: str,
        topic: str,
        interview_answers: Dict[str, Any],
        target_channel: Optional[str] = None,
        duration_target_sec: float = 180.0
    ) -> Dict[str, Any]:
        """Crea una nueva misión declarativa y la registra en local y Firestore."""
        mission_id = f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        mission_dir = self.storage_dir / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)
        (mission_dir / "artifacts").mkdir(parents=True, exist_ok=True)

        now_iso = datetime.now().isoformat()

        mission_data = {
            "mission_id": mission_id,
            "title": title,
            "topic": topic,
            "workflow_id": workflow_id,
            "status": HermesMissionStatus.PENDING,
            "target_channel": target_channel or "Hermes Documentary Studio",
            "duration_target_sec": duration_target_sec,
            "interview_answers": interview_answers,
            "created_at": now_iso,
            "updated_at": now_iso,
            "current_node_index": 0,
            "current_node_name": "node_01_investigacion_y_storyboard",
            "progress_percent": 0.0,
            "thinking_logs": [
                f"[{now_iso}] 🤖 Hermes Agent ha recibido la misión: '{title}'. Iniciando análisis de objetivos y arquetipo '{workflow_id}'."
            ],
            "nodes_state": {
                "node_01_investigacion_y_storyboard": {"status": "PENDING", "progress": 0, "label": "Investigación & Storyboard Studio"},
                "node_02_audio_first_y_foley": {"status": "PENDING", "progress": 0, "label": "Audio-First & Foley Diegético"},
                "node_03_generacion_activos_vox": {"status": "PENDING", "progress": 0, "label": "Generación de Activos Auténticos"},
                "node_04_composicion_3d_parallax": {"status": "PENDING", "progress": 0, "label": "Composición 3D Parallax"},
                "node_05_subtitulos_y_hud": {"status": "PENDING", "progress": 0, "label": "Subtítulos & Telemetría HUD"},
                "node_06_masterizacion_ebu_r128": {"status": "PENDING", "progress": 0, "label": "Masterización EBU R128"},
                "node_07_qa_contact_sheet_sync": {"status": "PENDING", "progress": 0, "label": "QA Loop & Cloud Sync"}
            },
            "artifacts": {
                "script_path": None,
                "audio_master_path": None,
                "storyboard_matrix": [],
                "generated_assets": [],
                "master_video_path": None,
                "qa_contact_sheet_path": None
            },
            "metrics": {
                "total_scenes": 0,
                "rendered_fps": 30,
                "audio_lufs": -14.0,
                "cost_estimate_usd": 0.0
            }
        }

        # 1. Guardar localmente
        mission_json_path = mission_dir / "mission.json"
        with open(mission_json_path, "w", encoding="utf-8") as f:
            json.dump(mission_data, f, indent=2, ensure_ascii=False)

        # 2. Persistir en Firebase Firestore
        self._sync_mission_to_firestore(mission_data)

        logger.info(f"✨ Misión creada con éxito: {mission_id} ({title})")
        return mission_data

    def append_thinking_log(self, mission_id: str, log_message: str, new_status: Optional[str] = None, progress_percent: Optional[float] = None) -> bool:
        """Añade una línea de razonamiento en vivo a la mente de Hermes y actualiza el estado."""
        mission_dir = self.storage_dir / mission_id
        mission_json_path = mission_dir / "mission.json"

        if not mission_json_path.is_file():
            logger.warning(f"Misión no encontrada para actualizar logs: {mission_id}")
            return False

        try:
            with open(mission_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            now_iso = datetime.now().isoformat()
            data["thinking_logs"].append(f"[{now_iso}] {log_message}")
            data["updated_at"] = now_iso

            if new_status:
                data["status"] = new_status
            if progress_percent is not None:
                data["progress_percent"] = min(100.0, max(0.0, float(progress_percent)))

            with open(mission_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Sincronizar en Firestore
            self._sync_mission_to_firestore(data)
            return True
        except Exception as ex:
            logger.error(f"Error al registrar log de razonamiento en {mission_id}: {ex}")
            return False

    def update_node_progress(self, mission_id: str, node_id: str, node_status: str, progress: int = 100, node_artifacts: Optional[Dict[str, Any]] = None) -> bool:
        """Actualiza el progreso específico de uno de los 7 nodos de producción."""
        mission_dir = self.storage_dir / mission_id
        mission_json_path = mission_dir / "mission.json"

        if not mission_json_path.is_file():
            return False

        try:
            with open(mission_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if node_id in data.get("nodes_state", {}):
                data["nodes_state"][node_id]["status"] = node_status
                data["nodes_state"][node_id]["progress"] = progress

            if node_artifacts:
                for k, v in node_artifacts.items():
                    if k in data.get("artifacts", {}):
                        data["artifacts"][k] = v

            data["updated_at"] = datetime.now().isoformat()

            with open(mission_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self._sync_mission_to_firestore(data)
            return True
        except Exception as ex:
            logger.error(f"Error al actualizar nodo {node_id} en {mission_id}: {ex}")
            return False

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Recupera el estado completo de una misión desde local con fallback a Firestore."""
        mission_json_path = self.storage_dir / mission_id / "mission.json"
        if mission_json_path.is_file():
            try:
                with open(mission_json_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Fallback a Firestore
        return self._fetch_mission_from_firestore(mission_id)

    def list_all_missions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lista todas las misiones registradas ordenadas por fecha reciente."""
        missions = []
        if self.storage_dir.is_dir():
            for m_dir in self.storage_dir.iterdir():
                if m_dir.is_dir() and (m_dir / "mission.json").is_file():
                    try:
                        with open(m_dir / "mission.json", "r", encoding="utf-8") as f:
                            missions.append(json.load(f))
                    except Exception:
                        pass

        missions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return missions[:limit]

    def _sync_mission_to_firestore(self, mission_data: Dict[str, Any]) -> bool:
        """Persiste el documento de la misión en Firestore de manera no bloqueante en hilo secundario."""
        def _do_sync():
            try:
                project_id = self._get_project_id()
                mission_id = mission_data["mission_id"]
                url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_missions/{mission_id}"

                fields = {
                    "mission_id": {"stringValue": mission_id},
                    "title": {"stringValue": mission_data.get("title", "")},
                    "workflow_id": {"stringValue": mission_data.get("workflow_id", "")},
                    "status": {"stringValue": mission_data.get("status", HermesMissionStatus.PENDING)},
                    "progress_percent": {"doubleValue": float(mission_data.get("progress_percent", 0.0))},
                    "updated_at": {"stringValue": mission_data.get("updated_at", datetime.now().isoformat())},
                    "payload_json": {"stringValue": json.dumps(mission_data, ensure_ascii=False)}
                }
                headers = self._get_firestore_headers()
                requests.patch(url, headers=headers, json={"fields": fields}, timeout=4)
            except Exception:
                pass

        threading.Thread(target=_do_sync, daemon=True).start()
        return True

    def _fetch_mission_from_firestore(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el JSON completo de la misión desde Firestore si no está en local."""
        project_id = self._get_project_id()
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/videopro_missions/{mission_id}"
        try:
            headers = self._get_firestore_headers()
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                doc = resp.json()
                raw_json = doc.get("fields", {}).get("payload_json", {}).get("stringValue", "")
                if raw_json:
                    return json.loads(raw_json)
        except Exception:
            pass
        return None
