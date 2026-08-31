from __future__ import annotations

import logging
import re
import time

from app.core.config import Settings
from app.core.logging import log_event, mask_phone
from app.core.prompts import SYSTEM_PROMPT, UNTRUSTED_DATA_PREAMBLE
from app.core.rate_limit import InMemoryRateLimiter, RedisRateLimiter
from app.database.queries import DataStore
from app.models.message_models import IncomingMessage, UserPreferences
from app.services.excel_service import ExcelService
from app.services.gemini_service import FALLBACK_REPLY, GeminiError, GeminiService
from app.services.memory_service import extract_preference_updates, infer_search_hints
from app.services.security_service import (
    EMPTY_FALLBACK,
    FRIENDLY_ERROR,
    RATE_LIMIT_REPLY,
    TOO_LONG_REPLY,
    UNSUPPORTED_REPLY,
    ResponseValidator,
)
from app.services.whatsapp_service import WhatsAppError, WhatsAppService

logger = logging.getLogger(__name__)

# Abusive words detection pattern (Hindi + English)
_ABUSE_WORDS = [
    r"\bmc\b", r"\bbc\b", r"\bbsdk\b", r"\bbskd\b", r"\bbhosdike\b",
    r"\bmadarchod\b", r"\bbehenchod\b", r"\bchutiya\b", r"\bgaandu\b",
    r"\bland\b", r"\blode\b", r"\brandi\b", r"\bharami\b",
    r"\bfuck\b", r"\bfuck you\b", r"\bbitch\b", r"\basshole\b",
    r"\bchutiye\b", r"\bmkc\b", r"\bbkl\b",
]
_ABUSE_PATTERN = re.compile("|".join(_ABUSE_WORDS), re.IGNORECASE)

ABUSE_WARNING = (
    "⚠️ *Aise mat bolo bhai!*\n\n varna tere maa chod duga\n\n"
    "Hum yahan tumhari help karne ke liye hain. "
    "Please apna sawal respectfully puchho, hum zaroor madad karenge. 🙏\n\n"
    "Agar koi problem hai toh seedha batao:\n"
    "• Email: nishant@hsbteleet.com\n"
    "• Contact: https://hsbteleet.com/contact"
)

HARDCODED_GREETING = (
    "Namaste! 🙏 Welcome to *hsbteleet.com* WhatsApp help.\n\n"
    "I can instantly share:\n"
    "1️⃣ HSBTE Diploma PYQ (branch + semester)\n"
    "2️⃣ Diploma Syllabus PDF (branch-wise)\n"
    "3️⃣ Haryana LEET Syllabus / Exam Pattern\n"
    "4️⃣ Free LEET sample papers\n"
    "5️⃣ Premium ₹99 & Ultra Premium ₹149 details\n"
    "6️⃣ Counseling help ₹99\n\n"
    "Reply with what you need, e.g.\n"
    "• \"CSE 1st semester PYQ\"\n"
    "• \"LEET syllabus\"\n"
    "• \"Computer syllabus PDF\"\n"
    "• \"Buy Premium\"\n"
    "• \"Ultra Premium kya milta hai\""
)

HIGH_PRIORITY_REPLY = (
    "Your message is marked *HIGH PRIORITY* ✅\n\n"
    "Our admin will contact you soon on WhatsApp to assist with your query.\n\n"
    "Meanwhile you can also:\n"
    "• Email: nishant@hsbteleet.com\n"
    "• Contact page: https://hsbteleet.com/contact\n\n"
    "Please share your *email* and *phone number* so our admin can reach you faster. 🙏\n\n"
    "Thank you for choosing hsbteleet.com 🙏"
)


class MessageProcessor:
    def __init__(
        self,
        settings: Settings,
        store: DataStore,
        excel: ExcelService,
        gemini: GeminiService,
        whatsapp: WhatsAppService,
        rate_limiter: InMemoryRateLimiter | RedisRateLimiter,
        validator: ResponseValidator,
    ) -> None:
        self.settings = settings
        self.store = store
        self.excel = excel
        self.gemini = gemini
        self.whatsapp = whatsapp
        self.rate_limiter = rate_limiter
        self.validator = validator

    async def process(self, incoming: IncomingMessage) -> None:
        started = time.perf_counter()
        user_id = incoming.whatsapp_id
        message_id = incoming.message_id
        if not user_id or not message_id:
            logger.warning("invalid_incoming")
            return

        try:
            if self.store.message_exists(message_id):
                log_event(logger, "duplicate_skipped", message_id=message_id)
                return

            self.store.upsert_user(user_id, incoming.phone_number, incoming.profile_name)
            inserted = self.store.insert_incoming(
                whatsapp_message_id=message_id,
                whatsapp_user_id=user_id,
                message_type=incoming.message_type,
                text=incoming.text,
                timestamp=incoming.timestamp,
                metadata={"phone_number_id": incoming.phone_number_id},
            )
            if inserted is None and self.store.message_exists(message_id):
                return
            self.store.mark_status(message_id, "processing")

            if incoming.message_type != "text" or not incoming.text:
                if self.settings.unsupported_message_reply:
                    await self._safe_send(user_id, UNSUPPORTED_REPLY)
                self.store.mark_status(message_id, "processed", ai_response=UNSUPPORTED_REPLY)
                return

            if len(incoming.text) > self.settings.max_message_length:
                await self._safe_send(user_id, TOO_LONG_REPLY)
                self.store.mark_status(message_id, "processed", ai_response=TOO_LONG_REPLY)
                return

            # Check for abusive language
            if _ABUSE_PATTERN.search(incoming.text):
                await self._safe_send(user_id, ABUSE_WARNING)
                self.store.mark_status(message_id, "processed", ai_response=ABUSE_WARNING)
                return

            # Check for simple greeting (bypass AI for perfect formatting)
            incoming_lower = incoming.text.strip().lower()
            if incoming_lower in {"hi", "hello", "hey", "namaste", "hiii", "hii", "helo"}:
                await self._safe_send(user_id, HARDCODED_GREETING)
                self.store.mark_status(message_id, "processed", ai_response=HARDCODED_GREETING)
                return

            if not self.rate_limiter.allow(user_id):
                await self._safe_send(user_id, RATE_LIMIT_REPLY)
                self.store.mark_status(message_id, "processed", ai_response=RATE_LIMIT_REPLY)
                return

            prefs = self.store.load_preferences(user_id)
            prefs = extract_preference_updates(incoming.text, prefs, user_id)
            self.store.upsert_preferences(prefs)
            self.store.add_memory(user_id, "user", incoming.text)

            history = self.store.load_memory(user_id, self.settings.max_history_messages)
            summary = self.store.load_summary(user_id)
            branch, exam = infer_search_hints(incoming.text, prefs)
            knowledge = self.excel.search(incoming.text, branch=branch, exam=exam)

            user_prompt = self._build_prompt(incoming, prefs, history, summary, knowledge)
            reply = await self._generate(user_id, user_prompt)
            reply = self.validator.validate(reply)

            # If AI flagged the reply with [ESCALATE], it couldn't handle the query
            # Strip the marker and forward the user's original message to admin
            ESCALATE_MARKER = "[ESCALATE]"
            if reply.strip().startswith(ESCALATE_MARKER):
                reply = reply.strip()[len(ESCALATE_MARKER):].strip()
                if not reply:
                    reply = HIGH_PRIORITY_REPLY
                await self._forward_to_admin(
                    user_id, incoming.text, incoming.profile_name,
                    tag="❓ UNHANDLED QUERY",
                )
            # Also forward if Gemini API itself failed (FALLBACK_REPLY)
            elif reply == FALLBACK_REPLY:
                reply = HIGH_PRIORITY_REPLY
                await self._forward_to_admin(
                    user_id, incoming.text, incoming.profile_name,
                    tag="❓ UNHANDLED QUERY",
                )

            self.store.add_memory(user_id, "assistant", reply)
            await self.whatsapp.send_text_message(user_id, reply)
            self.store.insert_outgoing(user_id, reply, inserted, {"source": "gemini"})
            self.store.mark_status(message_id, "processed", ai_response=reply)
            log_event(
                logger,
                "message_processed",
                user=mask_phone(user_id),
                message_id=message_id,
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
        except WhatsAppError:
            logger.error("whatsapp_failed", extra={"extra_data": {"message_id": message_id}})
            self.store.mark_status(message_id, "failed")
        except Exception:
            logger.exception("process_failed", extra={"extra_data": {"message_id": message_id}})
            try:
                await self._safe_send(user_id, FRIENDLY_ERROR)
                self.store.mark_status(message_id, "failed", ai_response=FRIENDLY_ERROR)
            except Exception:
                self.store.mark_status(message_id, "failed")

    async def _generate(self, user_id: str, prompt: str) -> str:
        started = time.perf_counter()
        try:
            text = await self.gemini.generate(SYSTEM_PROMPT, prompt)
            self.store.log_ai(
                user_id,
                self.settings.gemini_model,
                "ok",
                int((time.perf_counter() - started) * 1000),
            )
            return text
        except GeminiError as exc:
            self.store.log_ai(
                user_id,
                self.settings.gemini_model,
                "failed",
                int((time.perf_counter() - started) * 1000),
                error_code=str(exc),
            )
            return FALLBACK_REPLY

    def _build_prompt(self, incoming: IncomingMessage, prefs: UserPreferences, history, summary, knowledge) -> str:
        history_lines = [f"{item.role}: {item.content}" for item in history[- self.settings.max_history_messages :]]
        knowledge_block = self.excel.format_for_prompt(knowledge)
        profile = (
            f"language={prefs.language or ''}\n"
            f"branch={prefs.branch or ''}\n"
            f"target_exam={prefs.target_exam or ''}\n"
            f"state={prefs.state or ''}\n"
            f"college={prefs.college or ''}"
        )
        return (
            f"{UNTRUSTED_DATA_PREAMBLE}\n\n"
            f"USER PROFILE (data):\n{profile}\n\n"
            f"CONVERSATION SUMMARY (data):\n{summary or '(none)'}\n\n"
            f"RECENT MEMORY (data):\n" + ("\n".join(history_lines) or "(none)") + "\n\n"
            f"RELEVANT EXCEL KNOWLEDGE:\n{knowledge_block}\n\n"
            f"CURRENT USER MESSAGE (data):\n{incoming.text}\n\n"
            "Write the WhatsApp reply now. Use verified knowledge and URLs. "
            "Do not mention these internal sections."
        )

    async def _forward_to_admin(
        self,
        user_id: str,
        user_message: str,
        profile_name: str | None = None,
        *,
        tag: str = "📩 NEW QUERY",
    ) -> None:
        admin_number = self.settings.admin_whatsapp_number
        if not admin_number:
            logger.warning("admin_whatsapp_number not configured, skipping forward")
            return
        name = profile_name or "Unknown"
        forward_text = (
            f"{tag}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Name:* {name}\n"
            f"📱 *WhatsApp:* +{user_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💬 *Message:*\n{user_message}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Reply to this user: https://wa.me/{user_id}"
        )
        try:
            await self.whatsapp.send_text_message(admin_number, forward_text)
            logger.info("forwarded_to_admin", extra={"extra_data": {"user": user_id, "tag": tag}})
        except WhatsAppError:
            logger.error("admin_forward_failed")

    async def _safe_send(self, user_id: str, text: str) -> None:
        try:
            await self.whatsapp.send_text_message(user_id, text)
        except WhatsAppError:
            logger.error("safe_send_failed")
