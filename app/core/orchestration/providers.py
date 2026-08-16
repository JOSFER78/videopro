"""
Registro Central de Proveedores de Infraestructura (Providers) — VideoPro Studio
Define el "DÓNDE" corre un Engine concreto (Local, Serverless ZeroGPU, RunPod, Cloud).
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class InfraType(str, Enum):
    LOCAL_VPS = "local_vps"                    # CPU o GPU local en el VPS
    LOCAL_BRIDGE = "local_bridge"              # Bridge local de Antigravity (puerto 8742)
    LOCAL_HEADLESS = "local_headless"          # Navegador Chrome Playwright desatendido
    SERVERLESS_ZEROGPU = "serverless_zerogpu"  # Clúster de GPU gratis Hugging Face ZeroGPU
    SERVERLESS_RUNPOD = "serverless_runpod"    # RunPod Serverless ComfyUI / PyWorker
    CLOUD_S3 = "cloud_s3"                      # Cloudflare R2 / S3 Storage


class ProviderSpec(BaseModel):
    id: str
    name: str
    engine_id: str
    infra_type: InfraType
    endpoint: Optional[str] = None
    auth_token_field: Optional[str] = None
    cost_per_second: float = 0.0
    is_active: bool = True
    priority: int = 10
    health_status: str = "ONLINE"
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Catálogo Maestro de Proveedores por Motor
PROVIDERS_CATALOG: Dict[str, List[ProviderSpec]] = {
    "flux_video": [
        ProviderSpec(
            id="flux_zerogpu",
            name="Hugging Face ZeroGPU Pool ($0)",
            engine_id="flux_video",
            infra_type=InfraType.SERVERLESS_ZEROGPU,
            auth_token_field="hf_token",
            cost_per_second=0.0,
            priority=10,
            metadata={"token_rotation": True, "spaces": ["black-forest-labs/FLUX.1-schnell", "multimodalart/flux-lora-lab"]}
        ),
        ProviderSpec(
            id="flux_runpod",
            name="RunPod Serverless ComfyUI Worker ($0.0002/s)",
            engine_id="flux_video",
            infra_type=InfraType.SERVERLESS_RUNPOD,
            endpoint="https://api.runpod.ai/v2/flux3-worker/runsync",
            auth_token_field="runpod_api_key",
            cost_per_second=0.0002,
            priority=30,
            metadata={"gpu_type": "RTX 4090"}
        )
    ],
    "google_flow": [
        ProviderSpec(
            id="flow_playwright_local",
            name="Google Flow Playwright Automation (30.000 créditos/mes)",
            engine_id="google_flow",
            infra_type=InfraType.LOCAL_HEADLESS,
            endpoint="http://127.0.0.1:8742/v1",
            cost_per_second=0.0,
            priority=10,
            metadata={"session_storage": "flow.google.com"}
        )
    ],
    "nanobanana": [
        ProviderSpec(
            id="nanobanana_bridge",
            name="Antigravity Bridge Imagen 3 (Puerto 8742 $0)",
            engine_id="nanobanana",
            infra_type=InfraType.LOCAL_BRIDGE,
            endpoint="http://127.0.0.1:8742/v1",
            cost_per_second=0.0,
            priority=10
        )
    ],
    "ltx25": [
        ProviderSpec(
            id="ltx25_zerogpu",
            name="LTX-2.5 ZeroGPU Space ($0)",
            engine_id="ltx25",
            infra_type=InfraType.SERVERLESS_ZEROGPU,
            auth_token_field="hf_token",
            cost_per_second=0.0,
            priority=10
        )
    ],
    "stock_db": [
        ProviderSpec(
            id="stock_pexels_pixabay",
            name="Pexels & Pixabay Semantic Cloud API ($0)",
            engine_id="stock_db",
            infra_type=InfraType.LOCAL_VPS,
            auth_token_field="pexels_api_key",
            cost_per_second=0.0,
            priority=10
        )
    ],
    "vibevoice": [
        ProviderSpec(
            id="vibevoice_zerogpu",
            name="VibeVoice 1.5B ZeroGPU Space Pool ($0)",
            engine_id="vibevoice",
            infra_type=InfraType.SERVERLESS_ZEROGPU,
            auth_token_field="hf_token",
            cost_per_second=0.0,
            priority=10
        ),
        ProviderSpec(
            id="vibevoice_local_vps",
            name="VibeVoice 1.5B Local VPS Python Env",
            engine_id="vibevoice",
            infra_type=InfraType.LOCAL_VPS,
            endpoint="/home/ubuntu/vibevoice-venv/bin/python",
            cost_per_second=0.0,
            priority=20
        )
    ],
    "edge_tts": [
        ProviderSpec(
            id="edge_tts_cloud",
            name="Microsoft Edge-TTS Cloud Service ($0)",
            engine_id="edge_tts",
            infra_type=InfraType.LOCAL_VPS,
            cost_per_second=0.0,
            priority=10
        )
    ],
    "whisper": [
        ProviderSpec(
            id="whisper_local_cpu",
            name="Faster-Whisper CPU Local Host ($0)",
            engine_id="whisper",
            infra_type=InfraType.LOCAL_VPS,
            cost_per_second=0.0,
            priority=10
        )
    ],
    "flow_music": [
        ProviderSpec(
            id="flow_music_lyria",
            name="Google Flow Lyria 3 Headless ($0)",
            engine_id="flow_music",
            infra_type=InfraType.LOCAL_HEADLESS,
            cost_per_second=0.0,
            priority=10
        )
    ],
    "ffmpeg": [
        ProviderSpec(
            id="ffmpeg_local_host",
            name="FFmpeg 6.1.1 Local Subprocess Engine ($0)",
            engine_id="ffmpeg",
            infra_type=InfraType.LOCAL_VPS,
            endpoint="/usr/bin/ffmpeg",
            cost_per_second=0.0,
            priority=10
        )
    ],
    "comfyui": [
        ProviderSpec(
            id="comfyui_local",
            name="ComfyUI Local Instance (Puerto 8188)",
            engine_id="comfyui",
            infra_type=InfraType.LOCAL_VPS,
            endpoint="http://127.0.0.1:8188",
            cost_per_second=0.0,
            priority=10
        ),
        ProviderSpec(
            id="comfyui_runpod",
            name="ComfyUI RunPod Serverless GPU ($0.0003/s)",
            engine_id="comfyui",
            infra_type=InfraType.SERVERLESS_RUNPOD,
            endpoint="https://api.runpod.ai/v2/comfyui-worker/runsync",
            auth_token_field="runpod_api_key",
            cost_per_second=0.0003,
            priority=30
        )
    ],
    "hermes": [
        ProviderSpec(
            id="hermes_antigravity_bridge",
            name="Antigravity Bridge Gemini 3.7 Flash High (Puerto 8742 $0)",
            engine_id="hermes",
            infra_type=InfraType.LOCAL_BRIDGE,
            endpoint="http://127.0.0.1:8742/v1",
            cost_per_second=0.0,
            priority=10
        )
    ],
    "r2_storage": [
        ProviderSpec(
            id="cloudflare_r2_endpoint",
            name="Cloudflare R2 Object Storage Endpoint (Zero Egress)",
            engine_id="r2_storage",
            infra_type=InfraType.CLOUD_S3,
            endpoint="https://9d248b8b5baed3559e743ef138d25b64.r2.cloudflarestorage.com",
            auth_token_field="s3_secret_key",
            cost_per_second=0.0,
            priority=10
        )
    ]
}


def get_providers_for_engine(engine_id: str) -> List[ProviderSpec]:
    """Retorna los proveedores disponibles para un motor dado, ordenados por prioridad."""
    providers = PROVIDERS_CATALOG.get(engine_id, [])
    return sorted([p for p in providers if p.is_active], key=lambda x: x.priority)


def get_primary_provider(engine_id: str) -> Optional[ProviderSpec]:
    """Retorna el proveedor primario (más prioritario y activo) para un motor."""
    providers = get_providers_for_engine(engine_id)
    return providers[0] if providers else None
