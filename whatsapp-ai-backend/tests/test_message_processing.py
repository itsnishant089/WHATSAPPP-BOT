from unittest.mock import AsyncMock

import pytest

from app.core.rate_limit import InMemoryRateLimiter
from app.database.queries import InMemoryStore
from app.models.message_models import IncomingMessage
from app.services.excel_service import ExcelService
from app.services.message_processor import MessageProcessor
from app.services.message_service import extract_incoming_messages
from app.services.security_service import RATE_LIMIT_REPLY, ResponseValidator, UNSUPPORTED_REPLY
from tests.conftest import make_settings, sample_text_payload


def test_text_extraction():
    messages = extract_incoming_messages(sample_text_payload("hi"))
    assert len(messages) == 1
    assert messages[0].whatsapp_id == "919999000111"
    assert messages[0].text == "hi"
    assert messages[0].message_id == "wamid.1"


def test_unsupported_image_does_not_crash():
    payload = sample_text_payload()
    payload["entry"][0]["changes"][0]["value"]["messages"][0] = {
        "from": "919999000111",
        "id": "wamid.img",
        "timestamp": "1",
        "type": "image",
        "image": {"id": "x"},
    }
    messages = extract_incoming_messages(payload)
    assert messages[0].message_type == "image"
    assert messages[0].text is None


def _processor(store: InMemoryStore, excel: ExcelService) -> MessageProcessor:
    settings = make_settings()
    gemini = AsyncMock()
    gemini.generate = AsyncMock(return_value="Bilkul 👍 CSE syllabus: https://hsbteleet.com/hsbte-syllabus")
    whatsapp = AsyncMock()
    whatsapp.send_text_message = AsyncMock()
    return MessageProcessor(
        settings=settings,
        store=store,
        excel=excel,
        gemini=gemini,
        whatsapp=whatsapp,
        rate_limiter=InMemoryRateLimiter(30),
        validator=ResponseValidator(settings),
    )


@pytest.mark.asyncio
async def test_duplicate_message(tmp_path):
    excel = ExcelService(tmp_path)
    excel.rows = []
    store = InMemoryStore()
    processor = _processor(store, excel)
    incoming = IncomingMessage(
        whatsapp_id="919999000111",
        message_id="wamid.dup",
        message_type="text",
        text="hi",
    )
    await processor.process(incoming)
    await processor.process(incoming)
    assert processor.whatsapp.send_text_message.await_count == 1


@pytest.mark.asyncio
async def test_gemini_failure_fallback(tmp_path):
    excel = ExcelService(tmp_path)
    excel.rows = []
    store = InMemoryStore()
    processor = _processor(store, excel)
    from app.services.gemini_service import GeminiError

    processor.gemini.generate = AsyncMock(side_effect=GeminiError("down"))
    incoming = IncomingMessage(
        whatsapp_id="919999000111",
        message_id="wamid.ai",
        message_type="text",
        text="syllabus bhejo",
    )
    await processor.process(incoming)
    sent = processor.whatsapp.send_text_message.await_args.args[1]
    assert "high priority" in sent.lower() or "admin" in sent.lower()


@pytest.mark.asyncio
async def test_whatsapp_failure_marks_failed(tmp_path):
    from app.services.whatsapp_service import WhatsAppError

    excel = ExcelService(tmp_path)
    excel.rows = []
    store = InMemoryStore()
    processor = _processor(store, excel)
    processor.whatsapp.send_text_message = AsyncMock(side_effect=WhatsAppError("boom"))
    incoming = IncomingMessage(
        whatsapp_id="919999000111",
        message_id="wamid.wa",
        message_type="text",
        text="hi",
    )
    await processor.process(incoming)
    assert store.messages["wamid.wa"]["status"] == "failed"


@pytest.mark.asyncio
async def test_rate_limit(tmp_path):
    excel = ExcelService(tmp_path)
    excel.rows = []
    store = InMemoryStore()
    processor = _processor(store, excel)
    processor.rate_limiter = InMemoryRateLimiter(1)
    first = IncomingMessage(whatsapp_id="919999000111", message_id="wamid.r1", message_type="text", text="hi")
    second = IncomingMessage(whatsapp_id="919999000111", message_id="wamid.r2", message_type="text", text="syllabus")
    await processor.process(first)
    await processor.process(second)
    last = processor.whatsapp.send_text_message.await_args.args[1]
    assert last == RATE_LIMIT_REPLY


@pytest.mark.asyncio
async def test_unsupported_type_reply(tmp_path):
    excel = ExcelService(tmp_path)
    excel.rows = []
    store = InMemoryStore()
    processor = _processor(store, excel)
    incoming = IncomingMessage(
        whatsapp_id="919999000111",
        message_id="wamid.doc",
        message_type="document",
        text=None,
    )
    await processor.process(incoming)
    assert processor.whatsapp.send_text_message.await_args.args[1] == UNSUPPORTED_REPLY
