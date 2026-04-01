import json
from typing import AsyncGenerator, Dict, List

import httpx
from ai.token_provider import AITokenProvider


class LovableAIClient:
    BASE_URL = "https://ai.gateway.lovable.dev/v1/chat/completions"

    SYSTEM_PROMPT = """Ты — AI-ассистент Suggy Sweep (подготовка к переустановке Windows).
Объясняй файлы и папки простым языком, рекомендуй что сохранить. Отвечай на русском."""

    def __init__(self, model: str = "google/gemini-3-flash-preview") -> None:
        self.model = model
        self.token_provider = AITokenProvider(refresh_seconds=12)

    async def analyze_file(self, file_info: Dict) -> AsyncGenerator[str, None]:
        prompt = f"""Проанализируй файл:
Имя: {file_info.get("name")}
Путь: {file_info.get("path")}
Расширение: {file_info.get("extension")}
Категория: {file_info.get("category")}
Размер: {file_info.get("size")}"""
        async for chunk in self._stream_request([{"role": "user", "content": prompt}]):
            yield chunk

    async def analyze_directory(
        self, dir_path: str, files: List[str]
    ) -> AsyncGenerator[str, None]:
        file_list = "\n".join(f"  - {f}" for f in files[:50])
        prompt = f"""Папка: {dir_path}
Файлов: {len(files)}, первые 50:
{file_list}
Объясни назначение папки и стоит ли сохранять перед переустановкой."""
        async for chunk in self._stream_request([{"role": "user", "content": prompt}]):
            yield chunk

    async def chat(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        async for chunk in self._stream_request(messages):
            yield chunk

    async def get_backup_recommendations(
        self, scan_results: Dict
    ) -> AsyncGenerator[str, None]:
        summary = json.dumps(scan_results, ensure_ascii=False, indent=2)[:12000]
        prompt = f"""По результатам сканирования дай приоритизированные рекомендации по бэкапу:
🔴 критично 🟡 желательно 🟢 можно не сохранять

Данные:
{summary}"""
        async for chunk in self._stream_request([{"role": "user", "content": prompt}]):
            yield chunk

    async def _stream_request(self, messages: List[Dict]) -> AsyncGenerator[str, None]:
        api_key = await self.token_provider.get_token()
        if not api_key:
            yield (
                "AI не настроен: добавьте токен в ai.txt (в корне проекта) "
                "или в ai.txt репозитория https://github.com/suggy67/SuggySweep."
            )
            return

        full_messages: List[Dict] = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *messages,
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                self.BASE_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "messages": full_messages,
                    "stream": True,
                    "temperature": 0.7,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        parsed = json.loads(payload)
                        text = parsed["choices"][0]["delta"].get("content", "")
                        if text:
                            yield text
                    except Exception:
                        continue
