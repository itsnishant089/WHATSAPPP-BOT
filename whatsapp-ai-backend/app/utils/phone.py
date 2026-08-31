import re

_DIGITS = re.compile(r"\D")


def normalize_whatsapp_id(value: str | None) -> str:
    if not value:
        return ""
    return _DIGITS.sub("", value)


def is_valid_recipient(value: str | None) -> bool:
    digits = normalize_whatsapp_id(value)
    return 8 <= len(digits) <= 15
