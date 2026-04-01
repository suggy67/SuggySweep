from typing import Any, Dict, Literal

from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse

from core.installed_programs import list_installed_programs
from core.reinstall_script import generate_plain_list, generate_powershell

router = APIRouter()


@router.get("/list")
async def programs_list(limit: int = Query(4000, ge=1, le=20000)) -> Dict[str, Any]:
    return list_installed_programs(limit=limit)


@router.get("/reinstall-script")
async def reinstall_script(
    fmt: Literal["powershell", "txt"] = Query("powershell", alias="format"),
    limit: int = Query(8000, ge=1, le=20000),
) -> PlainTextResponse:
    data = list_installed_programs(limit=limit)
    programs = data.get("programs", [])
    if fmt == "txt":
        body = generate_plain_list(programs)
        filename = "suggy-programs-list.txt"
    else:
        body = generate_powershell(programs)
        filename = "suggy-reinstall.ps1"
    return PlainTextResponse(
        body,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
