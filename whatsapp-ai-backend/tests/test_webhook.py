import json

from tests.conftest import sample_text_payload, sign


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "whatsapp-ai-backend"
    assert "version" in body
    assert "gemini" not in json.dumps(body).lower()


def test_webhook_verify_ok(client):
    response = client.get(
        "/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "test_verify_token", "hub.challenge": "challenge-123"},
    )
    assert response.status_code == 200
    assert response.text == "challenge-123"


def test_webhook_verify_wrong_token(client):
    response = client.get(
        "/webhook/whatsapp",
        params={"hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "challenge-123"},
    )
    assert response.status_code == 403


def test_post_valid_signature(client):
    payload = sample_text_payload()
    raw = json.dumps(payload).encode()
    response = client.post(
        "/webhook/whatsapp",
        content=raw,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sign(raw)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_post_invalid_signature(client):
    payload = sample_text_payload()
    raw = json.dumps(payload).encode()
    response = client.post(
        "/webhook/whatsapp",
        content=raw,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=deadbeef"},
    )
    assert response.status_code == 403


def test_malformed_webhook(client):
    raw = b"not-json"
    response = client.post(
        "/webhook/whatsapp",
        content=raw,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sign(raw)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_admin_reload_requires_key(client):
    response = client.post("/admin/reload-knowledge")
    assert response.status_code == 403


def test_admin_reload_ok(client):
    response = client.post("/admin/reload-knowledge", headers={"X-Admin-Key": "test_admin_key"})
    assert response.status_code == 200
    assert response.json()["status"] == "reloaded"
