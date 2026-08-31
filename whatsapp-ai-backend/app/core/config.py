from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    meta_app_id: str = ""
    meta_app_secret: str
    meta_verify_token: str
    meta_graph_api_version: str = "v21.0"

    whatsapp_access_token: str
    whatsapp_business_account_id: str = ""
    whatsapp_phone_number_id: str

    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    supabase_url: str
    supabase_service_role_key: str

    environment: Literal["development", "staging", "production", "test"] = "development"
    log_level: str = "INFO"
    app_version: str = "1.0.0"

    webhook_path: str = "/webhook/whatsapp"
    require_webhook_signature: bool = True

    max_message_length: int = 4000
    max_history_messages: int = 20
    max_ai_output_chars: int = 3500
    whatsapp_max_chars: int = 4096

    rate_limit_per_minute: int = 30
    redis_url: str = ""

    admin_api_key: str = ""
    admin_whatsapp_number: str = ""

    http_timeout_seconds: float = 20.0
    gemini_timeout_seconds: float = 45.0
    whatsapp_timeout_seconds: float = 20.0
    supabase_timeout_seconds: float = 15.0

    message_retention_days: int = 180
    unsupported_message_reply: bool = True

    cors_allowed_origins: str = ""

    enable_vector_search: bool = False

    @field_validator("webhook_path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        if not value.startswith("/"):
            return "/" + value
        return value

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def cors_origins(self) -> list[str]:
        if not self.cors_allowed_origins.strip():
            return []
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @property
    def secret_values(self) -> list[str]:
        values = [
            self.meta_app_secret,
            self.whatsapp_access_token,
            self.gemini_api_key,
            self.supabase_service_role_key,
            self.admin_api_key,
        ]
        return [v for v in values if v and len(v) >= 8]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


def clear_settings_cache() -> None:
    get_settings.cache_clear()
