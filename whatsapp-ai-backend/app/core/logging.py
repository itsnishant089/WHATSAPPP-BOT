import json
import logging
import re
import sys
from datetime import datetime, timezone

from app.core.config import Settings

_PHONE_RE = re.compile(r"(\+?\d{2,4})(\d{4,})(\d{4})")


def mask_phone(value: str | None) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) < 6:
        return "***"
    return f"{digits[:2]}******{digits[-4:]}"


def redact_secrets(message: str, secrets: list[str]) -> str:
    redacted = message
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


class RedactingFormatter(logging.Formatter):
    def __init__(self, secrets: list[str]) -> None:
        super().__init__()
        self._secrets = secrets

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_data", None)
        if isinstance(extra, dict):
            payload.update(extra)
        text = json.dumps(payload, default=str, ensure_ascii=False)
        text = redact_secrets(text, self._secrets)
        text = _PHONE_RE.sub(lambda m: f"{m.group(1)}******{m.group(3)}", text)
        return text


def setup_logging(settings: Settings) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(RedactingFormatter(settings.secret_values))
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))


def log_event(logger: logging.Logger, message: str, **fields: object) -> None:
    logger.info(message, extra={"extra_data": fields})
