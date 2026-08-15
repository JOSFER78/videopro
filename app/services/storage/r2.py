import mimetypes
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

from app.services.storage.base import BaseStorageService

logger = logging.getLogger("videopro.storage.r2")

class CloudflareR2StorageService(BaseStorageService):
    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region_name: str = "auto",
        presigned_url_ttl: int = 900,
        storage_prefix: str = "videopro",
    ):
        self.bucket_name = bucket_name
        self.presigned_url_ttl = presigned_url_ttl
        self.storage_prefix = storage_prefix.strip("/")

        client_config = Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            s3={"addressing_style": "path"},
        )

        self._s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
            config=client_config,
        )

    def _normalize_key(self, remote_key: str) -> str:
        clean_key = remote_key.lstrip("/")
        if self.storage_prefix and not clean_key.startswith(self.storage_prefix):
            return f"{self.storage_prefix}/{clean_key}"
        return clean_key

    def upload_file(
        self,
        local_path: Path | str,
        remote_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        path_obj = Path(local_path)
        if not path_obj.exists() or not path_obj.is_file():
            raise FileNotFoundError(f"El archivo local no existe: {local_path}")

        key = self._normalize_key(remote_key)
        if not content_type:
            content_type, _ = mimetypes.guess_type(str(path_obj))
            content_type = content_type or "application/octet-stream"

        extra_args: Dict[str, Any] = {"ContentType": content_type}
        if metadata:
            extra_args["Metadata"] = metadata

        try:
            logger.info(f"Subiendo archivo a R2: {path_obj} -> s3://{self.bucket_name}/{key}")
            self._s3_client.upload_file(
                Filename=str(path_obj),
                Bucket=self.bucket_name,
                Key=key,
                ExtraArgs=extra_args,
            )
            return key
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Error subiendo a Cloudflare R2 ({key}): {err}")
            raise

    def upload_directory(
        self,
        local_dir: Path | str,
        remote_prefix: str,
    ) -> List[str]:
        dir_path = Path(local_dir)
        if not dir_path.exists() or not dir_path.is_dir():
            raise NotADirectoryError(f"Directorio local no encontrado: {local_dir}")

        uploaded_keys: List[str] = []
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(dir_path)
                target_key = f"{remote_prefix.rstrip('/')}/{rel_path.as_posix()}"
                key = self.upload_file(file_path, target_key)
                uploaded_keys.append(key)

        return uploaded_keys

    def get_presigned_url(
        self,
        remote_key: str,
        expiration_seconds: Optional[int] = None,
        http_method: str = "GET",
    ) -> str:
        key = self._normalize_key(remote_key)
        expires_in = expiration_seconds or self.presigned_url_ttl

        client_method = "get_object" if http_method.upper() == "GET" else "put_object"
        params = {"Bucket": self.bucket_name, "Key": key}

        try:
            url = self._s3_client.generate_presigned_url(
                ClientMethod=client_method,
                Params=params,
                ExpiresIn=expires_in,
            )
            return url
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Error generando Presigned URL para {key}: {err}")
            raise

    def download_file(self, remote_key: str, local_path: Path | str) -> Path:
        key = self._normalize_key(remote_key)
        dest_path = Path(local_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._s3_client.download_file(
                Bucket=self.bucket_name,
                Key=key,
                Filename=str(dest_path),
            )
            return dest_path
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Error descargando {key} de R2: {err}")
            raise

    def file_exists(self, remote_key: str) -> bool:
        key = self._normalize_key(remote_key)
        try:
            self._s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def delete_file(self, remote_key: str) -> bool:
        key = self._normalize_key(remote_key)
        try:
            self._s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            return True
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Error eliminando {key} de R2: {err}")
            return False
