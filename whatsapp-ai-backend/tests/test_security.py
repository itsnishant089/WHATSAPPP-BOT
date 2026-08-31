from app.core.security import verify_meta_signature
from app.utils.phone import is_valid_recipient, normalize_whatsapp_id
from tests.conftest import sign


def test_valid_signature():
    body = b'{"object":"whatsapp_business_account"}'
    header = sign(body)
    assert verify_meta_signature(body, header, "test_app_secret") is True


def test_invalid_signature():
    body = b'{"object":"whatsapp_business_account"}'
    assert verify_meta_signature(body, "sha256=00", "test_app_secret") is False


def test_missing_signature():
    assert verify_meta_signature(b"{}", None, "test_app_secret") is False


def test_phone_validation():
    assert normalize_whatsapp_id("+91 99990 00111") == "919999000111"
    assert is_valid_recipient("919999000111") is True
    assert is_valid_recipient("12") is False
