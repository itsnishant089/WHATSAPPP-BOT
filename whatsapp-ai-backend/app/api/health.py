from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {
        "status": "ok",
        "service": "whatsapp-ai-backend",
        "version": settings.app_version,
    }


@router.get("/health/dependencies")
async def health_dependencies(request: Request) -> dict[str, str]:
    excel = request.app.state.excel
    return {
        "status": "ok",
        "excel_rows": str(len(excel.rows)),
        "excel_errors": str(len(excel.errors)),
        "gemini_model": "configured" if request.app.state.settings.gemini_api_key else "missing",
        "supabase": "configured",
    }
