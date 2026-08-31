from __future__ import annotations

import logging
import time

import httpx

from app.core.config import Settings
from app.utils.phone import is_valid_recipient, normalize_whatsapp_id
from app.utils.text import normalize_text

logger = logging.getLogger(__name__)


class WhatsAppError(Exception):
    def __init__(self, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class WhatsAppService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    def _endpoint(self, phone_number_id: str | None = None) -> str:
        pnid = phone_number_id or self.settings.whatsapp_phone_number_id
        version = self.settings.meta_graph_api_version
        return f"https://graph.facebook.com/{version}/{pnid}/messages"

    async def send_text_message(
        self,
        recipient_phone: str,
        text: str,
        *,
        phone_number_id: str | None = None,
    ) -> None:
        recipient = normalize_whatsapp_id(recipient_phone)
        if not is_valid_recipient(recipient):
            raise WhatsAppError("invalid_recipient", retryable=False)
        body = text.strip()
        if not body:
            raise WhatsAppError("empty_body", retryable=False)
        chunks = split_whatsapp_text(body, self.settings.whatsapp_max_chars)
        sender_id = phone_number_id or self.settings.whatsapp_phone_number_id
        for chunk in chunks:
            await self._post(recipient, chunk, sender_id)

    async def _post(self, recipient: str, text: str, phone_number_id: str) -> None:
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": text, "preview_url": True},
        }
        headers = {
            "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
            "Content-Type": "application/json",
        }
        started = time.perf_counter()
        try:
            response = await self.client.post(
                self._endpoint(phone_number_id),
                json=payload,
                headers=headers,
                timeout=self.settings.whatsapp_timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise WhatsAppError("timeout", retryable=True) from exc
        latency_ms = int((time.perf_counter() - started) * 1000)
        if response.status_code in {400, 401, 403, 404}:
            logger.error("whatsapp_send_failed", extra={"extra_data": {"status": response.status_code}})
            raise WhatsAppError("permanent_error", retryable=False)
        if response.status_code >= 500:
            raise WhatsAppError("transient", retryable=True)
        if response.status_code >= 400:
            raise WhatsAppError("send_failed", retryable=False)
        logger.info("whatsapp_sent", extra={"extra_data": {"latency_ms": latency_ms}})


def split_whatsapp_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, max_chars)
        if cut < max_chars // 2:
            cut = remaining.rfind(" ", 0, max_chars)
        if cut < 1:
            cut = max_chars
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    return [c for c in chunks if c]
