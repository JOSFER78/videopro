import logging
from typing import Optional
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

        storage_cfg = config_manager.get("storage.s3", {}) or config_manager.get("r2", {})

        is_enabled = storage_cfg.get("enabled", False)
        fallback_allowed = storage_cfg.get("fallback_to_local", True)

        if is_enabled:
            endpoint = storage_cfg.get("endpoint_url")
            key_id = storage_cfg.get("access_key_id")
            secret = storage_cfg.get("secret_access_key")
            bucket = storage_cfg.get("bucket_name")

            if all([endpoint, key_id, secret, bucket]):
                try:
                    logger.info("Inicializando Cloudflare R2 Storage Adapter...")
                    r2_service = CloudflareR2StorageService(
                        endpoint_url=endpoint,
                        access_key_id=key_id,
                        secret_access_key=secret,
                        bucket_name=bucket,
                        region_name=storage_cfg.get("region_name", "auto"),
                        presigned_url_ttl=storage_cfg.get("presigned_url_ttl", 900),
                        storage_prefix=storage_cfg.get("storage_prefix", "videopro"),
                    )
                    cls._instance = r2_service
                    return cls._instance
                except Exception as ex:
                    logger.error(f"Error al inicializar Cloudflare R2: {ex}")
                    if not fallback_allowed:
                        raise

        local_base = config_manager.get("storage.local_dir", "/home/ubuntu/MoneyPrinterTurbo/storage")
        cls._instance = LocalStorageService(base_dir=local_base)
        return cls._instance
