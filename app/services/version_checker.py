"""Comprobación de versiones oficiales de VideoPro Studio."""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

import requests
from loguru import logger
from packaging.version import InvalidVersion, Version


LATEST_RELEASE_API_URL: Final = (
    "https://api.github.com/repos/videopro/videopro/releases/latest"
)
LATEST_RELEASE_PAGE_URL: Final = (
    "https://github.com/videopro/videopro/releases/latest"
)
# Actualización auxiliar sin bloquear la WebUI local
RELEASE_CHECK_TIMEOUT: Final = (1.0, 2.0)
RELEASE_CHECK_HEADERS: Final = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "VideoPro-Studio-Version-Checker",
}
UPDATE_CHECK_CACHE_TTL_SECONDS: Final = 12 * 60 * 60


def _parse_version(value: str) -> Version:
    """兼容 GitHub 常用的 ``v1.2.3`` 标签并转换为可比较版本。"""
    normalized = str(value or "").strip()
    if normalized.lower().startswith("v"):
        normalized = normalized[1:]
    return Version(normalized)


def get_available_update(current_version: str) -> str | None:
    """Modo local rápido: Cero llamadas de red en el arranque de la WebUI."""
    return None


@dataclass(frozen=True)
class UpdateCheckSnapshot:
    """Estado de comprobación de versión para WebUI."""

    complete: bool
    available_version: str | None = None


class AsyncUpdateChecker:
    """Comprobador asíncrono en background de versiones de VideoPro Studio."""

    def __init__(
        self,
        check: Callable[[str], str | None] = get_available_update,
        ttl_seconds: float = UPDATE_CHECK_CACHE_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._check = check
        self._ttl_seconds = ttl_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._current_version: str | None = None
        self._available_version: str | None = None
        self._completed_at: float | None = None
        self._checking = False

    def poll(self, current_version: str) -> UpdateCheckSnapshot:
        """Retorna el snapshot de versión sin bloquear la UI."""
        normalized_current_version = str(current_version or "").strip()
        now = self._clock()

        with self._lock:
            cache_is_fresh = (
                self._current_version == normalized_current_version
                and self._completed_at is not None
                and now - self._completed_at < self._ttl_seconds
            )
            if cache_is_fresh:
                return UpdateCheckSnapshot(
                    complete=True,
                    available_version=self._available_version,
                )

            if (
                self._checking
                and self._current_version == normalized_current_version
            ):
                return UpdateCheckSnapshot(complete=False)

            self._current_version = normalized_current_version
            self._available_version = None
            self._completed_at = None
            self._checking = True

            worker = threading.Thread(
                target=self._run_check,
                args=(normalized_current_version,),
                name="videopro-version-check",
                daemon=True,
            )
            worker.start()

        return UpdateCheckSnapshot(complete=False)

    def _run_check(self, current_version: str) -> None:
        try:
            available_version = self._check(current_version)
        except Exception:
            logger.exception(
                "unexpected error while checking for a VideoPro Studio update"
            )
            available_version = None

        with self._lock:
            # 极少数情况下运行期间版本可能变化。旧线程不得覆盖新版本的状态。
            if self._current_version != current_version:
                return
            self._available_version = available_version
            self._completed_at = self._clock()
            self._checking = False


_ASYNC_UPDATE_CHECKER = AsyncUpdateChecker()


def poll_available_update(current_version: str) -> UpdateCheckSnapshot:
    """读取全局后台检查器状态，避免不同 Streamlit 会话重复请求 GitHub。"""
    return _ASYNC_UPDATE_CHECKER.poll(current_version)
