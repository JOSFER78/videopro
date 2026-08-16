from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path

class BaseStorageService(ABC):
    @abstractmethod
    def upload_file(
        self,
        local_path: Path | str,
        remote_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        pass

    @abstractmethod
    def upload_directory(
        self,
        local_dir: Path | str,
        remote_prefix: str,
    ) -> List[str]:
        pass

    @abstractmethod
    def get_presigned_url(
        self,
        remote_key: str,
        expiration_seconds: int = 900,
        http_method: str = "GET",
    ) -> str:
        pass

    @abstractmethod
    def download_file(self, remote_key: str, local_path: Path | str) -> Path:
        pass

    @abstractmethod
    def file_exists(self, remote_key: str) -> bool:
        pass

    @abstractmethod
    def delete_file(self, remote_key: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        pass
