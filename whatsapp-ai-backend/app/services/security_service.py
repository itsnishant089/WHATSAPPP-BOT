from __future__ import annotations

from app.core.config import Settings
from app.core.security import contains_secret
from app.utils.text import looks_like_leak, normalize_text, strip_html

FRIENDLY_ERROR = (
    "Sorry, abhi thodi technical problem aa rahi hai. Please thodi der baad try karein. 🙏"
)
RATE_LIMIT_REPLY = "Please thoda wait karein aur fir try karein. 🙏"
TOO_LONG_REPLY = "Message thoda lamba ho gaya. Please shorter message bhejein. 🙏"
UNSUPPORTED_REPLY = (
    "Abhi main sirf *text messages* samajh pata hoon. "
    "Apna sawal text mein likh dein — jaise CSE syllabus ya LEET syllabus. 🙏"
)
EMPTY_FALLBACK = (
    "Sorry, is sawal ka verified answer abhi nahi mil paya. "
    "Thoda specific likhein (branch + semester / LEET syllabus / Premium) "
    "ya contact karein: https://hsbteleet.com/contact"
)


class ResponseValidator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, text: str | None) -> str:
        cleaned = strip_html(text or "").strip()
        if not cleaned:
            return EMPTY_FALLBACK
        if contains_secret(cleaned, self.settings.secret_values) or looks_like_leak(cleaned):
            return FRIENDLY_ERROR
        if len(cleaned) > self.settings.max_ai_output_chars:
            cleaned = cleaned[: self.settings.max_ai_output_chars].rsplit(" ", 1)[0] + "…"
        return cleaned
