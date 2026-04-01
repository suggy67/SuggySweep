import os
import time
from pathlib import Path
from typing import Optional

import httpx


class AITokenProvider:
    """Берет токен из локального ai.txt и из GitHub raw.

    Источники:
    1) <repo_root>/ai.txt
    2) https://raw.githubusercontent.com/suggy67/SuggySweep/main/ai.txt
    3) https://raw.githubusercontent.com/suggy67/SuggySweep/master/ai.txt
    """

    RAW_URLS = (
        "https://raw.githubusercontent.com/suggy67/SuggySweep/main/ai.txt",
        "https://raw.githubusercontent.com/suggy67/SuggySweep/master/ai.txt",
    )

    def __init__(self, refresh_seconds: int = 12) -> None:
        self.refresh_seconds = refresh_seconds
        self._cached_token: str = ""
        self._cached_source: str = ""
        self._last_refresh_ts: float = 0.0
        self._last_local_mtime: float = -1.0
        self.local_ai_file = Path(__file__).resolve().parents[2] / "ai.txt"

    async def get_token(self) -> str:
        now = time.time()
        local_mtime = self._read_local_mtime()
        should_refresh = (
            not self._cached_token
            or (now - self._last_refresh_ts) >= self.refresh_seconds
            or local_mtime != self._last_local_mtime
        )

        if should_refresh:
            await self._refresh_token()

        return self._cached_token

    @property
    def source(self) -> str:
        return self._cached_source

    def _read_local_mtime(self) -> float:
        try:
            return self.local_ai_file.stat().st_mtime
        except OSError:
            return -1.0

    def _normalize_token(self, text: str) -> str:
        for line in text.splitlines():
            candidate = line.strip()
            if not candidate or candidate.startswith("#"):
                continue
            return candidate
        return ""

    async def _refresh_token(self) -> None:
        self._last_refresh_ts = time.time()
        self._last_local_mtime = self._read_local_mtime()

        local_token = self._read_local_file_token()
        if local_token:
            self._cached_token = local_token
            self._cached_source = str(self.local_ai_file)
            return

        remote_token, source = await self._read_remote_token()
        if remote_token:
            self._cached_token = remote_token
            self._cached_source = source

    def _read_local_file_token(self) -> str:
        try:
            text = self.local_ai_file.read_text(encoding="utf-8")
        except OSError:
            return ""
        return self._normalize_token(text)

    async def _read_remote_token(self) -> tuple[str, str]:
        timeout = httpx.Timeout(8.0, connect=4.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            for url in self.RAW_URLS:
                try:
                    response = await client.get(url)
                except httpx.HTTPError:
                    continue
                if response.status_code != 200:
                    continue
                token = self._normalize_token(response.text)
                if token:
                    return token, url
        return "", ""

