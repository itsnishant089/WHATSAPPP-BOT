import re
import unicodedata

_WS = re.compile(r"\s+")
_TOKEN = re.compile(r"[a-zA-Z0-9]+")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKC", str(value))
    return _WS.sub(" ", text).strip()


def tokenize(value: str | None) -> list[str]:
    text = normalize_text(value).lower()
    return _TOKEN.findall(text)


def parse_bool(value: object, default: bool = True) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "active"}:
        return True
    if text in {"0", "false", "no", "n", "inactive"}:
        return False
    return default


def parse_int(value: object, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def split_keywords(value: str | None) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,|;/]+", value.lower())
    return [p.strip() for p in parts if p.strip()]


LEAK_MARKERS = (
    "system prompt",
    "system instructions",
    "api key",
    "service_role",
    "x-hub-signature",
    "traceback",
    "internal architecture",
    "supabase_service",
    "whatsapp_access_token",
)


def looks_like_leak(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in LEAK_MARKERS)


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)
