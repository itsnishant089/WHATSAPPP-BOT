from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request, Response, status
from fastapi.responses import JSONResponse, PlainTextResponse

from app.core.config import Settings
from app.core.logging import log_event
from app.core.security import payload_hash, tokens_match, verify_meta_signature
from app.services.message_service import extract_incoming_messages, is_status_only

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhook/whatsapp")
async def verify_webhook(request: Request) -> Response:
    settings: Settings = request.app.state.settings
    params = request.query_params
    mode = params.get("hub.mode", "")
    token = params.get("hub.verify_token", "")
    challenge = params.get("hub.challenge", "")
    if mode == "subscribe" and tokens_match(token, settings.meta_verify_token):
        log_event(logger, "webhook_verified")
        return PlainTextResponse(content=challenge, status_code=200)
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@router.post("/webhook/whatsapp")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    settings: Settings = request.app.state.settings
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" not in content_type:
        return {"status": "ignored"}

    raw = await request.body()
    if len(raw) > 512_000:
        return {"status": "ignored"}

    signature = request.headers.get("x-hub-signature-256")
    if settings.require_webhook_signature or settings.is_production:
        if not verify_meta_signature(raw, signature, settings.meta_app_secret):
            log_event(logger, "signature_rejected")
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"status": "forbidden"})

    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        return {"status": "ignored"}

    if not isinstance(payload, dict):
        return {"status": "ignored"}

    log_event(logger, "webhook_received")
    try:
        request.app.state.store.record_webhook_event(
            event_id=str((payload.get("entry") or [{}])[0].get("id") or "") or None,
            payload_hash=payload_hash(raw),
            event_type="whatsapp",
        )
    except Exception:
        logger.debug("webhook_event_log_failed")

    if is_status_only(payload):
        return {"status": "ok"}

    messages = extract_incoming_messages(payload)
    processor = request.app.state.processor
    for incoming in messages:
        background_tasks.add_task(processor.process, incoming)
    return {"status": "ok"}
