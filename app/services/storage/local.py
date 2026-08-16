import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from app.services.storage.base import BaseStorageService

logger = logging.getLogger("videopro.storage.local")

class LocalStorageService(BaseStorageService):
    def __init__(self, base_dir: Optional[Path | str] = None):
        if not base_dir:
            from app.utils import utils
            base_dir = utils.storage_dir() if hasattr(utils, "storage_dir") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "storage")
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, remote_key: str) -> Path:
        return self.base_dir / remote_key.lstrip("/")

    def upload_file(
        self,
        local_path: Path | str,
        remote_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        src = Path(local_path).resolve()
        dest = self._resolve_path(remote_key)
        dest.parent.mkdir(parents=True, exist_ok=True)

        if src != dest:
            shutil.copy2(src, dest)
        return str(dest)

    def upload_directory(
        self,
        local_dir: Path | str,
        remote_prefix: str,
    ) -> List[str]:
        src_dir = Path(local_dir).resolve()
        dest_dir = self._resolve_path(remote_prefix)
        dest_dir.mkdir(parents=True, exist_ok=True)

        uploaded = []
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(src_dir)
                dest_file = dest_dir / rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest_file)
                uploaded.append(str(dest_file))
        return uploaded

    def get_presigned_url(
        self,
        remote_key: str,
        expiration_seconds: int = 900,
        http_method: str = "GET",
    ) -> str:
        dest = self._resolve_path(remote_key)
        return f"file://{dest.as_posix()}"

    def download_file(self, remote_key: str, local_path: Path | str) -> Path:
        src = self._resolve_path(remote_key)
        dest = Path(local_path).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src != dest:
            shutil.copy2(src, dest)
        return dest

    def file_exists(self, remote_key: str) -> bool:
        return self._resolve_path(remote_key).exists()

    def delete_file(self, remote_key: str) -> bool:
        path = self._resolve_path(remote_key)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        target_dir = self._resolve_path(prefix)
        if not target_dir.exists() or not target_dir.is_dir():
            return []
        
        results = []
        for f in target_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(self.base_dir).as_posix()
                results.append({
                    "key": rel,
                    "size": f.stat().st_size,
                    "last_modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                })
        return results

