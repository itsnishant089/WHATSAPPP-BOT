from __future__ import annotations

from functools import lru_cache
from typing import Any

from supabase import Client, create_client

from app.core.config import Settings


def create_supabase_client(settings: Settings) -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


@lru_cache
def get_supabase(settings: Settings) -> Client:
    return create_supabase_client(settings)
