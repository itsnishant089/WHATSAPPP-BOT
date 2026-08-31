from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.api.webhook import router as webhook_router
from app.core.config import Settings, get_settings
from app.core.logging import setup_logging
from app.core.rate_limit import build_rate_limiter
from app.database.queries import InMemoryStore, SupabaseStore
from app.database.supabase import create_supabase_client
from app.services.excel_service import ExcelService
from app.services.gemini_service import GeminiService
from app.services.message_processor import MessageProcessor
from app.services.security_service import ResponseValidator
from app.services.whatsapp_service import WhatsAppService

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    http_client = httpx.AsyncClient(timeout=timeout)
    app.state.http = http_client

    excel = ExcelService(DATA_DIR)
    excel.load()
    app.state.excel = excel

    if settings.environment == "test":
        store = InMemoryStore()
    else:
        supabase = create_supabase_client(settings)
        store = SupabaseStore(supabase)
    app.state.store = store

    gemini = GeminiService(settings, http_client)
    whatsapp = WhatsAppService(settings, http_client)
    processor = MessageProcessor(
        settings=settings,
        store=store,
        excel=excel,
        gemini=gemini,
        whatsapp=whatsapp,
        rate_limiter=build_rate_limiter(settings.rate_limit_per_minute, settings.redis_url),
        validator=ResponseValidator(settings),
    )
    app.state.processor = processor
    yield
    await http_client.aclose()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging(settings)
    docs_url = None if settings.is_production else "/docs"
    app = FastAPI(
        title="WhatsApp AI Backend",
        version=settings.app_version,
        docs_url=docs_url,
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.add_middleware(SecurityHeadersMiddleware)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "X-Admin-Key"],
        )
    app.include_router(health_router)
    app.include_router(webhook_router)
    app.include_router(admin_router)
    return app


app = create_app()
