from __future__ import annotations

from typing import Any

from app.models.message_models import IncomingMessage
from app.utils.phone import normalize_whatsapp_id
from app.utils.text import normalize_text


def extract_incoming_messages(payload: dict[str, Any]) -> list[IncomingMessage]:
    results: list[IncomingMessage] = []
    for entry in payload.get("entry") or []:
        if not isinstance(entry, dict):
            continue
        waba_id = str(entry.get("id") or "")
        for change in entry.get("changes") or []:
            if not isinstance(change, dict):
                continue
            value = change.get("value") or {}
            if not isinstance(value, dict):
                continue
            metadata = value.get("metadata") or {}
            phone_number_id = str(metadata.get("phone_number_id") or "")
            contacts = value.get("contacts") or []
            profile_name = None
            if contacts and isinstance(contacts[0], dict):
                profile = contacts[0].get("profile") or {}
                profile_name = profile.get("name")
            messages = value.get("messages") or []
            if not messages:
                continue
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                msg_type = str(msg.get("type") or "unknown")
                text_body = None
                if msg_type == "text":
                    text_body = (msg.get("text") or {}).get("body")
                sender = normalize_whatsapp_id(str(msg.get("from") or ""))
                results.append(
                    IncomingMessage(
                        whatsapp_id=sender,
                        phone_number=sender,
                        profile_name=normalize_text(profile_name) or None,
                        message_id=str(msg.get("id") or ""),
                        timestamp=str(msg.get("timestamp") or ""),
                        message_type=msg_type,
                        text=normalize_text(text_body) if text_body else None,
                        phone_number_id=phone_number_id or None,
                        waba_id=waba_id or None,
                        raw=msg,
                    )
                )
    return results


def is_status_only(payload: dict[str, Any]) -> bool:
    for entry in payload.get("entry") or []:
        for change in (entry or {}).get("changes") or []:
            value = (change or {}).get("value") or {}
            if value.get("statuses") and not value.get("messages"):
                return True
    return False
