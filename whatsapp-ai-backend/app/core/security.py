import hashlib
import hmac
import secrets as pysecrets

from fastapi import HTTPException, Request, status

from app.core.config import Settings


def verify_meta_signature(raw_body: bytes, signature: str | None, app_secret: str) -> bool:
    """Validate X-Hub-Signature-256 over the raw request body.

    Meta sends: sha256=<hex digest>
    """
    if not signature or not app_secret:
        return False
    provided = signature.strip()
    if provided.lower().startswith("sha256="):
        provided = provided.split("=", 1)[1]
    expected = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, provided)


def tokens_match(provided: str, expected: str) -> bool:
    if not provided or not expected:
        return False
    return pysecrets.compare_digest(provided, expected)


def require_admin(request: Request, settings: Settings) -> None:
    if not settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API is not configured",
        )
    header = request.headers.get("x-admin-key") or request.headers.get("authorization", "")
    token = header.removeprefix("Bearer ").strip() if header.lower().startswith("bearer ") else header
    if not tokens_match(token, settings.admin_api_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def payload_hash(raw_body: bytes) -> str:
    return hashlib.sha256(raw_body).hexdigest()


def contains_secret(text: str, secrets: list[str]) -> bool:
    if not text:
        return False
    lowered = text.lower()
    for secret in secrets:
        if secret and secret.lower() in lowered:
            return True
    return False
