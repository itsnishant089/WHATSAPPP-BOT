from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Protocol

from app.core.logging import mask_phone
from app.models.message_models import MemoryItem, UserPreferences

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ts(value: str | None) -> str | None:
    if not value:
        return None
    if value.isdigit():
        return datetime.fromtimestamp(int(value), tz=timezone.utc).isoformat()
    return value


class DataStore(Protocol):
    def message_exists(self, whatsapp_message_id: str) -> bool: ...
    def upsert_user(self, whatsapp_id: str, phone: str | None, name: str | None) -> None: ...
    def insert_incoming(
        self,
        whatsapp_message_id: str,
        whatsapp_user_id: str,
        message_type: str,
        text: str | None,
        timestamp: str | None,
        metadata: dict[str, Any],
    ) -> str | None: ...
    def mark_status(self, whatsapp_message_id: str, status: str, ai_response: str | None = None) -> None: ...
    def insert_outgoing(
        self,
        whatsapp_user_id: str,
        text: str,
        related_incoming_id: str | None,
        metadata: dict[str, Any],
    ) -> None: ...
    def add_memory(self, whatsapp_user_id: str, role: str, content: str, message_id: str | None = None) -> None: ...
    def load_memory(self, whatsapp_user_id: str, limit: int) -> list[MemoryItem]: ...
    def load_summary(self, whatsapp_user_id: str) -> str | None: ...
    def save_summary(self, whatsapp_user_id: str, summary: str) -> None: ...
    def load_preferences(self, whatsapp_user_id: str) -> UserPreferences | None: ...
    def upsert_preferences(self, prefs: UserPreferences) -> None: ...
    def log_ai(
        self,
        whatsapp_user_id: str,
        model: str,
        status: str,
        latency_ms: int | None,
        error_code: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None: ...
    def record_webhook_event(self, event_id: str | None, payload_hash: str, event_type: str) -> None: ...


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, dict[str, Any]] = {}
        self.memory: dict[str, list[MemoryItem]] = {}
        self.summaries: dict[str, str] = {}
        self.preferences: dict[str, UserPreferences] = {}
        self.ai_logs: list[dict[str, Any]] = []
        self.webhook_events: list[dict[str, Any]] = []

    def message_exists(self, whatsapp_message_id: str) -> bool:
        return whatsapp_message_id in self.messages

    def upsert_user(self, whatsapp_id: str, phone: str | None, name: str | None) -> None:
        self.users[whatsapp_id] = {"phone": phone, "name": name}

    def insert_incoming(
        self,
        whatsapp_message_id: str,
        whatsapp_user_id: str,
        message_type: str,
        text: str | None,
        timestamp: str | None,
        metadata: dict[str, Any],
    ) -> str | None:
        if whatsapp_message_id in self.messages:
            return None
        self.messages[whatsapp_message_id] = {
            "id": whatsapp_message_id,
            "user": whatsapp_user_id,
            "type": message_type,
            "text": text,
            "status": "received",
            "metadata": metadata,
            "timestamp": timestamp,
        }
        return whatsapp_message_id

    def mark_status(self, whatsapp_message_id: str, status: str, ai_response: str | None = None) -> None:
        row = self.messages.get(whatsapp_message_id)
        if not row:
            return
        row["status"] = status
        if ai_response is not None:
            row["ai_response"] = ai_response

    def insert_outgoing(
        self,
        whatsapp_user_id: str,
        text: str,
        related_incoming_id: str | None,
        metadata: dict[str, Any],
    ) -> None:
        key = f"out:{related_incoming_id or _now()}"
        self.messages[key] = {"user": whatsapp_user_id, "text": text, "status": "processed"}

    def add_memory(self, whatsapp_user_id: str, role: str, content: str, message_id: str | None = None) -> None:
        self.memory.setdefault(whatsapp_user_id, []).append(MemoryItem(role=role, content=content))  # type: ignore[arg-type]

    def load_memory(self, whatsapp_user_id: str, limit: int) -> list[MemoryItem]:
        return self.memory.get(whatsapp_user_id, [])[-limit:]

    def load_summary(self, whatsapp_user_id: str) -> str | None:
        return self.summaries.get(whatsapp_user_id)

    def save_summary(self, whatsapp_user_id: str, summary: str) -> None:
        self.summaries[whatsapp_user_id] = summary

    def load_preferences(self, whatsapp_user_id: str) -> UserPreferences | None:
        return self.preferences.get(whatsapp_user_id)

    def upsert_preferences(self, prefs: UserPreferences) -> None:
        self.preferences[prefs.whatsapp_user_id] = prefs

    def log_ai(
        self,
        whatsapp_user_id: str,
        model: str,
        status: str,
        latency_ms: int | None,
        error_code: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        self.ai_logs.append({"user": whatsapp_user_id, "status": status, "error_code": error_code})

    def record_webhook_event(self, event_id: str | None, payload_hash: str, event_type: str) -> None:
        self.webhook_events.append({"event_id": event_id, "payload_hash": payload_hash, "event_type": event_type})


class SupabaseStore:
    def __init__(self, client: Any) -> None:
        self.client = client

    def message_exists(self, whatsapp_message_id: str) -> bool:
        result = (
            self.client.table("messages")
            .select("id")
            .eq("whatsapp_message_id", whatsapp_message_id)
            .limit(1)
            .execute()
        )
        return bool(result.data)

    def upsert_user(self, whatsapp_id: str, phone: str | None, name: str | None) -> None:
        now = _now()
        existing = (
            self.client.table("users")
            .select("id")
            .eq("whatsapp_id", whatsapp_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            self.client.table("users").update(
                {
                    "phone_number": phone,
                    "profile_name": name,
                    "last_seen_at": now,
                    "updated_at": now,
                }
            ).eq("whatsapp_id", whatsapp_id).execute()
            return
        self.client.table("users").insert(
            {
                "whatsapp_id": whatsapp_id,
                "phone_number": phone,
                "profile_name": name,
                "first_seen_at": now,
                "last_seen_at": now,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ).execute()
        logger.info("user_created", extra={"extra_data": {"user": mask_phone(whatsapp_id)}})

    def insert_incoming(
        self,
        whatsapp_message_id: str,
        whatsapp_user_id: str,
        message_type: str,
        text: str | None,
        timestamp: str | None,
        metadata: dict[str, Any],
    ) -> str | None:
        now = _now()
        try:
            result = (
                self.client.table("messages")
                .insert(
                    {
                        "whatsapp_message_id": whatsapp_message_id,
                        "whatsapp_user_id": whatsapp_user_id,
                        "direction": "incoming",
                        "message_type": message_type,
                        "message_text": text,
                        "status": "received",
                        "timestamp": _ts(timestamp),
                        "created_at": now,
                        "metadata": metadata,
                    }
                )
                .execute()
            )
        except Exception as exc:
            logger.warning("incoming_insert_conflict", extra={"extra_data": {"error": type(exc).__name__}})
            if self.message_exists(whatsapp_message_id):
                return None
            raise
        if result.data:
            return str(result.data[0].get("id"))
        return None

    def mark_status(self, whatsapp_message_id: str, status: str, ai_response: str | None = None) -> None:
        payload: dict[str, Any] = {"status": status}
        if ai_response is not None:
            payload["ai_response"] = ai_response
        self.client.table("messages").update(payload).eq("whatsapp_message_id", whatsapp_message_id).execute()

    def insert_outgoing(
        self,
        whatsapp_user_id: str,
        text: str,
        related_incoming_id: str | None,
        metadata: dict[str, Any],
    ) -> None:
        now = _now()
        outbound_id = f"out:{related_incoming_id or now}"
        self.client.table("messages").insert(
            {
                "whatsapp_message_id": outbound_id,
                "whatsapp_user_id": whatsapp_user_id,
                "direction": "outgoing",
                "message_type": "text",
                "message_text": text,
                "ai_response": text,
                "status": "processed",
                "timestamp": now,
                "created_at": now,
                "metadata": metadata,
            }
        ).execute()

    def add_memory(self, whatsapp_user_id: str, role: str, content: str, message_id: str | None = None) -> None:
        self.client.table("conversation_memory").insert(
            {
                "whatsapp_user_id": whatsapp_user_id,
                "role": role,
                "content": content,
                "message_id": message_id,
                "created_at": _now(),
            }
        ).execute()

    def load_memory(self, whatsapp_user_id: str, limit: int) -> list[MemoryItem]:
        result = (
            self.client.table("conversation_memory")
            .select("role,content")
            .eq("whatsapp_user_id", whatsapp_user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        rows = list(reversed(result.data or []))
        items: list[MemoryItem] = []
        for row in rows:
            role = row.get("role")
            if role not in {"user", "assistant", "system"}:
                continue
            items.append(MemoryItem(role=role, content=row.get("content") or ""))
        return items

    def load_summary(self, whatsapp_user_id: str) -> str | None:
        result = (
            self.client.table("conversation_summaries")
            .select("summary")
            .eq("whatsapp_user_id", whatsapp_user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0].get("summary")
        return None

    def save_summary(self, whatsapp_user_id: str, summary: str) -> None:
        self.client.table("conversation_summaries").insert(
            {
                "whatsapp_user_id": whatsapp_user_id,
                "summary": summary,
                "created_at": _now(),
            }
        ).execute()

    def load_preferences(self, whatsapp_user_id: str) -> UserPreferences | None:
        result = (
            self.client.table("users_preferences")
            .select("*")
            .eq("whatsapp_user_id", whatsapp_user_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        row = result.data[0]
        return UserPreferences(
            whatsapp_user_id=whatsapp_user_id,
            language=row.get("language"),
            branch=row.get("branch"),
            target_exam=row.get("target_exam"),
            state=row.get("state"),
            college=row.get("college"),
            metadata=row.get("metadata") or {},
        )

    def upsert_preferences(self, prefs: UserPreferences) -> None:
        now = _now()
        payload = {
            "whatsapp_user_id": prefs.whatsapp_user_id,
            "language": prefs.language,
            "branch": prefs.branch,
            "target_exam": prefs.target_exam,
            "state": prefs.state,
            "college": prefs.college,
            "metadata": prefs.metadata,
            "updated_at": now,
        }
        existing = (
            self.client.table("users_preferences")
            .select("id")
            .eq("whatsapp_user_id", prefs.whatsapp_user_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            self.client.table("users_preferences").update(payload).eq(
                "whatsapp_user_id", prefs.whatsapp_user_id
            ).execute()
            return
        payload["created_at"] = now
        self.client.table("users_preferences").insert(payload).execute()

    def log_ai(
        self,
        whatsapp_user_id: str,
        model: str,
        status: str,
        latency_ms: int | None,
        error_code: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        self.client.table("ai_logs").insert(
            {
                "whatsapp_user_id": whatsapp_user_id,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "status": status,
                "error_code": error_code,
                "created_at": _now(),
            }
        ).execute()

    def record_webhook_event(self, event_id: str | None, payload_hash: str, event_type: str) -> None:
        try:
            self.client.table("webhook_events").insert(
                {
                    "event_id": event_id,
                    "payload_hash": payload_hash,
                    "event_type": event_type,
                    "processed": True,
                    "created_at": _now(),
                }
            ).execute()
        except Exception:
            logger.debug("webhook_event_store_skipped")
