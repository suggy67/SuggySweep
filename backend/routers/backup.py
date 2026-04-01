from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backup.backup_manager import BackupManager

router = APIRouter()
_manager = BackupManager()


class BackupCreateRequest(BaseModel):
    files: List[Dict[str, Any]]
    dest_drive: str = Field(..., description="Буква или путь, например D: или D:\\")
    backup_name: Optional[str] = None
    compression: Literal["folder", "zip"] = "folder"


class RestoreRequest(BaseModel):
    backup_path: str
    restore_items: Optional[List[str]] = None
    dest_base: Optional[str] = None


class PreviewRequest(BaseModel):
    backup_path: str
    preview_limit: int = Field(500, ge=1, le=5000)


@router.post("/preview")
async def preview_backup(req: PreviewRequest) -> Dict[str, Any]:
    return _manager.preview_manifest(req.backup_path, preview_limit=req.preview_limit)


@router.post("/create")
async def create_backup(req: BackupCreateRequest) -> Dict[str, Any]:
    drive = req.dest_drive.rstrip("\\")
    if len(drive) == 1:
        drive = f"{drive}:\\"
    elif not drive.endswith(":"):
        drive = drive + "\\" if not drive.endswith("\\") else drive
    elif drive.endswith(":") and len(drive) == 2:
        drive = drive + "\\"

    return _manager.create_backup(
        req.files,
        drive,
        backup_name=req.backup_name,
        compression=req.compression,
    )


@router.post("/restore")
async def restore_backup(req: RestoreRequest) -> Dict[str, Any]:
    return _manager.restore_backup(
        req.backup_path,
        restore_items=req.restore_items,
        dest_base=req.dest_base,
    )
