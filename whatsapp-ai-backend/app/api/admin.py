from fastapi import APIRouter, Request

from app.core.security import require_admin

router = APIRouter()


@router.post("/admin/reload-knowledge")
async def reload_knowledge(request: Request) -> dict[str, str | int]:
    settings = request.app.state.settings
    require_admin(request, settings)
    excel = request.app.state.excel
    excel.reload()
    return {"status": "reloaded", "rows": len(excel.rows), "errors": len(excel.errors)}
