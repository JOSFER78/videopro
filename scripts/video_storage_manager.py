#!/usr/bin/env python3
"""
video_storage_manager.py — Central Video Storage & Path Management Engine
========================================================================
Skill: videopro (Hermes Autonomous Video Engine)

Strict Path Convention:
    <STORAGE_ROOT>/<YYYY>/<MM>/<YYYY-MM-DD>_<slug>/v<version>/

Standard Subdirectories in every version:
    - raw_clips/      : Raw video footage, Google Flow Omni Flash clips, camera files
    - audio/          : Voiceover (TTS/Piper/VibeVoice), BGM, Foley SFX, Whisper transcripts
    - assets/         : Photos (Nano Banana Pro), Cutouts (rembg), Logos (SVG), Keyframes, Flow Images, Vox
    - renders/        : Intermediate scene renders, composition passes, preview files
    - exports/ (out/) : Final deliverable MP4 masters, Telegram (<50MB), YouTube, TikTok
    - manifests/      : Timeline definitions (scenes.json), research dossiers, QA logs, project_manifest.json
    - .tmp/           : Isolated project temp folder (screenshots, scratch files; zero global /tmp pollution)

Key Features:
    - Deterministic and collision-free project initialization
    - Robust slugification and timestamp normalization
    - Standard subfolder provisioning with backwards-compatible aliases (out <-> exports)
    - Full version lifecycle management (v1, v2, v3... with optional asset cloning)
    - Comprehensive manifest.json tracking with asset validation gate (>5KB rule)
    - Canonical path resolution for local pipeline, Videomastery API & Google Flow
    - Python API & CLI for seamless integration with all videopro scripts
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

ENV_STORAGE_ROOT_KEYS = [
    "VIDEOPRO_PROJECTS_DIR",
    "HERMES_VIDEO_PROJECTS_DIR",
    "VIDEO_STORAGE_ROOT",
    "VIDEOMASTERY_STORAGE_ROOT",
]

DEFAULT_SKILL_PROJECTS_ROOT = Path("/home/ubuntu/.hermes/skills/creative/videopro/projects")
FALLBACK_STORAGE_ROOT = Path("/home/ubuntu/video_projects")
MIN_ASSET_SIZE_BYTES = 5120  # 5 KB strict minimum gate rule for videopro assets

STANDARD_SUBDIRECTORIES = [
    "raw_clips",
    "audio",
    "assets",
    "renders",
    "exports",
    "manifests",
    "scene_data",
    "src",
    ".tmp",
]

ORGANIZATION_SUBDIRECTORIES = {
    "raw_clips": ["flow", "broll", "temp"],
    "audio": ["vo", "bgm", "sfx", "transcripts"],
    "assets": [
        "photos",
        "images",
        "cutouts",
        "broll",
        "logos",
        "keyframes",
        "flow_images",
        "flow_videos",
        "vox",
    ],
    "renders": ["scenes", "previews", "cache"],
    "exports": ["telegram", "youtube", "tiktok", "master"],
    "manifests": ["logs", "qa"],
    ".tmp": ["screenshots"],
}


def get_utc_iso_now() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def get_default_storage_root() -> Path:
    """Resolve storage root from environment variables or fallback to skill projects path."""
    for key in ENV_STORAGE_ROOT_KEYS:
        env_val = os.getenv(key)
        if env_val and env_val.strip():
            return Path(env_val.strip()).expanduser().resolve()

    if DEFAULT_SKILL_PROJECTS_ROOT.exists():
        return DEFAULT_SKILL_PROJECTS_ROOT.resolve()

    if FALLBACK_STORAGE_ROOT.parent.exists():
        return FALLBACK_STORAGE_ROOT.resolve()

    return (Path.home() / "video_projects").resolve()


def slugify(text: str) -> str:
    """Convert text into a clean, URL-safe, filesystem-safe lowercase slug."""
    text = unicodedata.normalize("NFKD", str(text))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-") or "video-project"


def normalize_version(version: Union[str, int]) -> str:
    """Normalize version into standard 'v<N>' format (e.g. 1 -> 'v1', 'v2' -> 'v2')."""
    if isinstance(version, int):
        if version < 1:
            raise ValueError(f"Version number must be >= 1, got {version}")
        return f"v{version}"

    version_str = str(version).strip().lower()
    match = re.match(r"^v?(\d+)$", version_str)
    if not match:
        raise ValueError(f"Invalid version format: '{version}'. Expected 'v1', 'v2', or integer.")

    num = int(match.group(1))
    if num < 1:
        raise ValueError(f"Version number must be >= 1, got {version}")
    return f"v{num}"


def parse_version_number(version: Union[str, int]) -> int:
    """Extract integer component from version tag (e.g. 'v3' -> 3)."""
    normalized = normalize_version(version)
    return int(normalized[1:])


def compute_file_sha256(file_path: Union[str, Path]) -> str:
    """Compute SHA-256 hash of a file."""
    p = Path(file_path)
    if not p.exists() or not p.is_file():
        return ""
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


# ==============================================================================
# METADATA & ASSET MODELS
# ==============================================================================


class AssetDict(dict):
    """
    Hybrid dictionary and Path-compatible object representing a registered asset.
    Supports dictionary indexing (`asset["sha256"]`), property access (`asset.path`),
    and string/fspath operations.
    """

    @property
    def path(self) -> Path:
        return Path(self["path"])

    @property
    def file_path(self) -> Path:
        return Path(self["path"])

    @property
    def size_bytes(self) -> int:
        return self.get("filesize_bytes", 0)

    @property
    def sha256(self) -> str:
        return self.get("sha256", "")

    def __str__(self) -> str:
        return self["path"]

    def __fspath__(self) -> str:
        return self["path"]

    def exists(self) -> bool:
        return Path(self["path"]).exists()


@dataclass
class AssetRecord:
    id: str
    name: str
    category: str
    path: str
    relative_path: str
    filesize_bytes: int
    sha256: str
    source_engine: str = "manual"
    verified: bool = True
    created_at: str = field(default_factory=get_utc_iso_now)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> AssetDict:
        return AssetDict(asdict(self))


# ==============================================================================
# CORE CLASS: VideoProject
# ==============================================================================


class VideoProject:
    """
    Represents a specific version of a video project under the strict hierarchy:
    <storage_root>/<YYYY>/<MM>/<YYYY-MM-DD>_<slug>/v<version>/
    """

    def __init__(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
        version: Union[str, int] = "v1",
        base_dir: Optional[Union[str, Path]] = None,
        title: Optional[str] = None,
        auto_init: bool = True,
    ):
        self.storage_root = (
            Path(base_dir).resolve() if base_dir else get_default_storage_root()
        )
        self.slug = slugify(slug)
        self.version = normalize_version(version)
        self.version_num = parse_version_number(self.version)

        # Parse date
        if date is None:
            self.date_obj = datetime.date.today()
        elif isinstance(date, (datetime.date, datetime.datetime)):
            self.date_obj = date if isinstance(date, datetime.date) else date.date()
        elif isinstance(date, str):
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date)
            if match:
                self.date_obj = datetime.date(
                    int(match.group(1)), int(match.group(2)), int(match.group(3))
                )
            else:
                self.date_obj = datetime.date.today()
        else:
            self.date_obj = datetime.date.today()

        self.year_str = f"{self.date_obj.year:04d}"
        self.month_str = f"{self.date_obj.month:02d}"
        self.date_str = self.date_obj.strftime("%Y-%m-%d")

        self.project_id = f"{self.date_str}_{self.slug}"
        self.title = (
            title
            if title
            else self.slug.replace("-", " ").replace("_", " ").title()
        )

        # Canonical project and version directories
        self.project_base_dir = (
            self.storage_root / self.year_str / self.month_str / self.project_id
        )
        self.version_dir = self.project_base_dir / self.version

        # Subdirectories
        self.raw_clips_dir = self.version_dir / "raw_clips"
        self.audio_dir = self.version_dir / "audio"
        self.assets_dir = self.version_dir / "assets"
        self.renders_dir = self.version_dir / "renders"
        self.exports_dir = self.version_dir / "exports"
        self.manifests_dir = self.version_dir / "manifests"
        self.scene_data_dir = self.version_dir / "scene_data"
        self.src_dir = self.version_dir / "src"
        self.temp_dir = self.version_dir / ".tmp"
        self.screenshots_dir = self.temp_dir / "screenshots"

        # Manifest files
        self.manifest_path = self.version_dir / "manifest.json"
        self.legacy_manifest_path = self.version_dir / "project_manifest.json"
        self.scenes_path = self.version_dir / "scenes.json"
        self.dossier_path = self.version_dir / "RESEARCH_DOSSIER.md"
        self.vo_durations_path = self.version_dir / "vo_durations.json"
        self.qa_report_path = self.version_dir / "out" / "qa_report.json"

        if auto_init:
            self.initialize()

    # --- Property Aliases for Complete Compatibility ---

    @property
    def project_dir(self) -> Path:
        return self.version_dir

    @property
    def root_dir(self) -> Path:
        return self.version_dir

    @property
    def out_dir(self) -> Path:
        return self.exports_dir

    @property
    def rendered_dir(self) -> Path:
        return self.renders_dir

    @property
    def photos_dir(self) -> Path:
        return self.assets_dir / "photos"

    @property
    def images_dir(self) -> Path:
        return self.assets_dir / "images"

    @property
    def cutouts_dir(self) -> Path:
        return self.assets_dir / "cutouts"

    @property
    def broll_dir(self) -> Path:
        return self.assets_dir / "broll"

    @property
    def keyframes_dir(self) -> Path:
        return self.assets_dir / "keyframes"

    @property
    def flow_images_dir(self) -> Path:
        return self.assets_dir / "flow_images"

    @property
    def flow_videos_dir(self) -> Path:
        return self.assets_dir / "flow_videos"

    @property
    def logos_dir(self) -> Path:
        return self.assets_dir / "logos"

    @property
    def vox_dir(self) -> Path:
        return self.assets_dir / "vox"

    @property
    def bgm_dir(self) -> Path:
        return self.audio_dir / "bgm"

    @property
    def sfx_dir(self) -> Path:
        return self.audio_dir / "sfx"

    @property
    def final_video_path(self) -> Path:
        return self.exports_dir / "final.mp4"

    # --------------------------------------------------------------------------
    # Initialization & Directory Creation
    # --------------------------------------------------------------------------

    def initialize(
        self,
        metadata: Optional[Dict[str, Any]] = None,
        create_aliases: bool = True,
    ) -> Path:
        """Creates complete directory structure and initializes manifest.json."""
        self.version_dir.mkdir(parents=True, exist_ok=True)

        for subdir_name in STANDARD_SUBDIRECTORIES:
            sub_path = self.version_dir / subdir_name
            sub_path.mkdir(parents=True, exist_ok=True)
            for child in ORGANIZATION_SUBDIRECTORIES.get(subdir_name, []):
                (sub_path / child).mkdir(parents=True, exist_ok=True)

        if create_aliases:
            self._create_compatibility_aliases()

        if not self.manifest_path.exists() and not self.legacy_manifest_path.exists():
            self._create_initial_manifest(metadata)
        else:
            self.sync_manifest()

        return self.version_dir

    def ensure_structure(self) -> None:
        """Ensure all canonical subdirectories exist."""
        self.initialize()

    def _create_compatibility_aliases(self) -> None:
        """Create symlinks or aliases for backwards compatibility with videopro standards."""
        out_path = self.version_dir / "out"
        if not out_path.exists():
            try:
                out_path.symlink_to(self.exports_dir.name, target_is_directory=True)
            except Exception:
                out_path.mkdir(parents=True, exist_ok=True)

        if not self.legacy_manifest_path.exists() and self.manifest_path.exists():
            try:
                self.legacy_manifest_path.symlink_to(self.manifest_path.name)
            except Exception:
                pass

    def _create_initial_manifest(
        self, custom_meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate and save the default canonical manifest."""
        now_iso = get_utc_iso_now()
        meta = custom_meta or {}

        manifest_data: Dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "project_id": self.project_id,
            "title": self.title,
            "slug": self.slug,
            "date": self.date_str,
            "version": self.version,
            "version_number": self.version_num,
            "created_at": now_iso,
            "updated_at": now_iso,
            "status": "initialized",
            "storage_root": str(self.storage_root),
            "canonical_relative_path": f"{self.year_str}/{self.month_str}/{self.project_id}/{self.version}",
            "metadata": {
                "topic": meta.get("topic", self.title),
                "style": meta.get("style", "vox_documentary"),
                "narrative_framework": meta.get("narrative_framework", "bbc_3_act"),
                "target_duration_seconds": meta.get("target_duration_seconds", 45),
                "actual_duration_seconds": meta.get("actual_duration_seconds", None),
                "resolution": meta.get(
                    "resolution",
                    {
                        "width": 1920,
                        "height": 1080,
                        "aspect_ratio": "16:9",
                        "fps": 24,
                    },
                ),
                "language": meta.get(
                    "language",
                    {
                        "locale": "es-ES",
                        "tts_voice": "es-ES-AlvaroNeural",
                        "rate_adjustment": "+0%",
                    },
                ),
            },
            "directory_structure": {
                "version_root": str(self.version_dir),
                "raw_clips": str(self.raw_clips_dir),
                "audio": str(self.audio_dir),
                "assets": str(self.assets_dir),
                "renders": str(self.renders_dir),
                "exports": str(self.exports_dir),
                "manifests": str(self.manifests_dir),
                "manifest_file": str(self.manifest_path),
                "scenes_plan": str(self.scenes_path),
                "research_dossier": str(self.dossier_path),
                "qa_report": str(self.qa_report_path),
            },
            "pipeline_lifecycle": {
                "phase_1_bootstrap": {"status": "completed", "timestamp": now_iso},
                "phase_2_research_and_dossier": {"status": "pending", "timestamp": None},
                "phase_3_storyboard_and_scenes": {"status": "pending", "timestamp": None},
                "phase_4_assets_acquisition": {"status": "pending", "timestamp": None},
                "phase_5_audio_and_sync": {"status": "pending", "timestamp": None},
                "phase_6_render_and_composition": {"status": "pending", "timestamp": None},
                "phase_7_qa_and_delivery": {"status": "pending", "timestamp": None},
            },
            "engine_specifications": {
                "video_engine": meta.get("video_engine", "gemini-omni-flash-preview"),
                "image_engine": meta.get("image_engine", "gemini-3.1-flash-image"),
                "audio_tts_engine": meta.get("audio_tts_engine", "edge-tts"),
                "stt_engine": meta.get("stt_engine", "whisper-stable-ts"),
                "render_backend": meta.get("render_backend", "moviepy2"),
                "video_encoder": {
                    "codec": "libx264",
                    "crf": 28,
                    "preset": "slow",
                    "audio_codec": "aac",
                    "audio_bitrate": "96k",
                },
            },
            "assets_manifest": [],
            "clips_registry": [],
            "audio_registry": [],
            "renders_registry": [],
            "exports_registry": [],
            "integrations": {
                "google_flow": {
                    "session_id": None,
                    "interaction_id": None,
                    "consistency_pins": {},
                    "scenes": [],
                },
                "videomastery": {
                    "job_id": None,
                    "status": "pending",
                    "endpoint_url": None,
                    "public_url": None,
                },
            },
            "qa_checks": {
                "min_asset_size_gate_passed": True,
                "no_blackdetect_pure_black": True,
                "audio_duration_sync_tolerance_ms": 100,
                "telegram_under_50mb_passed": False,
                "ffprobe_verified": False,
            },
            "custom_metadata": meta.get("custom_metadata", {}),
        }

        self.save_manifest(manifest_data)
        return manifest_data

    # --------------------------------------------------------------------------
    # Manifest Operations
    # --------------------------------------------------------------------------

    def load_manifest(self) -> Dict[str, Any]:
        """Load manifest.json or legacy project_manifest.json safely."""
        if not self.manifest_path.exists():
            if self.legacy_manifest_path.exists():
                with open(self.legacy_manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return self._create_initial_manifest()

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_manifest(self, data: Dict[str, Any]) -> Path:
        """Save manifest.json atomically and sync legacy project_manifest.json."""
        data["updated_at"] = get_utc_iso_now()
        temp_file = self.manifest_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.manifest_path)

        if self.legacy_manifest_path.exists() and not self.legacy_manifest_path.is_symlink():
            try:
                shutil.copy2(self.manifest_path, self.legacy_manifest_path)
            except Exception:
                pass

        return self.manifest_path

    def update_manifest(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields in manifest.json."""
        manifest = self.load_manifest()

        def _deep_update(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    _deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        _deep_update(manifest, updates)
        self.save_manifest(manifest)
        return manifest

    def sync_manifest(self) -> Dict[str, Any]:
        """Ensure paths and version info in manifest match current state."""
        manifest = self.load_manifest()
        manifest["version"] = self.version
        manifest["version_number"] = self.version_num
        manifest["project_id"] = self.project_id
        manifest["directory_structure"] = {
            "version_root": str(self.version_dir),
            "raw_clips": str(self.raw_clips_dir),
            "audio": str(self.audio_dir),
            "assets": str(self.assets_dir),
            "renders": str(self.renders_dir),
            "exports": str(self.exports_dir),
            "manifests": str(self.manifests_dir),
            "manifest_file": str(self.manifest_path),
            "scenes_plan": str(self.scenes_path),
            "research_dossier": str(self.dossier_path),
            "qa_report": str(self.qa_report_path),
        }
        self.save_manifest(manifest)
        return manifest

    def update_phase(self, phase_name: str, status: str, **kwargs) -> Dict[str, Any]:
        """Update status and timestamps for a specific pipeline lifecycle phase."""
        manifest = self.load_manifest()
        lifecycle = manifest.setdefault("pipeline_lifecycle", {})
        phase = lifecycle.setdefault(phase_name, {})
        phase["status"] = status
        phase["timestamp"] = get_utc_iso_now()
        for k, v in kwargs.items():
            phase[k] = v
        self.save_manifest(manifest)
        return manifest

    # --------------------------------------------------------------------------
    # Asset Registration & Gate Validation (>5KB rule)
    # --------------------------------------------------------------------------

    def register_asset(
        self,
        name_or_path: Union[str, Path] = None,
        asset_type: str = "photos",
        source_path: Optional[Union[str, Path]] = None,
        content: Optional[bytes] = None,
        source_engine: str = "nanobanana",
        min_size_bytes: int = MIN_ASSET_SIZE_BYTES,
        metadata: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        verify_size_gate: bool = True,
        overwrite: bool = True,
        name: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> AssetDict:
        """
        Unified register_asset returning an AssetDict (supports record["field"], record.path, etc.).
        Validates the strict >5KB rule and records checksum in project manifest.
        """
        cat = category or asset_type or "photos"
        meta = metadata or extra or {}

        if file_path is not None:
            src_p = Path(file_path).resolve()
            dst_p = src_p
            asset_name = name or src_p.name
        elif source_path is not None:
            src_p = Path(source_path).resolve()
            asset_name = name or (str(name_or_path) if name_or_path else src_p.name)
            dst_p = self.get_asset_path(cat, asset_name)
            if src_p != dst_p and src_p.exists():
                shutil.copy2(src_p, dst_p)
        elif content is not None:
            asset_name = name or (str(name_or_path) if name_or_path else "asset_data.bin")
            dst_p = self.get_asset_path(cat, asset_name)
            if overwrite or not dst_p.exists():
                dst_p.write_bytes(content)
        elif name_or_path is not None:
            p_cand = Path(name_or_path)
            if p_cand.exists() and p_cand.is_file():
                src_p = p_cand.resolve()
                dst_p = src_p
                asset_name = name or src_p.name
            else:
                asset_name = str(name_or_path)
                dst_p = self.get_asset_path(cat, asset_name)
        else:
            raise ValueError("Must provide file_path, source_path, content, or name_or_path")

        if not dst_p.exists():
            raise FileNotFoundError(f"Asset file does not exist at destination: {dst_p}")

        size_bytes = dst_p.stat().st_size
        if (verify_size_gate or min_size_bytes > 0) and size_bytes < min_size_bytes:
            raise ValueError(
                f"Asset {dst_p.name} rejected by 5KB gate rule! Size: {size_bytes} bytes < {min_size_bytes} bytes."
            )

        sha256_hash = compute_file_sha256(dst_p)
        asset_id = (
            f"asset_{slugify(cat)}_{slugify(dst_p.stem)}_{sha256_hash[:8]}"
            if sha256_hash
            else f"asset_{slugify(dst_p.name)}"
        )

        try:
            rel_path = str(dst_p.relative_to(self.version_dir))
        except ValueError:
            rel_path = str(dst_p)

        record = AssetRecord(
            id=asset_id,
            name=asset_name,
            category=cat,
            path=str(dst_p),
            relative_path=rel_path,
            filesize_bytes=size_bytes,
            sha256=sha256_hash,
            source_engine=source_engine,
            verified=True,
            extra=meta,
        )

        manifest = self.load_manifest()
        assets_list = manifest.setdefault("assets_manifest", [])
        assets_list = [
            a for a in assets_list
            if a.get("id") != asset_id and a.get("path") != str(dst_p) and a.get("name") != asset_name
        ]
        assets_list.append(record.to_dict())
        manifest["assets_manifest"] = assets_list
        self.save_manifest(manifest)

        return record.to_dict()

    def register_clip(
        self,
        file_path: Union[str, Path],
        prompt: Optional[str] = None,
        node_id: Optional[int] = None,
        duration_s: Optional[float] = None,
        engine: str = "gemini-omni-flash-preview",
        extra: Optional[Dict[str, Any]] = None,
    ) -> AssetDict:
        """Registers a raw video clip generated by Omni Flash or Google Flow."""
        p = Path(file_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Clip file not found: {p}")

        size_bytes = p.stat().st_size
        sha256_hash = compute_file_sha256(p)
        clip_id = (
            f"clip_node_{node_id}" if node_id is not None else f"clip_{slugify(p.stem)}"
        )

        try:
            rel_path = str(p.relative_to(self.version_dir))
        except ValueError:
            rel_path = str(p)

        clip_data = AssetDict({
            "id": clip_id,
            "filename": p.name,
            "path": str(p),
            "relative_path": rel_path,
            "node_id": node_id,
            "duration_s": duration_s,
            "engine": engine,
            "prompt": prompt,
            "filesize_bytes": size_bytes,
            "sha256": sha256_hash,
            "created_at": get_utc_iso_now(),
            "verified": True,
            "extra": extra or {},
        })

        manifest = self.load_manifest()
        clips = manifest.setdefault("clips_registry", [])
        clips = [
            c for c in clips
            if c.get("id") != clip_id and c.get("path") != str(p)
        ]
        clips.append(clip_data)
        manifest["clips_registry"] = clips
        self.save_manifest(manifest)
        return clip_data

    def register_export(
        self,
        file_path: Union[str, Path],
        export_type: str = "master",
        platform: Optional[str] = None,
        crf: int = 28,
        extra: Optional[Dict[str, Any]] = None,
    ) -> AssetDict:
        """Registers a final rendered/exported master MP4."""
        p = Path(file_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Export file not found: {p}")

        size_bytes = p.stat().st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)
        telegram_ready = size_mb < 50.0

        try:
            rel_path = str(p.relative_to(self.version_dir))
        except ValueError:
            rel_path = str(p)

        export_data = AssetDict({
            "id": f"export_{export_type}_{slugify(platform or 'general')}_{p.stem}",
            "filename": p.name,
            "path": str(p),
            "relative_path": rel_path,
            "export_type": export_type,
            "platform": platform,
            "crf": crf,
            "filesize_bytes": size_bytes,
            "filesize_mb": size_mb,
            "telegram_under_50mb": telegram_ready,
            "sha256": compute_file_sha256(p),
            "created_at": get_utc_iso_now(),
            "verified": True,
            "extra": extra or {},
        })

        manifest = self.load_manifest()
        exports = manifest.setdefault("exports_registry", [])
        exports = [e for e in exports if e.get("path") != str(p)]
        exports.append(export_data)
        manifest["exports_registry"] = exports

        if export_type == "master" or telegram_ready:
            manifest.setdefault("qa_checks", {})["telegram_under_50mb_passed"] = telegram_ready

        self.save_manifest(manifest)
        return export_data

    # --------------------------------------------------------------------------
    # Path Resolvers & Helpers
    # --------------------------------------------------------------------------

    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        """Returns canonical destination path for an asset by type."""
        cat_clean = asset_type.lower().strip()
        type_dir_map = {
            "photo": self.photos_dir,
            "photos": self.photos_dir,
            "image": self.images_dir,
            "images": self.images_dir,
            "cutout": self.cutouts_dir,
            "cutouts": self.cutouts_dir,
            "broll": self.broll_dir,
            "video": self.broll_dir,
            "videos": self.broll_dir,
            "keyframe": self.keyframes_dir,
            "keyframes": self.keyframes_dir,
            "flow_image": self.flow_images_dir,
            "flow_images": self.flow_images_dir,
            "flow_video": self.flow_videos_dir,
            "flow_videos": self.flow_videos_dir,
            "logo": self.logos_dir,
            "logos": self.logos_dir,
            "vector": self.logos_dir,
            "vox": self.vox_dir,
            "overlay": self.vox_dir,
            "overlays": self.vox_dir,
            "audio": self.audio_dir,
            "narration": self.audio_dir,
            "vo": self.audio_dir,
            "bgm": self.bgm_dir,
            "sfx": self.sfx_dir,
        }
        target_dir = type_dir_map.get(cat_clean, self.assets_dir / cat_clean)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / filename

    def get_output_path(self, filename: str = "final.mp4") -> Path:
        """Returns canonical path in exports/ (out/)."""
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        return self.exports_dir / filename

    def get_rendered_path(self, filename: str) -> Path:
        """Returns path in renders/."""
        self.renders_dir.mkdir(parents=True, exist_ok=True)
        return self.renders_dir / filename

    def get_temp_path(self, filename: str) -> Path:
        """Returns path inside isolated project .tmp/."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        return self.temp_dir / filename

    def get_screenshot_path(self, name: str = "screenshot.png") -> Path:
        """Returns path inside project .tmp/screenshots/."""
        if not name.endswith(".png") and not name.endswith(".jpg"):
            name += ".png"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        return self.screenshots_dir / name

    def resolve_path(
        self,
        category: str,
        filename: Optional[str] = None,
        subcategory: Optional[str] = None,
    ) -> Path:
        """Resolves canonical path within this project version."""
        cat = category.lower().strip()
        if cat in ("root", "version_root"):
            base = self.version_dir
        elif cat == "raw_clips":
            base = self.raw_clips_dir
        elif cat == "audio":
            base = self.audio_dir
        elif cat == "assets":
            base = self.assets_dir
        elif cat == "renders":
            base = self.renders_dir
        elif cat in ("exports", "out"):
            base = self.exports_dir
        elif cat == "manifests":
            base = self.manifests_dir
        else:
            base = self.version_dir / cat

        if subcategory:
            base = base / subcategory

        if filename:
            return base / filename
        return base

    def resolve_asset_path(self, filename: str, subcategory: str = "photos") -> Path:
        return self.assets_dir / subcategory / filename

    def resolve_clip_path(self, filename: str, subcategory: str = "flow") -> Path:
        return self.raw_clips_dir / subcategory / filename

    def resolve_audio_path(self, filename: str, subcategory: str = "vo") -> Path:
        return self.audio_dir / subcategory / filename

    def resolve_render_path(self, filename: str, subcategory: str = "scenes") -> Path:
        return self.renders_dir / subcategory / filename

    def resolve_export_path(self, filename: str = "final.mp4", subcategory: str = "master") -> Path:
        return self.exports_dir / subcategory / filename

    def resolve_manifest_path(self, filename: str = "manifest.json") -> Path:
        if filename in ("manifest.json", "project_manifest.json"):
            return self.manifest_path
        return self.manifests_dir / filename

    def get_flow_paths(self) -> Dict[str, Any]:
        """Returns structured paths and template pins for Google Flow integration."""
        keyframes_dir = self.assets_dir / "keyframes"
        keyframes_dir.mkdir(parents=True, exist_ok=True)
        pins = {
            "<FIRST_FRAME>": str(keyframes_dir / "keyframe_0_first_frame.png"),
        }
        for i in range(6):
            pins[f"<IMAGE_REF_{i}>"] = str(keyframes_dir / f"keyframe_{i+1}_ref.png")

        return {
            "keyframes_dir": str(keyframes_dir),
            "flow_clips_dir": str(self.raw_clips_dir / "flow"),
            "consistency_pins": pins,
            "manifest_path": str(self.manifest_path),
        }

    def get_videomastery_integration_info(
        self, api_base_url: str = "http://127.0.0.1:9130"
    ) -> Dict[str, Any]:
        rel_path = f"{self.year_str}/{self.month_str}/{self.project_id}/{self.version}"
        return {
            "project_id": self.project_id,
            "version": self.version,
            "title": self.title,
            "local_path": str(self.version_dir),
            "relative_path": rel_path,
            "api_endpoints": {
                "create_project": f"{api_base_url}/api/project/create",
                "autocomplete": f"{api_base_url}/api/autocomplete",
                "render": f"{api_base_url}/api/render",
                "status": f"{api_base_url}/api/status/{self.project_id}",
            },
            "static_proxy_path": f"/pro/videomastery-api/projects/{rel_path}/",
            "final_master_export": str(self.resolve_export_path("final.mp4", "master")),
        }

    def cleanup_temp(self) -> None:
        """Safely cleans project .tmp directory without touching global storage."""
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                try:
                    if item.is_file() or item.is_symlink():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"[WARN] Error eliminando temporal {item}: {e}", file=sys.stderr)

    def validate_all_assets(self, min_size_bytes: int = MIN_ASSET_SIZE_BYTES) -> Tuple[bool, List[str]]:
        """Scans all assets under assets/ and returns (passed, list_of_errors)."""
        errors = []
        if not self.assets_dir.exists():
            return False, ["Directorio assets/ no existe"]

        for root, _, files in os.walk(self.assets_dir):
            for fname in files:
                if fname.startswith(".") or fname.endswith(".prompt") or fname.endswith(".subject"):
                    continue
                fpath = Path(root) / fname
                size = fpath.stat().st_size
                if size < min_size_bytes:
                    errors.append(f"{fpath.relative_to(self.version_dir)} ({size} B < {min_size_bytes} B)")

        return len(errors) == 0, errors

    def verify_integrity(self) -> Dict[str, Any]:
        """Validates project structure, manifest validity, and assets >5KB rule."""
        issues = []
        for folder in STANDARD_SUBDIRECTORIES:
            fpath = self.version_dir / folder
            if not fpath.exists() or not fpath.is_dir():
                issues.append(f"Missing standard subdirectory: {folder}")

        if not self.manifest_path.exists() and not self.legacy_manifest_path.exists():
            issues.append("Missing manifest.json")

        manifest = self.load_manifest()
        assets = manifest.get("assets_manifest", [])
        verified_assets = 0
        total_asset_bytes = 0

        for asset in assets:
            apath = Path(asset.get("path", ""))
            if not apath.is_absolute():
                apath = self.version_dir / apath
            if not apath.exists():
                issues.append(f"Asset file missing on disk: {apath}")
                continue
            size = apath.stat().st_size
            total_asset_bytes += size
            if size < MIN_ASSET_SIZE_BYTES:
                issues.append(
                    f"Asset below 5KB minimum gate: {apath.name} ({size} bytes)"
                )
            else:
                expected_sha = asset.get("sha256")
                if expected_sha:
                    actual_sha = compute_file_sha256(apath)
                    if actual_sha != expected_sha:
                        issues.append(
                            f"Asset checksum mismatch for {apath.name}: expected {expected_sha[:8]}, got {actual_sha[:8]}"
                        )
                        continue
                verified_assets += 1

        is_valid = len(issues) == 0
        return {
            "valid": is_valid,
            "project_id": self.project_id,
            "version": self.version,
            "version_dir": str(self.version_dir),
            "asset_count": len(assets),
            "verified_assets": verified_assets,
            "total_asset_bytes": total_asset_bytes,
            "issues": issues,
        }


# ==============================================================================
# MANAGER CLASS: VideoStorageManager
# ==============================================================================


class VideoStorageManager:
    """
    Top-level controller for managing all video projects across the storage root.
    Also acts as a wrapper around an active VideoProject when initialized with project_ref.
    """

    def __init__(
        self,
        storage_root: Optional[Union[str, Path]] = None,
        project_ref: Optional[Union[str, Path]] = None,
        base_dir: Optional[Union[str, Path]] = None,
        title: Optional[str] = None,
        version: str = "v1",
        auto_create: bool = True,
    ):
        root = base_dir or storage_root
        self.storage_root = (
            Path(root).resolve() if root else get_default_storage_root()
        )
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self._active_project: Optional[VideoProject] = None

        if project_ref is not None or title is not None:
            self._active_project = self._resolve_project(
                project_ref=project_ref, title=title, version=version, auto_create=auto_create
            )

    def _resolve_project(
        self,
        project_ref: Optional[Union[str, Path]],
        title: Optional[str],
        version: str,
        auto_create: bool,
    ) -> VideoProject:
        if project_ref:
            p = Path(project_ref).resolve()
            if p.is_file() or p.is_dir():
                curr = p if p.is_dir() else p.parent
                while curr != curr.parent:
                    if re.match(r"^v\d+$", curr.name):
                        slug_match = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+)$", curr.parent.name)
                        date_val = slug_match.group(1) if slug_match else None
                        slug_val = slug_match.group(2) if slug_match else curr.parent.name
                        return VideoProject(
                            slug=slug_val,
                            date=date_val,
                            version=curr.name,
                            base_dir=curr.parent.parent.parent.parent,
                            auto_init=auto_create,
                        )
                    if (curr / "manifest.json").exists() or (curr / "project_manifest.json").exists():
                        slug_match = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+)$", curr.parent.name)
                        date_val = slug_match.group(1) if slug_match else None
                        slug_val = slug_match.group(2) if slug_match else curr.name
                        return VideoProject(
                            slug=slug_val,
                            date=date_val,
                            version=curr.name if re.match(r"^v\d+$", curr.name) else "v1",
                            base_dir=self.storage_root,
                            auto_init=auto_create,
                        )
                    curr = curr.parent

            ref_str = str(project_ref)
            slug = slugify(ref_str)
            found = self.find_project_dir(slug)
            if found:
                date_val, slug_val = found
                return VideoProject(
                    slug=slug_val, date=date_val, version=version, base_dir=self.storage_root, auto_init=auto_create
                )
            return VideoProject(
                slug=slug, version=version, base_dir=self.storage_root, title=title or ref_str, auto_init=auto_create
            )

        if title:
            slug = slugify(title)
            return VideoProject(
                slug=slug, version=version, base_dir=self.storage_root, title=title, auto_init=auto_create
            )

        latest = self.get_latest_project()
        if latest:
            return latest

        return VideoProject(
            slug="video-project", version=version, base_dir=self.storage_root, auto_init=auto_create
        )

    # --------------------------------------------------------------------------
    # Delegation to Active Project
    # --------------------------------------------------------------------------

    def _get_active(self) -> VideoProject:
        if self._active_project is None:
            self._active_project = self.get_latest_project() or VideoProject(
                slug="video-project", base_dir=self.storage_root, auto_init=True
            )
        return self._active_project

    @property
    def project_id(self) -> str:
        return self._get_active().project_id

    @property
    def version(self) -> str:
        return self._get_active().version

    @property
    def version_num(self) -> int:
        return self._get_active().version_num

    @property
    def slug(self) -> str:
        return self._get_active().slug

    @property
    def title(self) -> str:
        return self._get_active().title

    @property
    def date_str(self) -> str:
        return self._get_active().date_str

    @property
    def project_dir(self) -> Path:
        return self._get_active().project_dir

    @property
    def version_dir(self) -> Path:
        return self._get_active().version_dir

    @property
    def root_dir(self) -> Path:
        return self._get_active().root_dir

    @property
    def raw_clips_dir(self) -> Path:
        return self._get_active().raw_clips_dir

    @property
    def assets_dir(self) -> Path:
        return self._get_active().assets_dir

    @property
    def photos_dir(self) -> Path:
        return self._get_active().photos_dir

    @property
    def images_dir(self) -> Path:
        return self._get_active().images_dir

    @property
    def cutouts_dir(self) -> Path:
        return self._get_active().cutouts_dir

    @property
    def broll_dir(self) -> Path:
        return self._get_active().broll_dir

    @property
    def keyframes_dir(self) -> Path:
        return self._get_active().keyframes_dir

    @property
    def flow_images_dir(self) -> Path:
        return self._get_active().flow_images_dir

    @property
    def flow_videos_dir(self) -> Path:
        return self._get_active().flow_videos_dir

    @property
    def logos_dir(self) -> Path:
        return self._get_active().logos_dir

    @property
    def vox_dir(self) -> Path:
        return self._get_active().vox_dir

    @property
    def audio_dir(self) -> Path:
        return self._get_active().audio_dir

    @property
    def bgm_dir(self) -> Path:
        return self._get_active().bgm_dir

    @property
    def sfx_dir(self) -> Path:
        return self._get_active().sfx_dir

    @property
    def scene_data_dir(self) -> Path:
        return self._get_active().scene_data_dir

    @property
    def src_dir(self) -> Path:
        return self._get_active().src_dir

    @property
    def out_dir(self) -> Path:
        return self._get_active().out_dir

    @property
    def exports_dir(self) -> Path:
        return self._get_active().exports_dir

    @property
    def renders_dir(self) -> Path:
        return self._get_active().renders_dir

    @property
    def rendered_dir(self) -> Path:
        return self._get_active().rendered_dir

    @property
    def manifests_dir(self) -> Path:
        return self._get_active().manifests_dir

    @property
    def temp_dir(self) -> Path:
        return self._get_active().temp_dir

    @property
    def screenshots_dir(self) -> Path:
        return self._get_active().screenshots_dir

    @property
    def manifest_path(self) -> Path:
        return self._get_active().manifest_path

    @property
    def legacy_manifest_path(self) -> Path:
        return self._get_active().legacy_manifest_path

    @property
    def scenes_path(self) -> Path:
        return self._get_active().scenes_path

    @property
    def dossier_path(self) -> Path:
        return self._get_active().dossier_path

    @property
    def vo_durations_path(self) -> Path:
        return self._get_active().vo_durations_path

    @property
    def final_video_path(self) -> Path:
        return self._get_active().final_video_path

    @property
    def qa_report_path(self) -> Path:
        return self._get_active().qa_report_path

    def ensure_structure(self) -> None:
        self._get_active().ensure_structure()

    def get_asset_path(self, asset_type: str, filename: str) -> Path:
        return self._get_active().get_asset_path(asset_type, filename)

    def get_output_path(self, filename: str = "final.mp4") -> Path:
        return self._get_active().get_output_path(filename)

    def get_rendered_path(self, filename: str) -> Path:
        return self._get_active().get_rendered_path(filename)

    def get_temp_path(self, filename: str) -> Path:
        return self._get_active().get_temp_path(filename)

    def get_screenshot_path(self, name: str = "screenshot.png") -> Path:
        return self._get_active().get_screenshot_path(name)

    def register_asset(self, *args, **kwargs) -> AssetDict:
        return self._get_active().register_asset(*args, **kwargs)

    def register_clip(self, *args, **kwargs) -> AssetDict:
        return self._get_active().register_clip(*args, **kwargs)

    def register_export(self, *args, **kwargs) -> AssetDict:
        return self._get_active().register_export(*args, **kwargs)

    def validate_all_assets(self, min_size_bytes: int = MIN_ASSET_SIZE_BYTES) -> Tuple[bool, List[str]]:
        return self._get_active().validate_all_assets(min_size_bytes)

    def verify_integrity(self) -> Dict[str, Any]:
        return self._get_active().verify_integrity()

    def load_manifest(self) -> Dict[str, Any]:
        return self._get_active().load_manifest()

    def save_manifest(self, data: Dict[str, Any]) -> Path:
        return self._get_active().save_manifest(data)

    def update_phase(self, phase_name: str, status: str, **kwargs) -> Dict[str, Any]:
        return self._get_active().update_phase(phase_name, status, **kwargs)

    def cleanup_temp(self) -> None:
        self._get_active().cleanup_temp()

    # --------------------------------------------------------------------------
    # Multi-Project Root Operations
    # --------------------------------------------------------------------------

    def init_project(
        self,
        title: str,
        slug: Optional[str] = None,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
        version: Union[str, int] = "v1",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VideoProject:
        """Initializes a new video project under strict convention."""
        project_slug = slugify(slug or title)
        project = VideoProject(
            slug=project_slug,
            date=date,
            version=version,
            base_dir=self.storage_root,
            title=title,
        )
        project.initialize(metadata=metadata)
        self._active_project = project
        return project

    create_project = init_project

    def get_project(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
        version: Optional[Union[str, int]] = None,
    ) -> VideoProject:
        """Retrieves a VideoProject instance."""
        clean_slug = slugify(slug)
        if date is None:
            located = self.find_project_dir(clean_slug)
            if located:
                parsed_date, parsed_slug = located
                clean_slug = parsed_slug
                date = parsed_date

        if version is None:
            version = self.get_latest_version(clean_slug, date=date)

        project = VideoProject(
            slug=clean_slug,
            date=date,
            version=version,
            base_dir=self.storage_root,
        )
        self._active_project = project
        return project

    def find_project_dir(self, slug: str) -> Optional[Tuple[datetime.date, str]]:
        """Searches storage root for a project directory matching the slug."""
        clean_slug = slugify(slug)
        for year_dir in sorted(self.storage_root.glob("????"), reverse=True):
            if not year_dir.is_dir():
                continue
            for month_dir in sorted(year_dir.glob("??"), reverse=True):
                if not month_dir.is_dir():
                    continue
                for proj_dir in month_dir.glob(f"*_{clean_slug}"):
                    if proj_dir.is_dir():
                        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_(.+)$", proj_dir.name)
                        if match:
                            y, m, d, s = match.groups()
                            return (
                                datetime.date(int(y), int(m), int(d)),
                                clean_slug,
                            )
                for proj_dir in month_dir.glob(f"*{clean_slug}*"):
                    if proj_dir.is_dir():
                        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})_(.+)$", proj_dir.name)
                        if match:
                            y, m, d, s = match.groups()
                            return (
                                datetime.date(int(y), int(m), int(d)),
                                s,
                            )
        return None

    def list_versions(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    ) -> List[str]:
        clean_slug = slugify(slug)
        date_obj = self._resolve_date(clean_slug, date)
        year_str = f"{date_obj.year:04d}"
        month_str = f"{date_obj.month:02d}"
        proj_id = f"{date_obj.strftime('%Y-%m-%d')}_{clean_slug}"
        proj_base = self.storage_root / year_str / month_str / proj_id

        if not proj_base.exists() or not proj_base.is_dir():
            return []

        versions = []
        for item in proj_base.iterdir():
            if item.is_dir() and re.match(r"^v\d+$", item.name):
                versions.append(item.name)

        return sorted(versions, key=lambda v: int(v[1:]))

    def get_latest_version(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    ) -> str:
        versions = self.list_versions(slug, date)
        return versions[-1] if versions else "v1"

    def get_next_version(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    ) -> str:
        versions = self.list_versions(slug, date)
        if not versions:
            return "v1"
        highest_num = max(int(v[1:]) for v in versions)
        return f"v{highest_num + 1}"

    def create_new_version(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
        base_version: Optional[Union[str, int]] = None,
        copy_assets: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VideoProject:
        clean_slug = slugify(slug)
        date_obj = self._resolve_date(clean_slug, date)
        next_ver = self.get_next_version(clean_slug, date=date_obj)

        new_project = VideoProject(
            slug=clean_slug,
            date=date_obj,
            version=next_ver,
            base_dir=self.storage_root,
        )
        new_project.initialize(metadata=metadata)

        if base_version:
            base_ver_str = normalize_version(base_version)
            old_project = VideoProject(
                slug=clean_slug,
                date=date_obj,
                version=base_ver_str,
                base_dir=self.storage_root,
            )
            if old_project.version_dir.exists():
                old_manifest = old_project.load_manifest()
                new_manifest = new_project.load_manifest()
                new_manifest["parent_version"] = base_ver_str
                new_manifest["metadata"] = old_manifest.get(
                    "metadata", new_manifest["metadata"]
                )
                new_manifest["engine_specifications"] = old_manifest.get(
                    "engine_specifications", new_manifest["engine_specifications"]
                )

                if copy_assets and old_project.assets_dir.exists():
                    shutil.copytree(
                        old_project.assets_dir,
                        new_project.assets_dir,
                        dirs_exist_ok=True,
                    )
                    new_manifest["assets_manifest"] = old_manifest.get(
                        "assets_manifest", []
                    )

                new_project.save_manifest(new_manifest)

        self._active_project = new_project
        return new_project

    def list_all_projects(
        self,
        year: Optional[Union[int, str]] = None,
        month: Optional[Union[int, str]] = None,
    ) -> List[Dict[str, Any]]:
        results = []
        year_pattern = f"{int(year):04d}" if year else "????"
        month_pattern = f"{int(month):02d}" if month else "??"

        for y_path in sorted(self.storage_root.glob(year_pattern)):
            if not y_path.is_dir() or not re.match(r"^\d{4}$", y_path.name):
                continue
            for m_path in sorted(y_path.glob(month_pattern)):
                if not m_path.is_dir() or not re.match(r"^\d{2}$", m_path.name):
                    continue
                for p_path in sorted(m_path.glob("*_*")):
                    if not p_path.is_dir():
                        continue
                    match = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+)$", p_path.name)
                    if not match:
                        continue

                    date_str, p_slug = match.groups()
                    versions = [
                        v.name
                        for v in p_path.iterdir()
                        if v.is_dir() and re.match(r"^v\d+$", v.name)
                    ]
                    versions = sorted(versions, key=lambda v: int(v[1:]))

                    latest_ver = versions[-1] if versions else "v1"
                    title = p_slug.replace("-", " ").title()

                    manifest_file = p_path / latest_ver / "manifest.json"
                    legacy_manifest_file = p_path / latest_ver / "project_manifest.json"
                    status = "unknown"
                    if manifest_file.exists():
                        try:
                            with open(manifest_file, "r", encoding="utf-8") as f:
                                m_data = json.load(f)
                                title = m_data.get("title", title)
                                status = m_data.get("status", status)
                        except Exception:
                            pass
                    elif legacy_manifest_file.exists():
                        try:
                            with open(legacy_manifest_file, "r", encoding="utf-8") as f:
                                m_data = json.load(f)
                                title = m_data.get("title", title)
                                status = m_data.get("status", status)
                        except Exception:
                            pass

                    results.append(
                        {
                            "project_id": p_path.name,
                            "title": title,
                            "slug": p_slug,
                            "date": date_str,
                            "year": y_path.name,
                            "month": m_path.name,
                            "path": str(p_path),
                            "versions": versions,
                            "latest_version": latest_ver,
                            "status": status,
                        }
                    )
        return results

    def find_projects(self, query: str) -> List[Dict[str, Any]]:
        """Search projects by query string in title or slug."""
        q = query.lower().strip()
        all_p = self.list_all_projects()
        return [
            p for p in all_p
            if q in p["slug"].lower()
            or q in p["title"].lower()
            or q in p["project_id"].lower()
        ]

    def get_latest_project(self) -> Optional[VideoProject]:
        candidates = []
        if not self.storage_root.exists():
            return None
        for manifest in self.storage_root.glob("*/*/*/*/manifest.json"):
            candidates.append(manifest.parent)
        for manifest in self.storage_root.glob("*/*/*/*/project_manifest.json"):
            if manifest.parent not in candidates:
                candidates.append(manifest.parent)
        for scenes in self.storage_root.glob("*/*/*/*/scenes.json"):
            if scenes.parent not in candidates:
                candidates.append(scenes.parent)
        if not candidates:
            return None
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        latest_dir = candidates[0]
        match = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+)$", latest_dir.parent.name)
        date_val = match.group(1) if match else None
        slug_val = match.group(2) if match else latest_dir.parent.name
        return VideoProject(
            slug=slug_val,
            date=date_val,
            version=latest_dir.name,
            base_dir=latest_dir.parent.parent.parent.parent,
            auto_init=False,
        )

    def _resolve_date(
        self,
        slug: str,
        date: Optional[Union[str, datetime.date, datetime.datetime]],
    ) -> datetime.date:
        if date is None:
            located = self.find_project_dir(slug)
            if located:
                return located[0]
            return datetime.date.today()
        if isinstance(date, datetime.datetime):
            return date.date()
        if isinstance(date, datetime.date):
            return date
        if isinstance(date, str):
            match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date)
            if match:
                return datetime.date(
                    int(match.group(1)), int(match.group(2)), int(match.group(3))
                )
        return datetime.date.today()

    @classmethod
    def get_latest_or_create(
        cls,
        default_title: str = "Video Production",
        base_dir: Optional[Union[str, Path]] = None,
    ) -> VideoStorageManager:
        mgr = cls(base_dir=base_dir, auto_create=False)
        latest = mgr.get_latest_project()
        if latest:
            mgr._active_project = latest
            return mgr
        new_proj = mgr.init_project(default_title)
        mgr._active_project = new_proj
        return mgr


# ==============================================================================
# TOP-LEVEL FUNCTIONAL API
# ==============================================================================

_default_manager = VideoStorageManager()


def init_project(
    title: str,
    slug: Optional[str] = None,
    date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    version: Union[str, int] = "v1",
    base_dir: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> VideoProject:
    mgr = VideoStorageManager(storage_root=base_dir) if base_dir else _default_manager
    return mgr.init_project(
        title=title, slug=slug, date=date, version=version, metadata=metadata
    )


create_project = init_project


def get_project(
    slug: str,
    date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    version: Optional[Union[str, int]] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> VideoProject:
    mgr = VideoStorageManager(storage_root=base_dir) if base_dir else _default_manager
    return mgr.get_project(slug=slug, date=date, version=version)


def create_version(
    slug: str,
    date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    base_version: Optional[Union[str, int]] = None,
    copy_assets: bool = False,
    base_dir: Optional[Union[str, Path]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> VideoProject:
    mgr = VideoStorageManager(storage_root=base_dir) if base_dir else _default_manager
    return mgr.create_new_version(
        slug=slug,
        date=date,
        base_version=base_version,
        copy_assets=copy_assets,
        metadata=metadata,
    )


def list_projects(
    year: Optional[Union[int, str]] = None,
    month: Optional[Union[int, str]] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> List[Dict[str, Any]]:
    mgr = VideoStorageManager(storage_root=base_dir) if base_dir else _default_manager
    return mgr.list_all_projects(year=year, month=month)


def resolve_canonical_path(
    slug: str,
    category: str,
    filename: Optional[str] = None,
    subcategory: Optional[str] = None,
    version: Union[str, int] = "v1",
    date: Optional[Union[str, datetime.date, datetime.datetime]] = None,
    base_dir: Optional[Union[str, Path]] = None,
) -> Path:
    proj = get_project(slug=slug, date=date, version=version, base_dir=base_dir)
    return proj.resolve_path(category=category, filename=filename, subcategory=subcategory)


# ==============================================================================
# COMMAND-LINE INTERFACE (CLI)
# ==============================================================================


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video_storage_manager.py",
        description="Central Video Storage and Path Manager for videopro (Hermes Agent).",
    )
    parser.add_argument(
        "--storage-root",
        "--base-dir",
        "-r",
        help="Override base storage root directory",
        default=None,
        dest="storage_root",
    )

    root_arg_parser = argparse.ArgumentParser(add_help=False)
    root_arg_parser.add_argument(
        "--storage-root",
        "--base-dir",
        "-r",
        help="Override base storage root directory",
        default=argparse.SUPPRESS,
        dest="storage_root",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init / create
    for cmd_name in ("init", "create"):
        p_init = subparsers.add_parser(cmd_name, help="Initialize a new project", parents=[root_arg_parser])
        p_init.add_argument("title", help="Project title")
        p_init.add_argument("--slug", "-s", help="Custom slug (defaults to slugified title)")
        p_init.add_argument("--date", "-d", help="Custom date (YYYY-MM-DD)", default=None)
        p_init.add_argument("--version", "-v", help="Initial version tag (default: v1)", default="v1")
        p_init.add_argument("--style", help="Video style (e.g. vox_documentary)", default="vox_documentary")
        p_init.add_argument("--duration", type=int, help="Target duration in seconds", default=45)

    # list
    p_list = subparsers.add_parser("list", help="List all video projects", parents=[root_arg_parser])
    p_list.add_argument("--year", "-y", help="Filter by year (YYYY)")
    p_list.add_argument("--month", "-m", help="Filter by month (MM)")
    p_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # info
    p_info = subparsers.add_parser("info", help="Get project information", parents=[root_arg_parser])
    p_info.add_argument("slug", help="Project slug, title or path")
    p_info.add_argument("--version", "-v", help="Version tag", default=None)
    p_info.add_argument("--date", "-d", help="Date (YYYY-MM-DD)", default=None)
    p_info.add_argument("--json", action="store_true", help="Output raw JSON")

    # new-version
    p_ver = subparsers.add_parser("new-version", help="Create a new version (e.g. v2) for a project", parents=[root_arg_parser])
    p_ver.add_argument("slug", help="Project slug")
    p_ver.add_argument("--base", "-b", help="Base version to branch from", default=None)
    p_ver.add_argument("--copy-assets", action="store_true", help="Copy assets from base version")
    p_ver.add_argument("--date", "-d", help="Date (YYYY-MM-DD)", default=None)

    # register-asset
    p_reg = subparsers.add_parser("register-asset", help="Register an asset file into manifest", parents=[root_arg_parser])
    p_reg.add_argument("slug", help="Project slug")
    p_reg.add_argument("file_path", help="Path to asset file")
    p_reg.add_argument("--category", "-c", help="Asset category (photos, cutouts, broll, logos, keyframes)", default="photos")
    p_reg.add_argument("--engine", help="Source engine (nanobanana, rembg, etc.)", default="nanobanana")
    p_reg.add_argument("--version", "-v", help="Version tag", default="v1")

    # resolve
    p_res = subparsers.add_parser("resolve", help="Resolve canonical path for a subfolder or file", parents=[root_arg_parser])
    p_res.add_argument("slug", help="Project slug")
    p_res.add_argument("category", help="Category (raw_clips, audio, assets, renders, exports, manifests, root)")
    p_res.add_argument("filename", nargs="?", help="Optional filename to append", default=None)
    p_res.add_argument("--subcategory", "-s", help="Subcategory folder", default=None)
    p_res.add_argument("--version", "-v", help="Version tag", default="v1")

    # verify / validate
    for v_name in ("verify", "validate"):
        p_val = subparsers.add_parser(v_name, help="Verify project integrity & 5KB gate", parents=[root_arg_parser])
        p_val.add_argument("slug", help="Project slug or path", nargs="?", default=".")
        p_val.add_argument("--version", "-v", help="Version tag", default="v1")
        p_val.add_argument("--date", "-d", help="Date (YYYY-MM-DD)", default=None)

    # export-flow
    p_flow = subparsers.add_parser("export-flow", help="Export Google Flow path configuration", parents=[root_arg_parser])
    p_flow.add_argument("slug", help="Project slug")
    p_flow.add_argument("--version", "-v", default="v1")

    # export-videomastery
    p_vm = subparsers.add_parser("export-videomastery", help="Export Videomastery API integration config", parents=[root_arg_parser])
    p_vm.add_argument("slug", help="Project slug")
    p_vm.add_argument("--version", "-v", default="v1")
    p_vm.add_argument("--api-url", default="http://127.0.0.1:9130", help="Backend API base URL")

    return parser


def main() -> int:
    parser = _build_cli_parser()
    args = parser.parse_args()

    mgr = VideoStorageManager(storage_root=args.storage_root)

    if args.command in ("init", "create"):
        meta = {
            "style": args.style,
            "target_duration_seconds": args.duration,
        }
        proj = mgr.init_project(
            title=args.title,
            slug=args.slug,
            date=args.date,
            version=args.version,
            metadata=meta,
        )
        print(f"✅ Project initialized successfully:")
        print(f"   ID:       {proj.project_id}")
        print(f"   Version:  {proj.version}")
        print(f"   Path:     {proj.version_dir}")
        print(f"   Manifest: {proj.manifest_path}")
        return 0

    elif args.command == "list":
        projects = mgr.list_all_projects(year=args.year, month=args.month)
        if args.json:
            print(json.dumps(projects, indent=2, ensure_ascii=False))
        else:
            print(f"\n📁 Video Projects in {mgr.storage_root} ({len(projects)} found):\n")
            for p in projects:
                vers_str = ", ".join(p["versions"]) if p["versions"] else "none"
                print(f" • [{p['date']}] {p['title']} ({p['slug']})")
                print(f"   Path:     {p['path']} (Latest: {p['latest_version']}, Versions: [{vers_str}])")
                print(f"   Status:   {p['status']}\n")
        return 0

    elif args.command == "info":
        if os.path.exists(args.slug):
            proj = VideoStorageManager(project_ref=args.slug)._get_active()
        else:
            proj = mgr.get_project(slug=args.slug, date=args.date, version=args.version)
        manifest = proj.load_manifest()
        if args.json:
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
        else:
            print(f"\n🎬 Project Info: {proj.title}")
            print(f"   ID:          {proj.project_id}")
            print(f"   Version:     {proj.version}")
            print(f"   Root Dir:    {proj.version_dir}")
            print(f"   Status:      {manifest.get('status', 'unknown')}")
            print(f"   Created:     {manifest.get('created_at')}")
            print(f"   Assets:      {len(manifest.get('assets_manifest', []))} registered")
            print(f"   Raw Clips:   {len(manifest.get('clips_registry', []))} registered")
            print(f"   Exports:     {len(manifest.get('exports_registry', []))} registered\n")
        return 0

    elif args.command == "new-version":
        proj = mgr.create_new_version(
            slug=args.slug,
            date=args.date,
            base_version=args.base,
            copy_assets=args.copy_assets,
        )
        print(f"✅ Created new project version:")
        print(f"   ID:       {proj.project_id}")
        print(f"   Version:  {proj.version}")
        print(f"   Path:     {proj.version_dir}")
        return 0

    elif args.command == "register-asset":
        proj = mgr.get_project(slug=args.slug, version=args.version)
        rec = proj.register_asset(
            file_path=args.file_path,
            category=args.category,
            source_engine=args.engine,
        )
        print(f"✅ Asset registered successfully in manifest:")
        print(f"   ID:       {rec.name if hasattr(rec, 'name') else rec.get('name')}")
        print(f"   Path:     {rec.path if hasattr(rec, 'path') else rec.get('path')}")
        return 0

    elif args.command == "resolve":
        path = resolve_canonical_path(
            slug=args.slug,
            category=args.category,
            filename=args.filename,
            subcategory=args.subcategory,
            version=args.version,
            date=args.date if hasattr(args, "date") else None,
            base_dir=args.storage_root,
        )
        print(str(path))
        return 0

    elif args.command in ("verify", "validate"):
        if os.path.exists(args.slug):
            proj = VideoStorageManager(project_ref=args.slug)._get_active()
        else:
            proj = mgr.get_project(slug=args.slug, date=args.date, version=args.version)
        report = proj.verify_integrity()
        status_icon = "✅" if report["valid"] else "❌"
        print(f"\n{status_icon} Integrity Report for {proj.project_id} ({proj.version}):")
        print(f"   Assets:   {report['verified_assets']}/{report['asset_count']} verified ({report['total_asset_bytes']} bytes)")
        if report["issues"]:
            print(f"   Issues ({len(report['issues'])}):")
            for issue in report["issues"]:
                print(f"     - ⚠️ {issue}")
        else:
            print("   Structure & assets gate: 100% PASS")
        print()
        return 0 if report["valid"] else 1

    elif args.command == "export-flow":
        proj = mgr.get_project(slug=args.slug, version=args.version)
        print(json.dumps(proj.get_flow_paths(), indent=2, ensure_ascii=False))
        return 0

    elif args.command == "export-videomastery":
        proj = mgr.get_project(slug=args.slug, version=args.version)
        print(
            json.dumps(
                proj.get_videomastery_integration_info(api_base_url=args.api_url),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
