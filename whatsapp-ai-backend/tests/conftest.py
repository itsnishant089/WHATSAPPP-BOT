import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("META_APP_SECRET", "test_app_secret")
os.environ.setdefault("META_VERIFY_TOKEN", "test_verify_token")
os.environ.setdefault("WHATSAPP_ACCESS_TOKEN", "test_wa_token")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "123456789")
os.environ.setdefault("GEMINI_API_KEY", "test_gemini_key")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test_service_role_key")
os.environ.setdefault("REQUIRE_WEBHOOK_SIGNATURE", "true")
os.environ.setdefault("ADMIN_API_KEY", "test_admin_key")
os.environ.setdefault("RATE_LIMIT_PER_MINUTE", "30")

import hmac
import hashlib
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, clear_settings_cache
from app.main import create_app


def make_settings(**overrides) -> Settings:
    clear_settings_cache()
    data = {
        "meta_app_secret": "test_app_secret",
        "meta_verify_token": "test_verify_token",
        "whatsapp_access_token": "test_wa_token",
        "whatsapp_phone_number_id": "123456789",
        "gemini_api_key": "test_gemini_key",
        "supabase_url": "https://example.supabase.co",
        "supabase_service_role_key": "test_service_role_key",
        "environment": "test",
        "require_webhook_signature": True,
        "admin_api_key": "test_admin_key",
    }
    data.update(overrides)
    return Settings(**data)


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def client(settings: Settings) -> TestClient:
    app = create_app(settings)
    with TestClient(app) as test_client:
        app.state.processor.process = AsyncMock()
        yield test_client


def sign(body: bytes, secret: str = "test_app_secret") -> str:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def sample_text_payload(text: str = "LEET syllabus bhejo", message_id: str = "wamid.1") -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "123456789"},
                            "contacts": [{"profile": {"name": "Student"}, "wa_id": "919999000111"}],
                            "messages": [
                                {
                                    "from": "919999000111",
                                    "id": message_id,
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": text},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
