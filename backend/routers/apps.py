from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel

from apps.detector import detect_all_apps
from apps.export_dispatch import export_application

router = APIRouter()


class AppExportRequest(BaseModel):
    app_id: str
    dest_path: str
    full_backup: bool = True


@router.get("/detect")
async def detect_apps():
    return detect_all_apps()


@router.post("/export")
async def export_app(req: AppExportRequest) -> Dict[str, Any]:
    return export_application(req.app_id, req.dest_path, req.full_backup)
