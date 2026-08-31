from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger(__name__)

FALLBACK_REPLY = (
    "Sorry 🙏 abhi AI service temporarily unavailable hai. Please thodi der baad try karein."
)


class GeminiError(Exception):
    def __init__(self, message: str, retryable: bool = False, status_code: int | None = None) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class GeminiService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    def _url(self) -> str:
        model = self.settings.gemini_model
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent"
        )

    async def generate(self, system_instruction: str, user_prompt: str) -> str:
        body: dict[str, Any] = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1024,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            ],
        }
        last_error: GeminiError | None = None
        for attempt in range(3):
            started = time.perf_counter()
            try:
                response = await self.client.post(
                    self._url(),
                    params={"key": self.settings.gemini_api_key},
                    json=body,
                    timeout=self.settings.gemini_timeout_seconds,
                )
            except httpx.TimeoutException as exc:
                last_error = GeminiError("timeout", retryable=True)
                logger.warning("gemini_timeout", extra={"extra_data": {"attempt": attempt + 1}})
                await asyncio.sleep(0.4 * (2**attempt))
                continue
            latency_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code in {401, 403}:
                raise GeminiError("auth_failed", retryable=False, status_code=response.status_code)
            if response.status_code in {429, 500, 502, 503, 504}:
                last_error = GeminiError("transient", retryable=True, status_code=response.status_code)
                await asyncio.sleep(0.4 * (2**attempt))
                continue
            if response.status_code >= 400:
                raise GeminiError("request_failed", retryable=False, status_code=response.status_code)
            data = response.json()
            text = self._extract_text(data)
            logger.info("gemini_ok", extra={"extra_data": {"latency_ms": latency_ms}})
            return text
        raise last_error or GeminiError("unknown")

    def _extract_text(self, data: dict[str, Any]) -> str:
        candidates = data.get("candidates") or []
        if not candidates:
            raise GeminiError("empty_response")
        parts = ((candidates[0].get("content") or {}).get("parts")) or []
        texts = [str(p.get("text") or "") for p in parts if isinstance(p, dict)]
        combined = "\n".join(t for t in texts if t).strip()
        if not combined:
            raise GeminiError("empty_response")
        return combined
