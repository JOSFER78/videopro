"""
Servicio de Almacenamiento Cloudflare R2 (S3 Compatible Zero Egress) — VideoPro Studio
Permite la subida eficiente de vídeos grandes (>300MB, >1GB) mediante transferencias multipart paralelas con Boto3.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import config

logger = logging.getLogger("videopro.r2_storage")

# Configuración de Transferencia Multipart de Alto Rendimiento
R2_TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=50 * 1024 * 1024,   # Archivos > 50 MB usan multipart
    max_concurrency=10,                      # 10 subidas paralelas concurrentes
    multipart_chunksize=16 * 1024 * 1024,    # Partes de 16 MB por fragmento
    use_threads=True
)


def get_r2_client() -> Optional[Any]:
    """Crea y retorna un cliente Boto3 configurado para Cloudflare R2."""
    endpoint = config.app.get("s3_endpoint", "").strip() or "https://9d248b8b5baed3559e743ef138d25b64.r2.cloudflarestorage.com"
    access_key = config.app.get("s3_access_key", "").strip()
    secret_key = config.app.get("s3_secret_key", "").strip()

    if not (access_key and secret_key):
        logger.warning("Cloudflare R2: Faltan credenciales (Access Key ID o Secret Access Key).")
        return None

    client_config = Config(
        signature_version="s3v4",
        connect_timeout=10,
        read_timeout=30,
        retries={"max_attempts": 3, "mode": "standard"}
    )

    return boto3.client(
        service_name="s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=client_config
    )


def upload_to_r2(local_file_path: str, remote_filename: Optional[str] = None, bucket: Optional[str] = None, prefix: str = "videpro/videos/") -> Dict[str, Any]:
    """
    Sube un archivo de vídeo o media a Cloudflare R2 con soporte multipart automático.
    
    :param local_file_path: Ruta al archivo local en disco.
    :param remote_filename: Nombre destino en el bucket (si no se indica, usa el nombre del archivo).
    :param bucket: Nombre del bucket R2 (por defecto lee de configuración o 'videpro').
    :param prefix: Prefijo de carpeta en el bucket (ej. 'videpro/videos/').
    :return: Diccionario con estado, URL pública o key y metadatos.
    """
    if not os.path.isfile(local_file_path):
        return {"success": False, "error": f"El archivo local no existe: {local_file_path}"}

    client = get_r2_client()
    if not client:
        return {
            "success": False,
            "error": "Credenciales de Cloudflare R2 no configuradas o incompletas en Ajustes (se requieren Access Key ID de 32 chars y Secret Access Key de 64 chars)."
        }

    raw_bucket = (bucket or config.app.get("s3_bucket", "videpro")).strip()
    # Si el usuario escribió 'videpro/videos/' en el campo bucket, separar el bucket del prefijo
    if "/" in raw_bucket:
        parts = raw_bucket.split("/", 1)
        target_bucket = parts[0]
        actual_prefix = parts[1].strip("/") + "/" if parts[1].strip("/") else prefix
    else:
        target_bucket = raw_bucket
        actual_prefix = prefix

    filename = remote_filename or os.path.basename(local_file_path)
    key = f"{actual_prefix.rstrip('/')}/{filename}".lstrip("/")

    size_bytes = os.path.getsize(local_file_path)
    size_mb = size_bytes / (1024 * 1024)

    logger.info(f"📤 Subiendo {local_file_path} ({size_mb:.1f} MB) → R2 Bucket: '{target_bucket}', Key: '{key}'")

    try:
        # Detectar content type
        content_type = "video/mp4" if filename.endswith(".mp4") else ("audio/wav" if filename.endswith(".wav") else "application/octet-stream")
        extra_args = {"ContentType": content_type}

        client.upload_file(
            Filename=local_file_path,
            Bucket=target_bucket,
            Key=key,
            Config=R2_TRANSFER_CONFIG,
            ExtraArgs=extra_args
        )

        cdn_url = config.app.get("s3_public_url", "").strip().rstrip("/")
        if cdn_url:
            public_url = f"{cdn_url}/{key}"
        else:
            public_url = f"https://{target_bucket}.r2.cloudflarestorage.com/{key}"

        logger.info(f"✅ Subida a R2 completada con éxito → {key}")
        return {
            "success": True,
            "bucket": target_bucket,
            "key": key,
            "size_mb": round(size_mb, 2),
            "public_url": public_url,
            "message": f"Archivo de {size_mb:.1f} MB subido con éxito a Cloudflare R2 ({target_bucket}/{key})."
        }
    except Exception as ex:
        err_msg = str(ex)
        logger.error(f"❌ Error al subir a Cloudflare R2: {err_msg}")
        return {
            "success": False,
            "error": err_msg,
            "bucket": target_bucket,
            "key": key
        }


def test_r2_upload_diagnostic() -> Dict[str, Any]:
    """Ejecuta una prueba completa de subida y diagnóstico de Cloudflare R2."""
    endpoint = config.app.get("s3_endpoint", "").strip() or "https://9d248b8b5baed3559e743ef138d25b64.r2.cloudflarestorage.com"
    access_key = config.app.get("s3_access_key", "").strip()
    secret_key = config.app.get("s3_secret_key", "").strip()
    bucket = config.app.get("s3_bucket", "videpro").strip()

    if "/" in bucket:
        bucket = bucket.split("/")[0]

    diagnostics = {
        "endpoint": endpoint,
        "bucket": bucket,
        "access_key_length": len(access_key),
        "access_key_preview": (access_key[:8] + "..." + access_key[-4:]) if len(access_key) > 12 else access_key,
        "has_secret_key": bool(secret_key),
        "secret_key_length": len(secret_key)
    }

    if not access_key:
        return {
            "success": False,
            "message": "Falta el 'Access Key ID' de Cloudflare R2 en Ajustes.",
            "diagnostics": diagnostics
        }

    if not secret_key:
        return {
            "success": False,
            "message": "Falta el 'Secret Access Key' de Cloudflare R2 en Ajustes (requerido para la API S3/Boto3).",
            "diagnostics": diagnostics,
            "hint": "Para obtener las credenciales S3 de R2: Ve a Cloudflare Dashboard > R2 > Manage R2 API Tokens > Create API Token (Permisos: Admin Read & Write). Cloudflare te entregará un 'Access Key ID' (32 caracteres) y un 'Secret Access Key' (64 caracteres)."
        }

    if len(access_key) != 32:
        return {
            "success": False,
            "message": f"El Access Key ID actual tiene {len(access_key)} caracteres (parece un Cloudflare User Token 'cfut_...'). La API S3 de R2 requiere un Access Key ID de 32 caracteres hexadecimales.",
            "diagnostics": diagnostics,
            "hint": "Crea un 'R2 API Token' en Cloudflare Dashboard > R2 > Manage R2 API Tokens con permisos de lectura y escritura sobre el bucket 'videpro'."
        }

    # Crear archivo temporal de prueba
    test_path = "/tmp/videopro_r2_diagnostic.txt"
    try:
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("VideoPro Studio Cloudflare R2 Diagnostic Test OK\n")

        res = upload_to_r2(test_path, remote_filename="videopro_r2_diagnostic.txt", bucket=bucket, prefix="videpro/videos/")
        if res.get("success"):
            return {
                "success": True,
                "message": f"✅ Conexión y subida a Cloudflare R2 verificadas con éxito en el bucket '{bucket}'.",
                "diagnostics": diagnostics,
                "details": res
            }
        else:
            return {
                "success": False,
                "message": f"Error al subir: {res.get('error')}",
                "diagnostics": diagnostics
            }
    except Exception as ex:
        return {
            "success": False,
            "message": f"Excepción durante la prueba: {ex}",
            "diagnostics": diagnostics
        }
