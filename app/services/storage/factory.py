import os
import logging
from typing import Optional
from app.config import config
from app.config.config_manager import config_manager
from app.services.storage.base import BaseStorageService
from app.services.storage.local import LocalStorageService
from app.services.storage.r2 import CloudflareR2StorageService

logger = logging.getLogger("videopro.storage.factory")

class StorageFactory:
    _instance: Optional[BaseStorageService] = None

    @classmethod
    def get_storage_service(cls, force_reload: bool = False) -> BaseStorageService:
        if cls._instance is not None and not force_reload:
            return cls._instance

        # Check storage configuration from config_manager or config.app
        endpoint = config_manager.get("storage.s3.endpoint_url") or config_manager.get("r2.endpoint_url") or config.app.get("s3_endpoint")
        key_id = config_manager.get("storage.s3.access_key_id") or config_manager.get("r2.access_key_id") or config.app.get("s3_access_key")
        secret = config_manager.get("storage.s3.secret_access_key") or config_manager.get("r2.secret_access_key") or config.app.get("s3_secret_key")
        bucket = config_manager.get("storage.s3.bucket_name") or config_manager.get("r2.bucket_name") or config.app.get("s3_bucket", "videopro-masters")

        is_enabled = bool(endpoint and key_id and secret and bucket)
        fallback_allowed = True

        if is_enabled:
            try:
                logger.info("Inicializando Cloudflare R2 Storage Adapter...")
                r2_service = CloudflareR2StorageService(
                    endpoint_url=endpoint,
                    access_key_id=key_id,
                    secret_access_key=secret,
                    bucket_name=bucket,
                    region_name="auto",
                    presigned_url_ttl=900,
                    storage_prefix="videopro",
                )
                cls._instance = r2_service
                return cls._instance
            except Exception as ex:
                logger.error(f"Error al inicializar Cloudflare R2: {ex}")
                if not fallback_allowed:
                    raise

        from app.utils import utils
        local_base = utils.storage_dir() if hasattr(utils, "storage_dir") else os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "storage")
        cls._instance = LocalStorageService(base_dir=local_base)
        return cls._instance
